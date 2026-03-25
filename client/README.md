# Client (Field Detection Unit Simulator)

Python simulator that generates synthetic RF detections and sends alerts periodically.

## Run

```bash
cd client
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python simulator.py --server http://127.0.0.1:8000 --terrain Himalaya --source-unit FDU-01
```

Run multiple simulators to emulate multiple field units.
