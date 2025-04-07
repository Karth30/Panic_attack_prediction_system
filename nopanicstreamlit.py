import streamlit as st
import pandas as pd
import joblib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ---------- Constants ----------
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRzXBG0e1DxhFgwu2nrGpq9A2rQXQAVlAtynFhfRvpnRvZDAK5CPn5r2DywtggJFbP8JgDBkq06FZZt/pub?output=csv"

SENDER_EMAIL = "karthayani2210333@ssn.edu.in"
APP_PASSWORD = "ssn2210333"  # Gmail App Password
RECEIVER_EMAIL = "gracia2210343@ssn.edu.in"

def send_email_alert():
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = " Panic Alert - Sensor Dashboard"

    body = """
    Immediate attention needed!

    A panic status has been detected from the sensor data. Please check the dashboard for more information.
    """
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(msg)
            st.info("Email alert sent.")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

def main():
    st.set_page_config("GSR Sensor Dashboard", layout="wide")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "email_sent" not in st.session_state:
        st.session_state.email_sent = False

    # ---------- Login ----------
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

    # ---------- Dashboard ----------
    st.title("Sensor Monitoring Dashboard")

    try:
        df = pd.read_csv(SHEET_CSV_URL)
    except Exception as e:
        st.error(f"Error loading Google Sheet: {e}")
        return

    required_cols = ["Timestamp", "GSR Voltage", "Temperature", "BPM", "Latitude", "Longitude"]
    if df.empty or not all(col in df.columns for col in required_cols):
        st.warning("Sheet is empty or missing required columns.")
        return

    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df = df.sort_values("Timestamp")

    # ---------- ML Prediction ----------
    try:
        model = joblib.load("panic_model.pkl")
        X_live = df[["GSR Voltage", "Temperature", "BPM"]]
        preds = model.predict(X_live)
        df["Status"] = ["Panic" if p == 1 else "Normal" for p in preds]
    except Exception as e:
        st.warning(f"ML Prediction failed: {e}")
        df["Status"] = "Unknown"

    # ---------- Latest Reading ----------
    latest = df.iloc[-1]
    st.subheader("Latest Sensor Reading")
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    col1.metric("Timestamp", latest["Timestamp"].strftime("%Y-%m-%d %H:%M:%S"))
    col2.metric("GSR Voltage", f'{latest["GSR Voltage"]:.4f} V')
    col3.metric("Temperature", f'{latest["Temperature"]:.2f} °C')
    col4.metric("BPM", int(latest["BPM"]))
    col5.metric("Latitude", f'{latest["Latitude"]}')
    col6.metric("Longitude", f'{latest["Longitude"]}')
    col7.metric("Status", latest["Status"])

    # ---------- GPS Map ----------
    st.subheader(" Device Location")
    try:
        gps_df = pd.DataFrame({
            "lat": [float(latest["Latitude"])],
            "lon": [float(latest["Longitude"])]
        })
        st.map(gps_df)
    except Exception as e:
        st.warning(f"Could not display map: {e}")

    # ---------- Alert System ----------
    if latest["Status"] == "Panic":
        st.error(" ALERT: Panic detected!")
        st.markdown("### Immediate action required!")
        if not st.session_state.email_sent:
            send_email_alert()
            st.session_state.email_sent = True
    elif latest["Status"] == "Normal":
        st.success("Status: Normal")
        st.session_state.email_sent = False
    else:
        st.warning("Status Unknown")

    # ---------- Graphs ----------
    st.markdown("---")
    st.subheader(" Trend Visualizations")

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
    st.subheader(" Historical Data")
    st.dataframe(df[["Timestamp", "GSR Voltage", "Temperature", "BPM", "Latitude", "Longitude", "Status"]], use_container_width=True)

if __name__ == "__main__":
    main()
