export default function LogPanel({ logs }) {
  return (
    <div className="panel p-4 h-[260px] overflow-y-auto">
      <h2 className="text-cyan-300 font-semibold mb-3">🧾 Live Logs</h2>
      <div className="space-y-2 font-mono text-xs">
        {logs.slice(-80).map((log, idx) => (
          <p key={`${log.timestamp}-${idx}`}>
            <span className="text-slate-400">[{new Date(log.timestamp).toLocaleTimeString()}]</span>{' '}
            <span className="text-cyan-200">{log.source}</span> — {log.message}
          </p>
        ))}
      </div>
    </div>
  );
}
