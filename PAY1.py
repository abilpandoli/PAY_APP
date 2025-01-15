import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Initialize session state for settings and data
if "settings" not in st.session_state:
    st.session_state.settings = {
        "pay": 20.0,  # Default hourly pay
        "week_start_date": datetime.now() - timedelta(days=datetime.now().weekday()),  # Start of the current week
    }
if "data" not in st.session_state:
    st.session_state.data = {}

# Function to calculate pay
def calculate_biweekly_pay(df, pay_rate):
    df['Total Hours'] = (df['End Time'] - df['Start Time']).dt.total_seconds() / 3600
    df['Pay'] = df['Total Hours'] * pay_rate
    return df

# Sidebar for settings
st.sidebar.header("Settings")
st.sidebar.subheader("Pay Settings")
st.session_state.settings["pay"] = st.sidebar.number_input(
    "Hourly Pay ($)", value=st.session_state.settings["pay"], min_value=0.0, step=0.5
)
st.session_state.settings["week_start_date"] = st.sidebar.date_input(
    "Week Start Date", value=st.session_state.settings["week_start_date"]
)

# Previous and Next Bi-Week Navigation
if st.button("Previous Bi-Week"):
    st.session_state.settings["week_start_date"] -= timedelta(days=14)

if st.button("Next Bi-Week"):
    st.session_state.settings["week_start_date"] += timedelta(days=14)

# Generate two weeks based on the current week start date
week_start_date = st.session_state.settings["week_start_date"]
dates = [week_start_date + timedelta(days=i) for i in range(14)]

# Ensure session state has data for these dates
for date in dates:
    date_str = date.strftime("%Y-%m-%d")
    if date_str not in st.session_state.data:
        st.session_state.data[date_str] = {
            "worked": False,
            "start_time": 8,
            "end_time": 16,
        }

# User Input: Editable horizontal calendar-like view with tiles
st.title("Bi-Weekly Pay Calculator")
st.write("Click on a day to unlock or lock it. Adjust your work hours for unlocked days:")

unlocked_data = []

# Horizontal calendar layout
columns = st.columns(7)  # 7 days per row (1 week)
for i, date in enumerate(dates):
    col = columns[i % 7]  # Wrap to new row every 7 days
    date_str = date.strftime("%Y-%m-%d")
    day_data = st.session_state.data[date_str]

    with col:
        # Display a toggleable tile for the day
        tile_label = (
            f"🔓 {date.strftime('%a, %b %d')}" if day_data["worked"] else f"🔒 {date.strftime('%a, %b %d')}"
        )
        tile_color = "background-color: #4CAF50; color: white;" if day_data["worked"] else "background-color: #F44336; color: white;"
        button_placeholder = st.empty()

        # Use a custom button style for the tile
        if button_placeholder.button(
            tile_label,
            key=f"toggle_{date_str}",
        ):
            st.session_state.data[date_str]["worked"] = not day_data["worked"]

        # If the day is unlocked, show sliders for Start Time and End Time
        if st.session_state.data[date_str]["worked"]:
            start_time = st.slider(
                "Start", min_value=0, max_value=24, value=day_data["start_time"], step=1, key=f"start_{date_str}"
            )
            end_time = st.slider(
                "End", min_value=0, max_value=24, value=day_data["end_time"], step=1, key=f"end_{date_str}"
            )
            st.session_state.data[date_str]["start_time"] = start_time
            st.session_state.data[date_str]["end_time"] = end_time

            # Append unlocked data
            unlocked_data.append({
                "Date": date,
                "Start Time": datetime.combine(date, datetime.min.time()) + timedelta(hours=start_time),
                "End Time": datetime.combine(date, datetime.min.time()) + timedelta(hours=end_time),
            })

# Convert unlocked data into DataFrame
if unlocked_data:
    unlocked_df = pd.DataFrame(unlocked_data)
    calculated_df = calculate_biweekly_pay(unlocked_df, st.session_state.settings["pay"])

    # Display Results
    st.subheader("Bi-Weekly Pay Details")
    st.write(f"Hourly Pay: ${st.session_state.settings['pay']}")
    st.write(f"Week Start Date: {week_start_date.strftime('%Y-%m-%d')}")
    st.write(f"Total Bi-Weekly Pay: **${calculated_df['Pay'].sum():,.2f}**")

    # Calendar View
    st.subheader("Calendar View")
    st.table(calculated_df[["Date", "Start Time", "End Time", "Total Hours", "Pay"]])
else:
    st.write("No days unlocked. Click on a day to unlock it.")
