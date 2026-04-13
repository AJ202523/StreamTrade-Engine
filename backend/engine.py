import json
import random
import time
import itertools
import operator
from multiprocessing import Process,Queue
from threading import Thread
from collections import deque
import websockets
import asyncio
import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials


#Predefined list of tickers(stocks)
#Tickers=['AAPL','GOOGL','MSFT','AMZN','TSLA','TCS','REL',]
'''
def gen_mock_trade():
    #generates a single mock trade as json
    trade={
        "timestamp":time.strftime("%Y-%m-%d %H-%M-%S",time.localtime(time.time())),
        "ticker":random.choice(Tickers),
        "price":round(random.uniform(100,500),2),
        "volume":random.randint(1,500)
        }
    return json.dumps(trade)
'''
def worker(data_queue):
    '''
    THIS function is a dedicated data receiver,running
    entirely as seprate process,pushing data into queue.
    '''
    print("Connecting to google sheets...",flush=True)
    scope=["https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"]
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        key_path = os.path.join(current_dir, "service_account.json")
        creds=ServiceAccountCredentials.from_json_keyfile_name(key_path,scope)
        client=gspread.authorize(creds)

        sheet=client.open("Copy of Stocks").sheet1
        print("Connected to Google Sheets",flush=True)
        last_seen_data = []
        while True:
            records=sheet.get_all_records()
            if records==last_seen_data:
                time.sleep(5)
                continue
            
            for row in records:
                if row not in last_seen_data:
                    trade_payload={
                        "timestamp":time.strftime("%Y-%m-%d %H-%M-%S",time.localtime(time.time())),
                        "ticker":str(row.get("Tickers","UNKNOWN")).upper(),
                        "name":str(row.get("Stock","UNKNOWN")).upper(),
                        "price":float(row.get("Current Price",0.0)),
                        "volume":int(row.get("Volume",0))
                    }
                    data_queue.put(json.dumps(trade_payload))
            last_seen_data = records
            time.sleep(5)
    except Exception as e:
        print("Error while connecting: ",e,flush=True)
        print("Sending Shutdown signal...",flush=True)
        data_queue.put(None)
def analyzer(data_queue,signal_queue):
    print("Analyzer: Online. Crunching Numbers dynamically...",flush=True)
    trade_history={}

    while True:
        raw_data=data_queue.get()
        if raw_data is None:
            print("Analyzer:Received shutdown Signal. Stopping.",flush=True)
            signal_queue.put(None)
            break
        trade=json.loads(raw_data)
        ticker=trade["ticker"]
        if ticker not in trade_history:
            trade_history[ticker]=deque(maxlen=5)
            print(f"Analyzer: New Ticker Detected: {ticker}",flush=True)
        trade_history[ticker].append(trade)
        history=trade_history[ticker]

        if len(history)>=1:
            prices=[t["price"] for t in history]
            volumes=[t["volume"] for t in history]
            sma = sum(prices)/5
            total_volume=sum(volumes)
            if total_volume>0:
                price_volume_products=itertools.starmap(operator.mul,zip(prices,volumes))
                vwap=sum(price_volume_products)/total_volume
            else:
                vwap=0
            signal_payload={
                "type":"Live Signal",
                "ticker":ticker,
                "name":trade["name"],
                "metrics":{
                    "sma":round(sma,2),
                    "vwap":round(vwap,2),
                    "volume":total_volume
                    }
                }
            signal_queue.put(json.dumps(signal_payload))
            
def broadcast_thread(signal_queue):
    print("Websocket Server: Booting up on ws://localhost:8765",flush=True)
    async def stream_data(websocket):
        print("Client Connected to Dashboard",flush=True)
        try:
            while True:
                if not signal_queue.empty():
                    signal_data=signal_queue.get()

                
                    if signal_data is None:
                        print("Broadcaster Shutdown Signal Received.",flush=True)
                        break
                    await websocket.send(signal_data)
                await asyncio.sleep(0.01)
        except websockets.exceptions.ConnectionClosed:
            print("Client Disconnected from Dashboard",flush=True)
    async def main():
        async with websockets.serve(stream_data,"localhost",8765):
            await asyncio.Future()#Run forever
    asyncio.run(main())
               
if __name__=="__main__":
    print("--- Booting StreamTrade Engine ---",flush=True)
    raw_data_pipeline=Queue()
    signal_pipeline=Queue()
    producer=Process(target=worker,args=(raw_data_pipeline,))
    consumer=Process(target=analyzer,args=(raw_data_pipeline,signal_pipeline))
    broadcaster=Process(target=broadcast_thread,args=(signal_pipeline,))

    broadcaster.start()
    consumer.start()
    producer.start()
    try:
        producer.join()
        consumer.join()
    except KeyboardInterrupt:
        print("\nStreamTrade Engine: Shutdown Signal Received.",flush=True)
    

    broadcaster.terminate()
    print("--- StreamTrade Engine Offline ---",flush=True)
