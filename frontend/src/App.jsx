/**
 * App.jsx
 * Root component with routing.
 * Lifts candidateId and candidateName into state and passes them to child components.
 */

import { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import LandingPage from "./components/LandingPage";
import ChatUI from "./components/ChatUI";

function App() {
  // Candidate state (shared across pages)
  const [candidateId, setCandidateId] = useState(null);
  const [candidateName, setCandidateName] = useState(null);
  const [role, setRole] = useState("ML");

  return (
    <BrowserRouter>
      <Routes>
        {/* Registration page → sets candidateId + candidateName */}
        <Route
          path="/"
          element={
            <LandingPage
              setCandidateId={setCandidateId}
              setCandidateName={setCandidateName}
              setRole={setRole}
              role={role} // Pass role to LandingPage for selection
            />
          }
        />

        {/* Chat UI → interview loop uses both */}
        <Route
          path="/chat"
          element={
            <ChatUI
              candidateId={candidateId}
              candidateName={candidateName}
              role={role} // or pass role dynamically if needed
            />
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
