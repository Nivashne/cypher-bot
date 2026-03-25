import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

export default function SignalChart({ alerts }) {
  const data = [...alerts]
    .slice(0, 20)
    .reverse()
    .map((a, idx) => ({
      i: idx + 1,
      signal: a.signal_strength,
      doppler: a.doppler_shift,
    }));

  return (
    <div className="panel p-4 h-[300px]">
      <h2 className="text-cyan-300 font-semibold mb-3">📊 Signal Intelligence</h2>
      <ResponsiveContainer width="100%" height="85%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis dataKey="i" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" />
          <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155' }} />
          <Line type="monotone" dataKey="signal" stroke="#22d3ee" dot={false} name="Signal (dBm)" />
          <Line type="monotone" dataKey="doppler" stroke="#f97316" dot={false} name="Doppler (Hz)" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
