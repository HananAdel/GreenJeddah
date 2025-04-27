from Factory.AirQuality import AirQuality
from Factory.WaterQuality import WaterQuality
from Factory.UHI import UHI
from Factory.Drought import Drought
from Location import Location

class CompareAnalysis:
    def __init__(self, indicator, first_start, first_end, second_start, second_end, district1, district2):
        self.indicator = indicator
        self.first_start = first_start
        self.first_end = first_end
        self.second_start = second_start
        self.second_end = second_end
        self.district1 = district1
        self.district2 = district2
        self.analysis1 = None
        self.analysis2 = None

    def setup_analysis(self):
        location1 = Location.get_district_location(self.district1).get_geometry()
        location2 = Location.get_district_location(self.district2).get_geometry()

        if self.indicator == "Air":
            self.analysis1 = AirQuality(name="NO2", location=location1, startTime=self.first_start, endTime=self.first_end)
            self.analysis2 = AirQuality(name="NO2", location=location2, startTime=self.second_start, endTime=self.second_end)
        elif self.indicator == "Water":
            self.analysis1 = WaterQuality(name="NDWI", location=location1, startTime=self.first_start, endTime=self.first_end)
            self.analysis2 = WaterQuality(name="NDWI", location=location2, startTime=self.second_start, endTime=self.second_end)
        elif self.indicator == "Drought":
            self.analysis1 = Drought(name="NDVI", location=location1, startTime=self.first_start, endTime=self.first_end)
            self.analysis2 = Drought(name="NDVI", location=location2, startTime=self.second_start, endTime=self.second_end)
        elif self.indicator == "UHI":
            self.analysis1 = UHI(name="UHI", location=location1, startTime=self.first_start, endTime=self.first_end)
            self.analysis2 = UHI(name="UHI", location=location2, startTime=self.second_start, endTime=self.second_end)
        else:
            raise ValueError("Unsupported indicator selected.")


    def generate_comparison(self, aggregation="monthly"):
        if not self.analysis1 or not self.analysis2:
            self.setup_analysis()

        map_url_1 = self.analysis1.generateMap(suffix=1)
        map_url_2 = self.analysis2.generateMap(suffix=2)
        chart_data_1 = self.analysis1.generateChart(aggregation)
        chart_data_2 = self.analysis2.generateChart(aggregation)

        # Merge charts into one list
        merged_chart = {
            "first_period": chart_data_1,
            "second_period": chart_data_2
        }

        analysis_text_1 = self.analysis1.generateAiAnalysis()
        analysis_text_2 = self.analysis2.generateAiAnalysis()

        full_analysis_text = f"First Period Analysis:\n{analysis_text_1}\n\nSecond Period Analysis:\n{analysis_text_2}"

        return {
            "map_url_1": map_url_1,
            "map_url_2": map_url_2,
            "chart_data": merged_chart,
            "analysis_text": full_analysis_text
        }