// frontend/src/components/ChatUI/SourceCitation.jsx
export default function SourceCitation({ sources }) {
  if (!sources || sources.length === 0) return null;
  return (
    <div className="mt-2 text-xs text-slate-400">
      <div className="font-medium mb-1">Sources:</div>
      <ul className="list-disc list-inside space-y-0.5">
        {sources.map((s, i) => (
          <li key={i}>{s}</li>
        ))}
      </ul>
    </div>
  );
}
