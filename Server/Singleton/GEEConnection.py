import os
import ee

class GEEConnection:
    _instance = None

    def __new__(cls, service_account=None, private_key_path=None):
        if cls._instance is None:
            print("[INFO] Initializing Google Earth Engine Connection...")

            if service_account and private_key_path:
                # Dynamically build absolute path for private key
                private_key_path = os.path.join(os.path.dirname(__file__), "..", private_key_path)
                private_key_path = os.path.abspath(private_key_path)

                print("[DEBUG] Using Private Key Path:", private_key_path)

                # Create credentials and initialize Earth Engine
                credentials = ee.ServiceAccountCredentials(service_account, private_key_path)
                ee.Initialize(credentials)
            else:
                # Fallback: try to initialize normally (e.g., if running with user auth)
                ee.Initialize()

            cls._instance = super(GEEConnection, cls).__new__(cls)

        return cls._instance
