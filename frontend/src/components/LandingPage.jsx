import { useState } from "react";
import { useNavigate } from "react-router-dom";

function LandingPage({ setCandidateId, setCandidateName, role, setRole }) {
  const [name, setName] = useState("");
  const [resume, setResume] = useState(null);

  const navigate = useNavigate(); 

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log("Submitting:", role);

    const formData = new FormData();
    formData.append("name", name);
    formData.append("resume", resume);  // PDF or text file
    formData.append("role", role);

    try {
      const res = await fetch("http://localhost:8000/candidate/", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      // Store candidate_id in React state (lifted to App.jsx)
      setCandidateId(data.candidate_id);
      setCandidateName(data.candidate_name); // Store candidate_name in state 

      // Route to ChatUI
      navigate("/chat");
    } catch (err) {
      console.error("Error registering candidate:", err);
    }
  };

  return (
    <div className="flex justify-center items-center h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 font-sans">
      <div className="w-full max-w-lg bg-white/5 backdrop-blur-xl border border-white/10 shadow-2xl rounded-2xl p-10 my-6">
        <h1 className="text-3xl font-bold text-white mb-10 text-left">
          HireQuest Registration
        </h1>

        <form onSubmit={handleSubmit} className="space-y-8 text-left">
          {/* Name Field */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-3">
              Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-3 rounded-lg bg-white/10 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-400 transition-all duration-200"
              placeholder="Enter your name"
              required
            />
          </div>

          {/* Resume Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-3">
              Upload Resume
            </label>
            <input
              type="file"
              accept=".pdf,.doc,.docx"
              onChange={(e) => setResume(e.target.files[0])}
              className="w-full text-gray-300 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-[#f1f5f9] file:text-gray-900 hover:file:bg-gray-200 transition-all duration-200"
              required
            />
          </div>

          {/* Role Dropdown */}
            <div className="relative">
              <select
                value={role}
                onChange={(e) => {
                  console.log("Selected role:", e.target.value);
                  setRole(e.target.value);
                }}
                className="appearance-none w-full px-4 py-3 pr-10 rounded-lg bg-white/10 text-white focus:outline-none focus:ring-2 focus:ring-blue-400"
              >
                <option value="ML">ML</option>
                <option value="Advanced_ML">Advanced_ML</option>
                <option value="Data_Science">Data_Science</option>
              </select>

              <div className="pointer-events-none absolute inset-y-0 right-3 flex items-center">
                ▼
              </div>
            </div>

          {/* Submit Button */} 
          <button
            type="submit"
            className="w-full bg-blue-500 hover:bg-blue-600 active:scale-95 text-white font-semibold py-3 rounded-lg shadow transition-transform duration-200"
          >
            Submit
          </button>
        </form>
      </div>
    </div>
  );
}

export default LandingPage;
