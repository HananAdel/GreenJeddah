import React, { useState, useEffect } from "react";
import "./SelectAnalysis.css";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const SelectAnalysis = () => {
  const [analysisType, setAnalysisType] = useState("air");
  const [mapUrl, setMapUrl] = useState(
    "http://127.0.0.1:5000/static/Base_map.html"
  );
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [pollutant, setPollutant] = useState("NO2");
  const [statusMsg, setStatusMsg] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [chartData, setChartData] = useState<any[]>([]);
  const [aggregation, setAggregation] = useState("daily");

  useEffect(() => {
    if (chartData.length > 0) {
      handleSubmit();
    }
  }, [aggregation]);

  const handleSubmit = async (e?: React.FormEvent | Event) => {
    e?.preventDefault?.();
    if (analysisType !== "air") return;
    setIsLoading(true);

    const formData = new FormData();
    formData.append("start_date", startDate);
    formData.append("end_date", endDate);
    formData.append("map_type", pollutant);
    formData.append("aggregation", aggregation);

    try {
      const res = await fetch("http://127.0.0.1:5000/air_analysis", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      if (data.map_url) {
        setMapUrl(`http://127.0.0.1:5000/${data.map_url}`);
        setChartData(data.chart_data || []);
        setStatusMsg("");
      } else {
        setStatusMsg("Failed to load air quality map.");
      }
    } catch (err) {
      console.error(err);
      setStatusMsg("Error contacting backend.");
    } finally {
      setIsLoading(false);
    }
  };

  const getChartExplanation = (type: string) => {
    switch (type) {
      case "NO2":
        return "This chart shows average NO₂ concentrations (μmol/m²) over your selected region and date range. NO₂ is a key pollutant from vehicle and industrial emissions.";
      case "SO2":
        return "SO₂ levels indicate the presence of sulfur-based pollution, typically from fossil fuel combustion and industrial processes.";
      case "CO":
        return "CO is a colorless gas produced by incomplete combustion. This chart reflects its atmospheric concentration.";
      case "Aerosol":
        return "This chart shows the Absorbing Aerosol Index (AAI), a unitless measure indicating the presence of UV-absorbing particles such as dust and smoke.";
      default:
        return "";
    }
  };

  const pollutantInfo: Record<string, { [key: string]: string }> = {
    NO2: {
      what: "Nitrogen Dioxide is a reddish-brown gas primarily released from vehicles and industrial activity.",
      health:
        "Exposure can worsen asthma, irritate the lungs, and increase respiratory infections.",
      environment:
        "Reduces photosynthesis, damages leaves, and contributes to acid rain and smog.",
      sources: "Traffic emissions, power plants, and fuel combustion.",
      importance:
        "Crucial to monitor in urban environments to reduce respiratory diseases and smog.",
      action:
        "Promote green transport, improve fuel efficiency, and plant pollution-absorbing trees.",
    },
    SO2: {
      what: "Sulfur Dioxide is a colorless gas with a strong odor, often associated with volcanic and industrial activity.",
      health:
        "Can aggravate lung diseases like asthma and cause shortness of breath.",
      environment:
        "Contributes to acid rain, harming ecosystems and corroding buildings.",
      sources:
        "Coal-burning power plants, industrial boilers, and metal smelting.",
      importance:
        "Important to track in regions with heavy industry and fuel burning.",
      action:
        "Support cleaner energy sources and reduce reliance on high-sulfur fuels.",
    },
    CO: {
      what: "Carbon Monoxide is a colorless, odorless gas from incomplete combustion.",
      health:
        "High levels reduce oxygen delivery to organs and can be fatal in enclosed spaces.",
      environment:
        "While not a greenhouse gas, it contributes indirectly to ozone formation.",
      sources: "Vehicle exhaust, cooking stoves, and fossil fuel combustion.",
      importance:
        "Monitoring helps prevent health risks in densely populated areas.",
      action:
        "Ventilate enclosed spaces, use clean stoves, and avoid idling engines.",
    },
    Aerosol: {
      what: "Aerosols are tiny particles or droplets in the air, some of which absorb sunlight.",
      health:
        "Can penetrate deep into lungs and lead to heart and lung diseases.",
      environment:
        "Affect climate by reflecting or absorbing solar radiation and altering cloud formation.",
      sources:
        "Dust storms, vehicle emissions, biomass burning, and sea spray.",
      importance:
        "Helps understand visibility, pollution spread, and climate impact.",
      action:
        "Reduce emissions, support reforestation, and monitor air quality alerts.",
    },
  };

  const currentInfo = pollutantInfo[pollutant];

  return (
    <div className="analysis-page-fixed">
      <div className="dashboard-section">
        <div className="analysis-sidebar">
          <h2>Select Analysis Type</h2>
          <select
            className="type-select"
            value={analysisType}
            onChange={(e) => setAnalysisType(e.target.value)}
          >
            <option value="air">Air Quality</option>
            <option value="water">Water Quality</option>
            <option value="drought">Drought</option>
            <option value="uhi">Urban Heat Island (UHI)</option>
          </select>

          <form onSubmit={handleSubmit} className="analysis-form">
            <p className="analysis-desc">
              Air quality monitoring detects harmful gases in the atmosphere
              like NO2, SO2, CO, and Aerosols using satellite data to visualize
              pollution levels over time.
            </p>
            <div className="form-row">
              <label>Start Date:</label>
              <input
                type="date"
                required
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>

            <div className="form-row">
              <label>End Date:</label>
              <input
                type="date"
                required
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>

            <div className="form-row">
              <label>Pollutant:</label>
              <select
                value={pollutant}
                onChange={(e) => setPollutant(e.target.value)}
              >
                <option value="NO2">NO2</option>
                <option value="SO2">SO2</option>
                <option value="CO">CO</option>
                <option value="Aerosol">Aerosol</option>
              </select>
            </div>

            <button type="submit" className="generate-button">
              Generate
            </button>
            {statusMsg && <p className="status-message">{statusMsg}</p>}
          </form>
        </div>

        <div className="analysis-map-container">
          {isLoading && (
            <div className="fvc-loading-overlay">
              <div className="fvc-spinner" />
              <p>Loading map...</p>
            </div>
          )}

          <iframe
            src={mapUrl}
            title="Analysis Map"
            width="100%"
            height="100%"
            style={{ borderRadius: "15px", border: "none" }}
          ></iframe>
        </div>

        <div className="analysis-right-panel">
          <h3>Analysis Results</h3>
          <p className="chart-description">{getChartExplanation(pollutant)}</p>

          <div className="form-row">
            <label>Aggregation:</label>
            <select
              value={aggregation}
              onChange={(e) => setAggregation(e.target.value)}
            >
              <option value="daily">Daily</option>
              <option value="monthly">Monthly</option>
              <option value="yearly">Yearly</option>
            </select>
          </div>

          {chartData.length > 0 ? (
            <div style={{ position: "relative" }}>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" name="Date" />
                  <YAxis
                    tickFormatter={(v) => `${v}`}
                    unit={
                      pollutant === "CO"
                        ? " mol/m²"
                        : pollutant === "Aerosol"
                        ? ""
                        : " μmol/m²"
                    }
                  />
                  <Tooltip
                    formatter={(value: number) => {
                      const unit =
                        pollutant === "CO"
                          ? "mol/m²"
                          : pollutant === "Aerosol"
                          ? ""
                          : "μmol/m²";
                      return [`${pollutant}: ${value} ${unit}`];
                    }}
                    labelFormatter={(label: string) => {
                      if (aggregation === "monthly") {
                        const [year, month] = label.split("-");
                        return `${month}/${year}`;
                      }
                      return label;
                    }}
                    contentStyle={{
                      backgroundColor: "#fff",
                      border: "1px solid #ccc",
                      borderRadius: "8px",
                      fontSize: "13px",
                      padding: "10px",
                      color: "#333",
                    }}
                    itemStyle={{
                      color: "#2ecc71",
                      fontWeight: 400,
                    }}
                    labelStyle={{
                      color: "#2ecc71",
                      fontWeight: 400,
                      marginBottom: "4px",
                    }}
                  />

                  <Line
                    type="monotone"
                    dataKey="value"
                    stroke="#2ecc71"
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p>No chart data to display yet.</p>
          )}
        </div>
      </div>

      <div className="analysis-info-section">
        <h2>Understanding {pollutant}</h2>
        <p>
          <strong>What is it?</strong> {currentInfo.what}
        </p>
        <p>
          <strong>Health Effects:</strong> {currentInfo.health}
        </p>
        <p>
          <strong>Environmental Impact:</strong> {currentInfo.environment}
        </p>
        <p>
          <strong>Sources:</strong> {currentInfo.sources}
        </p>
        <p>
          <strong>Why it matters:</strong> {currentInfo.importance}
        </p>
        <p>
          <strong>What you can do:</strong> {currentInfo.action}
        </p>
      </div>
    </div>
  );
};

export default SelectAnalysis;
