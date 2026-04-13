# StreamTrade Engine 📈

A high-performance market data ingestion engine and real-time dashboard built to simulate institutional trading environments. 

This project demonstrates the use of multi-process data pipelines in Python to handle high-frequency data streams, coupled with a minimalist React frontend for real-time visualization.



## 🏗️ Architecture
The system is divided into three main components:
* **The Firehose (Producer):** A dedicated process that generates thousands of mock trade records.
* **The Analyzer (Consumer):** A separate process that calculates rolling Simple Moving Averages (SMA) and Volume Weighted Average Price (VWAP) using high-speed `itertools` logic.
* **The Broadcaster:** An asynchronous WebSocket server that streams live signals to the frontend at `ws://localhost:8765`.

## 🛠️ Tech Stack
* **Backend:** Python 3.x
    * `multiprocessing` for parallel execution.
    * `asyncio` & `websockets` for real-time data streaming.
    * `collections.deque` for efficient rolling window memory.
* **Frontend:** React (via CDN) & Tailwind CSS
    * Minimalist dark-mode UI.
    * Monospaced typography for stable data rendering.
    * Pulse animations for live update cues.

## 🚀 How to Run Locally

### 1. Setup Backend
Ensure you have the `websockets` library installed:
```bash
pip install websockets
Navigate to the backend folder and start the engine:

Bash
python engine.py
2. Setup Frontend
Navigate to the frontend folder.

Open index.html in any modern web browser (Chrome/Edge recommended).

The dashboard will automatically connect to the Python server and begin displaying live ticker updates for AAPL, GOOGL, MSFT, TCS, REL, etc.

📊 Key Features
Zero-Latency Feel: Uses WebSockets instead of HTTP polling for instant data updates.

Fault Tolerance: Implements "poison pills" for graceful process shutdown.

Memory Efficient: Uses fixed-size deques to prevent memory leaks during long-running sessions.

Developed as a deep dive into Python's multiprocessing capabilities and real-time systems.