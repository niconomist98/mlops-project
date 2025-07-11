import streamlit as st
import requests
import json
import time
import os
import socket
from datetime import datetime, timezone

st.set_page_config(
    page_title="ML Inference Interface",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("Machine Learning Inference")
st.markdown(
    """
    <p style="font-size: 18px; color: gray;">
        An interface for demonstrating machine learning model inference with datetime and text inputs.
    </p>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown("<p><strong>Created At:</strong></p>", unsafe_allow_html=True)
    created_at_date = st.date_input(
        "Select a date",
        value=datetime.now().date(),
        label_visibility="collapsed"
    )
    created_at_time_input = st.time_input(
        "Select a time",
        value=datetime.now().time(),
        label_visibility="collapsed"
    )
    combined_datetime_naive = datetime.combine(created_at_date, created_at_time_input)

    created_at_datetime_utc = combined_datetime_naive.astimezone(timezone.utc)


    st.markdown("<p><strong>Input Text:</strong></p>", unsafe_allow_html=True)
    text = st.text_area(
        "Enter text here",
        value="This is a default text input for the model.",
        height=150,
        label_visibility="collapsed"
    )

    predict_button = st.button("Run Inference", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h2>Inference Results</h2>", unsafe_allow_html=True)

    if predict_button:
        with st.spinner("Running inference..."):
            formatted_created_at = created_at_datetime_utc.isoformat(timespec='milliseconds').replace('+00:00', 'Z')

            api_data = {
                "created_at": formatted_created_at,
                "text": text
            }

            try:
                api_endpoint = os.getenv("API_URL", "http://model:8000")
                predict_url = f"{api_endpoint.rstrip('/')}/predict"

                st.write(f"Connecting to API at: {predict_url}")
                st.json(api_data)

                response = requests.post(predict_url, json=api_data)
                response.raise_for_status()
                prediction = response.json()

                st.session_state.prediction = prediction
                st.session_state.prediction_time = time.time()
            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to API: {e}")
                if response is not None:
                    st.write("API Response Content (for debugging):", response.text)
                st.warning("Using mock data for demonstration purposes. Please check your API connection.")
                st.session_state.prediction = {
                    "prediction_score": 0.85,
                    "predicted_class": "positive",
                    "confidence": 0.92,
                    "processing_time_ms": 50,
                    "model_version": "1.0.0"
                }
                st.session_state.prediction_time = time.time()

    if "prediction" in st.session_state:
        pred = st.session_state.prediction

        st.markdown(f'<div class="prediction-value">Prediction: {pred.get("predicted_class", "N/A")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="prediction-score">Score: {pred.get("prediction_score", "N/A"):.2f}</div>', unsafe_allow_html=True)


        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown('<p class="info-label">Confidence</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="info-value">{(pred.get("confidence", 0) * 100):.0f}%</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_b:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown('<p class="info-label">Model Version</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="info-value">{pred.get("model_version", "N/A")}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        col_c, col_d = st.columns(2)
        with col_c:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown('<p class="info-label">Processing Time</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="info-value">{pred.get("processing_time_ms", "N/A")} ms</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="top-factors">', unsafe_allow_html=True)
        st.markdown("<p><strong>Raw Prediction Output:</strong></p>", unsafe_allow_html=True)
        st.json(pred)
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown("""
        <div style="display: flex; height: 300px; align-items: center; justify-content: center; color: #6b7280; text-align: center;">
            Enter the datetime and text, then click "Run Inference" to see the model's output.
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

version = os.getenv("APP_VERSION", "1.0.0")
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    f"""
    <div style="text-align: center; font-size: 12px; color: gray;">
        App Version: {version} | Hostname: {hostname} | IP: {ip_address}
    </div>
    """,
    unsafe_allow_html=True,
)