/**
 * ChatUI.jsx
 * Candidate interview chat interface.
 * Uses candidate's name and QuestAI bot for Q&A loop.
 * Integrates backend APIs: /interview (first question), /answer, /interview/{id}/question.
 */

import { useState, useRef, useEffect } from "react";
import { FaRobot } from "react-icons/fa";

function ChatUI({ candidateId, candidateName, role }) {
  const BOT_NAME = "QuestAI"; // branded interviewer

  // Chat state
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const textareaRef = useRef(null);
  const [loading, setLoading] = useState(false);

  // 🔹 Call /interview on mount to get the first question
  useEffect(() => {
    const startInterview = async () => {
      try {
        const res = await fetch("http://localhost:8000/candidate/interview", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            candidate_id: candidateId,
            role: role,
          }),
        });
        const data = await res.json();

        // Add welcome + first question
        setMessages([
          { text: `Hello ${candidateName}, welcome to your ${role} interview!`, sender: BOT_NAME },
          { text: data.question, sender: BOT_NAME },
        ]);
      } catch (err) {
        console.error("Error starting interview:", err);
      }
    };

    if (candidateId) {
      startInterview();
    }
  }, [candidateId, role, candidateName]);

  // Handle answer submission + fetch next question
    const handleSend = async () => {
    if (input.trim() === "" || loading) return;
    setLoading(true);

    // Push candidate answer
    const userMessage = { text: input, sender: candidateName };
    setMessages((prev) => [...prev, userMessage]);

    try {
      // Save answer to backend
      await fetch("http://localhost:8000/interview/answer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          candidate_id: candidateId,
          role: role,
          question: messages[messages.length - 1].text, // last bot question
          answer: input,
        }),
      });

      // Fetch next question or summary
      const res = await fetch(`http://localhost:8000/interview/${candidateId}/question`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          candidate_id: candidateId,
          role: role,
        }),
      });
      const data = await res.json();

      // Branch: summary vs next question
      if (data.status === "complete") {
        setMessages((prev) => [
          ...prev,
          { text: data.summary, sender: BOT_NAME },
          { text: data.closing, sender: BOT_NAME },
        ]);
      } else {
        setMessages((prev) => [...prev, { text: data.question, sender: BOT_NAME }]);
      }
    } catch (err) {
      console.error(err);
      setMessages((prev) => [...prev, { text: "Error fetching next question.", sender: BOT_NAME }]);
    } finally {
      setInput("");
      setLoading(false);
      if (textareaRef.current) textareaRef.current.style.height = "auto";
    }
  };


  return (
    <div className="flex flex-col h-screen">
      {/* Chat area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div key={idx} className={msg.sender === candidateName ? "text-right" : "text-left"}>
            <p
              className={`inline-block p-2 rounded ${
                msg.sender === candidateName ? "bg-gray-200 text-gray-900" : "bg-blue-200 text-gray-900"
              }`}
            >
              {msg.text}
            </p>
            <div className="text-xs text-gray-400 mt-1">{msg.sender}</div>
          </div>
        ))}
      </div>

      {/* Input area */}
      <div className="p-3 border-t flex items-end gap-2">
        <textarea
          ref={textareaRef}
          rows={1}
          className="flex-1 border rounded px-2 py-1"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
          placeholder={`Answer as ${candidateName}...`}
        />
        <button onClick={handleSend} className="bg-blue-500 text-white px-4 py-2 rounded">
          ➤
        </button>
      </div>
    </div>
  );
}

export default ChatUI;
