# streamlit_app.py
import streamlit as st
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import threading
import time
import pandas as pd
import datetime

# Variabili globali
data = []
lock = threading.Lock()

# Add current date/time as the first row when script launches
current_datetime = datetime.datetime.now().strftime("%A, %B %d, %Y - %H:%M:%S")
initial_row = {"Subject": f"Current Time: {current_datetime}", "Trial": None, "Instrument": None, 
            "Room": None, "Condition": None, "Time(ms)": None, "LoudnessFrontal": None, 
            "LoudnessCentral": None, "LoudnessRear": None, "dBSPL": None}
data.append(initial_row)

# Handler OSC
def osc_handler(address, *args):
    timestamp = time.time()
    with lock:
        data.append({
            "timestamp": timestamp, 
            "address": address, 
            #"value": args[0] if args else None
            "Subject": args[0] if len(args) > 0 else None,
            "Trial": args[1] if len(args) > 1 else None,
            "Instrument": args[2] if len(args) > 2 else None,
            "Room": args[3] if len(args) > 3 else None,
            "Condition": args[4] if len(args) > 4 else None,
            "Time(ms)": args[5] if len(args) > 5 else None,
            "LoudnessFrontal": args[6] if len(args) > 5 else None,
            "LoudnessCentral": args[7] if len(args) > 5 else None,
            "LoudnessRear": args[8] if len(args) > 5 else None,
            "dBSPL": args[9] if len(args) > 5 else None,
            })

# Setup server OSC in un thread
def start_osc_server():
    dispatcher = Dispatcher()
    dispatcher.set_default_handler(osc_handler)
    server = BlockingOSCUDPServer(("0.0.0.0", 5010), dispatcher)
    server.serve_forever()

osc_thread = threading.Thread(target=start_osc_server, daemon=True)
osc_thread.start()

# Interfaccia Streamlit
st.set_page_config(page_title="MAX OSC Live Logger", layout="wide")
st.title("🎛️ Max/MSP OSC Live Logger")

# Mostra la tabella aggiornata in tempo reale
placeholder = st.empty()

# Bottone per scaricare CSV
if st.button("💾 Scarica CSV"):
    with lock:
        df = pd.DataFrame(data)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "osc_log.csv", "text/csv")

# Aggiorna live
while True:
    with lock:

        df = pd.DataFrame(data, columns=["Subject","Trial","Instrument","Room","Condition","Time(ms)","LoudnessFrontal","LoudnessCentral","LoudnessRear","dBSPL"])  # cambia qui se vuoi piu o meno dati!
    placeholder.dataframe(df)
    time.sleep(1)
