import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
from datetime import datetime, timedelta

# Sidebar dropdown for location
location = st.sidebar.selectbox("Choose a Location:", ["Bali", "India"])

# Display the main image and title
st.image("https://raw.githubusercontent.com/antoniusawe/sales-report/main/images/house_of_om-removebg-preview.png",  
         use_column_width=True)
st.markdown("<h1 style='text-align: center; font-size: 50px;'>HOUSE OF OM - DASHBOARD</h1>", unsafe_allow_html=True)

# Display today's date
today = datetime.today()
st.markdown(f"<h3 style='text-align: center; font-size: 16px;'>{today.strftime('%d %B %Y')}</h3>", unsafe_allow_html=True)

# Extract month from today's date for comparison
current_month = today.month

if location == "Bali":
    occupancy_url = "https://raw.githubusercontent.com/antoniusawe/sales-report/main/Bali%20data/bali_occupancy.xlsx"
    sales_url = "https://raw.githubusercontent.com/antoniusawe/sales-report/main/Bali%20data/bali_sales.xlsx"
    # Sub-dropdown for specific options under "Bali"
    bali_option = st.sidebar.selectbox("Choose a Section:", ["Overview", "Location", "Batch"])
    
    try:
        # Load data for occupancy and sales
        bali_occupancy_data = pd.read_excel(occupancy_url)
        bali_sales_data = pd.read_excel(sales_url)
        
        # Convert 'Batch start date' to datetime if it's not already
        if 'Batch start date' in bali_sales_data.columns:
            bali_sales_data['Batch start date'] = pd.to_datetime(bali_sales_data['Batch start date'], errors='coerce')
        # Convert 'Occupancy' column to numeric if it's not already (remove % and convert to float)
        if 'Occupancy' in bali_occupancy_data.columns:
            bali_occupancy_data['Occupancy'] = bali_occupancy_data['Occupancy'].replace('%', '', regex=True).astype(float)

    except Exception as e:
        st.error("Failed to load data. Please check the URL or your connection.")
        st.write(f"Error: {e}")

    # Dropdown for program selection when location is "Bali"
    program = st.selectbox("Choose a Program:", ["200HR", "300HR"], key="program_bali")

    if bali_option == "Overview":
        if program == "200HR":
            # Filter data for 200HR category
            data_200hr_bali = bali_sales_data[bali_sales_data['Category'] == '200HR']
            st.write("Ini adalah Overview untuk program 200HR")
            # Tambahkan analisis atau tampilan data untuk program 200HR di sini

        elif program == "300HR":
            st.write("Ini adalah Overview untuk program 300HR")
            # Tambahkan analisis atau tampilan data untuk program 300HR di sini

elif location == "India":
    # Dropdown for program selection when location is "India"
    program = st.selectbox("Choose a Program:", ["200HR", "300HR"], key="program_india")
