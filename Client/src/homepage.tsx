import React from "react";
import "./App.css";

function HomePage({ setPage }: { setPage: (page: string) => void }) {
  return (
    <div className="container">
      {/* Navbar */}
      

      {/* Hero Section */}
      <header className="hero">
        <div className="hero-box">
          <h1>Welcome To <br /><span className="gradient-text">GREEN</span> JEDDAH</h1>
          <p>A digital platform that monitors Jeddah’s environment using satellite data.</p>
          <button className="cta" onClick={() => setPage("about")}>Learn More</button>
        </div>
      </header>

      {/* Scrollable Sections */}
      <div className="scroll-section">
        {/* First Scroll Section */}
        <div className="problem_page">
          <div className="problem-image">
            <img src="\frontseaimge.jpg" alt="Jeddah Environment" />
          </div>
          <div className="problem-content">
            <h2>Problem Definition</h2>
            <p>The city of Jeddah is facing several environmental challenges that impact the health and well-
              being of its residents, as well as the sustainability of the urban environment. These challenges
              include:</p>
            <ul>
              <li><strong>Urban Heat Island Effect:</strong> Elevated temperatures in urban areas compared to rural regions, increasing energy consumption and health risks.</li>
              <li><strong>Air Pollution:</strong> Rising air pollutants affecting respiratory health and life quality.</li>
              <li><strong>Drought:</strong> Limited water availability impacting agriculture and urban supplies.</li>
              <li><strong>Water Quality Decline:</strong> Water contamination threatening public health and ecosystems.</li>
            </ul>
          </div>
        </div>

        {/* Second Scroll Section (Reversed) */}
        <div className="page_reverse">
          <div className="solution-image">
            <img src="/jeddahphoto.jpg" alt="Environmental Issues" />
          </div>
          <div className="solution-content">
            <h2>Probosed solution</h2>
            <p>the proposed solution is to develop an integrated environmental monitoring
              website using GEE (Google Earth engine) to track these issues. The website will alert users to
              problem areas and assist researchers and authorities by providing them with analytical data.
              By utilizing data from multiple satellites, the system applies algorithms and AI to generate
              results and actionable insights displayed on an interactive map.</p>
            
          </div>
        </div>
      </div>
    </div>
  );
}

export default HomePage;
