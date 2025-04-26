import ee
import folium
from Factory.EcoVariable import EcoVariable
from collections import defaultdict
from statistics import mean as stat_mean

class Drought(EcoVariable):
    def __init__(self, name, location, startTime, endTime):
        super().__init__(name, location, startTime, endTime)
        self.admin_boundaries = ee.FeatureCollection("projects/inlaid-crane-446610-m5/assets/JEDAdminstrative_Boundaries")

    def retrieveData(self):
        ndvi_collection = (
            ee.ImageCollection("MODIS/061/MOD13Q1")
            .filterBounds(self.location)
            .filterDate(self.startTime, self.endTime)
            .select("NDVI")
        )
        return ndvi_collection

    def generateMap(self):
        ndvi_collection = self.retrieveData()

        ndvi_min = ndvi_collection.reduce(ee.Reducer.min())
        ndvi_max = ndvi_collection.reduce(ee.Reducer.max())
        ndvi_mean = ndvi_collection.reduce(ee.Reducer.mean())
        ndvi_stddev = ndvi_collection.reduce(ee.Reducer.stdDev())

        # Get latest image, fallback to mean
        latest_ndvi_raw = ndvi_collection.sort("system:time_start", False).first()
        latest_ndvi = ee.Image(ee.Algorithms.If(latest_ndvi_raw, latest_ndvi_raw, ndvi_mean))

        if self.name == "VCI":
            drought_index = latest_ndvi.subtract(ndvi_min).divide(ndvi_max.subtract(ndvi_min)).rename("VCI")
            vis_params = {'min': 0, 'max': 1, 'palette': ['red', 'yellow', 'green']}
        elif self.name == "DSI":
            drought_index = latest_ndvi.subtract(ndvi_mean).divide(ndvi_stddev).rename("DSI")
            vis_params = {'min': -3, 'max': 3, 'palette': ['red', 'yellow', 'green']}
        elif self.name == "NDVI":
            drought_index = latest_ndvi.rename("NDVI")
            vis_params = {'min': -2000, 'max': 10000, 'palette': ['blue', 'white', 'green']}
        else:
            raise ValueError("Invalid drought index selected.")

        # Reproject to WGS84 before clipping
        drought_index = drought_index.reproject(crs="EPSG:4326", scale=1000)
        drought_index = drought_index.clip(self.location)

        map_id_dict = drought_index.getMapId(vis_params)

        m = folium.Map(location=[21.48581, 39.19797], zoom_start=11)
        folium.raster_layers.TileLayer(
            tiles=map_id_dict['tile_fetcher'].url_format,
            attr=f'{self.name} Data',
            name=self.name,
            overlay=True,
            control=True
        ).add_to(m)

        boundary_geojson = self.admin_boundaries.getInfo()
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

        folium.TileLayer(
            tiles="https://mt1.google.com/vt/lyrs=h&x={x}&y={y}&z={z}",
            attr="Google Labels",
            name="Labels",
            overlay=True,
            control=True
        ).add_to(m)

        folium.LayerControl().add_to(m)

        output_file = f"static/{self.name}_map.html"
        m.save(output_file)
        return output_file

    def generateChart(self, aggregation="daily"):
        if aggregation == "monthly":
            date_format = "YYYY-MM"
        elif aggregation == "yearly":
            date_format = "YYYY"
        else:
            date_format = "YYYY-MM-dd"

        ndvi_collection = (
            ee.ImageCollection("MODIS/061/MOD13Q1")
            .filterBounds(self.location)
            .filterDate(self.startTime, self.endTime)
            .select("NDVI")
        )

        ndvi_min = ndvi_collection.reduce(ee.Reducer.min())
        ndvi_max = ndvi_collection.reduce(ee.Reducer.max())
        ndvi_mean = ndvi_collection.reduce(ee.Reducer.mean())
        ndvi_stddev = ndvi_collection.reduce(ee.Reducer.stdDev())

        def compute_index(img):
            if self.name == "VCI":
                index = img.subtract(ndvi_min).divide(ndvi_max.subtract(ndvi_min)).rename("index")
            elif self.name == "DSI":
                index = img.subtract(ndvi_mean).divide(ndvi_stddev).rename("index")
            elif self.name == "NDVI":
                index = img.multiply(0.0001).rename("index")
            else:
                raise ValueError("Invalid drought index selected.")

            mean = index.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=self.location,
                scale=1000,
                maxPixels=1e13
            ).get("index")

            return img.set("mean_val", mean).set("date", img.date().format(date_format))

        collection_indexed = ndvi_collection.map(compute_index)
        collection_indexed = collection_indexed.filter(ee.Filter.notNull(["mean_val"]))

        feature_list = collection_indexed.getInfo()["features"]

        

        date_val_pairs = [
            (f["properties"]["date"], f["properties"]["mean_val"])
            for f in feature_list
        ]

        buckets = defaultdict(list)
        for date, val in date_val_pairs:
            buckets[date].append(val)

        chart_data = [
            {"date": date, "value": round(stat_mean(vals), 6)}
            for date, vals in sorted(buckets.items())
        ]
        # Save mean value for AI analysis
        all_means = [d["value"] for d in chart_data]
        if all_means:
            self.mean_val = round(stat_mean(all_means), 6)
        else:
            self.mean_val = None

        return chart_data

    def generateAiAnalysis(self):
        if self.mean_val is None:
            return "Statistics are not available to generate analysis."
        
        description = f"{self.name} mean: {self.mean_val:.6f}"
        return self.gemini.generate(description, self.startTime, self.endTime)


    def legendHTML(self):
        return f'''
        <div style="position: fixed; bottom: 50px; left: 50px; width: 250px; height: 220px; background-color: white; z-index:9999; font-size:14px; border-radius: 10px; padding: 10px; box-shadow: 3px 3px 5px rgba(0,0,0,0.4);">
            <b>{self.name} Concentration Levels</b><br>
            <i>(units vary by index)</i><br>
            <div style="background:black; width:20px; height:20px; display:inline-block"></div> Very Low<br>
            <div style="background:blue; width:20px; height:20px; display:inline-block"></div> Low<br>
            <div style="background:purple; width:20px; height:20px; display:inline-block"></div> Moderate<br>
            <div style="background:cyan; width:20px; height:20px; display:inline-block"></div> Slightly High<br>
            <div style="background:green; width:20px; height:20px; display:inline-block"></div> High<br>
            <div style="background:yellow; width:20px; height:20px; display:inline-block"></div> Very High<br>
            <div style="background:red; width:20px; height:20px; display:inline-block"></div> Extreme<br>
        </div>
        '''
