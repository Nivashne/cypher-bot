from __future__ import annotations

import argparse
import random
import time
from dataclasses import dataclass
from datetime import datetime, timezone

import numpy as np
import requests

DRONE_SIGNATURES = {
    "DJI Phantom": {"base_freq": 22.0, "doppler": 1.5, "strength": -62},
    "Military UAV": {"base_freq": 15.0, "doppler": 2.4, "strength": -68},
    "Stealth UAV": {"base_freq": 8.0, "doppler": 3.5, "strength": -74},
    "Unknown Object": {"base_freq": 5.0, "doppler": 4.2, "strength": -78},
}

TERRAIN_PROFILES = {
    "Himalaya": {"attenuation": 0.48, "noise": 0.85, "latency": (1.2, 2.0)},
    "Urban": {"attenuation": 0.72, "noise": 0.55, "latency": (0.5, 1.1)},
    "Desert": {"attenuation": 0.82, "noise": 0.35, "latency": (0.3, 0.8)},
}


@dataclass
class TrackState:
    lat: float
    lon: float
    vel_lat: float
    vel_lon: float


def kalman_smooth(signal: np.ndarray, process_noise: float = 0.02, measurement_noise: float = 0.1) -> np.ndarray:
    x_est = np.zeros_like(signal)
    p = 1.0
    x_est[0] = signal[0]
    for i in range(1, len(signal)):
        p = p + process_noise
        k = p / (p + measurement_noise)
        x_est[i] = x_est[i - 1] + k * (signal[i] - x_est[i - 1])
        p = (1 - k) * p
    return x_est


def mock_lstm_classifier(features: dict[str, float]) -> tuple[str, float]:
    candidates = []
    for drone_type, sig in DRONE_SIGNATURES.items():
        score = 1.0
        score -= abs(features["dom_freq"] - sig["base_freq"]) / 30
        score -= abs(features["doppler_shift"] - sig["doppler"]) / 6
        score -= abs(features["signal_strength"] - sig["strength"]) / 40
        candidates.append((drone_type, max(0.0, score)))

    candidates.sort(key=lambda x: x[1], reverse=True)
    best = candidates[0]
    confidence = min(0.98, 0.52 + best[1] * 0.48 + random.uniform(-0.04, 0.06))
    return best[0], max(0.5, confidence)


def generate_rf_signal(drone_type: str, terrain: str, t: np.ndarray) -> tuple[np.ndarray, float, float]:
    sig = DRONE_SIGNATURES[drone_type]
    terrain_cfg = TERRAIN_PROFILES[terrain]

    doppler = sig["doppler"] + np.random.normal(0, 0.3)
    freq = sig["base_freq"] + doppler
    attenuation = terrain_cfg["attenuation"]

    clean = np.sin(2 * np.pi * freq * t)
    reflected = 0.4 * np.sin(2 * np.pi * (freq * 0.65) * t + 0.5)
    noise = np.random.normal(0, terrain_cfg["noise"], len(t))

    composite = attenuation * (clean + reflected) + 0.3 * noise
    signal_strength = sig["strength"] + (1 - attenuation) * -20 + np.random.normal(0, 1.5)
    return composite, float(signal_strength), float(doppler)


def extract_features(signal: np.ndarray, sample_rate: int, signal_strength: float, doppler: float) -> dict[str, float]:
    spectrum = np.abs(np.fft.rfft(signal))
    freqs = np.fft.rfftfreq(len(signal), d=1 / sample_rate)
    dom_freq = float(freqs[np.argmax(spectrum)])
    return {
        "dom_freq": dom_freq,
        "signal_strength": signal_strength,
        "doppler_shift": doppler,
    }


def random_move(track: TrackState) -> TrackState:
    jitter_lat = random.uniform(-0.0002, 0.0002)
    jitter_lon = random.uniform(-0.0002, 0.0002)
    track.vel_lat = 0.75 * track.vel_lat + jitter_lat
    track.vel_lon = 0.75 * track.vel_lon + jitter_lon

    track.lat += track.vel_lat
    track.lon += track.vel_lon
    return track


def run_simulation(server_url: str, terrain: str, source_unit: str, interval: float) -> None:
    t = np.linspace(0, 1.5, 768)
    sample_rate = int(len(t) / (t[-1] - t[0]))

    track = TrackState(31.1048, 77.1734, 0.0003, 0.0001)
    rare_unknown_counter = 0

    while True:
        rare_unknown_counter += 1
        if rare_unknown_counter % 9 == 0 and terrain == "Himalaya":
            chosen = "Unknown Object"
            print("[Scenario] Unknown stealth object detected in weak signal zone")
        else:
            chosen = random.choice(list(DRONE_SIGNATURES.keys())[:-1])

        print("Receiving signal from LEO satellite...")
        raw_signal, signal_strength, doppler = generate_rf_signal(chosen, terrain, t)

        print("Applying Kalman filter...")
        filtered = kalman_smooth(raw_signal)

        print("Running LSTM model...")
        features = extract_features(filtered, sample_rate, signal_strength, doppler)
        drone_type, confidence = mock_lstm_classifier(features)

        print("Detection complete")
        print(f"→ type={drone_type} conf={confidence:.2f} strength={signal_strength:.1f} dBm doppler={doppler:.2f}Hz")

        track = random_move(track)
        payload = {
            "drone_type": drone_type,
            "confidence": round(confidence, 3),
            "location": [round(track.lat, 6), round(track.lon, 6)],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "signal_strength": round(signal_strength, 2),
            "doppler_shift": round(doppler, 3),
            "terrain": terrain,
            "source_unit": source_unit,
        }

        latency = random.uniform(*TERRAIN_PROFILES[terrain]["latency"])
        time.sleep(latency)

        try:
            res = requests.post(f"{server_url}/alert", json=payload, timeout=10)
            print(f"Alert sent [{res.status_code}] from {source_unit}\n")
        except requests.RequestException as exc:
            print(f"Failed to send alert: {exc}\n")

        time.sleep(interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Field Detection Unit (LEO passive bistatic radar simulator)")
    parser.add_argument("--server", default="http://127.0.0.1:8000", help="Backend API base URL")
    parser.add_argument("--terrain", choices=list(TERRAIN_PROFILES.keys()), default="Himalaya")
    parser.add_argument("--source-unit", default=f"FDU-{random.randint(10,99)}")
    parser.add_argument("--interval", type=float, default=2.5, help="Seconds between alert batches")
    args = parser.parse_args()

    run_simulation(args.server, args.terrain, args.source_unit, args.interval)
