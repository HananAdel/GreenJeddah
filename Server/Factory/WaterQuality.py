import ee
import folium
from Factory.EcoVariable import EcoVariable

class WaterQuality(EcoVariable):
    def __init__(self, name, location, startTime, endTime):
        # location = ee.Geometry.Rectangle([38.381, 22.246, 39.966, 20.813]) This location was for testing
        super().__init__(name, location, startTime, endTime)
        self.dataset = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        self.admin_boundaries = ee.FeatureCollection("projects/inlaid-crane-446610-m5/assets/JEDAdminstrative_Boundaries")

    def retrieveData(self):
        # Load the collection
        collection = (
            self.dataset
            .filterBounds(self.location)
            .filterDate(self.startTime, self.endTime)
        )
        # Cloud mask per image
        def mask_clouds(image):
            qa = image.select('QA60')
            cloud_bit_mask = 1 << 10
            cirrus_bit_mask = 1 << 11
            mask = qa.bitwiseAnd(cloud_bit_mask).eq(0).And(
                qa.bitwiseAnd(cirrus_bit_mask).eq(0)
            )
            return image.updateMask(mask)  
        
        # Apply cloud masking on each image
        collection_masked = collection.map(mask_clouds)

        # Take median AFTER masking
        median_image = collection_masked.median()
        return median_image



    def generateMap(self,suffix=""):
        image = self.retrieveData()

        # Calculate indices
        ndwi = image.normalizedDifference(['B3', 'B8']).rename('NDWI')
        mndwi = image.normalizedDifference(['B3', 'B11']).rename('MNDWI')
        b2 = image.select('B2').divide(10000)
        b3 = image.select('B3').divide(10000)
        turbidity = b2.divide(b3).rename('Turbidity')

        if self.name == 'NDWI':
            index_image = ndwi
            vis_params = {'min': -0.5, 'max': 0.5, 'palette': ['#FF0000', '#FFD700', '#0000FF']}
        elif self.name == 'MNDWI':
            index_image = mndwi
            vis_params = {'min': -0.5, 'max': 0.5, 'palette': ['#8B4513', '#32CD32', '#1E90FF']}
        elif self.name == 'Turbidity':
            index_image = turbidity
            vis_params = {'min': 0.2, 'max': 1.5, 'palette': ['#00FFFF', '#FFFF00', '#FF4500']}
        else:
            raise ValueError("Invalid water quality index selected.")

        # DO NOT apply land mask!!
        # Only clip to the rectangle
        index_image = index_image.clip(self.location)

        map_id_dict = index_image.getMapId(vis_params)

        m = folium.Map(location=[21.48581, 39.19797], zoom_start=10)
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

        output_file = f"static/{self.name}_map{suffix}.html"
        m.save(output_file) 
        return output_file


    def generateChart(self, aggregation="daily"):
        if aggregation == "monthly":
            date_format = "YYYY-MM"
        elif aggregation == "yearly":
            date_format = "YYYY"
        else:
            date_format = "YYYY-MM-dd"

        # Load collection
        collection = (
            self.dataset
            .filterBounds(self.location)
            .filterDate(self.startTime, self.endTime)
        )

        # Cloud masking function
        def mask_clouds(image):
            qa = image.select('QA60')
            cloud_bit_mask = 1 << 10
            cirrus_bit_mask = 1 << 11
            mask = qa.bitwiseAnd(cloud_bit_mask).eq(0).And(
                qa.bitwiseAnd(cirrus_bit_mask).eq(0)
            )
            return image.updateMask(mask)

        # Apply cloud masking
        collection_masked = collection.map(mask_clouds)

        # Calculate index for each image
        def compute_index(img):
            if self.name == "NDWI":
                index = img.normalizedDifference(['B3', 'B8']).rename('index')
            elif self.name == "MNDWI":
                index = img.normalizedDifference(['B3', 'B11']).rename('index')
            elif self.name == "Turbidity":
                #scale values then divide
                b2 = img.select('B2').divide(10000)
                b3 = img.select('B3').divide(10000)
                index = b2.divide(b3).rename('index')
            
            mean = index.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=self.location,
                scale=20,
                maxPixels=1e9
            ).get('index')

            return img.set('mean_val', mean).set('date', img.date().format(date_format))

        collection_indexed = collection_masked.map(compute_index)
        collection_indexed = collection_indexed.filter(ee.Filter.notNull(["mean_val"]))

        feature_list = collection_indexed.getInfo()["features"]

        from collections import defaultdict
        from statistics import mean as stat_mean

        # Extract list of (date, value)
        date_val_pairs = [
            (f["properties"]["date"], f["properties"]["mean_val"])
            for f in feature_list
        ]

        # Group by date
        buckets = defaultdict(list)
        for date, val in date_val_pairs:
            buckets[date].append(val)

        # Calculate mean per group
        chart_data = [
            {"date": date, "value": round(stat_mean(vals), 6)}
            for date, vals in sorted(buckets.items())
        ]
        #Save one general mean value for AI analysis
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
