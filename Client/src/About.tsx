import React from "react";
import "./About.css";


const About = ({ setPage }: { setPage: (page: string) => void }) => {
  return (
    <div className="about-container">
      {/* Navbar */}
      
      <div className="logo-container">
      <img src="\LogojeddahW.png" alt="Green Jeddah Logo" />
        </div>
      {/* Section 1 */}
      {/* Section 1 */}
      <div className="section">
         <h2>What is Green Jeddah?</h2>
         <p>Green Jeddah is a digital platform that leverages satellite data and remote sensing to monitor environmental conditions in Jeddah. Using Google Earth Engine (GEE), 
            it provides insights on air and water quality, urban heat, and drought, helping you to make decisions. The platform aims to enhance sustainability efforts in alignment with Saudi Vision 2030.</p>
     </div>
      <div className="section">
        <h2>Our Vision</h2>
        <p>To be a pioneering digital platform that leverages satellite technology and remote sensing to enhance environmental 
            monitoring and sustainability in Jeddah, empowering decision-makers, researchers, 
            and the community to build a greener and more resilient city.</p>
      </div>
      <div className="section">
  <h2>Our Mission</h2>
  <p>provide accurate insights that support sustainable urban planning and decision-making. Through innovation and data-driven 
    solutions, we aim to contribute to a greener and more resilient Jeddah.</p>
</div>

<div className="section">
  <h2> Our Objectives</h2>
  <p>This project aims to achieve the following objectives:</p>
        <ul>
          <li><strong>Environmental Monitoring and Analysis:</strong> Monitor and analyze environmental
            issues using satellite imagery and remote sensing data.</li>
          <li><strong>Interactive Map Development:</strong>  Create an interactive map that highlights problem
            areas.</li>
          <li><strong>Promote Sustainable Development:</strong> Contribute to Jeddah’s sustainable
            development. </li>
          <li><strong>Facilitate Research and Innovation:</strong> Offer a platform that supports environmental
            research.
          </li>
        </ul>
      </div>

    </div>

  );
};

export default About;