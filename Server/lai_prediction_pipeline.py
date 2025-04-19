import ee
import numpy as np
import tensorflow as tf
from pickle import load
from keras.layers import Layer
from tensorflow.keras.saving import register_keras_serializable
import datetime
from Singleton.GEEConnection import GEEConnection
from Location import Location


# --------------------- GEE Initialization ----------------------

GEEConnection(
    service_account='greenjeddah@inlaid-crane-446610-m5.iam.gserviceaccount.com',
    private_key_path='PrivateKey/inlaid-crane-446610-m5-7e775309cd44.json'
)

# --------------------- Time2Vec (Custom Layer) ----------------------
@register_keras_serializable()
class Time2Vec(Layer):
    def __init__(self, output_dim=None, **kwargs):
        self.output_dim = output_dim
        super(Time2Vec, self).__init__(**kwargs)

    def build(self, input_shape):
        self.W = self.add_weight(name='W', shape=(input_shape[-1], self.output_dim), initializer='uniform', trainable=True)
        self.P = self.add_weight(name='P', shape=(input_shape[1], self.output_dim), initializer='uniform', trainable=True)
        self.w = self.add_weight(name='w', shape=(input_shape[1], 1), initializer='uniform', trainable=True)
        self.p = self.add_weight(name='p', shape=(input_shape[1], 1), initializer='uniform', trainable=True)
        super(Time2Vec, self).build(input_shape)

    def call(self, x):
        original = self.w * x + self.p
        sin_trans = tf.sin(tf.matmul(x, self.W) + self.P)
        return tf.concat([sin_trans, original], -1)

# --------------------- Step 1: Get GEE Features ----------------------
def fetch_latest_features(geometry=None, area_name="jeddah_admin"):
    region = geometry if geometry else Location.get_predefined_region(area_name).get_geometry()


    today = datetime.date.today()
    total_days = 30
    max_days = 90  # 3 months

    while total_days <= max_days:
        end = ee.Date(str(today))
        start = end.advance(-total_days, 'day')

        # Fpar (MODIS scaled to 0–100 → 0–1)
        fpar_col = ee.ImageCollection("MODIS/061/MCD15A3H").select("Fpar").filterDate(start, end)
        fpar_img_raw = fpar_col.mean()
        fpar_valid = fpar_img_raw.bandNames().size().getInfo() != 0

        # Dewpoint from ERA5
        era5_dew_col = ee.ImageCollection("ECMWF/ERA5_LAND/HOURLY").select("dewpoint_temperature_2m").filterDate(start, end)
        dew_img_raw = era5_dew_col.mean()
        dew_valid = dew_img_raw.bandNames().size().getInfo() != 0

        # Wind from ERA5
        u10_col = ee.ImageCollection("ECMWF/ERA5_LAND/HOURLY").select("u_component_of_wind_10m").filterDate(start, end)
        v10_col = ee.ImageCollection("ECMWF/ERA5_LAND/HOURLY").select("v_component_of_wind_10m").filterDate(start, end)
        u10 = u10_col.mean()
        v10 = v10_col.mean()
        wind_valid = u10.bandNames().size().getInfo() != 0 and v10.bandNames().size().getInfo() != 0

        if fpar_valid and dew_valid and wind_valid:
            fpar_img = fpar_img_raw.multiply(0.01).rename("Fpar")
            dew_img = dew_img_raw.subtract(273.15).rename("Tdew")
            wind_img = u10.pow(2).add(v10.pow(2)).sqrt().rename("Wind")

            image = fpar_img.addBands([dew_img, wind_img])

            sample = image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=region,
                scale=1000,
                maxPixels=1e9
            )

            result = sample.getInfo()

            # Double-check no None values
            if None not in result.values():
                print(f"[INFO] Found GEE data in range: {total_days} days")
                return result

        # If data not valid, expand search range
        total_days += 10
        print(f"[INFO] Expanding GEE data search to {total_days} days")

    raise ValueError("No environmental features data available in the last 3 months for the selected area.")


# --------------------- Step 2: Build Model Input ----------------------
def build_model_input(temp, gee_features):

    fpar = gee_features['Fpar']
    dew = gee_features['Tdew']
    wind = gee_features['Wind']

    feature_vector = [fpar, dew, temp, wind]

    # ---- SCALE HERE ----
    input_scaler = load(open("model/input_scaler.pkl", "rb"))  # Load trained input scaler
    scaled_vector = input_scaler.transform([feature_vector])  # shape: (1, 4)

    # Tile to match (10, 4) input shape
    sequence = np.tile(scaled_vector, (10, 1))  # shape: (10, 4)
    return np.expand_dims(sequence, axis=0)     # shape: (1, 10, 4)

# --------------------- Step 3: Run Model Prediction ----------------------
def predict_lai(model_input):
    model = tf.keras.models.load_model('model/finalized_model.keras', custom_objects={'Time2Vec': Time2Vec})
    result = model.predict(model_input)

    return float(result[0][0])

# --------------------- Full Pipeline Wrapper ----------------------
def get_lai_prediction(temp, geometry=None):
    gee_data = fetch_latest_features(geometry=geometry)
    model_input = build_model_input(temp, gee_data)
    lai_val = predict_lai(model_input)
    return lai_val

# --------------------- Get Current LAI ----------------------
def get_current_lai(geometry=None):
    
    aoi = geometry if geometry else Location.get_predefined_region("jeddah_admin").get_geometry()

    today = datetime.date.today()
    total_days = 30
    max_days = 90  # 3 months limit

    while total_days <= max_days:
        end_date = ee.Date(str(today))
        start_date = end_date.advance(-total_days, 'day')

        lai_collection = (ee.ImageCollection("MODIS/061/MCD15A3H")
                          .filterDate(start_date, end_date)
                          .filterBounds(aoi)
                          .select('Lai'))

        lai_image = lai_collection.mean()

        lai_stats = lai_image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=aoi,
            scale=1000,
            maxPixels=1e9
        )

        lai_value = lai_stats.get('Lai').getInfo()

        if lai_value is not None and lai_value > 0:
            print(f"[INFO] Found LAI data in range: {total_days} days")
            return {
                "lai_value": lai_value,
                "date_range": f"{start_date.format('YYYY-MM-dd').getInfo()} to {end_date.format('YYYY-MM-dd').getInfo()}"
            }

        # No data found, expand the range
        total_days += 10
        print(f"[INFO] No data found, expanding range to: {total_days} days")

    raise ValueError("No LAI data available in the last 3 months for the selected area.")






