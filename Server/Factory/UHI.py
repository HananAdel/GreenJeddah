import ee
import os
from Factory.EcoVariable import EcoVariable


class UHI(EcoVariable):
    def __init__(self, name, location, startTime, endTime):
        super().__init__(name, location, startTime, endTime)
        

    def retrieveData(self):
        collection = (
            ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
            .filterDate(self.startTime, self.endTime)
            .filterBounds(self.location)
        )
        return collection
        
        
    def generateMap(self):
        try:
            def apply_scale_factors(image):
                optical = image.select('SR_B.').multiply(0.0000275).add(-0.2)
                thermal = image.select('ST_B.*').multiply(0.00341802).add(149.0)
                return image.addBands(optical, None, True).addBands(thermal, None, True)

            def mask_clouds(image):
                qa = image.select('QA_PIXEL')
                cloud = qa.bitwiseAnd(1 << 3).eq(0).And(qa.bitwiseAnd(1 << 5).eq(0))
                return image.updateMask(cloud)

            collection = self.retrieveData().map(apply_scale_factors).map(mask_clouds)
            image = collection.median().clip(self.location)

            ndvi = image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
            ndvi_stats = ndvi.reduceRegion(ee.Reducer.minMax(), self.location, 100)
            ndvi_min = ee.Number(ndvi_stats.get('NDVI_min'))
            ndvi_max = ee.Number(ndvi_stats.get('NDVI_max'))

            fv = ndvi.subtract(ndvi_min).divide(ndvi_max.subtract(ndvi_min)).pow(2).rename('FV')
            em = fv.multiply(0.004).add(0.986)

            thermal = image.select('ST_B10').rename('thermal')

            lst = thermal.expression(
                '(tb / (1 + ((11.5 * (tb / 14380)) * log(em)))) - 273.15',
                {'tb': thermal, 'em': em}
            ).rename('LST')

            if self.name == "LST":
                index_image = lst
                vis_params = {'min': 7, 'max': 50,
                            'palette':  [
                '040274', '040281', '0502a3', '0502b8', '0502ce', '0502e6',
                '0602ff', '235cb1', '307ef3', '269db1', '30c8e2', '32d3ef',
                '3be285', '3ff38f', '86e26f', '3ae237', 'b5e22e', 'd6e21f',
                'fff705', 'ffd611', 'ffb613', 'ff8b13', 'ff6e08', 'ff500d',
                'ff0000', 'de0101', 'c21301', 'a71001', '911003'
            ]}
                # Save mean and std
                self.lst_mean = lst.reduceRegion(ee.Reducer.mean(), self.location, 100).get('LST').getInfo()
                self.lst_std = lst.reduceRegion(ee.Reducer.stdDev(), self.location, 100).get('LST').getInfo()

            elif self.name == "UHI":
                lst_mean = lst.reduceRegion(ee.Reducer.mean(), self.location, 100).get('LST')
                lst_std = lst.reduceRegion(ee.Reducer.stdDev(), self.location, 100).get('LST')
                index_image = lst.subtract(ee.Image.constant(lst_mean)).divide(ee.Image.constant(lst_std)).rename('UHI')

                vis_params = {'min': -4, 'max': 4,
                            'palette': ['313695', '74add1', 'fed976', 'feb24c', 'fd8d3c', 'fc4e2a', 'e31a1c', 'b10026']}
                # Save mean and std
                self.lst_mean = lst_mean.getInfo()
                self.lst_std = lst_std.getInfo()

            elif self.name == "UTFVI":
                lst_mean = lst.reduceRegion(ee.Reducer.mean(), self.location, 100).get('LST')
                index_image = lst.subtract(ee.Image.constant(lst_mean)).divide(lst).rename('UTFVI')
                vis_params = {'min': -1, 'max': 0.3,
                            'palette': ['313695', '74add1', 'fed976', 'feb24c', 'fd8d3c', 'fc4e2a', 'e31a1c', 'b10026']}
                # Save mean only (UTFVI doesn't need std)
                self.lst_mean = lst_mean.getInfo()
                self.lst_std = None

            else:
                raise ValueError("Invalid selected index")

            map_id_dict = index_image.getMapId(vis_params)

            import folium
            m = folium.Map(location=[21.4858, 39.1896], zoom_start=11)

            admin_boundaries = ee.FeatureCollection("projects/inlaid-crane-446610-m5/assets/JEDAdminstrative_Boundaries")
            boundary_geojson = admin_boundaries.getInfo()

            folium.GeoJson(
                boundary_geojson,
                name="Administrative Boundaries",
                style_function=lambda feature: {
                    "fillColor": "green",
                    "color": "black",
                    "weight": 1,
                    "fillOpacity": 0
                }
            ).add_to(m)

            folium.raster_layers.TileLayer(
                tiles=map_id_dict['tile_fetcher'].url_format,
                attr=f'{self.name} Map',
                name=self.name,
                overlay=True,
                control=True
            ).add_to(m)

            folium.TileLayer(
                tiles="https://mt1.google.com/vt/lyrs=h&x={x}&y={y}&z={z}",
                attr="Google Labels",
                name="Labels",
                overlay=True,
                control=True
            ).add_to(m)

            folium.LayerControl().add_to(m)

             # Save inside Server/static/
            static_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
            os.makedirs(static_folder, exist_ok=True)

            output_path = os.path.join(static_folder, f"{self.name}_map.html")
            m.save(output_path)

            return f"static/{self.name}_map.html"

            
        except Exception as e:
            print("[UHI Map Error]", str(e))
            raise e

    def generateChart(self, aggregation="daily"):
            collection = self.retrieveData()

            # Decide date format based on aggregation
            if aggregation == "monthly":
                date_format = "YYYY-MM"
            elif aggregation == "yearly":
                date_format = "YYYY"
            else:
                date_format = "YYYY-MM-dd"

            def apply(img):
                optical = img.select('SR_B.').multiply(0.0000275).add(-0.2)
                thermal = img.select('ST_B.*').multiply(0.00341802).add(149.0)
                img = img.addBands(optical, None, True).addBands(thermal, None, True)
                ndvi = img.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')

                ndvi_stats = ndvi.reduceRegion(ee.Reducer.minMax(), self.location, 100)
                ndvi_min = ee.Number(ndvi_stats.get('NDVI_min'))
                ndvi_max = ee.Number(ndvi_stats.get('NDVI_max'))

                fv = ndvi.subtract(ndvi_min).divide(ndvi_max.subtract(ndvi_min)).pow(2).rename('FV')
                em = fv.multiply(0.004).add(0.986)

                thermal = img.select('ST_B10').rename('thermal')

                lst = thermal.expression(
                    '(tb / (1 + ((11.5 * (tb / 14380)) * log(em)))) - 273.15',
                    {'tb': thermal, 'em': em}
                ).rename('LST')

                if self.name == "LST":
                    index = lst
                elif self.name == "UHI":
                    lst_mean = lst.reduceRegion(ee.Reducer.mean(), self.location, 100).get('LST')
                    lst_std = lst.reduceRegion(ee.Reducer.stdDev(), self.location, 100).get('LST')
                    index = lst.subtract(ee.Image.constant(lst_mean)).divide(ee.Image.constant(lst_std)).rename('UHI')
                elif self.name == "UTFVI":
                    lst_mean = lst.reduceRegion(ee.Reducer.mean(), self.location, 100).get('LST')
                    index = lst.subtract(ee.Image.constant(lst_mean)).divide(lst).rename('UTFVI')
                else:
                    raise ValueError("Invalid selected index")

                mean_val = index.reduceRegion(
                    reducer=ee.Reducer.mean(),
                    geometry=self.location,
                    scale=100,
                    maxPixels=1e9
                ).get(self.name)

                return ee.Feature(None, {
                    "date": img.date().format(date_format),
                    "value": mean_val
                })



            processed = collection.map(apply).filter(ee.Filter.notNull(["value"]))

            features = processed.aggregate_array('date').getInfo()
            values = processed.aggregate_array('value').getInfo()

            from collections import defaultdict
            from statistics import mean as stat_mean

            # Group by aggregation (date format)
            buckets = defaultdict(list)
            for d, v in zip(features, values):
                buckets[d].append(v)

            # Calculate average per bucket
            chart_data = [
                {"date": date, "value": round(stat_mean(vals), 6)}
                for date, vals in sorted(buckets.items())
            ]

            return chart_data


    def generateAiAnalysis(self):
        if self.lst_mean is None:
            return "Statistics are not available to generate analysis."

        std_val = self.lst_std if self.lst_std is not None else 0.0

        description = f"{self.name} mean: {self.lst_mean:.2f}, std dev: {std_val:.2f}"

        return self.gemini.generate(description, self.startTime, self.endTime)


