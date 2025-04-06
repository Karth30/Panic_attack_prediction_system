import streamlit as st
import pandas as pd
import joblib

# Your Published Google Sheet CSV Link
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRzXBG0e1DxhFgwu2nrGpq9A2rQXQAVlAtynFhfRvpnRvZDAK5CPn5r2DywtggJFbP8JgDBkq06FZZt/pub?output=csv"

def main():
    st.set_page_config("GSR Sensor Dashboard", layout="wide")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

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

    # -- ML Prediction --
    try:
        model = joblib.load("panic_model.pkl")  # Ensure this file exists in the same directory
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
