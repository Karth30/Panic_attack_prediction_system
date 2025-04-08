import streamlit as st
import pandas as pd
import joblib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from geopy.distance import geodesic

# ---------- Constants ----------
SENSOR_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRzXBG0e1DxhFgwu2nrGpq9A2rQXQAVlAtynFhfRvpnRvZDAK5CPn5r2DywtggJFbP8JgDBkq06FZZt/pub?output=csv"
LOCATION_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRIIqsqYTbIGAYoplhrxnS4V7zjE0-SBs1rNEM52eUS8RoA2EhTWHgTsfN5vQT0fQ5WiG3RVTy1uphM/pub?output=csv"

SENDER_EMAIL = "karthayani2210333@ssn.edu.in"
APP_PASSWORD = "ssn2210333"
RECEIVER_EMAIL = "gracia2210343@ssn.edu.in"

# ---------- Email Alert ----------
def send_email_alert():
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = " PANIC ALERT - Sensor Dashboard"

    body = """
    Immediate attention needed!

    A PANIC status has been detected from the sensor data.
    Please check the dashboard for more information.
    """
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(msg)
            st.info(" Email alert sent.")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# ---------- Main Dashboard ----------
def main():
    st.set_page_config("GSR Sensor Dashboard", layout="wide")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "email_sent" not in st.session_state:
        st.session_state.email_sent = False

    if not st.session_state.logged_in:
        st.title("Login to Dashboard")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username == "admin" and password == "1234":
                st.session_state.logged_in = True
                st.success("Login successful")
            else:
                st.error("Incorrect credentials")
        return

    st.title("Sensor Monitoring Dashboard")

    try:
        df = pd.read_csv(SENSOR_CSV_URL)
    except Exception as e:
        st.error(f"Error loading sensor sheet: {e}")
        return

    required_cols = ["Timestamp", "GSR Voltage", "Temperature", "BPM"]
    if df.empty or not all(col in df.columns for col in required_cols):
        st.warning("Sheet is empty or missing required columns.")
        return

    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df = df.sort_values("Timestamp")

    # ---------- ML Prediction ----------
    try:
        model = joblib.load("nopanic.pkl")
        X_live = df[["GSR Voltage", "Temperature", "BPM"]]
        preds = model.predict(X_live)

        # Updated label map: 0 - Normal, 1 - Low Stress, 2 - Panic
        label_map = {0: "Normal", 1: "Low Stress", 2: "Panic"}
        df["Status"] = [label_map.get(p, "Unknown") for p in preds]
    except Exception as e:
        st.warning(f"ML Prediction failed: {e}")
        df["Status"] = "Unknown"

    # ---------- Latest Reading ----------
    latest = df.iloc[-1]
    st.subheader("Latest Sensor Reading")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Timestamp", latest["Timestamp"].strftime("%Y-%m-%d %H:%M:%S"))
    col2.metric("GSR Voltage", f'{latest["GSR Voltage"]:.4f} V')
    col3.metric("Temperature", f'{latest["Temperature"]:.2f} °C')
    col4.metric("BPM", int(latest["BPM"]))
    col5.metric("Status", latest["Status"])

    # ---------- Panic Alert ----------
    if latest["Status"] == "Panic":
        st.error(" ALERT: PANIC Detected!")
        st.markdown("### Immediate attention required!")
        if not st.session_state.email_sent:
            send_email_alert()
            st.session_state.email_sent = True
    elif latest["Status"] == "Normal":
        st.success("Status: Normal")
        st.session_state.email_sent = False
    elif latest["Status"] == "Low Stress":
        st.info("Status: Low Stress")
        st.session_state.email_sent = False
    else:
        st.warning("Status Unknown")

    # ---------- Graphs ----------
    st.markdown("---")
    st.subheader("Trend Visualizations")
    tab1, tab2, tab3, tab4 = st.tabs(["GSR Voltage", "Temperature", "BPM", "Status"])

    with tab1:
        st.line_chart(df.set_index("Timestamp")["GSR Voltage"])
    with tab2:
        st.line_chart(df.set_index("Timestamp")["Temperature"])
    with tab3:
        st.line_chart(df.set_index("Timestamp")["BPM"])
    with tab4:
        st.line_chart(df.set_index("Timestamp")["Status"].apply(lambda x: 1 if x == "Panic" else 0))

    # ---------- Full Table ----------
    st.markdown("---")
    st.subheader("Historical Sensor Data")
    st.dataframe(df[["Timestamp", "GSR Voltage", "Temperature", "BPM", "Status"]], use_container_width=True)

    # ---------- GPS Location Tracking ----------
    st.markdown("---")
    st.subheader("GPS Location and Distance Tracking")

    try:
        gps_df = pd.read_csv(LOCATION_CSV_URL)
        gps_df["Timestamp"] = pd.to_datetime(gps_df["Timestamp"])
        gps_df = gps_df.sort_values("Timestamp")

        st.sidebar.subheader("Safe Zone Settings")
        safe_lat = st.sidebar.number_input("Safe Zone Latitude", value=12.753682, format="%.6f")
        safe_lon = st.sidebar.number_input("Safe Zone Longitude", value=80.197107, format="%.6f")
        safe_radius = st.sidebar.slider("Safe Radius (meters)", min_value=1, max_value=100, value=10)

        def check_zone(row):
            current = (row["Latitude"], row["Longitude"])
            center = (safe_lat, safe_lon)
            distance = geodesic(current, center).meters
            return pd.Series({
                "DistanceFromSafeZone": distance,
                "ZoneStatus": "Inside" if distance <= safe_radius else "Outside"
            })

        gps_df[["DistanceFromSafeZone", "ZoneStatus"]] = gps_df.apply(check_zone, axis=1)

        st.map(gps_df.rename(columns={"Latitude": "lat", "Longitude": "lon"}))
        st.line_chart(gps_df.set_index("Timestamp")["DistanceFromSafeZone"])

        latest_gps = gps_df.iloc[-1]
        if latest_gps["ZoneStatus"] == "Outside":
            st.error(f"OUT OF SAFE ZONE! Distance: {latest_gps['DistanceFromSafeZone']:.2f} m")
        else:
            st.success(f"Within Safe Zone. Distance: {latest_gps['DistanceFromSafeZone']:.2f} m")

        st.subheader("Historical GPS Data")
        st.dataframe(
            gps_df[["Timestamp", "Latitude", "Longitude", "DistanceFromSafeZone", "ZoneStatus"]],
            use_container_width=True
        )

    except Exception as e:
        st.warning(f"GPS Tracking Failed: {e}")

if __name__ == "__main__":
    main()
