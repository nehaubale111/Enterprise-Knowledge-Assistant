// frontend/src/components/ChatUI/MessageBubble.jsx
export default function MessageBubble({ role, text }) {
  const isUser = role === "user";
  return (
    <div
      className={`flex ${isUser ? "justify-end" : "justify-start"} mb-2`}
    >
      <div
        className={`max-w-xl px-4 py-2 rounded-2xl text-sm whitespace-pre-wrap ${
          isUser
            ? "bg-indigo-600 text-white rounded-br-sm"
            : "bg-slate-800 text-slate-100 rounded-bl-sm border border-slate-700"
        }`}
      >
        {text}
      </div>
    </div>
  );
}
