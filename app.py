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
        # st.write("Location details for Bali")

        # Pilihan program (200HR atau 300HR) akan menentukan data mana yang digunakan
        if program == "200HR":
            # Filter data untuk kategori 200HR
            data_200hr_batches = bali_sales_data[bali_sales_data['Category'] == '200HR']
            
            # Radio button untuk memilih tahun (Year) pada program 200HR
            unique_years = data_200hr_batches['Year'].dropna().unique()
            unique_years = sorted(unique_years)
            unique_years = ["All"] + list(unique_years)
            selected_year = st.radio("Select a Year:", unique_years, key="year_selection_200hr")

            if selected_year != "All":
                # Filter data untuk tahun yang dipilih
                year_data = data_200hr_batches[data_200hr_batches['Year'] == selected_year]
                
                # Pastikan kolom 'Batch start date' dalam year_data berformat datetime
                if 'Batch start date' in year_data.columns:
                    year_data['Batch start date'] = pd.to_datetime(year_data['Batch start date'], errors='coerce')
                
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
                
                # Filter bali_occupancy_data juga berdasarkan bulan yang dipilih
                occupancy_data_filtered = bali_occupancy_data[bali_occupancy_data['Year'] == selected_year] if selected_year != "All" else bali_occupancy_data
                if 'Batch start date' in occupancy_data_filtered.columns:
                    occupancy_data_filtered['Batch start date'] = pd.to_datetime(occupancy_data_filtered['Batch start date'], errors='coerce')
                occupancy_data_filtered = occupancy_data_filtered[occupancy_data_filtered['Batch start date'].dt.month == month_num]
            else:
                filtered_data = year_data
                occupancy_data_filtered = bali_occupancy_data

            # Calculate metrics
            newest_batch_date = filtered_data['Batch start date'].max()
            cut_off_date = newest_batch_date.strftime('%d %b %Y') if pd.notnull(newest_batch_date) else "No date available"
            total_booking_ctr = filtered_data[filtered_data["BALANCE"] == 0]["NAME"].count()
            total_paid_amount = filtered_data[filtered_data["BALANCE"] == 0]["PAID"].sum()
            average_occupancy = occupancy_data_filtered['Occupancy'].mean()

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

            # Update Top Frequent Sites and Rooms based on filtered occupancy_data_filtered
            site_fill_data = occupancy_data_filtered.groupby('Site')['Fill'].sum().reset_index().sort_values(by='Fill', ascending=False)
            room_fill_data = occupancy_data_filtered.groupby('Room')['Fill'].sum().reset_index().sort_values(by='Fill', ascending=False)

            # Chart configurations for Top Frequent Sites
            highest_fill_value_site = site_fill_data['Fill'].max()
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

            # Chart configurations for Top Frequent Rooms
            highest_fill_value_room = room_fill_data['Fill'].max()
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

            # Create and display Month bar chart based on fully paid data
            balance_zero_data = filtered_data[filtered_data['BALANCE'] == 0]
            month_counts = balance_zero_data.groupby('Month')['NAME'].count().reset_index()
            month_counts = month_counts.sort_values(by='NAME', ascending=False)
            highest_value_month = month_counts['NAME'].max()

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

            # Display charts side by side
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
            
            # Radio button untuk memilih tahun (Year) pada program 300HR
            unique_years = data_300hr_batches['Year'].dropna().unique()
            unique_years = sorted(unique_years)
            unique_years = ["All"] + list(unique_years)
            selected_year = st.radio("Select a Year:", unique_years, key="year_selection_300hr")

            if selected_year != "All":
                # Filter data untuk tahun yang dipilih
                year_data = data_300hr_batches[data_300hr_batches['Year'] == selected_year]
                
                # Pastikan kolom 'Batch start date' dalam year_data berformat datetime
                if 'Batch start date' in year_data.columns:
                    year_data['Batch start date'] = pd.to_datetime(year_data['Batch start date'], errors='coerce')
                
                unique_months = year_data['Batch start date'].dt.month.dropna().unique()
                unique_months = sorted(unique_months)
                month_names = ["All"] + [datetime(2000, month, 1).strftime('%B') for month in unique_months]
                selected_month = st.selectbox("Select a Month:", month_names, key="month_selection_300hr")
            else:
                selected_month = "All"
                year_data = data_300hr_batches

            # Filter data lebih lanjut untuk bulan jika bulan bukan "All"
            if selected_month != "All":
                month_num = datetime.strptime(selected_month, '%B').month
                filtered_data = year_data[year_data['Batch start date'].dt.month == month_num]
                
                # Filter bali_occupancy_data juga berdasarkan bulan yang dipilih
                occupancy_data_filtered = bali_occupancy_data[bali_occupancy_data['Year'] == selected_year] if selected_year != "All" else bali_occupancy_data
                if 'Batch start date' in occupancy_data_filtered.columns:
                    occupancy_data_filtered['Batch start date'] = pd.to_datetime(occupancy_data_filtered['Batch start date'], errors='coerce')
                occupancy_data_filtered = occupancy_data_filtered[occupancy_data_filtered['Batch start date'].dt.month == month_num]
            else:
                filtered_data = year_data
                occupancy_data_filtered = bali_occupancy_data[bali_occupancy_data['Category'] == '300HR']  # Pastikan hanya data 300HR

            # Jika tidak ada data untuk 300HR, beri nilai 0 atau tampilkan pesan 'No Data'
            if filtered_data.empty:
                cut_off_date = "No date available"
                total_booking_ctr = 0
                total_paid_amount = 0
                average_occupancy = 0.0
                st.write("No data available for 300HR program")
            else:
                # Calculate metrics jika data tidak kosong
                newest_batch_date = filtered_data['Batch start date'].max()
                cut_off_date = newest_batch_date.strftime('%d %b %Y') if pd.notnull(newest_batch_date) else "No date available"
                total_booking_ctr = filtered_data[filtered_data["BALANCE"] == 0]["NAME"].count()
                total_paid_amount = filtered_data[filtered_data["BALANCE"] == 0]["PAID"].sum()
                average_occupancy = occupancy_data_filtered['Occupancy'].mean()

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

            # Update Top Frequent Sites and Rooms based on filtered occupancy_data_filtered
            if not occupancy_data_filtered.empty and not filtered_data.empty:
                site_fill_data = occupancy_data_filtered.groupby('Site')['Fill'].sum().reset_index().sort_values(by='Fill', ascending=False)
                room_fill_data = occupancy_data_filtered.groupby('Room')['Fill'].sum().reset_index().sort_values(by='Fill', ascending=False)

                # Chart configurations for Top Frequent Sites
                highest_fill_value_site = site_fill_data['Fill'].max()
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

                # Chart configurations for Top Frequent Rooms
                highest_fill_value_room = room_fill_data['Fill'].max()
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
            else:
                # Jika occupancy_data_filtered kosong, tampilkan chart kosong
                site_bar_chart_data = {"title": {"text": "No Data for Sites", "left": "center"}}
                room_bar_chart_data = {"title": {"text": "No Data for Rooms", "left": "center"}}

            # Create and display Month bar chart based on fully paid data
            balance_zero_data = filtered_data[filtered_data['BALANCE'] == 0]
            month_counts = balance_zero_data.groupby('Month')['NAME'].count().reset_index()
            month_counts = month_counts.sort_values(by='NAME', ascending=False)
            highest_value_month = month_counts['NAME'].max() if not month_counts.empty else 0

            if not month_counts.empty:
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
            else:
                month_bar_chart_data = {"title": {"text": "No Data for Months", "left": "center"}}

            # Display charts side by side
            col1, col2, col3 = st.columns(3)
            with col1:
                st_echarts(options=site_bar_chart_data, height="300px")
            with col2:
                st_echarts(options=room_bar_chart_data, height="300px")
            with col3:
                st_echarts(options=month_bar_chart_data, height="300px")



    elif bali_option == "Location":
        if program == "200HR":
            # Filter data untuk kategori 200HR dan konversi kolom 'Batch start date'
            data_200hr_batches = bali_occupancy_data[bali_occupancy_data['Category'] == '200HR']
            if 'Batch start date' in data_200hr_batches.columns:
                data_200hr_batches['Batch start date'] = pd.to_datetime(data_200hr_batches['Batch start date'], errors='coerce')

            # Radio button untuk memilih tahun (Year)
            unique_years = ["All"] + sorted(data_200hr_batches['Year'].dropna().unique())
            selected_year = st.radio("Select a Year:", unique_years, key="year_selection_location_200hr")

            # Filter data berdasarkan tahun yang dipilih
            year_data = data_200hr_batches if selected_year == "All" else data_200hr_batches[data_200hr_batches['Year'] == selected_year]

            # Menampilkan Selectbox untuk memilih bulan hanya jika tahun yang dipilih bukan "All"
            if selected_year != "All":
                unique_months = sorted(year_data['Batch start date'].dt.month.dropna().unique())
                month_names = ["All"] + [datetime(2000, month, 1).strftime('%B') for month in unique_months]
                selected_month = st.selectbox("Select a Month:", month_names, key="month_selection_location_200hr")
            else:
                selected_month = "All"  # Set selected month to "All" jika tahun "All" dipilih

            # Menentukan bulan saat ini atau bulan yang dipilih untuk ditampilkan
            if selected_year == "All" or selected_month == "All":
                # Get the current month if "All" is selected
                current_month = datetime.now().strftime('%B')
                filtered_data = bali_occupancy_data[bali_occupancy_data['Month'] == current_month]
            else:
                # Filter berdasarkan bulan yang dipilih
                month_num = datetime.strptime(selected_month, '%B').month
                filtered_data = year_data[year_data['Batch start date'].dt.month == month_num]
                current_month = selected_month

            # Menghitung ketersediaan per site dan per tanggal batch
            site_availability_summary = filtered_data.groupby(['Site', 'Batch start date'])['Available'].sum().reset_index()

            # Pastikan kolom 'Batch start date' sudah dalam format datetime
            if site_availability_summary['Batch start date'].dtype == 'O':  # 'O' stands for object type
                site_availability_summary['Batch start date'] = pd.to_datetime(site_availability_summary['Batch start date'], errors='coerce')

            # Agregasi data dengan memastikan format tanggal sesuai
            aggregated_data = site_availability_summary.groupby('Site').agg({
                'Available': 'sum',
                'Batch start date': lambda x: ', '.join([
                    f"{a.strftime('%d %b %Y')} ({b})" if pd.notnull(a) else "Unknown Date" 
                    for a, b in zip(x, site_availability_summary.loc[x.index, 'Available'])
                ])
            }).reset_index()

            # Rename columns for clarity
            aggregated_data.columns = ['Site', 'Total Available', 'Batch Details']

            st.markdown(f"""
                <h3 style='text-align: center;'>Availability for Sites in {current_month}</h3>
            """, unsafe_allow_html=True)

            # Define the number of columns per row to control the layout
            num_columns = 4
            rows = [st.columns(num_columns) for _ in range((len(aggregated_data) + num_columns - 1) // num_columns)]

            # Display data in a grid format
            for index, row in enumerate(aggregated_data.iterrows()):
                site_name = row[1]['Site']
                total_available = row[1]['Total Available']
                batch_details = row[1]['Batch Details']
                
                row_index = index // num_columns
                col_index = index % num_columns

                with rows[row_index][col_index]:
                    st.markdown(f"""
                        <div style='text-align: center; width: 200px; padding: 20px; margin: 10px;'>
                            <div style='font-size: 16px; color: #333333;'>{site_name}</div>
                            <br>
                            <div style='font-size: 48px; color: #202fb2;'>{total_available}</div>
                            <div style='color: #202fb2; font-size: 18px;'>Total Available Rooms</div>
                            <br>
                            <div style='font-size: 16px; color: #333333;'>Batch:</div>
                            <div style='font-size: 14px; color: #666666;'>{batch_details}</div>
                        </div>
                    """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

        elif program == "300HR":
            # Filter data untuk kategori 300HR dan konversi kolom 'Batch start date'
            data_300hr_batches = bali_occupancy_data[bali_occupancy_data['Category'] == '300HR']
            if 'Batch start date' in data_300hr_batches.columns:
                data_300hr_batches['Batch start date'] = pd.to_datetime(data_300hr_batches['Batch start date'], errors='coerce')

            # Radio button untuk memilih tahun (Year)
            unique_years = ["All"] + sorted(data_300hr_batches['Year'].dropna().unique())
            selected_year = st.radio("Select a Year:", unique_years, key="year_selection_location_300hr")

            # Filter data berdasarkan tahun yang dipilih
            year_data = data_300hr_batches if selected_year == "All" else data_300hr_batches[data_300hr_batches['Year'] == selected_year]

            # Menampilkan Selectbox untuk memilih bulan hanya jika tahun yang dipilih bukan "All"
            if selected_year != "All":
                unique_months = sorted(year_data['Batch start date'].dt.month.dropna().unique())
                month_names = ["All"] + [datetime(2000, month, 1).strftime('%B') for month in unique_months]
                selected_month = st.selectbox("Select a Month:", month_names, key="month_selection_location_300hr")
            else:
                selected_month = "All"  # Set selected month to "All" jika tahun "All" dipilih

            # Menentukan bulan saat ini atau bulan yang dipilih untuk ditampilkan
            if selected_year == "All" or selected_month == "All":
                # Get the current month if "All" is selected, filtered only for 300HR data
                current_month = datetime.now().strftime('%B')
                filtered_data = data_300hr_batches[data_300hr_batches['Month'] == current_month]
            else:
                # Filter berdasarkan bulan yang dipilih untuk 300HR
                month_num = datetime.strptime(selected_month, '%B').month
                filtered_data = year_data[year_data['Batch start date'].dt.month == month_num]
                current_month = selected_month

            # Cek apakah filtered_data kosong
            if filtered_data.empty:
                st.write("No data available for the selected filters.")
            else:
                # Menghitung ketersediaan per site dan per tanggal batch
                site_availability_summary = filtered_data.groupby(['Site', 'Batch start date'])['Available'].sum().reset_index()
                
                # Pastikan kolom 'Batch start date' dalam format datetime
                if site_availability_summary['Batch start date'].dtype == 'O':  # 'O' stands for object type
                    site_availability_summary['Batch start date'] = pd.to_datetime(site_availability_summary['Batch start date'], errors='coerce')

                # Agregasi data dengan memastikan format tanggal sesuai
                aggregated_data = site_availability_summary.groupby('Site').agg({
                    'Available': 'sum',
                    'Batch start date': lambda x: ', '.join([
                        f"{a.strftime('%d %b %Y')} ({b})" if pd.notnull(a) else "Unknown Date"
                        for a, b in zip(x, site_availability_summary.loc[x.index, 'Available'])
                    ])
                }).reset_index()

                # Rename columns for clarity
                aggregated_data.columns = ['Site', 'Total Available', 'Batch Details']

                st.markdown(f"""
                    <h3 style='text-align: center;'>Availability for Sites in {current_month}</h3>
                """, unsafe_allow_html=True)

                # Define the number of columns per row to control the layout
                num_columns = 4
                rows = [st.columns(num_columns) for _ in range((len(aggregated_data) + num_columns - 1) // num_columns)]

                # Display data in a grid format
                for index, row in enumerate(aggregated_data.iterrows()):
                    site_name = row[1]['Site']
                    total_available = row[1]['Total Available']
                    batch_details = row[1]['Batch Details']
                    
                    row_index = index // num_columns
                    col_index = index % num_columns

                    with rows[row_index][col_index]:
                        st.markdown(f"""
                            <div style='text-align: center; width: 200px; padding: 20px; margin: 10px;'>
                                <div style='font-size: 16px; color: #333333;'>{site_name}</div>
                                <br>
                                <div style='font-size: 48px; color: #202fb2;'>{total_available}</div>
                                <div style='color: #202fb2; font-size: 18px;'>Total Available Rooms</div>
                                <br>
                                <div style='font-size: 16px; color: #333333;'>Batch:</div>
                                <div style='font-size: 14px; color: #666666;'>{batch_details}</div>
                            </div>
                        """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

        # Menambahkan pilihan untuk analisis
        location_analysis_option = st.radio(
            "Select Analysis Type:",
            ["Occupancy Rate", "Location Performance"]
        )

        if location_analysis_option == "Occupancy Rate":
            # Tentukan program yang dipilih, baik "200HR" atau "300HR"
            selected_program = "200HR" if program == "200HR" else "300HR"
            
            # Filter data untuk kategori yang sesuai (200HR atau 300HR)
            occupancy_data = bali_occupancy_data[bali_occupancy_data['Category'] == selected_program]

            # Filter occupancy data untuk bulan saat ini dan dua bulan sebelumnya
            current_month = datetime.now().strftime('%B')
            previous_month_1 = (datetime.now().replace(day=1) - pd.DateOffset(months=1)).strftime('%B')
            previous_month_2 = (datetime.now().replace(day=1) - pd.DateOffset(months=2)).strftime('%B')
            base_month = (datetime.now().replace(day=1) - pd.DateOffset(months=3)).strftime('%B')  # Bulan sebagai baseline

            # Pastikan kolom 'Occupancy' dalam bentuk numerik setelah menghapus '%'
            occupancy_data['Occupancy'] = occupancy_data['Occupancy'].astype(str).str.replace('%', '', regex=True).astype(float)

            # Membuat tabel ringkasan occupancy untuk baseline dan tiga bulan terakhir
            occupancy_summary = occupancy_data.pivot_table(
                index='Site',
                columns='Month',
                values='Occupancy',
                aggfunc='mean'
            ).fillna(0)

            # Pastikan bahwa kolom yang diperlukan ada di `occupancy_summary`
            required_months = [base_month, previous_month_2, previous_month_1, current_month]
            available_months = [month for month in required_months if month in occupancy_summary.columns]

            if len(available_months) < 3:
                st.write("No sufficient data available for the selected filters.")
            else:
                # Filter hanya untuk bulan-bulan yang tersedia
                occupancy_summary = occupancy_summary[available_months]

                # Hitung Growth untuk setiap bulan dibandingkan dengan bulan sebelumnya
                growth_summary = occupancy_summary.pct_change(axis=1) * 100  # Hitung sebagai persentase
                growth_summary = growth_summary[available_months[1:]].copy()

                # Styling pertumbuhan untuk tampilan
                def style_growth(value):
                    if value > 0:
                        color = "green"
                    elif value < 0:
                        color = "red"
                    else:
                        color = "black"
                    return f"<span style='color: {color};'>{value:.2f}%</span>"

                # Terapkan styling untuk setiap sel dalam DataFrame untuk growth_display
                growth_display = growth_summary.applymap(style_growth)

                st.markdown(
                    f"<div style='display: flex; justify-content: center; margin-top: 20px;'>"
                    f"<div style='text-align: center;'>"
                    f"<p style='font-size: 14px; font-weight: bold; color: #333;'>"
                    f"Avg Occupancy for {', '.join(available_months[1:])} ({selected_program})</p>"
                    f"</div></div>",
                    unsafe_allow_html=True
                )

                # Tampilkan occupancy_summary dalam format tabel
                st.markdown(
                    f"<div style='display: flex; justify-content: center;'>"
                    f"{occupancy_summary[available_months[1:]].applymap(lambda x: f'{x:.2f}%').to_html(index=True, classes='dataframe', border=0)}"
                    f"</div>",
                    unsafe_allow_html=True
                )

                # Siapkan data untuk bar chart
                sites = occupancy_summary.index.tolist()  # Daftar site
                months = available_months[1:]  # Daftar bulan yang tersedia

                # Inisialisasi data seri untuk setiap bulan
                series_data = []
                for month in months:
                    # Ambil nilai rata-rata occupancy untuk setiap site
                    avg_values = occupancy_summary[month].values.tolist()

                    # Buat entri seri untuk chart dengan tooltip
                    series_data.append({
                        "name": month,
                        "type": "bar",
                        "data": avg_values,
                    })

                # Definisikan opsi chart dengan tooltip
                chart_options = {
                    "title": {
                        "text": f"Occupancy Rate ({selected_program})",
                        "left": "center",
                        "top": "top",
                        "textStyle": {"fontSize": 16, "fontWeight": "bold"}
                    },
                    "tooltip": {
                        "trigger": "item",
                        "formatter": "{a} <br/>{b}: {c}%",  # Menampilkan nama bulan, site, dan nilai
                        "axisPointer": {
                            "type": "shadow"
                        },
                    },
                    "legend": {
                        "data": months,
                        "orient": "horizontal",
                        "bottom": "0",
                        "left": "center"
                    },
                    "xAxis": {
                        "type": "category",
                        "data": sites,
                        "axisLabel": {
                            "interval": 0,
                            "fontSize": 12,
                            "rotate": 0,
                            "fontWeight": "bold"
                        }
                    },
                    "yAxis": {
                        "type": "value",
                        "axisLabel": {
                            "formatter": "{value}%",  # Menampilkan persentase
                            "fontSize": 12
                        }
                    },
                    "series": series_data
                }

                # Render bar chart
                st.markdown("<div style='display: flex; justify-content: center; margin-top: 10px;'>", unsafe_allow_html=True)
                st_echarts(options=chart_options, height="400px")
                st.markdown("</div>", unsafe_allow_html=True)

                # Tampilkan tabel pertumbuhan dengan styling
                st.markdown(
                    f"<div style='text-align: center; font-size: 14px; font-weight: bold; color: #333; margin-top: 20px;'>"
                    f"Growth Occupancy Rate from Previous Months</div>",
                    unsafe_allow_html=True
                )

                # Pusatkan tampilan growth table dengan div wrapper
                st.markdown(
                    f"<div style='display: flex; justify-content: center; margin-top: 10px;'>"
                    f"{growth_display.to_html(escape=False, index=True)}"
                    f"</div>",
                    unsafe_allow_html=True
                )

        elif location_analysis_option == "Location Performance":
            # Tentukan program yang dipilih, baik "200HR" atau "300HR"
            selected_program = "200HR" if program == "200HR" else "300HR"

            # Filter data untuk kategori yang sesuai (200HR atau 300HR)
            performance_data = bali_occupancy_data[bali_occupancy_data['Category'] == selected_program]

            # Tentukan bulan untuk analisis
            current_month = datetime.now().strftime('%B')
            previous_month_1 = (datetime.now().replace(day=1) - pd.DateOffset(months=1)).strftime('%B')
            previous_month_2 = (datetime.now().replace(day=1) - pd.DateOffset(months=2)).strftime('%B')
            base_month = (datetime.now().replace(day=1) - pd.DateOffset(months=3)).strftime('%B')  # Bulan baseline

            # Membuat tabel "Site Filled" berdasarkan nilai "Fill", termasuk base_month untuk perhitungan
            fill_summary = performance_data.pivot_table(
                index='Site',
                columns='Month',
                values='Fill',
                aggfunc='sum'
            ).fillna(0)
            
            # Pastikan kolom yang diperlukan ada di `fill_summary`
            required_months = [base_month, previous_month_2, previous_month_1, current_month]
            available_months = [month for month in required_months if month in fill_summary.columns]

            if len(available_months) < 3:
                st.write("No sufficient data available for the selected filters.")
            else:
                # Filter hanya untuk bulan-bulan yang tersedia
                fill_summary = fill_summary[available_months].astype(int)

                # Tampilkan tabel "Site Filled" hanya untuk tiga bulan terakhir (tanpa base_month)
                st.markdown(
                    f"<div style='text-align: center; font-size: 14px; font-weight: bold; color: #333;'>"
                    f"Students for {', '.join(available_months[1:])} ({selected_program})</div><br>",
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"<div style='display: flex; justify-content: center;'>"
                    f"{fill_summary[available_months[1:]].to_html(index=True, classes='dataframe', border=0)}"
                    f"</div>",
                    unsafe_allow_html=True
                )

                # Siapkan data untuk grafik batang (menggunakan bulan yang ditampilkan saja)
                sites = fill_summary.index.tolist()  # Daftar situs (baris)
                months = available_months[1:]  # Daftar bulan untuk tampilan

                # Inisialisasi data seri untuk setiap bulan
                series_data = []
                for month in months:
                    # Ambil nilai Fill untuk setiap site
                    fill_values = fill_summary[month].values.tolist()
                    
                    # Buat entri seri untuk chart dengan tooltip
                    series_data.append({
                        "name": month,
                        "type": "bar",
                        "data": fill_values,
                    })

                # Definisikan opsi chart dengan tooltip
                chart_options = {
                    "title": {
                        "text": f"Number of Students by Month ({selected_program})",
                        "left": "center",
                        "top": "top",
                        "textStyle": {"fontSize": 16, "fontWeight": "bold"}
                    },
                    "tooltip": {
                        "trigger": "item",
                        "formatter": "{a} <br/>{b}: {c}",  # Menampilkan nama bulan, site, dan nilai
                        "axisPointer": {
                            "type": "shadow"
                        },
                    },
                    "legend": {
                        "data": months,
                        "orient": "horizontal",
                        "bottom": "0",
                        "left": "center"
                    },
                    "xAxis": {
                        "type": "category",
                        "data": sites,
                        "axisLabel": {
                            "interval": 0,
                            "fontSize": 12,
                            "rotate": 0,
                            "fontWeight": "bold"
                        }
                    },
                    "yAxis": {
                        "type": "value",
                        "axisLabel": {
                            "formatter": "{value}",  # Menampilkan nilai sebagai bilangan bulat
                            "fontSize": 12
                        }
                    },
                    "series": series_data
                }

                # Render bar chart
                st.markdown("<div style='display: flex; justify-content: center; margin-top: 10px;'>", unsafe_allow_html=True)
                st_echarts(options=chart_options, height="400px")
                st.markdown("</div>", unsafe_allow_html=True)

                # Hitung Growth Summary sebagai perbedaan jumlah siswa untuk tiga bulan terakhir saja
                growth_summary = fill_summary.diff(axis=1)  # Hitung perbedaan antara bulan-bulan berurutan
                growth_summary = growth_summary[available_months[1:]].copy()  # Tampilkan hanya tiga bulan terakhir
                
                # Styling pertumbuhan untuk tampilan
                def style_growth(value):
                    if value > 0:
                        color = "green"
                    elif value < 0:
                        color = "red"
                    else:
                        color = "black"
                    return f"<span style='color: {color};'>{value}</span>"

                # Terapkan styling ke growth summary
                growth_display = growth_summary.applymap(style_growth)

                # Tampilkan Growth Summary table di bagian bawah
                st.markdown(
                    f"<div style='text-align: center; font-size: 14px; font-weight: bold; color: #333; margin-top: 20px;'>"
                    f"Growth in Number of Students from Previous Months</div>",
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"<div style='display: flex; justify-content: center; margin-top: 10px;'>"
                    f"{growth_display.to_html(escape=False, index=True)}"
                    f"</div>",
                    unsafe_allow_html=True
                )


    elif bali_option == "Batch":
        # Pilihan Site
        site_option = st.radio("Select Site", bali_sales_data['Site'].unique())

        # Filter data hanya untuk site yang dipilih
        selected_site_data = bali_sales_data[bali_sales_data['Site'] == site_option]

        # Pastikan semua entri di kolom 'PAID STATUS' menggunakan huruf kapital
        selected_site_data['PAID STATUS'] = selected_site_data['PAID STATUS'].str.upper()

        # Convert 'Year' ke tipe integer untuk pemrosesan, lalu kembali ke string untuk tampilan
        selected_site_data['Year'] = selected_site_data['Year'].astype(int).astype(str)

        # Convert 'Month' ke datetime, urutkan, lalu ubah kembali ke nama bulan
        selected_site_data['Month'] = pd.to_datetime(selected_site_data['Month'], format='%B')
        selected_site_data = selected_site_data.sort_values(by='Month')
        selected_site_data['Month'] = selected_site_data['Month'].dt.strftime('%B')

        # Format 'Batch start date' dan 'Batch end date' untuk tampilan konsisten
        selected_site_data['Batch start date'] = pd.to_datetime(selected_site_data['Batch start date']).dt.strftime('%d %b %Y')
        selected_site_data['Batch end date'] = pd.to_datetime(selected_site_data['Batch end date']).dt.strftime('%d %b %Y')

        # Mengisi nilai kosong di kolom 'Group' dengan label 'No Group'
        selected_site_data['Group'] = selected_site_data['Group'].fillna('No Group')

        # Menggunakan pilihan program dari dropdown yang ada di atas (misalnya, `program` variabel yang sudah dipilih pengguna)
        # Filter data berdasarkan program yang sudah dipilih (200HR atau 300HR)
        program_data = selected_site_data[selected_site_data['Category'] == program]

        if program_data.empty:
            st.write("No data available for the selected site and program.")
        else:
            # Group data berdasarkan Year, Month, Batch start date, Batch end date, dan Group
            grouped_data = program_data.groupby(
                ['Year', 'Month', 'Batch start date', 'Batch end date', 'Group']
            ).agg(
                FULLY_PAID=('PAID STATUS', lambda x: (x == 'FULLY PAID').sum()),
                DEPOSIT=('PAID STATUS', lambda x: (x == 'DEPOSIT').sum()),
                NOT_PAID=('PAID STATUS', lambda x: x.isna().sum())
            ).reset_index()

            # Menambahkan kolom 'Total' sebagai jumlah dari fully_paid, deposit, dan not_paid
            grouped_data['Total'] = grouped_data['FULLY_PAID'] + grouped_data['DEPOSIT'] + grouped_data['NOT_PAID']

            grouped_data['Month'] = pd.to_datetime(grouped_data['Month'], format='%B')
            grouped_data['Year'] = grouped_data['Year'].astype(int)  # Pastikan 'Year' adalah integer untuk pengurutan

            # Mengurutkan grouped_data berdasarkan 'Year' dan 'Month'
            grouped_data = grouped_data.sort_values(by=['Year', 'Month'])

            # Kembalikan 'Month' ke format nama bulan setelah pengurutan
            grouped_data['Month'] = grouped_data['Month'].dt.strftime('%B')

            # Pastikan kolom `Year` tetap dalam tipe string agar tidak menampilkan koma
            grouped_data['Year'] = grouped_data['Year'].astype(str)

            # Tampilkan hasil dalam bentuk tabel di Streamlit
            st.markdown(f"### {site_option} ({program} Program)")
            st.dataframe(grouped_data)

# Conditional logic based on location selection
elif location == "India":
    # Dropdown for program selection when location is "India"
    program = st.selectbox("Choose a Program:", ["200HR", "300HR"])

    # Load and process data if "200HR" is selected
    if program == "200HR":
        # Load the Excel file from the URL
        url = "https://raw.githubusercontent.com/antoniusawe/sales-report/main/RYP%20data/ryp_student_database_200hr.xlsx"
        
        try:
            data_200hr = pd.read_excel(url)
            # Calculate Total Booking, Total Payable, and Outstanding
            total_booking_ctr = data_200hr["Name of student"].count()
            total_payable_sum = data_200hr["Total Payable (in USD or USD equiv)"].sum()
            outstanding_sum = data_200hr["Student still to pay"].sum()
            
            # Calculate the percentage of Outstanding from Total Payable
            outstanding_percentage = (outstanding_sum / total_payable_sum * 100) if total_payable_sum else 0

            # Display Total Booking, Total Payable, and Outstanding in a centered format
            st.markdown(f"""
            <div style='display: flex; justify-content: center; gap: 50px; padding: 20px;'>
                <div style='text-align: left;'>
                    <div style='font-size: 16px; color: #333333;'>Total Booking</div>
                    <div style='font-size: 48px;'>{total_booking_ctr}</div>
                    <div style='color: #202fb2; font-size: 18px;'>Number of Students</div>
                </div>
                <div style='text-align: left;'>
                    <div style='font-size: 16px; color: #333333;'>Total Payable</div>
                    <div style='font-size: 48px;'>{total_payable_sum:,.0f}</div>
                    <div style='color: #202fb2; font-size: 18px;'>in USD or USD equiv</div>
                </div>
                <div style='text-align: left;'>
                    <div style='font-size: 16px; color: #333333;'>Outstanding</div>
                    <div style='font-size: 48px;'>{outstanding_sum:,.0f}</div>
                    <div style='color: #202fb2; font-size: 18px;'>{outstanding_percentage:.2f}% of Total Payable</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Dropdown for chart data selection
            chart_option = st.selectbox("Choose Data to Display:", ["Total Booking", "Total Payable", "Data"])

            if chart_option == "Total Booking":
                # Process data for Number of Students chart
                batch_counts = data_200hr.groupby(['Batch start date', 'Batch end date'])['Name of student'].count().reset_index()
                
                batch_counts['Batch start date'] = pd.to_datetime(batch_counts['Batch start date'])
                batch_counts['Batch end date'] = pd.to_datetime(batch_counts['Batch end date'])
                batch_counts['Days in Batch'] = (batch_counts['Batch end date'] - batch_counts['Batch start date']).dt.days + 1
                
                batch_counts['Average Bookings per Day'] = batch_counts['Name of student'] / batch_counts['Days in Batch']
                batch_counts = batch_counts.sort_values(by='Batch start date')
                
                batch_counts['Batch'] = batch_counts['Batch start date'].dt.strftime('%B %d, %Y') + " to " + batch_counts['Batch end date'].dt.strftime('%B %d, %Y')
                
                wrapped_labels = [label.replace(" to ", "\nto\n") for label in batch_counts['Batch']]
                student_counts = batch_counts['Name of student'].tolist()
                average_bookings_per_day = batch_counts['Average Bookings per Day'].tolist()

                # Bar chart for Number of Students
                bar_options = {
                "title": {
                    "text": "Total Booking",  # Adding the title for the bar chart
                    "left": "center",          # Center the title
                    "top": "top",              # Position it at the top of the chart
                    "textStyle": {"fontSize": 18, "fontWeight": "bold"}
                },
                "tooltip": {"trigger": "axis"},
                "xAxis": {
                    "type": "category",
                    "data": wrapped_labels,
                    "axisLabel": {
                        "interval": 0,
                        "fontSize": 7,
                        "rotate": 0,
                        "lineHeight": 12,
                        "fontWeight": "bold"
                    }
                },
                "yAxis": {"type": "value"},
                "series": [
                    {
                        "data": student_counts,
                        "type": "bar",
                        "name": "Student Count",
                        "itemStyle": {"color": "#5470C6"}
                    }
                ]
            }

                # Render the bar chart
                st_echarts(bar_options)

                # Line chart for Average Bookings per Day
                line_options = {
                "title": {
                    "text": "Average Booking per Day",  # Adding the title for the line chart
                    "left": "center",           # Center the title
                    "top": "top",               # Position it at the top of the chart
                    "textStyle": {"fontSize": 18, "fontWeight": "bold"}
                },
                "tooltip": {"trigger": "axis"},
                "xAxis": {
                    "type": "category",
                    "data": wrapped_labels,
                    "axisLabel": {
                        "interval": 0,
                        "fontSize": 7,
                        "rotate": 0,
                        "lineHeight": 12,
                        "fontWeight": "bold"
                    }
                },
                "yAxis": {"type": "value"},
                "series": [
                    {
                        "data": average_bookings_per_day,
                        "type": "line",
                        "name": "Average Bookings per Day",
                        "itemStyle": {"color": "#EE6666"},
                        "lineStyle": {"width": 2}
                    }
                ]
            }

                # Render the line chart below the bar chart
                st_echarts(line_options)

            elif chart_option == "Total Payable":
                # Process data for Financial Overview chart
                batch_counts = data_200hr.groupby(['Batch start date', 'Batch end date']).agg(
                    {"Total Payable (in USD or USD equiv)": "sum",
                     "Total paid (as of today)": "sum",
                     "Student still to pay": "sum"}).reset_index()

                batch_counts['Batch start date'] = pd.to_datetime(batch_counts['Batch start date'])
                batch_counts['Batch end date'] = pd.to_datetime(batch_counts['Batch end date'])
                batch_counts = batch_counts.sort_values(by='Batch start date')
                
                batch_counts['Batch'] = batch_counts['Batch start date'].dt.strftime('%B %d, %Y') + " to " + batch_counts['Batch end date'].dt.strftime('%B %d, %Y')
                
                wrapped_labels = [label.replace(" to ", "\nto\n") for label in batch_counts['Batch']]
                total_payable = batch_counts["Total Payable (in USD or USD equiv)"].tolist()
                total_paid = batch_counts["Total paid (as of today)"].tolist()
                student_still_to_pay = batch_counts["Student still to pay"].tolist()

                # Combo chart for Financial Overview
                combo_options = {
                    "title": {
                        "text": "Financial Overview",
                        "left": "center",
                        "top": "top",
                        "textStyle": {"fontSize": 18, "fontWeight": "bold"}
                    },
                    "tooltip": {"trigger": "axis"},
                    "legend": {
                        "data": ["Total Payable", "Total Paid", "Student Still to Pay"],
                        "orient": "horizontal",  # Orientasi horizontal
                        "bottom": "0",           # Posisikan legend di bawah
                        "left": "center"         # Rata tengah
                    },
                    "xAxis": {
                        "type": "category",
                        "data": wrapped_labels,
                        "axisLabel": {
                            "interval": 0,
                            "fontSize": 7,
                            "rotate": 0,
                            "lineHeight": 12,
                            "fontWeight": "bold"
                        }
                    },
                    "yAxis": {"type": "value"},
                    "series": [
                        {
                            "name": "Total Payable",
                            "data": total_payable,
                            "type": "line",
                            "itemStyle": {"color": "#5470C6"},
                            "lineStyle": {"type": "dashed", "width": 1},
                            "symbol": "circle",
                            "symbolSize": 8    
                        },
                        {
                            "name": "Total Paid",
                            "data": total_paid,
                            "type": "line",
                            "itemStyle": {"color": "#91CC75"},
                            "lineStyle": {"width": 2},
                            "symbol": "circle",
                            "symbolSize": 8     
                        },
                        {
                            "name": "Student Still to Pay",
                            "data": student_still_to_pay,
                            "type": "line",
                            "lineStyle": {"width": 1, "type": "dotted"},     
                            "itemStyle": {"color": "grey"},
                            "symbol": "circle",
                            "symbolSize": 8     
                        }
                    ]
                }

                # Render the combo chart
                st_echarts(combo_options)

                # Display the grouped summary table below the Financial Overview chart
                # st.write("### Financial Summary by Batch")

                # Display the aggregated data as a table
                financial_summary = batch_counts[['Batch start date', 'Batch end date', 
                                                  'Total Payable (in USD or USD equiv)', 
                                                  'Total paid (as of today)', 
                                                  'Student still to pay']]
                
                # Rename columns for readability
                financial_summary.columns = ["Batch Start Date", "Batch End Date", "Total Payable (USD)", 
                                             "Total Paid (USD)", "Outstanding (USD)"]
                
                financial_summary['Batch Start Date'] = financial_summary['Batch Start Date'].dt.strftime('%B %d, %Y')
                financial_summary['Batch End Date'] = financial_summary['Batch End Date'].dt.strftime('%B %d, %Y')
                
                # Display the table
                st.dataframe(financial_summary)

            # Logika untuk "Data"
            elif chart_option == "Data":
                # Remove the 'S.No.' column from data_200hr before displaying
                data_200hr_display = data_200hr.drop(columns=['S.No.'])

                # Display the modified dataframe as a table
                st.write("Detailed Data View")
                st.dataframe(data_200hr_display) 
            
        except Exception as e:
            st.error("Failed to load data. Please check the URL or your connection.")
            st.write(f"Error: {e}")

    # Load and process data if "200HR" is selected
    elif program == "300HR":
        # Load the Excel file from the URL
        url = "https://raw.githubusercontent.com/antoniusawe/sales-report/main/RYP%20data/ryp_student_database_300hr.xlsx"
        
        try:
            data_300hr = pd.read_excel(url)
            # Calculate Total Booking, Total Payable, and Outstanding
            total_booking_ctr = data_300hr["Name of student"].count()
            total_payable_sum = data_300hr["Total Payable (in USD or USD equiv)"].sum()
            outstanding_sum = data_300hr["Student still to pay"].sum()
            
            # Calculate the percentage of Outstanding from Total Payable
            outstanding_percentage = (outstanding_sum / total_payable_sum * 100) if total_payable_sum else 0

            # Display Total Booking, Total Payable, and Outstanding in a centered format
            st.markdown(f"""
            <div style='display: flex; justify-content: center; gap: 50px; padding: 20px;'>
                <div style='text-align: left;'>
                    <div style='font-size: 16px; color: #333333;'>Total Booking</div>
                    <div style='font-size: 48px;'>{total_booking_ctr}</div>
                    <div style='color: #202fb2; font-size: 18px;'>Number of Students</div>
                </div>
                <div style='text-align: left;'>
                    <div style='font-size: 16px; color: #333333;'>Total Payable</div>
                    <div style='font-size: 48px;'>{total_payable_sum:,.0f}</div>
                    <div style='color: #202fb2; font-size: 18px;'>in USD or USD equiv</div>
                </div>
                <div style='text-align: left;'>
                    <div style='font-size: 16px; color: #333333;'>Outstanding</div>
                    <div style='font-size: 48px;'>{outstanding_sum:,.0f}</div>
                    <div style='color: #202fb2; font-size: 18px;'>{outstanding_percentage:.2f}% of Total Payable</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Dropdown for chart data selection
            chart_option = st.selectbox("Choose Data to Display:", ["Total Booking", "Total Payable", "Data"])

            if chart_option == "Total Booking":
                # Process data for Number of Students chart
                batch_counts = data_300hr.groupby(['Batch start date', 'Batch end date'])['Name of student'].count().reset_index()
                
                batch_counts['Batch start date'] = pd.to_datetime(batch_counts['Batch start date'])
                batch_counts['Batch end date'] = pd.to_datetime(batch_counts['Batch end date'])
                batch_counts['Days in Batch'] = (batch_counts['Batch end date'] - batch_counts['Batch start date']).dt.days + 1
                
                batch_counts['Average Bookings per Day'] = batch_counts['Name of student'] / batch_counts['Days in Batch']
                batch_counts = batch_counts.sort_values(by='Batch start date')
                
                batch_counts['Batch'] = batch_counts['Batch start date'].dt.strftime('%B %d, %Y') + " to " + batch_counts['Batch end date'].dt.strftime('%B %d, %Y')
                
                wrapped_labels = [label.replace(" to ", "\nto\n") for label in batch_counts['Batch']]
                student_counts = batch_counts['Name of student'].tolist()
                average_bookings_per_day = batch_counts['Average Bookings per Day'].tolist()

                # Bar chart for Number of Students
                bar_options = {
                "title": {
                    "text": "Total Booking",  # Adding the title for the bar chart
                    "left": "center",          # Center the title
                    "top": "top",              # Position it at the top of the chart
                    "textStyle": {"fontSize": 18, "fontWeight": "bold"}
                },
                "tooltip": {"trigger": "axis"},
                "xAxis": {
                    "type": "category",
                    "data": wrapped_labels,
                    "axisLabel": {
                        "interval": 0,
                        "fontSize": 7,
                        "rotate": 0,
                        "lineHeight": 12,
                        "fontWeight": "bold"
                    }
                },
                "yAxis": {"type": "value"},
                "series": [
                    {
                        "data": student_counts,
                        "type": "bar",
                        "name": "Student Count",
                        "itemStyle": {"color": "#5470C6"}
                    }
                ]
            }

                # Render the bar chart
                st_echarts(bar_options)

                # Line chart for Average Bookings per Day
                line_options = {
                "title": {
                    "text": "Average Booking per Day",  # Adding the title for the line chart
                    "left": "center",           # Center the title
                    "top": "top",               # Position it at the top of the chart
                    "textStyle": {"fontSize": 18, "fontWeight": "bold"}
                },
                "tooltip": {"trigger": "axis"},
                "xAxis": {
                    "type": "category",
                    "data": wrapped_labels,
                    "axisLabel": {
                        "interval": 0,
                        "fontSize": 7,
                        "rotate": 0,
                        "lineHeight": 12,
                        "fontWeight": "bold"
                    }
                },
                "yAxis": {"type": "value"},
                "series": [
                    {
                        "data": average_bookings_per_day,
                        "type": "line",
                        "name": "Average Bookings per Day",
                        "itemStyle": {"color": "#EE6666"},
                        "lineStyle": {"width": 2}
                    }
                ]
            }

                # Render the line chart below the bar chart
                st_echarts(line_options)

            elif chart_option == "Total Payable":
                # Process data for Financial Overview chart
                batch_counts = data_300hr.groupby(['Batch start date', 'Batch end date']).agg(
                    {"Total Payable (in USD or USD equiv)": "sum",
                     "Total paid (as of today)": "sum",
                     "Student still to pay": "sum"}).reset_index()

                batch_counts['Batch start date'] = pd.to_datetime(batch_counts['Batch start date'])
                batch_counts['Batch end date'] = pd.to_datetime(batch_counts['Batch end date'])
                batch_counts = batch_counts.sort_values(by='Batch start date')
                
                batch_counts['Batch'] = batch_counts['Batch start date'].dt.strftime('%B %d, %Y') + " to " + batch_counts['Batch end date'].dt.strftime('%B %d, %Y')
                
                wrapped_labels = [label.replace(" to ", "\nto\n") for label in batch_counts['Batch']]
                total_payable = batch_counts["Total Payable (in USD or USD equiv)"].tolist()
                total_paid = batch_counts["Total paid (as of today)"].tolist()
                student_still_to_pay = batch_counts["Student still to pay"].tolist()

                # Combo chart for Financial Overview
                combo_options = {
                    "title": {
                        "text": "Financial Overview",
                        "left": "center",
                        "top": "top",
                        "textStyle": {"fontSize": 18, "fontWeight": "bold"}
                    },
                    "tooltip": {"trigger": "axis"},
                    "legend": {
                        "data": ["Total Payable", "Total Paid", "Student Still to Pay"],
                        "orient": "horizontal",  # Orientasi horizontal
                        "bottom": "0",           # Posisikan legend di bawah
                        "left": "center"         # Rata tengah
                    },
                    "xAxis": {
                        "type": "category",
                        "data": wrapped_labels,
                        "axisLabel": {
                            "interval": 0,
                            "fontSize": 7,
                            "rotate": 0,
                            "lineHeight": 12,
                            "fontWeight": "bold"
                        }
                    },
                    "yAxis": {"type": "value"},
                    "series": [
                        {
                            "name": "Total Payable",
                            "data": total_payable,
                            "type": "line",
                            "itemStyle": {"color": "#5470C6"},
                            "lineStyle": {"type": "dashed", "width": 1},
                            "symbol": "circle",
                            "symbolSize": 8    
                        },
                        {
                            "name": "Total Paid",
                            "data": total_paid,
                            "type": "line",
                            "itemStyle": {"color": "#91CC75"},
                            "lineStyle": {"width": 2},
                            "symbol": "circle",
                            "symbolSize": 8     
                        },
                        {
                            "name": "Student Still to Pay",
                            "data": student_still_to_pay,
                            "type": "line",
                            "lineStyle": {"width": 1, "type": "dotted"},     
                            "itemStyle": {"color": "grey"},
                            "symbol": "circle",
                            "symbolSize": 8     
                        }
                    ]
                }

                # Render the combo chart
                st_echarts(combo_options)

                # Display the grouped summary table below the Financial Overview chart
                # st.write("### Financial Summary by Batch")

                # Display the aggregated data as a table
                financial_summary = batch_counts[['Batch start date', 'Batch end date', 
                                                  'Total Payable (in USD or USD equiv)', 
                                                  'Total paid (as of today)', 
                                                  'Student still to pay']]
                
                # Rename columns for readability
                financial_summary.columns = ["Batch Start Date", "Batch End Date", "Total Payable (USD)", 
                                             "Total Paid (USD)", "Outstanding (USD)"]
                
                financial_summary['Batch Start Date'] = financial_summary['Batch Start Date'].dt.strftime('%B %d, %Y')
                financial_summary['Batch End Date'] = financial_summary['Batch End Date'].dt.strftime('%B %d, %Y')
                
                # Display the table
                st.dataframe(financial_summary)

            # Logika untuk "Data"
            elif chart_option == "Data":
                # Remove the 'S.No.' column from data_200hr before displaying
                data_200hr_display = data_300hr.drop(columns=['S.No.'])

                # Display the modified dataframe as a table
                st.write("Detailed Data View")
                st.dataframe(data_300hr) 
            
        except Exception as e:
            st.error("Failed to load data. Please check the URL or your connection.")
            st.write(f"Error: {e}")   


else:
    st.write("Data currently unavailable.")
