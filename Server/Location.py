import ee
from Singleton.GEEConnection import GEEConnection

class Location:
    district_list = [
        {"id": 1, "name": "حي الروضة", "coordinates": [21.567884, 39.160012]},
        {"id": 2, "name": "حي النزهة", "coordinates": [21.617282, 39.1688026]},
        {"id": 3, "name": "حي الحمراء", "coordinates": [21.530280, 39.163816]},
        {"id": 4, "name": "حي المشرفة", "coordinates": [21.537645, 39.197368]},
        {"id": 5, "name": "حي النهضة", "coordinates": [21.614985, 39.129830]},
        {"id": 6, "name": "حي الزهراء", "coordinates": [21.587692, 39.131120]},
        {"id": 7, "name": "حي السلامة", "coordinates": [21.585454, 39.153442]},
        {"id": 8, "name": "حي البوادي", "coordinates": [21.599469, 39.166396]},
        {"id": 10, "name": "حي الصفا", "coordinates": [21.584388, 39.217724]},
        {"id": 11, "name": "حي المروة", "coordinates": [21.613939, 39.208989]},
        {"id": 12, "name": "حي العزيزية", "coordinates": [21.558460, 39.207995]},
        {"id": 13, "name": "حي البغدادية الغربية", "coordinates": [21.498760, 39.176598]},
        {"id": 14, "name": "حي البغدادية الشرقية", "coordinates": [21.498124, 39.190319]},
        {"id": 15, "name": "حي الكندرة", "coordinates": [21.498584, 39.199257]},
        {"id": 16, "name": "حي العمارية", "coordinates": [21.489810, 39.191480]},
        {"id": 17, "name": "حي الشرفية", "coordinates": [21.515411, 39.189228]},
        {"id": 18, "name": "حي الرويس", "coordinates": [21.517194, 39.171001]},
        {"id": 19, "name": "حي بني مالك", "coordinates": [21.531457, 39.213672]},
        {"id": 20, "name": "حي الفيصلية", "coordinates": [21.569141, 39.175223]},
        {"id": 21, "name": "حي السليمانية", "coordinates": [21.505158, 39.250503]},
        {"id": 22, "name": "حي النسيم", "coordinates": [21.516774, 39.231317]},
        {"id": 23, "name": "حي الربوة", "coordinates": [21.603513, 39.182107]},
        {"id": 24, "name": "حي الفيحاء", "coordinates": [21.488163, 39.218346]},
        {"id": 25, "name": "حي الورود", "coordinates": [21.524641, 39.195691]},
        {"id": 27, "name": "حي الصحيفة", "coordinates": [21.486550, 39.195359]},
        {"id": 28, "name": "حي الجامعة", "coordinates": [21.471459, 39.243828]},
        {"id": 29, "name": "حي الفضيلة", "coordinates": [21.305725, 39.271569]},
        {"id": 30, "name": "حي الفروسية", "coordinates": [21.826056, 39.207979]},
    ]

    district_radius = {
        "1": 2.5, "2": 2.2, "3": 2.3, "4": 1.8, "5": 1.7,
        "6": 2.0, "7": 1.8, "8": 2.5, "10": 2.0, "11": 2.1,
        "12": 2.5, "13": 1.5, "14": 1.5, "15": 1.5, "16": 1.2,
        "17": 1.6, "18": 1.3, "19": 1.8, "20": 1.4, "21": 1.3,
        "22": 1.2, "23": 1.3, "24": 1.2, "25": 1.3, "27": 1.2,
        "28": 3.0, "29": 1.3, "30": 1.2
    }

    def __init__(self, coords=None, lon_min=None, lat_min=None, lon_max=None, lat_max=None, geometry=None, label=None):
        self.label = label or "Custom Region"
        if geometry:
            self.geometry = geometry
        elif coords:
            self.geometry = ee.Geometry.Polygon([coords])
        elif all(v is not None for v in [lon_min, lat_min, lon_max, lat_max]):
            self.geometry = ee.Geometry.Rectangle([lon_min, lat_min, lon_max, lat_max])
        else:
            raise ValueError("Provide either 'coords', bounding box values, or 'geometry'.")

    @staticmethod
    def get_predefined_region(name):
        name = name.lower()

        if name == "jeddah":
            return Location(
                lon_min=38.97906, lat_min=21.19958, lon_max=39.38555, lat_max=21.81669,
                label="Jeddah Box"
            )

        elif name == "jeddah_admin":
            GEEConnection()
            admin_fc = ee.FeatureCollection("projects/inlaid-crane-446610-m5/assets/JEDAdminstrative_Boundaries")
            geometry = admin_fc.geometry()
            return Location(geometry=geometry, label="Jeddah Admin")

        raise ValueError(f"Region '{name}' not recognized")

    @staticmethod
    def get_district_location(district_id):
        district = next((d for d in Location.district_list if str(d["id"]) == str(district_id)), None)
        if not district:
            raise ValueError("District ID not found.")

        lat, lon = district["coordinates"]
        radius_km = Location.district_radius.get(str(district_id), 1.5)

        center_point = ee.Geometry.Point([lon, lat])
        buffered_area = center_point.buffer(radius_km * 1000)
        simple_polygon = buffered_area.simplify(100)  # 🛠 Force valid polygon (not bounding box)

        return Location(geometry=simple_polygon, label=f"District {district_id}")



    
    def get_geometry(self):
        return self.geometry

    def get_area_sq_km(self):
        if self.label == "Jeddah Admin":
            return 1686.0
        return self.geometry.area().divide(1e6).getInfo()

    def __str__(self):
        return f"Region: {self.label}"
