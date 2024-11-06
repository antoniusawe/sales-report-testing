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

    # Dropdown for program selection when location is "Bali"
    program = st.selectbox("Choose a Program:", ["200HR", "300HR"], key="program_bali")

    if bali_option == "Overview":
        # Get unique years from the 'Year' column in bali_sales_data and add "All" option
        if 'Year' in bali_sales_data.columns:
            unique_years = bali_sales_data['Year'].dropna().unique()
            unique_years = sorted(unique_years)  # Sorting years for a better user experience
            unique_years = ["All"] + list(unique_years)  # Adding "All" option
            
            # Radio button for year selection
            selected_year = st.radio("Select a Year:", unique_years, key="year_selection")
        else:
            st.warning("Year data not found in the dataset.")
            selected_year = "All"

        # Only show month selection if a specific year is chosen
        if selected_year != "All":
            # Filter data for the selected year
            year_data = bali_sales_data[bali_sales_data['Year'] == selected_year]
            
            # Get unique months from the 'Batch start date' or another date column
            unique_months = year_data['Batch start date'].dt.month.dropna().unique()
            unique_months = sorted(unique_months)  # Sorting months for better user experience
            month_names = ["All"] + [datetime(2000, month, 1).strftime('%B') for month in unique_months]  # Add "All" and month names
            
            # Dropdown for month selection
            selected_month = st.selectbox("Select a Month:", month_names, key="month_selection")
        else:
            selected_month = "All"

        # Filter data based on the program, year, and month
        if program == "200HR":
            # Base filter for 200HR and selected year
            data_200hr_bali = bali_sales_data[(bali_sales_data['Category'] == '200HR')]
            
            if selected_year != "All":
                data_200hr_bali = data_200hr_bali[data_200hr_bali['Year'] == selected_year]
                
            if selected_month != "All":
                month_num = datetime.strptime(selected_month, '%B').month
                data_200hr_bali = data_200hr_bali[data_200hr_bali['Batch start date'].dt.month == month_num]
            
            st.write("Ini adalah Overview untuk program 200HR")
            st.write(data_200hr_bali)  # Display the filtered data (or add further analysis)

        elif program == "300HR":
            # Base filter for 300HR and selected year
            data_300hr_bali = bali_sales_data[(bali_sales_data['Category'] == '300HR')]
            
            if selected_year != "All":
                data_300hr_bali = data_300hr_bali[data_300hr_bali['Year'] == selected_year]
                
            if selected_month != "All":
                month_num = datetime.strptime(selected_month, '%B').month
                data_300hr_bali = data_300hr_bali[data_300hr_bali['Batch start date'].dt.month == month_num]
            
            st.write("Ini adalah Overview untuk program 300HR")
            st.write(data_300hr_bali)  # Display the filtered data (or add further analysis)

elif location == "India":
    # Dropdown for program selection when location is "India"
    program = st.selectbox("Choose a Program:", ["200HR", "300HR"], key="program_india")
