# 📈 StreamTrade Engine

A high-performance, real-time trading data ingestion and analysis engine. 

This project utilizes Python's `multiprocessing` architecture to independently fetch live market data from a Google Sheet, calculate quantitative metrics (SMA, VWAP), and stream live buy/sell signals to a frontend dashboard via WebSockets.

## 🚀 Architecture overview

The backend is built with three concurrent processes to ensure zero-blocking performance:
1. **The Worker:** Polls a Google Sheet API for live market data, dynamically detecting new tickers and managing state to avoid duplicate ingestion.
2. **The Analyzer:** Consumes raw data, maintains a moving queue for individual stocks, and calculates real-time Simple Moving Averages (SMA) and Volume Weighted Average Prices (VWAP).
3. **The Broadcaster:** An asynchronous WebSocket server that streams processed signals to connected clients instantly.

## 🛠️ Tech Stack
* **Backend:** Python (Multiprocessing, Asyncio)
* **Data Ingestion:** Google Sheets API (`gspread`, `oauth2client`)
* **Real-time Streaming:** WebSockets
* **Frontend:** HTML, Vanilla JS, Tailwind CSS

## ⚙️ Setup & Installation

**1. Clone the repository**
```bash
git clone [https://github.com/YourUsername/StreamTrade_Engine.git](https://github.com/YourUsername/StreamTrade_Engine.git)
cd StreamTrade_Engine
2. Install Dependencies

Bash
pip install gspread oauth2client websockets
3. Google Sheets Authentication

Create a Google Cloud Service Account and download the JSON key.

Rename the file to service_account.json and place it in the backend/ directory.

Ensure your .gitignore is active so this file is never pushed to public repositories.

4. Google Sheet Format
Your Google Sheet must include the following headers in Row 1:
Stock | Tickers | Current Price | Volume

5. Boot the Engine

Bash
python backend/engine.py
Then, open frontend/index.html in your browser to view the live dashboard.