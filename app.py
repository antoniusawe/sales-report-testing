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
        st.write("Location details for Bali")

        # Pilihan program (200HR atau 300HR) akan menentukan data mana yang digunakan
        if program == "200HR":
            # Filter data untuk kategori 200HR
            data_200hr_batches = bali_sales_data[bali_sales_data['Category'] == '200HR']
            st.write("Batch Data for 200HR Program")

            # Radio button untuk memilih tahun (Year)
            unique_years = data_200hr_batches['Year'].dropna().unique()
            unique_years = sorted(unique_years)
            unique_years = ["All"] + list(unique_years)
            selected_year = st.radio("Select a Year:", unique_years, key="year_selection_200hr")

            if selected_year != "All":
                # Filter data untuk tahun yang dipilih
                year_data = data_200hr_batches[data_200hr_batches['Year'] == selected_year]
                unique_months = year_data['Batch start date'].dt.month.dropna().unique()
                unique_months = sorted(unique_months)
                month_names = ["All"] + [datetime(2000, month, 1).strftime('%B') for month in unique_months]
                selected_month = st.selectbox("Select a Month:", month_names, key="month_selection_200hr")
            else:
                selected_month = "All"
                year_data = data_200hr_batches

            # Filter data lebih lanjut untuk bulan jika bulan bukan "All"
            if selected_month != "All":
                month_num = datetime.strptime(selected_month, '%B').month
                filtered_data = year_data[year_data['Batch start date'].dt.month == month_num]
            else:
                filtered_data = year_data

            # Menghitung metrik
            newest_batch_date = filtered_data['Batch start date'].max()
            cut_off_date = newest_batch_date.strftime('%d %b %Y') if pd.notnull(newest_batch_date) else "No date available"
            
            # Total booking (count) untuk siswa dengan BALANCE = 0
            total_booking_ctr = filtered_data[filtered_data["BALANCE"] == 0]["NAME"].count()

            # Total amount yang sudah dibayar (PAID) dengan BALANCE = 0
            total_paid_amount = filtered_data[filtered_data["BALANCE"] == 0]["PAID"].sum()

            # Rata-rata occupancy untuk data yang difilter berdasarkan Occupancy di occupancy data
            if selected_year != "All" or selected_month != "All":
                occupancy_data_filtered = bali_occupancy_data[bali_occupancy_data['Year'] == selected_year] if selected_year != "All" else bali_occupancy_data
                if selected_month != "All":
                    occupancy_data_filtered = occupancy_data_filtered[occupancy_data_filtered['Batch start date'].dt.month == month_num]
                average_occupancy = occupancy_data_filtered['Occupancy'].mean()
            else:
                average_occupancy = bali_occupancy_data['Occupancy'].mean()

            # Display Cut-off date and Total Booking in a centered format
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

            # Tambahkan grafik untuk data terpilih
            # Mengelompokkan data Site, Room, dan Month berdasarkan pilihan pengguna
            site_fill_data = bali_occupancy_data.groupby('Site')['Fill'].sum().reset_index().sort_values(by='Fill', ascending=False)
            room_fill_data = bali_occupancy_data.groupby('Room')['Fill'].sum().reset_index().sort_values(by='Fill', ascending=False)
            balance_zero_data = filtered_data[filtered_data['BALANCE'] == 0]
            month_counts = balance_zero_data.groupby('Month')['NAME'].count().reset_index()
            month_counts = month_counts.sort_values(by='NAME', ascending=False)

            # Mengidentifikasi nilai tertinggi untuk tiap grafik
            highest_fill_value_site = site_fill_data['Fill'].max()
            highest_fill_value_room = room_fill_data['Fill'].max()
            highest_value_month = month_counts['NAME'].max()

            # Konfigurasi grafik (Site, Room, dan Month) dengan tooltip dan label
            site_bar_chart_data = {
                "title": {"text": "Top Frequent Sites", "left": "center"},
                "tooltip": {"trigger": "item", "formatter": "{b}: {c}"},
                "xAxis": {"type": "category", "data": site_fill_data['Site'].tolist()},
                "yAxis": {"type": "value"},
                "series": [{
                    "data": [
                        {"value": fill, "itemStyle": {"color": "#FF5733" if fill == highest_fill_value_site else "#5470C6"}}
                        for fill in site_fill_data['Fill']
                    ],
                    "type": "bar",
                    "label": {"show": True, "position": "top", "formatter": "{c}", "fontSize": 9, "color": "#333333"}
                }]
            }

            room_bar_chart_data = {
                "title": {"text": "Top Frequent Rooms", "left": "center"},
                "tooltip": {"trigger": "item", "formatter": "{b}: {c}"},
                "xAxis": {"type": "category", "data": room_fill_data['Room'].tolist()},
                "yAxis": {"type": "value"},
                "series": [{
                    "data": [
                        {"value": fill, "itemStyle": {"color": "#FF5733" if fill == highest_fill_value_room else "#5470C6"}}
                        for fill in room_fill_data['Fill']
                    ],
                    "type": "bar",
                    "label": {"show": True, "position": "top", "formatter": "{c}", "fontSize": 9, "color": "#333333"}
                }]
            }

            month_bar_chart_data = {
                "title": {"text": "Top Months", "left": "center"},
                "tooltip": {"trigger": "item", "formatter": "{b}: {c}"},
                "xAxis": {"type": "category", "data": month_counts['Month'].tolist()},
                "yAxis": {"type": "value"},
                "series": [{
                    "data": [
                        {"value": count, "itemStyle": {"color": "#FF5733" if count == highest_value_month else "#5470C6"}}
                        for count in month_counts['NAME']
                    ],
                    "type": "bar",
                    "label": {"show": True, "position": "top", "formatter": "{c}", "fontSize": 9, "color": "#333333"}
                }]
            }

            # Menampilkan grafik berdampingan
            col1, col2, col3 = st.columns(3)
            with col1:
                st_echarts(options=site_bar_chart_data, height="300px")
            with col2:
                st_echarts(options=room_bar_chart_data, height="300px")
            with col3:
                st_echarts(options=month_bar_chart_data, height="300px")

        elif program == "300HR":
            # Filter data untuk kategori 300HR
            data_300hr_batches = bali_sales_data[bali_sales_data['Category'] == '300HR']
            st.write("Batch Data for 300HR Program")

            # Radio button untuk memilih tahun (Year) pada program 300HR
            unique_years = data_300hr_batches['Year'].dropna().unique()
            unique_years = sorted(unique_years)
            unique_years = ["All"] + list(unique_years)
            selected_year = st.radio("Select a Year:", unique_years, key="year_selection_300hr")

            if selected_year != "All":
                # Filter data untuk tahun yang dipilih
                year_data = data_300hr_batches[data_300hr_batches['Year'] == selected_year]
                unique_months = year_data['Batch start date'].dt.month.dropna().unique()
                unique_months = sorted(unique_months)
                month_names = ["All"] + [datetime(2000, month, 1).strftime('%B') for month in unique_months]
                selected_month = st.selectbox("Select a Month:", month_names, key="month_selection_300hr")
            else:
                selected_month = "All"

            # Menampilkan data yang difilter berdasarkan Year dan Month pada 300HR
            if selected_year != "All" and selected_month != "All":
                month_num = datetime.strptime(selected_month, '%B').month
                filtered_data = year_data[year_data['Batch start date'].dt.month == month_num]
            elif selected_year != "All":
                filtered_data = year_data
            else:
                filtered_data = data_300hr_batches

            st.write("Filtered data for 300HR:")
            st.dataframe(filtered_data)



    elif bali_option == "Location":
        st.write("Location details for Bali")
        if program == "200HR":
            data_200hr_batches = bali_sales_data[bali_sales_data['Category'] == '200HR']
            st.write("Batch Data for 200HR Program")
        elif program == "300HR":
            data_300hr_batches = bali_sales_data[bali_sales_data['Category'] == '300HR']
            st.write("Batch Data for 300HR Program")
            st.write(data_300hr_batches)

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
    program = st.selectbox("Choose a Program:", ["200HR", "300HR"], key="program_india")
