import React, { useState } from "react";
import { MapContainer, TileLayer, FeatureGroup } from "react-leaflet";
import { EditControl } from "react-leaflet-draw";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet-draw/dist/leaflet.draw.css";
import "./FVC.css";

const FVC = () => {
  const [temperature, setTemperature] = useState(23);
  const [selectedArea, setSelectedArea] = useState("Entire Jeddah region");
  const [drawnCoords, setDrawnCoords] = useState<number[][] | null>(null);
  const [showResult, setShowResult] = useState(false);
  const [resultData, setResultData] = useState<any>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleEstimate = () => {
    const isDrawing = selectedArea === "Draw custom area";
    setIsLoading(true);

    fetch("http://127.0.0.1:5000/predict_fvc", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        temperature,
        area_mode: isDrawing ? "draw" : "admin",
        geometry: isDrawing ? drawnCoords : null,
      }),
    })
      .then((res) => {
        if (!res.ok) {
          return res.json().then((err) => {
            throw new Error(err.error || "Unknown server error");
          });
        }
        return res.json();
      })
      .then((data) => {
        setResultData(data);
        setShowResult(true);
        setErrorMessage(null);
      })
      .catch((err) => {
        console.error(err);
        setErrorMessage(err.message);
        setShowResult(false);
      })
      .finally(() => {
        setIsLoading(false); // ✅ end loading
      });
  };

  const handleDrawCreate = (e: any) => {
    const latlngs = e.layer.getLatLngs()[0];
    const polygon = latlngs.map((point: L.LatLng) => [point.lng, point.lat]);
    polygon.push(polygon[0]); // close loop
    setDrawnCoords(polygon);
  };

  return (
    <div className="fvc-page">
      <div className="fvc-sidebar">
        <h2>Discover the Power of Green Spaces in Jeddah!</h2>
        <p>
          This tool empowers you to explore how increasing green spaces in
          Jeddah can help lower temperatures and improve the environment.
        </p>
        <ul>
          <li>
            🌿 Select any area, adjust the temperature target, and see how
            enhancing vegetation can cool your community and improve urban
            living.
          </li>
          <li>
            <strong>What is FVC?</strong> <br />
            Fractional Vegetation Cover (FVC) is a measure of how much ground is
            covered by vegetation. Higher FVC means more greenery, which helps
            reduce urban heat and improve air quality.
          </li>
        </ul>

        <label htmlFor="area">Select Area</label>
        <select
          id="area"
          value={selectedArea}
          onChange={(e) => setSelectedArea(e.target.value)}
        >
          <option>Entire Jeddah region</option>
          <option>Draw custom area</option>
        </select>

        <label>Select Desired Temperature</label>
        <input
          type="range"
          min={20}
          max={28}
          value={temperature}
          onChange={(e) => setTemperature(Number(e.target.value))}
        />
        <span>{temperature}°C</span>

        <button onClick={handleEstimate}>Estimate Green Cover</button>
      </div>

      <div className="fvc-map-container">
        <MapContainer
          center={[21.5, 39.2]}
          zoom={10}
          style={{ width: "100%", height: "100%" }}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution="&copy; OpenStreetMap contributors"
          />
          {selectedArea === "Draw custom area" && (
            <FeatureGroup>
              <EditControl
                position="topright"
                onCreated={handleDrawCreate}
                draw={{
                  polygon: true,
                  rectangle: false,
                  circle: false,
                  circlemarker: false,
                  marker: false,
                  polyline: false,
                }}
              />
            </FeatureGroup>
          )}
        </MapContainer>
        {isLoading && (
          <div className="fvc-loading-overlay">
            <div className="fvc-spinner" />
            <p>Loading prediction...</p>
          </div>
        )}

        {/* Modal shown on error */}
        {errorMessage && (
          <div className="fvc-error-modal">
            <div className="fvc-error-box">
              <h3>⚠️ No Data Available</h3>
              <p>{errorMessage}</p>
              <div
                style={{
                  display: "flex",
                  justifyContent: "flex-end",
                  gap: "10px",
                  marginTop: "10px",
                }}
              >
                <button onClick={() => setErrorMessage(null)}>OK</button>
              </div>
            </div>
          </div>
        )}

        {showResult && resultData && (
          <div className="fvc-result">
            <h3>Results:</h3>
            <p>
              🌿 The predicted FVC for a temperature of {temperature}°C in your
              selected area of {resultData.area_km2} km² is{" "}
              <strong>{resultData.predicted_fvc}%</strong>. To achieve your
              desired temperature reduction, you need to increase vegetation
              cover by{" "}
              <strong>
                {(resultData.predicted_fvc - resultData.current_fvc).toFixed(2)}
                %
              </strong>
              . Current cover: <strong>{resultData.current_fvc}%</strong>.
            </p>
            <p>
              🌱 Increase FVC by planting trees, using green roofs, and
              restoring land.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default FVC;
