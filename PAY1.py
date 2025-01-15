import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(layout="wide")

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
            "start_time": "08:00 AM",
            "end_time": "04:00 PM",
        }

# User Input: Editable calendar-like view
st.title("Bi-Weekly Pay Calculator")

# Display Total Bi-Weekly Salary on Top
if "biweekly_pay" in st.session_state:
    st.subheader(f"Total Bi-Weekly Pay: **${st.session_state['biweekly_pay']:.2f}**")

st.write("Click on a day to adjust your work hours:")

# Full-width layout for calendar
columns = st.columns(14)  # 14 days per row (bi-weekly view)
for i, date in enumerate(dates):
    col = columns[i % 14]  # Display all 14 days in one row
    date_str = date.strftime("%Y-%m-%d")
    day_data = st.session_state.data[date_str]

    with col:
        # Display day tile
        tile_label = f"{date.strftime('%a, %b %d')}\n{day_data['start_time']} - {day_data['end_time']}"
        if st.button(tile_label, key=f"edit_{date_str}"):
            # Open pop-up for time editing
            st.session_state.edit_date = date_str

# Show time editor if a date is selected for editing
if "edit_date" in st.session_state:
    edit_date = st.session_state.edit_date
    st.subheader(f"Edit Work Hours for {edit_date}")

    col1, col2, col3 = st.columns(3)
    with col1:
        start_hour = st.selectbox("Start Hour", [f"{h:02}" for h in range(1, 13)], key="start_hour")
        end_hour = st.selectbox("End Hour", [f"{h:02}" for h in range(1, 13)], key="end_hour")
    with col2:
        start_minute = st.selectbox("Start Minute", [f"{m:02}" for m in range(0, 60)], key="start_minute")
        end_minute = st.selectbox("End Minute", [f"{m:02}" for m in range(0, 60)], key="end_minute")
    with col3:
        start_ampm = st.selectbox("AM/PM", ["AM", "PM"], key="start_ampm")
        end_ampm = st.selectbox("AM/PM", ["AM", "PM"], key="end_ampm")

    if st.button("Save Changes"):
        # Update session state with the new times
        st.session_state.data[edit_date]["start_time"] = f"{start_hour}:{start_minute} {start_ampm}"
        st.session_state.data[edit_date]["end_time"] = f"{end_hour}:{end_minute} {end_ampm}"
        del st.session_state["edit_date"]
        

# Convert data into DataFrame for calculation
unlocked_data = []
for date, data in st.session_state.data.items():
    start_dt = datetime.strptime(f"{date} {data['start_time']}", "%Y-%m-%d %I:%M %p")
    end_dt = datetime.strptime(f"{date} {data['end_time']}", "%Y-%m-%d %I:%M %p")
    unlocked_data.append({"Date": date, "Start Time": start_dt, "End Time": end_dt})

if unlocked_data:
    unlocked_df = pd.DataFrame(unlocked_data)
    calculated_df = calculate_biweekly_pay(unlocked_df, st.session_state.settings["pay"])

    # Store total bi-weekly pay in session state
    st.session_state["biweekly_pay"] = calculated_df['Pay'].sum()

    # Display Results
    st.subheader("Bi-Weekly Pay Details")
    st.write(f"Hourly Pay: ${st.session_state.settings['pay']}")
    st.write(f"Week Start Date: {week_start_date.strftime('%Y-%m-%d')}")

    # Calendar View
    st.subheader("Calendar View")
    st.table(calculated_df[["Date", "Start Time", "End Time", "Total Hours", "Pay"]])
else:
    st.write("No data available. Adjust work hours to see details.")
