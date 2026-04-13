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


#Predefined list of tickers(stocks)
Tickers=['AAPL','GOOGL','MSFT','AMZN','TSLA','TCS','REL',]

def gen_mock_trade():
    #generates a single mock trade as json
    trade={
        "timestamp":time.strftime("%Y-%m-%d %H-%M-%S",time.localtime(time.time())),
        "ticker":random.choice(Tickers),
        "price":round(random.uniform(100,500),2),
        "volume":random.randint(1,500)
        }
    return json.dumps(trade)
def worker(data_queue,trades_to_generate=50):
    '''
    THIS function is a dedicated data receiver,running
    entirely as seprate process,pushing data into queue.
    '''
    print(f"Starting up,Generating {trades_to_generate} trades...",flush=True)
    for _ in range(trades_to_generate):
        trade_json=gen_mock_trade()
        data_queue.put(trade_json)
        time.sleep(0.01)
    data_queue.put(None)#A poison pill to tell queue that data stream has ended and it can shutdown
    print("Finished sending data",flush=True)
def analyzer(data_queue,signal_queue):
    print("Analyzer: Online. Crunching Numbers...",flush=True)
    trade_history={ticker:deque(maxlen=5)for ticker in Tickers}

    while True:
        raw_data=data_queue.get()
        if raw_data is None:
            print("Analyzer:Received shutdown Signal. Stopping.",flush=True)
            signal_queue.put(None)
            break
        trade=json.loads(raw_data)
        ticker=trade["ticker"]
        trade_history[ticker].append(trade)
        history=trade_history[ticker]

        if len(history)==5:
            prices=[t["price"] for t in history]
            volumes=[t["volume"] for t in history]
            sma = sum(prices)/5
            total_volume=sum(volumes)
            price_volume_products=itertools.starmap(operator.mul,zip(prices,volumes))
            vwap=sum(price_volume_products)/total_volume
            signal_payload={
                "type":"Live Signal",
                "ticker":ticker,
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
    producer=Process(target=worker,args=(raw_data_pipeline,150))
    consumer=Process(target=analyzer,args=(raw_data_pipeline,signal_pipeline))
    broadcaster=Process(target=broadcast_thread,args=(signal_pipeline,))

    broadcaster.start()
    consumer.start()
    producer.start()
    
    producer.join()
    consumer.join()
    

    broadcaster.terminate()
    print("--- StreamTrade Engine Offline ---",flush=True)
