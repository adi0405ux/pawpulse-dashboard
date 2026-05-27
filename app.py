import streamlit as st
import paho.mqtt.client as mqtt
import json
import time
import os

st.set_page_config(page_title="PawPulse Dashboard", page_icon="🐾", layout="centered")

# 1. The File Bridge
DATA_FILE = "sensor_data.json"

def on_connect(client, userdata, flags, rc):
    client.subscribe("pawpulse/aditri/alerts")

def on_message(client, userdata, msg):
    # Background thread writes incoming internet data directly to the local disk
    try:
        data = json.loads(msg.payload.decode())
        data["last_sync"] = time.strftime("%I:%M:%S %p")
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)
    except:
        pass

@st.cache_resource
def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("broker.hivemq.com", 1883, 60)
    client.loop_start()
    return client

start_mqtt()

# 2. Main UI Thread reads from the disk safely
status = "NORMAL"
delta = 0
last_sync = "Never"

if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            status = data.get("status", "NORMAL")
            delta = data.get("transient_delta", 0)
            last_sync = data.get("last_sync", "Never")
    except:
        pass

# 3. UI Rendering
st.title("🩺 PawPulse Clinical Dashboard")
st.markdown("---")
st.subheader("Patient Vitals Profile")

col1, col2 = st.columns(2)
with col1:
    st.info("**Patient ID:** \n\n Canine Unit A")
with col2:
    st.success("**Hardware Link:** \n\n ONLINE")

st.markdown("### Active Diagnostics Gating")

if status == "CRITICAL_RALE_DETECTED":
    st.error("⚠️ **CRITICAL ANOMALY VERIFIED**")
    st.warning(f"**Calculated Signal Delta ($dV/dt$):** {delta}")
else:
    st.success("✅ **Patient Breathing Baseline Normal**")
    st.info("No pulmonary anomalies caught within current sampling cycle.")

st.markdown("---")

if st.button("🔄 Acknowledge & Clear Alert"):
    with open(DATA_FILE, "w") as f:
        json.dump({"status": "NORMAL", "transient_delta": 0, "last_sync": "Cleared by Vet"}, f)
    st.rerun()

st.caption(f"Last Telemetry Sync Frame: {last_sync}")

# Force the UI to refresh every second
time.sleep(1)
st.rerun()
