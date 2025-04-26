import React, { useState, useEffect } from "react";
import "./SelectAnalysis.css";
import ReactMarkdown from "react-markdown";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";
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
  const [uhiIndex, setUhiIndex] = useState("UHI");
  const [statusMsg, setStatusMsg] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [chartData, setChartData] = useState<any[]>([]);
  const [aggregation, setAggregation] = useState("daily");
  const [analysisText, setAnalysisText] = useState(""); // 🆕 For AI text

  useEffect(() => {
    if (chartData.length > 0) {
      handleSubmit();
    }
  }, [aggregation]);

  const handleSubmit = async (e?: React.FormEvent | Event) => {
    e?.preventDefault?.();
    setIsLoading(true);

    let endpoint = "";
    if (analysisType === "air") endpoint = "air_analysis";
    else if (analysisType === "uhi") endpoint = "uhi_analysis";
    else return;

    const formData = new FormData();
    formData.append("start_date", startDate);
    formData.append("end_date", endDate);
    formData.append("aggregation", aggregation);

    if (analysisType === "air") {
      formData.append("selected_index", pollutant);
    } else if (analysisType === "uhi") {
      formData.append("selected_index", uhiIndex);
    }

    try {
      const res = await fetch(`http://127.0.0.1:5000/${endpoint}`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      if (data.map_url) {
        setMapUrl(
          `http://127.0.0.1:5000/static/${data.map_url.replace(/^static\//, "")}`
        );

        setChartData(data.chart_data || []);
        setAnalysisText(data.analysis_text || ""); // 🆕 Save AI text
        setStatusMsg("");
      } else {
        setStatusMsg("Failed to load map.");
      }
    } catch (err) {
      console.error(err);
      setStatusMsg("Error contacting backend.");
    } finally {
      setIsLoading(false);
    }
  };

  //  Export CSV
  const exportCSV = () => {
    const csvRows = [
      ["Index", "Date", "Value"],
      ...chartData.map((d) => [
        analysisType === "uhi" ? uhiIndex : pollutant,
        d.date,
        d.value,
      ]),
    ];

    const csvContent =
      "data:text/csv;charset=utf-8," + csvRows.map((e) => e.join(",")).join("\n");

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "chart_data.csv");
    document.body.appendChild(link);
    link.click();
  };

  //  Export PDF
  const exportPDF = () => {
    const doc = new jsPDF();
    const indexName = analysisType === "uhi" ? uhiIndex : pollutant;
  
    // --- Page 1: AI Summary ---
    doc.setFont("Times", "Normal");
    doc.setFontSize(18);
    doc.setTextColor(46, 204, 113);
    doc.text("AI Analysis Summary", 10, 20);
  
    doc.setFontSize(12);
    doc.setTextColor(0, 0, 0);
    doc.setFont("Times", "Normal");
  
    // Clean markdown-like text into readable layout
    let cleaned = analysisText
      .replace(/\*\*(.*?)\*\*/g, (_, p1) => `\n\n${p1.toUpperCase()}\n`) // Section titles
      .replace(/\* (.*?)(?=\n|$)/g, '   $1')                            // Bullets
      .replace(/\n{2,}/g, "\n")                                       // Double line spacing
      .replace(/:{2,}/g, ':')                                           // Fix "::"
      .replace(/`/g, '');                                               // Remove code ticks
  
    const lines = doc.splitTextToSize(cleaned.trim(), 180);
  
    let y = 30;
    const lineHeight = 8;
  
    lines.forEach((line) => {
      // Add spacing before section titles
      if (line === line.toUpperCase() && line.length < 40) {
        doc.setFont("Times", "Bold");
        y += 4;
      } else {
        doc.setFont("Times", "Normal");
      }
  
      doc.text(line, 10, y);
      y += lineHeight;
  
      // If nearing page bottom
      if (y > 270) {
        doc.addPage();
        y = 20;
      }
    });
  
    // --- Page 2: Time Series Table ---
    if (chartData.length > 0) {
      doc.addPage();
      doc.setFont("Times", "Bold");
      doc.setFontSize(16);
      doc.setTextColor(46, 204, 113);
      doc.text("Time Series Trend Data", 10, 20);
  
      const tableData = chartData.map((d) => [
        indexName,
        d.date,
        d.value.toFixed(2),
      ]);
  
      autoTable(doc, {
        head: [["Index", "Date", "Value"]],
        body: tableData,
        startY: 30,
        headStyles: {
          fillColor: [46, 204, 113],
          textColor: 255,
          fontStyle: 'bold',
          font: 'times'
        },
        bodyStyles: {
          font: 'times',
          fontSize: 11,
          textColor: 50,
        },
        styles: {
          halign: 'center',
          cellPadding: 4,
        },
        alternateRowStyles: {
          fillColor: [245, 245, 245],
        },
      });
    }
  
    doc.save("analysis_report.pdf");
  };
  
  
  

  return (
    <div className="analysis-page-fixed">
      <div className="dashboard-section">
        {/* Left Sidebar */}
        <div className="analysis-sidebar">
          <h2>Select Analysis Type</h2>
          <select
            className="type-select"
            value={analysisType}
            onChange={(e) => setAnalysisType(e.target.value)}
          >
            <option value="air">Air Quality</option>
            <option value="uhi">Urban Heat Island (UHI)</option>
            <option value="water">Water Quality (Coming Soon)</option>
            <option value="drought">Drought Monitoring (Coming Soon)</option>
          </select>

          <form onSubmit={handleSubmit} className="analysis-form">
            {/* If Air Quality */}
            {analysisType === "air" && (
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
            )}

            {/* If UHI */}
            {analysisType === "uhi" && (
              <div className="form-row">
                <label>Index:</label>
                <select
                  value={uhiIndex}
                  onChange={(e) => setUhiIndex(e.target.value)}
                >
                  <option value="UHI">UHI</option>
                  <option value="LST">LST</option>
                  <option value="UTFVI">UTFVI</option>
                </select>
              </div>
            )}

            {/* Dates */}
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

            {/* Submit */}
            <button type="submit" className="generate-button">
              Generate
            </button>
            {statusMsg && <p className="status-message">{statusMsg}</p>}
          </form>
        </div>

        {/* Center Map Display */}
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

        {/* Right Panel - Chart */}
        <div className="analysis-right-panel">
          <h3>Time Series Trend</h3>
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
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip
                    content={({ active, payload, label }) => {
                      if (active && payload && payload.length) {
                        return (
                          <div
                            style={{
                              background: "#1a1a1a",
                              padding: "10px",
                              borderRadius: "8px",
                              color: "#fff",
                            }}
                          >
                            <p>
                              <strong>Date:</strong> {label}
                            </p>
                            <p>
                              <strong>Value:</strong> {payload[0].value}
                            </p>
                          </div>
                        );
                      }
                      return null;
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
              <div style={{ marginTop: "10px" }}>
                <button className="generate-button" onClick={exportCSV}>
                  Download CSV
                </button>
              </div>
            </div>
          ) : (
            <p>No chart data yet.</p>
          )}

          {/* AI Text Analysis Result */}
          {analysisText && (
            <div
              style={{
                marginTop: "20px",
                padding: "15px",
                backgroundColor: "#1a1a1a",
                borderRadius: "8px",
              }}
            >
              <h4 style={{ color: "#2ecc71", marginBottom: "10px" }}>
                AI Analysis Summary
              </h4>
              <ReactMarkdown
                children={analysisText}
                components={{
                  h1: ({ node, ...props }) => (
                    <h1 style={{ fontSize: "24px", color: "#2ecc71" }} {...props} />
                  ),
                  h2: ({ node, ...props }) => (
                    <h2 style={{ fontSize: "20px", color: "#2ecc71" }} {...props} />
                  ),
                  p: ({ node, ...props }) => (
                    <p style={{ fontSize: "14px", color: "#cccccc" }} {...props} />
                  ),
                  strong: ({ node, ...props }) => (
                    <strong style={{ color: "#ffffff" }} {...props} />
                  ),
                }}
              />
              <div style={{ marginTop: "10px" }}>
                <button className="generate-button" onClick={exportPDF}>
                  Download PDF
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SelectAnalysis;
