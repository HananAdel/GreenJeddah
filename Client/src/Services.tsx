import React from "react";
import "./Services.css";

const customServices = [
  {
    id: "ai-model",
    title: "AI Recommendation",
    description:
      "Use AI-based recommendations to support sustainable city planning and green initiatives.",
    button: "Learn more",
  },
  {
    id: "compare-data",
    title: "Compare Data over time",
    description:
      "Track environmental changes over time using satellite data and historical comparisons.",
    button: "Learn more",
  },
  {
    id: "monitoring",
    title: "Environmental Monitoring",
    description:
      "Monitor air, water, drought, and heat levels in Jeddah with interactive maps.",
    button: "Learn more",
  },
];

const CustomServices = ({ setPage }: { setPage: (page: string) => void }) => {
  const handleButtonClick = (id: string) => {
    if (id === "monitoring") {
      setPage("monitoring");
    }

    // Change "services" to your Monitoring page ID if needed
    else if (id === "ai-model") {
      setPage("ai-model");
    } else {
      alert(`Button clicked for ${id}`);
    }
  };

  return (
    <div className="custom-services-container">
      {customServices.map((service) => (
        <div key={service.id} className="custom-service-card">
          <h3 className="custom-service-title">{service.title}</h3>
          <p className="custom-service-description">{service.description}</p>
          <button
            className="custom-service-button"
            onClick={() => handleButtonClick(service.id)}
          >
            {service.button}
          </button>
        </div>
      ))}
    </div>
  );
};

export default CustomServices;
