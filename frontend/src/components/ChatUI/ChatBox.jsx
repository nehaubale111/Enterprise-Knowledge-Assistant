// frontend/src/components/ChatUI/ChatBox.jsx
import { useState } from "react";
import api from "../../utils/api.js";
import MessageBubble from "./MessageBubble.jsx";
import SourceCitation from "./SourceCitation.jsx";

export default function ChatBox() {
  const [messages, setMessages] = useState([]);
  const [sources, setSources] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    const question = input;
    setInput("");
    setLoading(true);

    try {
      const res = await api.post("/rag/query", { question, top_k: 5 });
      const botMsg = { role: "assistant", text: res.data.answer };
      setMessages((prev) => [...prev, botMsg]);
      setSources(res.data.sources || []);
    } catch (err) {
      const botMsg = {
        role: "assistant",
        text: "Error while fetching answer from backend.",
      };
      setMessages((prev) => [...prev, botMsg]);
      setSources([]);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {messages.map((m, idx) => (
          <MessageBubble key={idx} role={m.role} text={m.text} />
        ))}
        <SourceCitation sources={sources} />
      </div>

      <div className="border-t border-slate-800 p-3">
        <div className="flex items-end gap-2">
          <textarea
            rows={2}
            className="flex-1 bg-slate-900 border border-slate-700 rounded-xl text-sm text-slate-100 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="Ask a question about company policies, HR, SOPs..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKey}
          />
          <button
            onClick={sendMessage}
            disabled={loading}
            className="px-4 py-2 rounded-xl bg-indigo-500 hover:bg-indigo-600 text-white text-sm font-medium disabled:opacity-60"
          >
            {loading ? "Thinking..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}
