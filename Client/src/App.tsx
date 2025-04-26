import React, { useState } from "react";
import HomePage from "./homepage.tsx";
import About from "./About.tsx";
import Services from "./Services.tsx";
import Signup from "./Signup.tsx";
import SelectAnalysis from "./SelectAnalysis.tsx";
import FVC from "./FVC.tsx";

function App() {
  const [page, setPage] = useState("home"); // Track the current page

  return (
    <div className="container">
      {/* Navbar */}
      <nav className="navbar">
        <div className="logo">
          <img src="\Logojeddah.png" alt="logo" />
        </div>
        <button className="button1" onClick={() => setPage("home")}>
          Home
        </button>
        <button className="button2" onClick={() => setPage("about")}>
          About
        </button>
        <button className="button3" onClick={() => setPage("services")}>
          Services
        </button>
        <button className="button4" onClick={() => setPage("signup")}>
          signup
        </button>
      </nav>

      {/* Conditional Rendering of Pages */}
      {page === "home" && <HomePage setPage={setPage} />}
      {page === "about" && <About setPage={setPage} />}
      {page === "services" && <Services setPage={setPage} />}
      {page === "signup" && <Signup setPage={setPage} />}
      {page === "monitoring" && <SelectAnalysis setPage={setPage} />}
      {page === "ai-model" && <FVC setPage={setPage} />}
    </div>
  );
}

export default App;
