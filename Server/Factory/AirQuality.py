import ee
import folium
from Factory.EcoVariable import EcoVariable
from collections import defaultdict
from statistics import mean

class AirQuality(EcoVariable):
    def __init__(self, name, location, startTime, endTime):
        super().__init__(name, location, startTime, endTime)
        self.dataset_mapping = {
            "NO2": ('COPERNICUS/S5P/NRTI/L3_NO2', 'NO2_column_number_density', {'min': 0, 'max': 0.0002, 'palette': ['black', 'blue', 'purple', 'cyan', 'green', 'yellow', 'red']}),
            "SO2": ('COPERNICUS/S5P/OFFL/L3_SO2', 'SO2_column_number_density', {'min': 0.0, 'max': 0.0005, 'palette': ['black', 'blue', 'purple', 'cyan', 'green', 'yellow', 'red']}),
            "CO": ('COPERNICUS/S5P/OFFL/L3_CO', 'CO_column_number_density', {'min': 0.0, 'max': 0.05, 'palette': ['black', 'blue', 'purple', 'cyan', 'green', 'yellow', 'red']}),
            "Aerosol": ('COPERNICUS/S5P/OFFL/L3_AER_AI', 'absorbing_aerosol_index', {'min': -1.0, 'max': 2.0, 'palette': ['black', 'blue', 'purple', 'cyan', 'green', 'yellow', 'red']})
        }

        self.admin_boundaries = ee.FeatureCollection("projects/inlaid-crane-446610-m5/assets/JEDAdminstrative_Boundaries")

    def retrieveData(self):
        if self.name not in self.dataset_mapping:
            raise ValueError("Invalid air quality variable selected.")
        dataset_id, band, _ = self.dataset_mapping[self.name]
        return ee.ImageCollection(dataset_id).select(band).filterDate(self.startTime, self.endTime)

    def generateMap(self):
        if self.name not in self.dataset_mapping:
            raise ValueError("Invalid air quality variable selected.")
        
        viz_params = self.dataset_mapping[self.name][2]
        collection = self.retrieveData()
        mean_image = collection.mean().clip(self.location)
        map_id_dict = mean_image.getMapId(viz_params)

        boundary_geojson = self.admin_boundaries.getInfo()
        m = folium.Map(location=[21.48581, 39.19797], zoom_start=11)
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
            attr=f'{self.name} Data',
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

        # Add legend
        m.get_root().html.add_child(folium.Element(self.legendHTML()))
        folium.LayerControl().add_to(m)

        output_file = f"static/{self.name}_map.html"
        m.save(output_file)
        return output_file


    def generateChart(self, aggregation="daily"):
        if self.name not in ["NO2", "SO2", "CO", "Aerosol"]:
            raise ValueError("Charting is only supported for NO2 and SO2.")

        if aggregation == "monthly":
            date_format = "YYYY-MM"
        elif aggregation == "yearly":
            date_format = "YYYY"
        else:
            date_format = "YYYY-MM-dd"

        dataset_id, band, _ = self.dataset_mapping[self.name]
        
        def compute_mean(img):
            mean = img.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=self.location,
                scale=1000,
                maxPixels=1e9
            ).get(band)

            return img.set("mean_val", mean).set("date", img.date().format(date_format))


        # Apply processing
        collection = (
            ee.ImageCollection(dataset_id)
            .select(band)
            .filterDate(self.startTime, self.endTime)
            .filterBounds(self.location)
            .map(compute_mean)
            .filter(ee.Filter.notNull(["mean_val"]))  #  filter nulls before mapping
        )

        def extract_feature(img):

            if self.name in ["NO2", "SO2"]:
                value = ee.Number(img.get("mean_val")).multiply(1e6)
            else:
                value = ee.Number(img.get("mean_val"))  # CO and Aerosol stay raw


            return ee.Feature(None, {
                "date": img.get("date"),
                "value": value
            })

        feature_collection = collection.map(extract_feature)
        feature_list = feature_collection.getInfo()["features"]  #  fix here
        

        # Extract list of (grouped_date, value) pairs
        date_val_pairs = [
            (f["properties"]["date"], f["properties"]["value"])
            for f in feature_list
        ]

        # Bucket by grouping key
        buckets = defaultdict(list)
        for date, val in date_val_pairs:
            buckets[date].append(val)

        # Reduce values per group
        chart_data = [
            {"date": date, "value": round(mean(vals), 6)}
            for date, vals in sorted(buckets.items())
        ]

        return chart_data




    def generateAiAnalysis(self):
        # Placeholder for future AI analysis
        pass

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
