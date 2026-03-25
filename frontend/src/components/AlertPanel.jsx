const levelColor = {
  LOW: 'bg-emerald-500/20 text-emerald-300',
  MEDIUM: 'bg-amber-500/20 text-amber-300',
  CRITICAL: 'bg-red-500/20 text-red-300',
};

export default function AlertPanel({ alerts }) {
  return (
    <div className="panel p-4 h-[300px] overflow-y-auto">
      <h2 className="text-cyan-300 font-semibold mb-3">🚨 Alert Panel</h2>
      <div className="space-y-3 text-sm">
        {alerts.map((alert) => (
          <div key={alert.id ?? `${alert.timestamp}-${Math.random()}`} className="border border-slate-700 rounded-lg p-3 bg-slate-900/60">
            <div className="flex items-center justify-between">
              <p className="font-semibold text-slate-100">{alert.drone_type}</p>
              <span className={`px-2 py-1 text-xs rounded ${levelColor[alert.threat_level] ?? ''}`}>
                {alert.threat_level}
              </span>
            </div>
            <p>Confidence: {(alert.confidence * 100).toFixed(1)}%</p>
            <p>Signal: {alert.signal_strength} dBm | Doppler: {alert.doppler_shift} Hz</p>
            <p>Terrain: {alert.terrain} | Unit: {alert.source_unit}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
