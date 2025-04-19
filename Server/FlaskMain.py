from flask import Flask, jsonify, render_template, request
import numpy as np
from lai_prediction_pipeline import get_lai_prediction, get_current_lai
from flask_cors import CORS
from Location import Location  
from Factory.AirQuality import AirQuality



app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET", "POST"])
def home():
    return render_template('index.html')



@app.route("/air_analysis", methods=["POST"])
def air_analysis():
    try:
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        map_type = request.form["map_type"]
        aggregation = request.form.get("aggregation", "daily")


        print(f"[INFO] Air analysis request: {start_date} to {end_date}, type: {map_type}")

        location = Location.get_predefined_region("jeddah_admin").get_geometry()
        analysis = AirQuality(name=map_type, location=location, startTime=start_date, endTime=end_date)

        map_url = analysis.generateMap()
        chart_data = analysis.generateChart(aggregation)




        return jsonify({
            "map_url": map_url,
            "chart_data": chart_data
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/predict_fvc", methods=["POST"])
def predict_fvc():
    data = request.json
    temp = data.get("temperature")
    coords = data.get("geometry")
    area_mode = data.get("area_mode", "admin")  # "draw" or "admin"
    

    try:
        # Create a Location object based on mode
        if area_mode == "draw" and coords:
            location = Location(coords=coords)
        else:
            location = Location.get_predefined_region("jeddah_admin")

        # Use geometry from the location
        geometry = location.get_geometry()
        area_km2 = location.get_area_sq_km()

        # Pass location.get_geometry()
        current = get_current_lai(geometry=geometry)
        predicted = get_lai_prediction(temp=temp, geometry=geometry)

        def lai_to_fvc(lai): return np.exp(-0.5 * lai)

        return jsonify({
            "predicted_lai": predicted,
            "current_lai": current["lai_value"],
            "predicted_fvc": round(lai_to_fvc(predicted) * 100, 2),
            "current_fvc": round(lai_to_fvc(current["lai_value"]) * 100, 2),
            "date_range": current["date_range"],
            "area_km2": round(area_km2, 2)
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
