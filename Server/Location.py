import ee
from Singleton.GEEConnection import GEEConnection

class Location:
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

    def get_geometry(self):
        return self.geometry

    def get_area_sq_km(self):
        if self.label == "Jeddah Admin":
            return 1686.0
        return self.geometry.area().divide(1e6).getInfo()

    def __str__(self):
        return f"Region: {self.label}"
