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
@st.cache_resource
def get_sensor_data():
    # Includes all THREE metrics
    return {"bpm": "--", "temp": "--", "resp": "--"}

sensor_data = get_sensor_data()

# --- 2. MQTT CALLBACKS ---
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe("pawpulse/vitals")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        # The .get() method prevents fatal KeyErrors if a sensor fails
        sensor_data["bpm"] = payload.get("bpm", sensor_data["bpm"])
        sensor_data["temp"] = payload.get("temp", sensor_data["temp"])
        sensor_data["resp"] = payload.get("resp", sensor_data["resp"])
    except Exception:
        pass

# --- 3. DAEMON INITIALIZATION ---
@st.cache_resource
def init_mqtt():
    client = mqtt.Client(transport="websockets")
    client.tls_set()  
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect("broker.hivemq.com", 8884, 60)
        client.loop_start()
        return client
    except Exception:
        return None

client = init_mqtt()

# --- 4. DASHBOARD UI ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="❤️ Heart Rate", value=f"{sensor_data['bpm']} BPM")

with col2:
    st.metric(label="🌡️ Body Temp", value=f"{sensor_data['temp']} °F")

with col3:
    st.metric(label="🫁 Resp Rate", value=f"{sensor_data['resp']} BPM")

st.markdown("---")
if client is None:
    st.error("Fatal Error: Could not bind to MQTT Broker.")
else:
    st.caption("Status: Active | Shared Memory | 3-Axis Telemetry")
