import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

const threatColor = {
  LOW: '#10b981',
  MEDIUM: '#f59e0b',
  CRITICAL: '#ef4444',
};

export default function ThreatMap({ alerts }) {
  return (
    <div className="panel p-4 h-[430px]">
      <h2 className="text-cyan-300 font-semibold mb-3">🌍 Tactical Map</h2>
      <MapContainer center={[30.3753, 78.4832]} zoom={5} style={{ height: '90%', width: '100%', borderRadius: '0.75rem' }}>
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {alerts.map((alert, idx) => (
          <CircleMarker
            key={`${alert.id ?? idx}-${alert.timestamp}`}
            center={alert.location}
            radius={8}
            pathOptions={{ color: threatColor[alert.threat_level] ?? '#22d3ee' }}
          >
            <Popup>
              <p><b>{alert.drone_type}</b></p>
              <p>Threat: {alert.threat_level}</p>
              <p>Confidence: {(alert.confidence * 100).toFixed(1)}%</p>
              <p>{alert.terrain} | {alert.source_unit}</p>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
}
