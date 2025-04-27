import React, { useState } from "react";
import "./SelectAnalysis.css";

const districts = [
  { id: 1, name: "حي الروضة" },
  { id: 2, name: "حي النزهة" },
  { id: 3, name: "حي الحمراء" },
  { id: 4, name: "حي المشرفة" },
  { id: 5, name: "حي النهضة" },
  { id: 6, name: "حي الزهراء" },
  { id: 7, name: "حي السلامة" },
  { id: 8, name: "حي البوادي" },
  { id: 10, name: "حي الصفا" },
  { id: 11, name: "حي المروة" },
  { id: 12, name: "حي العزيزية" },
  { id: 13, name: "حي البغدادية الغربية" },
  { id: 14, name: "حي البغدادية الشرقية" },
  { id: 15, name: "حي الكندرة" },
  { id: 16, name: "حي العمارية" },
  { id: 17, name: "حي الشرفية" },
  { id: 18, name: "حي الرويس" },
  { id: 19, name: "حي بني مالك" },
  { id: 20, name: "حي الفيصلية" },
  { id: 21, name: "حي السليمانية" },
  { id: 22, name: "حي النسيم" },
  { id: 23, name: "حي الربوة" },
  { id: 24, name: "حي الفيحاء" },
  { id: 25, name: "حي الورود" },
  { id: 27, name: "حي الصحيفة" },
  { id: 28, name: "حي الجامعة" },
  { id: 29, name: "حي الفضيلة" },
  { id: 30, name: "حي الفروسية" },
];

const CompareData = () => {
  const [firstStart, setFirstStart] = useState("");
  const [firstEnd, setFirstEnd] = useState("");
  const [secondStart, setSecondStart] = useState("");
  const [secondEnd, setSecondEnd] = useState("");
  const [indicator, setIndicator] = useState("UHI");
  const [district1, setDistrict1] = useState("1");
  const [district2, setDistrict2] = useState("2");
  const [loading, setLoading] = useState(false);
  const [mapUrl1, setMapUrl1] = useState("");
  const [mapUrl2, setMapUrl2] = useState("");
  const [chartData, setChartData] = useState<{
    first_period: { date: string; value: number }[];
    second_period: { date: string; value: number }[];
  }>({ first_period: [], second_period: [] });
  const [analysisText, setAnalysisText] = useState("");
  const [severityMessage, setSeverityMessage] = useState("");

  const getSeverity = (value: number) => {
    if (indicator === "UHI") {
      if (value > 2) return "Severe";
      if (value > 1) return "Moderate";
      return "Normal";
    }
    if (indicator === "Air") {
      if (value > 100) return "Severe";
      if (value > 50) return "Moderate";
      return "Normal";
    }
    if (indicator === "Water") {
      if (value < 0) return "Severe";
      if (value < 0.1) return "Moderate";
      return "Normal";
    }
    if (indicator === "Drought") {
      if (value < 0.2) return "Severe";
      if (value < 0.3) return "Moderate";
      return "Normal";
    }
    return "Unknown";
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("first_start", firstStart);
      formData.append("first_end", firstEnd);
      formData.append("second_start", secondStart);
      formData.append("second_end", secondEnd);
      formData.append("indicator", indicator);
      formData.append("district1", district1);
      formData.append("district2", district2);

      const response = await fetch("http://127.0.0.1:5000/compare_data", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setMapUrl1(`http://127.0.0.1:5000/${data.map_url_1}`);
      setMapUrl2(`http://127.0.0.1:5000/${data.map_url_2}`);
      setChartData(data.chart_data);
      setAnalysisText(data.analysis_text);
      setSeverityMessage(
        `First: ${getSeverity(
          data.chart_data.first_period[0].value
        )} | Second: ${getSeverity(data.chart_data.second_period[0].value)}`
      );
    } catch (error) {
      console.error("Error fetching comparison data:", error);
    }
    setLoading(false);
  };

  return (
    <div className="analysis-page-fixed">
      <div className="dashboard-section">
        {/* Sidebar */}
        <div className="analysis-sidebar">
          <h2>Compare Data</h2>
          <form onSubmit={handleSubmit} className="analysis-form">
            {/* Dates and Inputs */}
            <label>First Period Start:</label>
            <input
              type="date"
              value={firstStart}
              onChange={(e) => setFirstStart(e.target.value)}
              required
            />
            <label>First Period End:</label>
            <input
              type="date"
              value={firstEnd}
              onChange={(e) => setFirstEnd(e.target.value)}
              required
            />
            <label>Second Period Start:</label>
            <input
              type="date"
              value={secondStart}
              onChange={(e) => setSecondStart(e.target.value)}
              required
            />
            <label>Second Period End:</label>
            <input
              type="date"
              value={secondEnd}
              onChange={(e) => setSecondEnd(e.target.value)}
              required
            />

            <label>Indicator:</label>
            <select
              value={indicator}
              onChange={(e) => setIndicator(e.target.value)}
            >
              <option value="UHI">UHI</option>
              <option value="Air">Air</option>
              <option value="Water">Water</option>
              <option value="Drought">Drought</option>
            </select>

            <label>First District:</label>
            <select
              value={district1}
              onChange={(e) => setDistrict1(e.target.value)}
            >
              {districts.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}
                </option>
              ))}
            </select>

            <label>Second District:</label>
            <select
              value={district2}
              onChange={(e) => setDistrict2(e.target.value)}
            >
              {districts.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}
                </option>
              ))}
            </select>

            <button type="submit" className="generate-button">
              Compare
            </button>
          </form>
        </div>

        {/* Map and Result Box */}
        <div
          className="analysis-map-container"
          style={{
            display: "flex",
            flexDirection: "row",
            gap: "10px",
            position: "relative",
          }}
        >
          {loading && (
            <div className="fvc-loading-overlay">
              <div className="fvc-spinner"></div>
              <p>Loading...</p>
            </div>
          )}
          {severityMessage && !loading && (
            <div className="fvc-result">
              <h3>Results:</h3>
              <p>{severityMessage}</p>
              <p>Normal range depends on indicator selected.</p>
            </div>
          )}

          {!loading && (
            <>
              <div style={{ width: "50%", height: "100%" }}>
                <h4 style={{ textAlign: "center" }}>First Period Map</h4>
                <iframe
                  src={mapUrl1}
                  title="First Map"
                  style={{ width: "100%", height: "90%" }}
                />
              </div>
              <div style={{ width: "50%", height: "100%" }}>
                <h4 style={{ textAlign: "center" }}>Second Period Map</h4>
                <iframe
                  src={mapUrl2}
                  title="Second Map"
                  style={{ width: "100%", height: "90%" }}
                />
              </div>
            </>
          )}
        </div>

        {/* Right Chart Panel */}
        <div className="analysis-right-panel">
          <h3>Comparison Chart</h3>
          <div>
            {chartData.first_period.length > 0 ? (
              <>
                <h4>First Period</h4>
                <ul>
                  {chartData.first_period.map((point, idx) => (
                    <li key={idx}>
                      {point.date}: {point.value}
                    </li>
                  ))}
                </ul>
                <h4>Second Period</h4>
                <ul>
                  {chartData.second_period.map((point, idx) => (
                    <li key={idx}>
                      {point.date}: {point.value}
                    </li>
                  ))}
                </ul>
              </>
            ) : (
              <p>No data yet.</p>
            )}
          </div>
          <div style={{ marginTop: "20px" }}>
            <h4>AI Analysis</h4>
            <p>{analysisText}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompareData;
