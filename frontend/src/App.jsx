import { useEffect, useMemo, useState } from 'react';
import AlertPanel from './components/AlertPanel';
import LogPanel from './components/LogPanel';
import SignalChart from './components/SignalChart';
import ThreatMap from './components/ThreatMap';

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8000';

export default function App() {
  const [alerts, setAlerts] = useState([]);
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const bootstrap = async () => {
      try {
        const [alertsRes, logsRes] = await Promise.all([
          fetch(`${API_BASE}/alerts`),
          fetch(`${API_BASE}/logs`),
        ]);
        setAlerts(await alertsRes.json());
        setLogs(await logsRes.json());
      } catch (error) {
        console.error(error);
      }
    };

    bootstrap();
  }, []);

  useEffect(() => {
    const ws = new WebSocket(API_BASE.replace('http', 'ws') + '/ws');

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === 'alert') {
        setAlerts((prev) => [msg.payload, ...prev].slice(0, 300));
      }
      if (msg.type === 'log') {
        setLogs((prev) => [...prev, msg.payload].slice(-1000));
      }
    };

    return () => ws.close();
  }, []);

  const summary = useMemo(() => {
    const critical = alerts.filter((a) => a.threat_level === 'CRITICAL').length;
    const medium = alerts.filter((a) => a.threat_level === 'MEDIUM').length;
    const low = alerts.filter((a) => a.threat_level === 'LOW').length;
    return { critical, medium, low };
  }, [alerts]);

  return (
    <div className="min-h-screen bg-drdo-bg text-slate-100 p-5">
      <header className="mb-5">
        <h1 className="text-2xl md:text-3xl font-bold tracking-wide text-cyan-200">DRDO Command Dashboard — Passive Bistatic LEO Radar Net</h1>
        <p className="text-slate-400">Defense-grade stealth drone detection simulation with real-time field telemetry.</p>
      </header>

      <section className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <SummaryCard label="Critical Threats" value={summary.critical} color="text-red-300" />
        <SummaryCard label="Medium Threats" value={summary.medium} color="text-amber-300" />
        <SummaryCard label="Low Threats" value={summary.low} color="text-emerald-300" />
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ThreatMap alerts={alerts.slice(0, 120)} />
        <div className="space-y-4">
          <SignalChart alerts={alerts} />
          <AlertPanel alerts={alerts.slice(0, 12)} />
        </div>
      </section>

      <section className="mt-4">
        <LogPanel logs={logs} />
      </section>
    </div>
  );
}

function SummaryCard({ label, value, color }) {
  return (
    <div className="panel p-4">
      <p className="text-slate-400 text-sm">{label}</p>
      <p className={`text-3xl font-bold ${color}`}>{value}</p>
    </div>
  );
}
