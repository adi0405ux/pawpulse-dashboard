import streamlit as st
import paho.mqtt.client as mqtt
import json
from streamlit_autorefresh import st_autorefresh

# --- UI CONFIGURATION ---
st.set_page_config(page_title="PawPulse Dashboard", page_icon="🐾", layout="centered")
st.title("🐾 PawPulse: Live Vitals")
st.markdown("---")

# --- AUTO-REFRESH ENGINE ---
st_autorefresh(interval=2000, key="data_refresh")

# --- SESSION STATE (PERSISTENT MEMORY) ---
if 'bpm' not in st.session_state:
    st.session_state.bpm = "--"
if 'temp' not in st.session_state:
    st.session_state.temp = "--"

# --- MQTT CALLBACKS ---
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe("pawpulse/vitals")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        st.session_state.bpm = payload.get("bpm", "--")
        st.session_state.temp = payload.get("temp", "--")
    except Exception:
        pass

# --- MQTT SETUP ---
if 'mqtt_client' not in st.session_state:
    # Force WebSockets to bypass the cloud firewall
    client = mqtt.Client(transport="websockets")
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        # HiveMQ WebSocket port is 8000
        client.connect("broker.hivemq.com", 8000, 60)
        client.loop_start()
        st.session_state.mqtt_client = client
    except Exception as e:
        st.error(f"MQTT Connection Error: {e}")

# --- DASHBOARD UI ---
col1, col2 = st.columns(2)

with col1:
    st.metric(label="❤️ Heart Rate", value=f"{st.session_state.bpm} BPM")

with col2:
    st.metric(label="🌡️ Body Temp", value=f"{st.session_state.temp} °F")

st.markdown("---")
st.caption("Listening on broker.hivemq.com (WebSockets) | Topic: pawpulse/vitals")
