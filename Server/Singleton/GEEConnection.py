# This creates a single instance of GEE connection
# To intilaize it !!once!! use 
# gee = GEEConnection(
#    service_account='greenjeddah@inlaid-crane-446610-m5.iam.gserviceaccount.com',
#    private_key_path='PrivateKey/inlaid-crane-446610-m5-7e775309cd44.json'
# )
# To call it again use
# gee_conn = GEEConnection()  # Returns the same initialized instance

import ee

class GEEConnection:
    _instance = None

    def __new__(cls, service_account=None, private_key_path=None):
        if cls._instance is None:
            if not service_account or not private_key_path:
                raise ValueError("GEE not initialized yet. Provide service_account and private_key_path.")
            cls._instance = super(GEEConnection, cls).__new__(cls)
            credentials = ee.ServiceAccountCredentials(service_account, private_key_path)
            ee.Initialize(credentials)
            cls._instance.service_account = service_account
            cls._instance.private_key_path = private_key_path
        else:
            # Optional: log that it's returning existing instance
            if service_account or private_key_path:
                print("[INFO] GEEConnection already initialized. Ignoring extra credentials.")

        return cls._instance

    def get_service_account(self):
        return self.service_account
