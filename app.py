import streamlit as st
import paho.mqtt.client as mqtt
import json
import ssl
from streamlit_autorefresh import st_autorefresh

# --- UI CONFIGURATION ---
st.set_page_config(page_title="PawPulse Dashboard", page_icon="🐾", layout="centered")
st.title("🐾 PawPulse: Live Vitals")
st.markdown("---")

# --- AUTO-REFRESH ENGINE ---
st_autorefresh(interval=2000, key="data_refresh")

# --- 1. SHARED MEMORY (The Bypass) ---
# This creates a persistent dictionary that ignores Streamlit's thread locks
@st.cache_resource
def get_sensor_data():
    return {"bpm": "--", "temp": "--"}

sensor_data = get_sensor_data()

# --- 2. MQTT CALLBACKS ---
# We write directly to the shared Python dictionary now, NOT session_state
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe("pawpulse/vitals")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        sensor_data["bpm"] = payload.get("bpm", "--")
        sensor_data["temp"] = payload.get("temp", "--")
    except Exception:
        pass

# --- 3. DAEMON INITIALIZATION ---
# This ensures the MQTT connection only boots up exactly once
@st.cache_resource
def init_mqtt():
    client = mqtt.Client(transport="websockets")
    client.tls_set()  # Keep the WSS encryption for the cloud firewall
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect("broker.hivemq.com", 8884, 60)
        client.loop_start()
        return client
    except Exception as e:
        return None

client = init_mqtt()

# --- 4. DASHBOARD UI ---
col1, col2 = st.columns(2)

# Read the data straight from the shared memory dictionary
with col1:
    st.metric(label="❤️ Heart Rate", value=f"{sensor_data['bpm']} BPM")

with col2:
    st.metric(label="🌡️ Body Temp", value=f"{sensor_data['temp']} °F")

st.markdown("---")
if client is None:
    st.error("Fatal Error: Could not bind to MQTT Broker.")
else:
    st.caption("Listening on broker.hivemq.com | Shared Memory Architecture Active")
