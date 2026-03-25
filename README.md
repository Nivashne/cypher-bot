# DRDO-Style LEO Passive Bistatic Radar Drone Detection Network (Simulation)

This project is a complete full-stack simulation of a defense-style stealth drone detection network using **LEO satellite passive bistatic radar concepts**.

## Architecture

- `backend/` — FastAPI server for alert ingestion, persistence, and websocket broadcast.
- `client/` — Python Field Detection Unit simulator (synthetic RF + mock LSTM/Kalman pipeline).
- `frontend/` — React + Tailwind command dashboard (map, alerts, charts, logs).

---

## 1) Backend Setup (FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Endpoints:

- `POST /alert`
- `GET /alerts`
- `GET /logs`
- `WS /ws`

Threat policy:

- `< 0.75` -> `LOW`
- `0.75 - 0.9` -> `MEDIUM`
- `> 0.9` -> `CRITICAL`

---

## 2) Client Setup (Field Detection Unit)

```bash
cd client
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python simulator.py --server http://127.0.0.1:8000 --terrain Himalaya --source-unit FDU-01
```

Run multiple clients in separate terminals for multi-unit simulation:

```bash
python simulator.py --server http://127.0.0.1:8000 --terrain Urban --source-unit FDU-02
python simulator.py --server http://127.0.0.1:8000 --terrain Desert --source-unit FDU-03
```

Client behavior includes:

- Synthetic RF waveform generation (noise + Doppler + attenuation)
- Terrain attenuation profiles (Himalaya, Urban, Desert)
- Mock Kalman + LSTM-like classifier
- Artificial latency (satellite delay)
- Randomized moving drone coordinates
- Periodic unknown stealth-object scenario in Himalaya mode

---

## 3) Frontend Setup (DRDO Command Dashboard)

```bash
cd frontend
npm install
npm run dev
```

Then open: `http://127.0.0.1:5173`

Optional API endpoint override:

```bash
VITE_API_BASE=http://127.0.0.1:8000 npm run dev
```

Dashboard modules:

- 🌍 Tactical map (Leaflet) with live threat markers
- 📊 Signal intelligence chart (signal + Doppler over time)
- 🚨 Alert panel with color-coded threat levels
- 🧾 Live logs panel with backend processing messages
- 🔄 WebSocket real-time streaming updates

---

## Alert JSON format

```json
{
  "drone_type": "Stealth UAV",
  "confidence": 0.92,
  "location": [31.12222, 77.19123],
  "timestamp": "2026-03-25T10:05:22.120002+00:00",
  "signal_strength": -70,
  "doppler_shift": 3.5,
  "terrain": "Himalaya",
  "source_unit": "FDU-01"
}
```

---

## Example runtime output

Client console sample:

```text
Receiving signal from LEO satellite...
Applying Kalman filter...
Running LSTM model...
Detection complete
→ type=Stealth UAV conf=0.93 strength=-73.6 dBm doppler=3.51Hz
Alert sent [200] from FDU-01
```

Backend logs sample:

```text
Signal received from field unit
Analyzing threat level...
```

---

## Demo notes

This is a simulation intended for academic/demo use. It is engineered to look operationally realistic while using synthetic RF and mock AI inference.
