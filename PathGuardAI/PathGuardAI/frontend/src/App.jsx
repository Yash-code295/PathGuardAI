import { useState } from "react";
import axios from "axios";
import "./App.css";

const API = "https://pathguardai.onrender.com";

export default function App() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("Ready for mission analysis");
  const [showResults, setShowResults] = useState(false);
  const [resilience, setResilience] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [steps, setSteps] = useState([]);
  const [refreshKey, setRefreshKey] = useState(Date.now());

  const missionSteps = [
    "Upload",
    "Road Extraction",
    "Criticality",
    "Simulation",
    "Routing",
    "Resilience",
    "Recommendation",
    "Completed",
  ];

  const analyze = async () => {
  if (!file) return setStatus("Please upload a satellite image first.");

  const callAPI = async (name, url) => {
    setStatus(`${name}...`);
    console.log("Running:", name, url);
    const response = await axios.get(url);
    console.log(`${name} done`, response.data);
  };

  try {
    const fd = new FormData();
    fd.append("file", file);

    setShowResults(false);
    setResilience(null);
    setRecommendation(null);
    setSteps([]);

    setStatus("Uploading satellite frame...");
    setSteps(["Upload"]);
    await axios.post(`${API}/upload`, fd);

    setSteps(["Upload", "Road Extraction"]);
    await callAPI("Extracting roads", `${API}/predict?t=${Date.now()}`);

    setSteps(["Upload", "Road Extraction", "Criticality"]);
    await callAPI("Finding critical nodes", `${API}/criticality?t=${Date.now()}`);

    setSteps(["Upload", "Road Extraction", "Criticality", "Simulation"]);
    await callAPI("Running simulation", `${API}/simulate?t=${Date.now()}`);

    setSteps(["Upload", "Road Extraction", "Criticality", "Simulation", "Routing"]);
    await callAPI("Planning route", `${API}/route?t=${Date.now()}`);

    setSteps(["Upload", "Road Extraction", "Criticality", "Simulation", "Routing", "Resilience"]);
    await callAPI("Calculating resilience", `${API}/resilience?t=${Date.now()}`);

    setSteps(["Upload", "Road Extraction", "Criticality", "Simulation", "Routing", "Resilience", "Recommendation"]);
    await callAPI("Generating recommendation", `${API}/recommendation?t=${Date.now()}`);

    const res = await axios.get(`${API}/resilience-data?t=${Date.now()}`);
    setResilience(res.data);

    const rec = await axios.get(`${API}/outputs/recommendation.json?t=${Date.now()}`);
    setRecommendation(rec.data);

    setRefreshKey(Date.now());
    setStatus("Mission analysis completed ✅");
    setSteps(missionSteps);
    setShowResults(true);
  } catch (err) {
    console.error("FULL ERROR:", err);
    setStatus(`Pipeline error ❌ ${err.message}`);
  }
};

  return (
    <main className="mission-page">
      <nav className="nav">
        <div className="brand">PATHGUARD<span>AI</span></div>
        <div className="nav-links">
          <a href="#mission">Mission</a>
          <a href="#pipeline">Pipeline</a>
          <a href="#results">Dashboard</a>
        </div>
      </nav>

      <section className="hero" id="mission">
        <div className="hero-left">
          <p className="eyebrow">Bharatiya Antariksh Hackathon 2026</p>
          <h1>Road Resilience<br />Intelligence from Space</h1>
          <p className="sub">
            Occlusion-robust road extraction, graph-theoretic criticality,
            disaster simulation, emergency routing and AI-powered response
            recommendations.
          </p>

          <div className="mission-panel">
            <label className="uploadLabel">
              <input type="file" onChange={(e) => setFile(e.target.files[0])} />
              <span className="uploadIcon"></span>
              <div>
                <h4>{file ? file.name : "Upload Satellite Image"}</h4>
                <p>Drop or select a satellite road frame</p>
              </div>
            </label>
            <button onClick={analyze}>Launch Analysis ↗</button>
          </div>

          <p className="status">{status}</p>

          <div className="timeline">
            {missionSteps.map((step) => (
              <div className={steps.includes(step) ? "step active" : "step"} key={step}>
                <span></span>
                <p>{step}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="hero-visual">
          <video className="spaceVideo" autoPlay muted loop playsInline>
            <source src="/space-bg.mp4" type="video/mp4" />
          </video>
          <div className="videoOverlay"></div>
          <div className="missionText">
          </div>
        </div>
      </section>

      <section className="mission-strip">
        <div><h3>AI Vision</h3><p>Road Segmentation</p></div>
        <div><h3>Graph Theory</h3><p>Critical Node Ranking</p></div>
        <div><h3>Risk Engine</h3><p>Disaster Simulation</p></div>
        <div><h3>Rescue Logic</h3><p>Emergency Routing</p></div>
      </section>

      <section className="pipeline" id="pipeline">
        <p className="section-kicker">Mission Pipeline</p>
        <h2>From satellite pixels to actionable intelligence</h2>
        <div className="pipeline-grid">
          <div>Satellite Input</div><span>→</span>
          <div>Road Extraction</div><span>→</span>
          <div>Graph Analysis</div><span>→</span>
          <div>Disaster Simulation</div><span>→</span>
          <div>AI Recommendations</div>
        </div>
      </section>

      <section className="cards">
        <div className="card"><h3>01 / Road Extraction</h3><p>Detects roads from satellite imagery even under partial occlusion.</p></div>
        <div className="card blue"><h3>02 / Critical Nodes</h3><p>Identifies high-risk network bottlenecks using graph centrality.</p></div>
        <div className="card"><h3>03 / Disaster Impact</h3><p>Simulates critical route failure and network fragmentation.</p></div>
        <div className="card blue"><h3>04 / Rescue Route</h3><p>Finds emergency route alternatives for response teams.</p></div>
      </section>

      {showResults && (
        <section className="results" id="results">
          <div className="results-header">
            <p className="section-kicker">Command Dashboard</p>
            <h2>Live Mission Outputs</h2>
            <p>Generated from the uploaded satellite image using PathGuardAI’s road intelligence pipeline.</p>
          </div>

          <div className="summary-grid">
            {resilience && (
              <div className="score-card">
                <p>Resilience Score</p>
                <h1>{resilience.score}%</h1>
                <span>{resilience.status}</span>
              </div>
            )}

            {recommendation && (
              <div className="recommendation-card">
                <h3>AI Suggested Actions</h3>
                <p><b>Risk Level:</b> {recommendation.risk_level}</p>
                <ul>
                  {recommendation.recommendations.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <div className="dashboard-grid">
            <div className="output-card large">
              <h3>Predicted Road Mask</h3>
              <p>AI-extracted road network from satellite frame.</p>
              <img src={`${API}/outputs/pred_mask.png?t=${refreshKey}`} alt="Predicted road mask" />
            </div>

            <div className="output-card">
              <h3>Critical Nodes</h3>
              <p>Red points indicate graph-critical road bottlenecks.</p>
              <img src={`${API}/outputs/critical_nodes_fixed.png?t=${refreshKey}`} alt="Critical nodes" />
            </div>

            <div className="output-card">
              <h3>Disaster Simulation</h3>
              <p>Network fragmentation after critical road failure.</p>
              <img src={`${API}/outputs/disaster_simulation.png?t=${refreshKey}`} alt="Disaster simulation" />
            </div>

            <div className="output-card">
              <h3>Emergency Route</h3>
              <p>Generated rescue corridor after disruption.</p>
              <img src={`${API}/outputs/emergency_route.png?t=${refreshKey}`} alt="Emergency route" />
            </div>
          </div>
        </section>
      )}
    </main>
  );
}