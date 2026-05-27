import streamlit as st
import paho.mqtt.client as mqtt
import json
import time

# --- UI CONFIGURATION ---
st.set_page_config(page_title="PawPulse Dashboard", page_icon="🐾", layout="centered")
st.title("🐾 PawPulse: Live Vitals")
st.markdown("---")

# --- SESSION STATE INITIALIZATION ---
if 'bpm' not in st.session_state:
    st.session_state.bpm = "--"
if 'temp' not in st.session_state:
    st.session_state.temp = "--"

# --- MQTT CALLBACKS ---
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe("pawpulse/vitals")
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    try:
        # Decode the JSON payload from the ESP32
        payload = json.loads(msg.payload.decode())
        
        # Update the session state variables
        st.session_state.bpm = payload.get("bpm", "--")
        st.session_state.temp = payload.get("temp", "--")
    except Exception as e:
        print(f"Data parsing error: {e}")

# --- MQTT CLIENT SETUP (THE HIVEMQ PIVOT) ---
broker = "broker.hivemq.com"
port = 1883

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(broker, port, 60)
    client.loop_start()
except Exception as e:
    st.error(f"MQTT Connection Error: {e}")

# --- DASHBOARD UI ---
col1, col2 = st.columns(2)

with col1:
    st.metric(label="❤️ Heart Rate", value=f"{st.session_state.bpm} BPM")

with col2:
    st.metric(label="🌡️ Body Temp", value=f"{st.session_state.temp} °F")

st.markdown("---")
st.caption("Awaiting real-time telemetry from ESP32 Edge Node...")

# Auto-refresh the Streamlit UI every 2 seconds to fetch new data
time.sleep(2)
st.rerun()
