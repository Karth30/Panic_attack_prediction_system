import streamlit as st
import pandas as pd
import joblib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Your Published Google Sheet CSV Link (CSV format)
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRzXBG0e1DxhFgwu2nrGpq9A2rQXQAVlAtynFhfRvpnRvZDAK5CPn5r2DywtggJFbP8JgDBkq06FZZt/pub?output=csv"

def send_email_alert():
    sender_email = "karthayani2210333@ssn.edu.in"
    app_password = "ssn2210333"  # Use Gmail App Password
    receiver_email = "gracia2210343@ssn.edu.in"

    subject = " Panic Alert - Sensors Dashboard"
    body = "Immediate attention needed!\n\nA panic status has been detected in the latest GSR sensor reading."

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(msg)
            st.info(" Email alert sent successfully.")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

def main():
    st.set_page_config("GSR Sensor Dashboard", layout="wide")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "email_sent" not in st.session_state:
        st.session_state.email_sent = False

    # Login
    if not st.session_state.logged_in:
        st.title("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username == "admin" and password == "1234":
                st.session_state.logged_in = True
                st.success("Login successful!")
            else:
                st.error("Incorrect credentials")
        return

    # Dashboard
    st.title("GSR Sensor Dashboard")

    # Load data from Google Sheets
    try:
        df = pd.read_csv(SHEET_CSV_URL)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return

    if df.empty or not all(col in df.columns for col in ["Timestamp", "Raw Value", "GSR Voltage", "Temperature"]):
        st.warning("Sheet is empty or missing expected columns.")
        return

    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df = df.sort_values("Timestamp")

    # ML Prediction
    try:
        model = joblib.load("panic_model.pkl")  # Your trained model
        X_live = df[["Raw Value", "GSR Voltage", "Temperature"]]
        preds = model.predict(X_live)
        df["Status"] = ["Panic" if p == 1 else "Normal" for p in preds]
    except Exception as e:
        st.error(f"ML Prediction error: {e}")
        df["Status"] = "Unknown"

    # Latest Readings
    latest = df.iloc[-1]
    st.subheader("Latest Readings")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Raw Value", f'{latest["Raw Value"]:.2f}')
    col2.metric("GSR Voltage", f'{latest["GSR Voltage"]:.4f} V')
    col3.metric("Temperature", f'{latest["Temperature"]:.2f} °C')
    col4.metric("Status", latest["Status"])

    # Display Alert and Send Email
    if latest["Status"] == "Panic":
        st.error("🚨 ALERT: Panic detected in the latest reading!")
        st.markdown("#### **Immediate action required!**")
        if not st.session_state.email_sent:
            send_email_alert()
            st.session_state.email_sent = True
    elif latest["Status"] == "Normal":
        st.success("Status: Normal")
        st.session_state.email_sent = False  # Reset for next alert
    else:
        st.warning("Status Unknown")

    st.markdown("---")
    st.subheader("Trend Graphs")

    tab1, tab2, tab3 = st.tabs(["Raw Value", "GSR Voltage", "Temperature"])
    with tab1:
        st.line_chart(df.set_index("Timestamp")["Raw Value"])
    with tab2:
        st.line_chart(df.set_index("Timestamp")["GSR Voltage"])
    with tab3:
        st.line_chart(df.set_index("Timestamp")["Temperature"])

    st.markdown("---")
    st.subheader("Prediction Table")
    st.dataframe(df[["Timestamp", "Raw Value", "GSR Voltage", "Temperature", "Status"]])

if __name__ == "__main__":
    main()
