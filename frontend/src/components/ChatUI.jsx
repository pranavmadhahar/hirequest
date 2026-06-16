/**
 * ChatUI.jsx
 * Candidate interview chat interface.
 * Uses candidate's name and QuestAI bot for Q&A loop.
 * Integrates backend APIs:
 * - POST /candidate/interview
 * - POST /interview/answer
 * - POST /interview/{id}/question
 */

import { useState, useRef, useEffect } from "react";
import { FaRobot } from "react-icons/fa";

/* ---------------- Typewriter ---------------- */

function Typewriter({ text, onComplete }) {
  const [displayed, setDisplayed] = useState("");
  const onCompleteRef = useRef(onComplete);

  // Always keep latest callback without restarting animation
  useEffect(() => {
    onCompleteRef.current = onComplete;
  }, [onComplete]);

  useEffect(() => {
    setDisplayed("");

    let index = 0;

    const interval = setInterval(() => {
      if (index >= text.length) {
        clearInterval(interval);

        if (onCompleteRef.current) {
          onCompleteRef.current();
        }

        return;
      }

      const char = text.charAt(index);

      setDisplayed((prev) => prev + char);

      index++;
    }, 30);

    return () => clearInterval(interval);
  }, [text]);

  return <span>{displayed}</span>;
}

/* ---------------- Chat UI ---------------- */

function ChatUI({ candidateId, candidateName, role }) {
  console.log("role:", role);
  const BOT_NAME = "QuestAI";

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const textareaRef = useRef(null);

  /* ---------------- Helper ---------------- */

  const addBotMessage = (text) => {
    setMessages((prev) => [
      ...prev,
      {
        text,
        sender: BOT_NAME,
        animate: true,
      },
    ]);
  };

  /* ---------------- Start Interview ---------------- */

  useEffect(() => {
    const startInterview = async () => {
      try {
        const res = await fetch(
          "http://localhost:8000/candidate/interview",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              candidate_id: candidateId,
              role: role,
            }),
          }
        );

        const data = await res.json();

        setMessages([
          {
            text: `Hello ${candidateName}, welcome to your ${role} interview!`,
            sender: BOT_NAME,
            animate: false,
          },
          {
            text: data.question,
            sender: BOT_NAME,
            animate: true,
          },
        ]);
      } catch (err) {
        console.error("Error starting interview:", err);

        setMessages([
          {
            text: "Unable to start interview.",
            sender: BOT_NAME,
            animate: false,
          },
        ]);
      }
    };

    if (candidateId) {
      startInterview();
    }
  }, [candidateId, candidateName, role]);

  /* ---------------- Textarea Resize ---------------- */

  const handleInputChange = (e) => {
    setInput(e.target.value);

    const textarea = textareaRef.current;

    if (!textarea) return;

    textarea.style.height = "auto";
    textarea.style.height = `${textarea.scrollHeight}px`;
  };

  /* ---------------- Send Answer ---------------- */

  const handleSend = async () => {
    const answerText = input.trim();

    if (!answerText || loading) return;

    const lastBotQuestion =
      [...messages]
        .reverse()
        .find((msg) => msg.sender === BOT_NAME)?.text || "";

    setInput("");

    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }

    setLoading(true);

    const userMessage = {
      text: answerText,
      sender: candidateName,
      animate: false,
    };

    setMessages((prev) => [...prev, userMessage]);

    try {
      await fetch("http://localhost:8000/interview/answer", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          candidate_id: candidateId,
          role,
          question: lastBotQuestion,
          answer: answerText,
        }),
      });

      const res = await fetch(
        `http://localhost:8000/interview/${candidateId}/question`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            candidate_id: candidateId,
            role,
          }),
        }
      );

      const data = await res.json();

      if (data.status === "complete") {
        setMessages((prev) => [
          ...prev,
          {
            text: data.summary,
            sender: BOT_NAME,
            animate: true,
            isSummary: true,
            closing: data.closing,
          },
        ]);
      } else {
        addBotMessage(data.question);
      }
    } catch (err) {
      console.error("Send error:", err);

      addBotMessage("Error fetching next question.");
    } finally {
      setLoading(false);
    }
  };

  /* ---------------- UI ---------------- */

  return (
    <div className="flex justify-center items-center h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 font-sans">
      <div className="w-full max-w-3xl h-[90vh] bg-white/5 backdrop-blur-xl border border-white/10 shadow-2xl rounded-2xl flex flex-col my-4">

        {/* HEADER */}

        <div className="p-4 border-b border-white/10 flex items-center gap-3">
          <div className="p-2 bg-blue-500/20 rounded-md text-blue-400">
            <FaRobot size={20} />
          </div>

          <div>
            <h2 className="font-semibold text-white">HireQuest</h2>
            <p className="text-xs text-gray-400">
              Interview Assistant • Online
            </p>
          </div>
        </div>

        {/* CHAT AREA */}

        <div className="flex-1 overflow-y-auto p-4 space-y-4 transition-all duration-300 ease-in-out">
          {messages.map((msg, idx) => {
            const isUser = msg.sender === candidateName;

            return (
              <div
                key={idx}
                className={isUser ? "text-right" : "text-left"}
              >
                <p
                  className={`inline-block px-4 py-2 rounded-2xl text-sm shadow-md max-w-[70%] transition-transform duration-200 ${
                    isUser
                      ? "bg-gray-200 text-gray-900 rounded-br-none"
                      : "bg-blue-500/20 text-blue-100 rounded-bl-none"
                  }`}
                >
                  {msg.animate ? (
                    <Typewriter
                      text={msg.text}
                        onComplete={() => {
                          if (msg.isSummary && msg.closing) {
                            addBotMessage(msg.closing);
                          }

                          setMessages((prev) =>
                            prev.map((message, messageIndex) =>
                              messageIndex === idx
                                ? {
                                    ...message,
                                    animate: false,
                                  }
                                : message
                            )
                          );
                        }}
                    />
                  ) : (
                    msg.text
                  )}
                </p>

                <div className="text-xs text-gray-400 mt-1">
                  {msg.sender}
                </div>
              </div>
            );
          })}
        </div>

        {/* INPUT AREA */}

        <div className="p-3 border-t border-white/10 flex items-end gap-2">
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            disabled={loading}
            onChange={handleInputChange}
            placeholder={`Answer as ${candidateName}...`}
            className="flex-1 bg-white/10 text-white placeholder-gray-400 rounded-2xl px-4 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400 resize-none overflow-hidden max-h-32 transition-all duration-200"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
          />

          <button
            onClick={handleSend}
            disabled={loading}
            className={`text-white p-3 rounded-full shadow transition-transform duration-200 ${
              loading
                ? "bg-gray-500 cursor-not-allowed"
                : "bg-blue-500 hover:bg-blue-600 hover:scale-105 active:scale-95"
            }`}
          >
            {loading ? "..." : "➤"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ChatUI;