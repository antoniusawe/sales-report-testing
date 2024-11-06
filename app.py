import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
from datetime import datetime

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

    # Dropdown for program selection when location is "Bali"
    program = st.selectbox("Choose a Program:", ["200HR", "300HR"], key="program_bali")

    if bali_option == "Overview":
        # Year selection
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

        # Filter data based on program, year, and month
        filtered_data = bali_sales_data[bali_sales_data['Category'] == program]
        if selected_year != "All":
            filtered_data = filtered_data[filtered_data['Year'] == selected_year]
        if selected_month != "All":
            month_num = datetime.strptime(selected_month, '%B').month
            filtered_data = filtered_data[filtered_data['Batch start date'].dt.month == month_num]

        # Calculate metrics
        newest_batch_date = filtered_data['Batch start date'].max()
        cut_off_date = newest_batch_date.strftime('%d %b %Y') if pd.notnull(newest_batch_date) else "No date available"
        total_booking_ctr = filtered_data[filtered_data["BALANCE"] == 0]["NAME"].count()
        total_paid_amount = filtered_data[filtered_data["BALANCE"] == 0]["PAID"].sum()
        average_occupancy = bali_occupancy_data['Occupancy'].mean()

        # Display metrics
        st.markdown(f"""
        <div style='text-align: left;'>
            <div style='font-size: 16px; color: #333333;'>Cut-off data: {cut_off_date}</div>
        </div>
        <div style='display: flex; justify-content: center; gap: 50px; padding: 20px;'>
            <div style='text-align: left;'>
                <div style='font-size: 16px; color: #333333;'>Total Booking</div>
                <div style='font-size: 48px;'>{total_booking_ctr}</div>
                <div style='color: #202fb2; font-size: 18px;'>Number of students</div>
            </div>
            <div style='text-align: left;'>
                <div style='font-size: 16px; color: #333333;'>Amount</div>
                <div style='font-size: 48px;'>{total_paid_amount:,.0f}</div>
                <div style='color: #202fb2; font-size: 18px;'>in USD or USD equiv</div>
            </div>
            <div style='text-align: left;'>
                <div style='font-size: 16px; color: #333333;'>Occupancy</div>
                <div style='font-size: 48px;'>{average_occupancy:.2f}%</div>
                <div style='color: #202fb2; font-size: 18px;'>Occupancy Rate</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Menggunakan st.button untuk fungsi interaktif
        if 'show_data' not in st.session_state:
            st.session_state['show_data'] = False

        # Display Generate Data and Clear buttons
        st.markdown(
            """
            <style>
            .button-container {
                display: flex;
                justify-content: center;
                gap: 20px;
                margin-top: 20px;
            }
            .button-style {
                padding: 10px 20px;
                font-size: 16px;
                border-radius: 8px;
                cursor: pointer;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("<div class='button-container'>", unsafe_allow_html=True)
        generate = st.button("Generate Data", key="generate_button")
        clear = st.button("Clear", key="clear_button")
        st.markdown("</div>", unsafe_allow_html=True)

        if generate:
            st.session_state['show_data'] = True
        if clear:
            st.session_state['show_data'] = False

        # Kondisi untuk menampilkan data jika Generate Data ditekan
        if st.session_state.get('show_data', False):
            st.markdown("<h2 style='text-align: left; font-size: 16px;'>Bali Occupancy Data</h2>", unsafe_allow_html=True)
            st.dataframe(bali_occupancy_data)

            # Format kolom 'Batch start date' untuk konsistensi
            filtered_data['Batch start date'] = filtered_data['Batch start date'].dt.strftime('%d %b %Y')
            st.markdown("<h2 style='text-align: left; font-size: 16px;'>Bali Sales Data</h2>", unsafe_allow_html=True)
            st.dataframe(filtered_data)

        # Bar chart data preparation
        site_fill_data = bali_occupancy_data.groupby('Site')['Fill'].sum().reset_index().sort_values(by='Fill', ascending=False)
        room_fill_data = bali_occupancy_data.groupby('Room')['Fill'].sum().reset_index().sort_values(by='Fill', ascending=False)
        month_counts = filtered_data[filtered_data['BALANCE'] == 0].groupby('Month')['NAME'].count().reset_index()

        # Bar chart configurations
        highest_fill_value_site = site_fill_data['Fill'].max()
        highest_fill_value_room = room_fill_data['Fill'].max()
        highest_value_month = month_counts['NAME'].max()

        # Configure and display bar charts
        col1, col2, col3 = st.columns(3)
        with col1:
            st_echarts(options={"title": {"text": "Top Frequent Sites"}, "series": [{"data": site_fill_data['Fill'].tolist(), "type": "bar"}]}, height="300px")
        with col2:
            st_echarts(options={"title": {"text": "Top Frequent Rooms"}, "series": [{"data": room_fill_data['Fill'].tolist(), "type": "bar"}]}, height="300px")
        with col3:
            st_echarts(options={"title": {"text": "Top Months"}, "series": [{"data": month_counts['NAME'].tolist(), "type": "bar"}]}, height="300px")

elif location == "India":
    program = st.selectbox("Choose a Program:", ["200HR", "300HR"], key="program_india")
