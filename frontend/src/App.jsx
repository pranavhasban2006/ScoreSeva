import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import HealthPage from "./pages/HealthPage";
import ScorePage from "./pages/ScorePage";
import FraudPage from "./pages/FraudPage";
import TrajectoryPage from "./pages/TrajectoryPage";

// Phase 3B-3D pages — placeholders until those phases are built
const Placeholder = ({ title }) => (
  <div className="card max-w-lg mx-auto text-center py-16">
    <p className="text-4xl mb-4">🔧</p>
    <p className="text-xl font-bold text-gray-800">{title}</p>
    <p className="text-sm text-gray-500 mt-2">
      Coming in the next phase — form and results UI will appear here.
    </p>
  </div>
);

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index          element={<ScorePage />} />
          <Route path="fraud"      element={<FraudPage />} />
          <Route path="trajectory" element={<TrajectoryPage />} />
          <Route path="nlp"        element={<Placeholder title="NLP Psychometric" />} />
          <Route path="health"     element={<HealthPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
