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

if location == "Bali":
    # Sub-dropdown for specific options under "Bali"
    bali_option = st.sidebar.selectbox("Choose a Section:", ["Overview", "Location", "Batch"])
    occupancy_url = "https://raw.githubusercontent.com/antoniusawe/sales-report/main/Bali%20data/bali_occupancy.xlsx"
    sales_url = "https://raw.githubusercontent.com/antoniusawe/sales-report/main/Bali%20data/bali_sales.xlsx"
    
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

    # Program dropdown for "Overview" and "Batch" sections
    if bali_option in ["Overview", "Batch"]:
        program = st.selectbox("Choose a Program:", ["200HR", "300HR"], key=f"program_{bali_option.lower()}")

    # Overview section
    if bali_option == "Overview":
        # Year selection for "Overview"
        if 'Year' in bali_sales_data.columns:
            unique_years = bali_sales_data['Year'].dropna().unique()
            unique_years = sorted(unique_years)
            unique_years = ["All"] + list(unique_years)
            
            selected_year = st.radio("Select a Year:", unique_years, key="year_selection")
        else:
            st.warning("Year data not found in the dataset.")
            selected_year = "All"

        # Month selection if a specific year is chosen
        if selected_year != "All":
            year_data = bali_sales_data[bali_sales_data['Year'] == selected_year]
            unique_months = year_data['Batch start date'].dt.month.dropna().unique()
            unique_months = sorted(unique_months)
            month_names = ["All"] + [datetime(2000, month, 1).strftime('%B') for month in unique_months]
            selected_month = st.selectbox("Select a Month:", month_names, key="month_selection")
        else:
            selected_month = "All"

        # Filter data based on program, year, and month for "Overview"
        if program == "200HR":
            data_200hr_bali = bali_sales_data[(bali_sales_data['Category'] == '200HR')]
            if selected_year != "All":
                data_200hr_bali = data_200hr_bali[data_200hr_bali['Year'] == selected_year]
            if selected_month != "All":
                month_num = datetime.strptime(selected_month, '%B').month
                data_200hr_bali = data_200hr_bali[data_200hr_bali['Batch start date'].dt.month == month_num]
            st.write("Overview for 200HR Program")
            st.write(data_200hr_bali)

        elif program == "300HR":
            data_300hr_bali = bali_sales_data[(bali_sales_data['Category'] == '300HR')]
            if selected_year != "All":
                data_300hr_bali = data_300hr_bali[data_300hr_bali['Year'] == selected_year]
            if selected_month != "All":
                month_num = datetime.strptime(selected_month, '%B').month
                data_300hr_bali = data_300hr_bali[data_300hr_bali['Batch start date'].dt.month == month_num]
            st.write("Overview for 300HR Program")
            st.write(data_300hr_bali)

    # Location section
    elif bali_option == "Location":
        st.write("Location details for Bali")
        # You can add specific location-based information or analysis here, like maps, venue details, etc.

    # Batch section
    elif bali_option == "Batch":
        # Batch details based on program selection
        st.write(f"Batch details for {program} program")
        if program == "200HR":
            data_200hr_batches = bali_sales_data[bali_sales_data['Category'] == '200HR']
            st.write("Batch Data for 200HR Program")
            st.write(data_200hr_batches)
        elif program == "300HR":
            data_300hr_batches = bali_sales_data[bali_sales_data['Category'] == '300HR']
            st.write("Batch Data for 300HR Program")
            st.write(data_300hr_batches)

elif location == "India":
    # Dropdown for program selection when location is "India"
    program = st.selectbox("Choose a Program:", ["200HR", "300HR"], key="program_india")
