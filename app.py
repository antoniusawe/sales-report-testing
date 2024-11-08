#!/usr/bin/env python
# coding: utf-8

# In[224]:


import pandas as pd
import streamlit as st
from datetime import datetime
import matplotlib.pyplot as plt
import plotly.express as px


# In[225]:


# Load the two uploaded files to examine their contents
occupancy_df = pd.read_excel("https://raw.githubusercontent.com/antoniusawe/sales-report/main/Bali%20data/bali_occupancy.xlsx")
sales_df = pd.read_excel("https://raw.githubusercontent.com/antoniusawe/sales-report/main/Bali%20data/bali_sales.xlsx")

# Display the first few rows of each DataFrame to understand their structure
# occupancy_df.head(), sales_df.head()

unique_years = sorted(set(sales_df['Year'].dropna().unique()).union(occupancy_df['Year'].dropna().unique()))
unique_years_with_all = ["All"] + unique_years


# In[226]:


def get_sorted_months_for_year(selected_year):
    if selected_year != "All":
        # Fetch months from both dataframes for the selected year
        sales_months = sales_df[sales_df['Year'] == selected_year]['Month'].dropna().unique()
        occupancy_months = occupancy_df[occupancy_df['Year'] == selected_year]['Month'].dropna().unique()
        
        # Combine and convert to datetime objects for sorting
        all_months = sorted(set(sales_months).union(occupancy_months), key=lambda x: datetime.strptime(x, "%B"))
        
        # Convert sorted datetime objects back to month names as strings
        sorted_month_strings = [month.strftime("%B") for month in map(lambda m: datetime.strptime(m, "%B"), all_months)]
    else:
        sorted_month_strings = []  # No months needed for "All"
    
    return sorted_month_strings

# Test the function by simulating a selection of "2024" as the year
sorted_months_for_2024 = get_sorted_months_for_year(2024)


# In[227]:


def get_sales_summary_count_amount_paid_and_occupancy_mean(category, selected_year="All", selected_month=None):
    # Filter pada sales_df berdasarkan kategori
    filtered_sales_df = sales_df[sales_df['Category'] == category]
    
    # Filter sales_df berdasarkan tahun jika tahun tertentu dipilih
    if selected_year != "All":
        filtered_sales_df = filtered_sales_df[filtered_sales_df['Year'] == selected_year]
        
    # Filter sales_df berdasarkan bulan jika bulan tertentu dipilih
    if selected_month:
        filtered_sales_df = filtered_sales_df[filtered_sales_df['Month'] == selected_month]
    
    # Hitung jumlah pemesanan ('NAME') di mana 'PAID STATUS' tidak kosong
    summary_count = filtered_sales_df[filtered_sales_df['PAID STATUS'].notna()]['NAME'].count()
    
    # Hitung total amount paid (jumlah dari kolom 'PAID')
    total_amount_paid = filtered_sales_df['PAID'].sum()
    
    # Filter pada occupancy_df dengan kategori yang sama
    filtered_occupancy_df = occupancy_df[occupancy_df['Category'] == category]
    
    # Filter occupancy_df berdasarkan tahun jika tahun tertentu dipilih
    if selected_year != "All":
        filtered_occupancy_df = filtered_occupancy_df[filtered_occupancy_df['Year'] == selected_year]
        
    # Filter occupancy_df berdasarkan bulan jika bulan tertentu dipilih
    if selected_month:
        filtered_occupancy_df = filtered_occupancy_df[filtered_occupancy_df['Month'] == selected_month]
    
    # Bersihkan kolom 'Occupancy' dengan menghapus '%' dan ubah menjadi numerik
    filtered_occupancy_df['Occupancy'] = filtered_occupancy_df['Occupancy'].str.replace('%', '').astype(float)
    
    # Hitung rata-rata occupancy (mean dari kolom 'Occupancy')
    occupancy_mean = filtered_occupancy_df['Occupancy'].mean()
    
    return summary_count, total_amount_paid, occupancy_mean


# In[228]:


def get_favorite_sites(category, selected_year="All", selected_month=None):
    # Filter occupancy_df berdasarkan kategori
    filtered_occupancy_df = occupancy_df[occupancy_df['Category'] == category]
    
    # Filter berdasarkan tahun jika tahun tertentu dipilih
    if selected_year != "All":
        filtered_occupancy_df = filtered_occupancy_df[filtered_occupancy_df['Year'] == selected_year]
        
    # Filter berdasarkan bulan jika bulan tertentu dipilih
    if selected_month:
        filtered_occupancy_df = filtered_occupancy_df[filtered_occupancy_df['Month'] == selected_month]
    
    # Hitung jumlah setiap 'Site' berdasarkan kolom 'Fill'
    site_counts = filtered_occupancy_df.groupby('Site')['Fill'].sum().sort_values(ascending=False)
    
    return site_counts


# In[229]:


def get_fill_by_room(category, selected_year="All", selected_month=None):
    # Filter occupancy_df berdasarkan kategori
    filtered_occupancy_df = occupancy_df[occupancy_df['Category'] == category]
    
    # Filter berdasarkan tahun jika tahun tertentu dipilih
    if selected_year != "All":
        filtered_occupancy_df = filtered_occupancy_df[filtered_occupancy_df['Year'] == selected_year]
        
    # Filter berdasarkan bulan jika bulan tertentu dipilih
    if selected_month:
        filtered_occupancy_df = filtered_occupancy_df[filtered_occupancy_df['Month'] == selected_month]
    
    # Mengelompokkan berdasarkan 'Room' dan menjumlahkan nilai kolom 'Fill'
    room_counts = filtered_occupancy_df.groupby('Room')['Fill'].sum().sort_values(ascending=False)
    
    return room_counts


# In[230]:


def get_fill_counts(category, selected_year="All", selected_month=None, group_by="Site"):
    # Filter occupancy_df berdasarkan kategori
    filtered_occupancy_df = occupancy_df[occupancy_df['Category'] == category]
    
    # Filter berdasarkan tahun jika tahun tertentu dipilih
    if selected_year != "All":
        filtered_occupancy_df = filtered_occupancy_df[filtered_occupancy_df['Year'] == selected_year]
        
    # Filter berdasarkan bulan jika bulan tertentu dipilih
    if selected_month:
        filtered_occupancy_df = filtered_occupancy_df[filtered_occupancy_df['Month'] == selected_month]
    
    # Mengelompokkan data berdasarkan kolom yang ditentukan ('Site', 'Room', atau 'Month') dan menjumlahkan nilai kolom 'Fill'
    fill_counts = filtered_occupancy_df.groupby(group_by)['Fill'].sum().sort_values(ascending=False)
    
    return fill_counts


# In[231]:


# Title of the application
st.title("Choose Your Location and Program")

# Step 1: Location Selection
location = st.sidebar.selectbox("Choose Location:", ["Bali", "RYP"])

# Step 2: Program Selection (displayed regardless of location selection)
program = st.sidebar.selectbox("Choose Program:", ["200HR", "300HR"])

# Display the selection
st.write(f"{location} - {program}")

# Add specific logic for each combination if needed
if location == "Bali" and program == "200HR":
    # Step 3: Year Selection for Bali - 200HR
    year = st.selectbox("Choose Year:", unique_years_with_all)
    
    # Step 4: Month Selection if specific year (not "All") is selected
    if year != "All":
        # Get sorted months for the selected year
        months_for_selected_year = get_sorted_months_for_year(year)
        
        # Display month dropdown
        month = st.selectbox("Choose Month:", months_for_selected_year)
        
        # Display view options only if a month is selected
        if month:
            view_option = st.radio("Choose View:", ["Overview", "Location", "Batch"])

            if view_option == "Overview":
                # Mendapatkan jumlah pemesanan dan total amount paid untuk tampilan Overview berdasarkan tahun dan bulan
                sales_summary_count, total_amount_paid, occupancy_mean = get_sales_summary_count_amount_paid_and_occupancy_mean(
                    category=program, selected_year=year, selected_month=month
                )
                
                # Displaying the summary in a styled format
                st.markdown(f"""
                    <div style='display: flex; justify-content: center; gap: 50px; padding: 20px;'>
                        <div style='text-align: left;'>
                            <div style='font-size: 16px; color: #333333;'>Total Booking</div>
                            <div style='font-size: 48px; color: #3D3D3D;'>{sales_summary_count}</div>
                            <div style='color: #202fb2; font-size: 18px;'>Students</div>
                        </div>
                        <div style='text-align: left;'>
                            <div style='font-size: 16px; color: #333333;'>Total Amount Paid</div>
                            <div style='font-size: 48px; color: #3D3D3D;'>${total_amount_paid:,.2f}</div>
                            <div style='color: #202fb2; font-size: 18px;'>In USD (equiv)</div>
                        </div>
                        <div style='text-align: left;'>
                            <div style='font-size: 16px; color: #333333;'>Occupancy</div>
                            <div style='font-size: 48px; color: #3D3D3D;'>{occupancy_mean:.2f}%</div>
                            <div style='color: #202fb2; font-size: 18px;'>Occupancy Rate</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # Menghitung site favorit berdasarkan filter yang dipilih
                site_counts = get_favorite_sites(category=program, selected_year=year, selected_month=month if year != "All" else None)
                    
                # Menampilkan chart Site Favorit di Streamlit dengan Plotly
                # st.subheader("Site Paling Favorit Berdasarkan Jumlah 'Fill'")
                fig = px.bar(
                    site_counts,
                    x=site_counts.index,
                    y=site_counts.values,
                    labels={'x': 'Site', 'y': 'Count'},
                    title="Top Sites",
                    text_auto=True
                )

                # Menyesuaikan tampilan chart
                fig.update_layout(
                    xaxis_title="Site",
                    yaxis_title="Count",
                    template="plotly_white"
                )

                st.plotly_chart(fig)

                # Menghitung total Fill berdasarkan Room
                room_counts = get_fill_by_room(category=program, selected_year=year, selected_month=month if year != "All" else None)

                # Menampilkan chart Fill by Room di Streamlit dengan Plotly
                # st.subheader("Room Paling Favorit Berdasarkan Jumlah 'Fill'")
                fig = px.bar(
                    room_counts,
                    x=room_counts.index,
                    y=room_counts.values,
                    labels={'x': 'Room', 'y': 'Total Fill'},
                    title="Top Rooms",
                    text_auto=True
                )

                # Menyesuaikan tampilan chart
                fig.update_layout(
                    xaxis_title="Room",
                    yaxis_title="Total Fill",
                    template="plotly_white"
                )

                st.plotly_chart(fig)

                #  Menghitung total Fill berdasarkan Month yang terhubung ke dropdown dan radio button
                month_counts = get_fill_counts(category=program, selected_year=year, group_by="Month")
                # Konversi bulan ke datetime untuk pengurutan kronologis
                month_counts.index = pd.to_datetime(month_counts.index, format='%B')
                # Mengurutkan bulan
                month_counts = month_counts.sort_index()
                # Konversi kembali ke format string untuk visualisasi
                month_counts.index = month_counts.index.strftime('%B')
                # Mengurutkan bulan berdasarkan nilai Fill dari terbesar ke terkecil
                month_counts = month_counts.sort_values(ascending=False)

                # Menampilkan chart Fill by Month di Streamlit dengan Plotly
                # st.subheader("Total Fill Berdasarkan Bulan")
                fig = px.bar(
                    month_counts,
                    x=month_counts.index,
                    y=month_counts.values,
                    labels={'x': 'Month', 'y': 'Total Fill'},
                    title="Total Fill",
                    text_auto=True  # Menampilkan nilai di atas bar
                )

                # Menyesuaikan tampilan chart
                fig.update_layout(
                    xaxis_title="Month",
                    yaxis_title="Total Fill",
                    template="plotly_white"
                )

                # Menampilkan chart di Streamlit
                st.plotly_chart(fig)


    else:
        # If "All" is selected for the year, show the view options without a month selection
        view_option = st.radio("Choose View:", ["Overview", "Location", "Batch"])

        if view_option == "Overview":
            # Mendapatkan jumlah pemesanan dan total amount paid untuk semua tahun
            sales_summary_count, total_amount_paid, occupancy_mean = get_sales_summary_count_amount_paid_and_occupancy_mean(
                category=program, selected_year=year
            )
            
            # Displaying the summary in a styled format
            st.markdown(f"""
                <div style='display: flex; justify-content: center; gap: 50px; padding: 20px;'>
                    <div style='text-align: left;'>
                        <div style='font-size: 16px; color: #333333;'>Total Booking</div>
                        <div style='font-size: 48px; color: #3D3D3D;'>{sales_summary_count}</div>
                        <div style='color: #202fb2; font-size: 18px;'>Students</div>
                    </div>
                    <div style='text-align: left;'>
                        <div style='font-size: 16px; color: #333333;'>Total Amount Paid</div>
                        <div style='font-size: 48px; color: #3D3D3D;'>${total_amount_paid:,.2f}</div>
                        <div style='color: #202fb2; font-size: 18px;'>In USD (equiv)</div>
                    </div>
                    <div style='text-align: left;'>
                        <div style='font-size: 16px; color: #333333;'>Occupancy</div>
                        <div style='font-size: 48px; color: #3D3D3D;'>{occupancy_mean:.2f}%</div>
                        <div style='color: #202fb2; font-size: 18px;'>Occupancy Rate</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Menghitung site favorit berdasarkan filter yang dipilih
            site_counts = get_favorite_sites(category=program, selected_year=year, selected_month=month if year != "All" else None)
                
            # Menampilkan chart Site Favorit di Streamlit dengan Plotly
            # st.subheader("Site Paling Favorit Berdasarkan Jumlah 'Fill'")
            fig = px.bar(
                site_counts,
                x=site_counts.index,
                y=site_counts.values,
                labels={'x': 'Site', 'y': 'Count'},
                title="Top Sites",
                text_auto=True
            )

            # Menyesuaikan tampilan chart
            fig.update_layout(
                xaxis_title="Site",
                yaxis_title="Count",
                template="plotly_white"
            )

            st.plotly_chart(fig)

            # Menghitung total Fill berdasarkan Room
            room_counts = get_fill_by_room(category=program, selected_year=year, selected_month=month if year != "All" else None)

            # Menampilkan chart Fill by Room di Streamlit dengan Plotly
            # st.subheader("Room Paling Favorit Berdasarkan Jumlah 'Fill'")
            fig = px.bar(
                room_counts,
                x=room_counts.index,
                y=room_counts.values,
                labels={'x': 'Room', 'y': 'Total Fill'},
                title="Top Rooms",
                text_auto=True
            )

            # Menyesuaikan tampilan chart
            fig.update_layout(
                xaxis_title="Room",
                yaxis_title="Total Fill",
                template="plotly_white"
            )

            st.plotly_chart(fig)

            #  Menghitung total Fill berdasarkan Month yang terhubung ke dropdown dan radio button
            month_counts = get_fill_counts(category=program, selected_year=year, group_by="Month")
            # Konversi bulan ke datetime untuk pengurutan kronologis
            month_counts.index = pd.to_datetime(month_counts.index, format='%B')
            # Mengurutkan bulan
            month_counts = month_counts.sort_index()
            # Konversi kembali ke format string untuk visualisasi
            month_counts.index = month_counts.index.strftime('%B')
            # Mengurutkan bulan berdasarkan nilai Fill dari terbesar ke terkecil
            month_counts = month_counts.sort_values(ascending=False)

            # Menampilkan chart Fill by Month di Streamlit dengan Plotly
            # st.subheader("Total Fill Berdasarkan Bulan")
            fig = px.bar(
                month_counts,
                x=month_counts.index,
                y=month_counts.values,
                labels={'x': 'Month', 'y': 'Total Fill'},
                title="Total Fill",
                text_auto=True  # Menampilkan nilai di atas bar
            )

            # Menyesuaikan tampilan chart
            fig.update_layout(
                xaxis_title="Month",
                yaxis_title="Total Fill",
                template="plotly_white"
            )

            # Menampilkan chart di Streamlit
            st.plotly_chart(fig)

        if view_option == "Location":
            st.write("Disini")

elif location == "Bali" and program == "300HR":
    # Step 3: Year Selection for Bali - 300HR
    year = st.selectbox("Choose Year:", unique_years_with_all)
    
    # Step 4: Month Selection if specific year (not "All") is selected
    if year != "All":
        # Get sorted months for the selected year
        months_for_selected_year = get_sorted_months_for_year(year)
        
        # Display month dropdown
        month = st.selectbox("Choose Month:", months_for_selected_year)
        
        # Display view options only if a month is selected
        if month:
            view_option = st.radio("Choose View:", ["Overview", "Location", "Batch"])
            
            if view_option == "Overview":
                # Mendapatkan jumlah pemesanan dan total amount paid untuk tampilan Overview berdasarkan tahun dan bulan
                sales_summary_count, total_amount_paid, occupancy_mean = get_sales_summary_count_amount_paid_and_occupancy_mean(
                    category=program, selected_year=year, selected_month=month
                )
                
                # Displaying the summary in a styled format
                st.markdown(f"""
                    <div style='display: flex; justify-content: center; gap: 50px; padding: 20px;'>
                        <div style='text-align: left;'>
                            <div style='font-size: 16px; color: #333333;'>Total Booking</div>
                            <div style='font-size: 48px; color: #3D3D3D;'>{sales_summary_count}</div>
                            <div style='color: #202fb2; font-size: 18px;'>Students</div>
                        </div>
                        <div style='text-align: left;'>
                            <div style='font-size: 16px; color: #333333;'>Total Amount Paid</div>
                            <div style='font-size: 48px; color: #3D3D3D;'>${total_amount_paid:,.2f}</div>
                            <div style='color: #202fb2; font-size: 18px;'>In USD (equiv)</div>
                        </div>
                        <div style='text-align: left;'>
                            <div style='font-size: 16px; color: #333333;'>Occupancy</div>
                            <div style='font-size: 48px; color: #3D3D3D;'>{occupancy_mean:.2f}%</div>
                            <div style='color: #202fb2; font-size: 18px;'>Occupancy Rate</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # Menghitung site favorit untuk semua tahun
            site_counts = get_favorite_sites(category=program, selected_year=year, selected_month=month if year != "All" else None)
            
            # Menampilkan chart Site Favorit di Streamlit
            # st.subheader("Site Paling Favorit Berdasarkan Jumlah 'Fill'")
            fig = px.bar(
                site_counts,
                x=site_counts.index,
                y=site_counts.values,
                labels={'x': 'Site', 'y': 'Count'},
                title="Top Sites",
                text_auto=True
            )

            # Menyesuaikan tampilan chart
            fig.update_layout(
                xaxis_title="Site",
                yaxis_title="Count",
                template="plotly_white"
            )

            st.plotly_chart(fig)

            # Menghitung total Fill berdasarkan Room
            room_counts = get_fill_by_room(category=program, selected_year=year, selected_month=month if year != "All" else None)

            # Menampilkan chart Fill by Room di Streamlit dengan Plotly
            # st.subheader("Room Paling Favorit Berdasarkan Jumlah 'Fill'")
            fig = px.bar(
                room_counts,
                x=room_counts.index,
                y=room_counts.values,
                labels={'x': 'Room', 'y': 'Total Fill'},
                title="Top Rooms",
                text_auto=True
            )

            # Menyesuaikan tampilan chart
            fig.update_layout(
                xaxis_title="Room",
                yaxis_title="Total Fill",
                template="plotly_white"
            )

            st.plotly_chart(fig)

            #  Menghitung total Fill berdasarkan Month yang terhubung ke dropdown dan radio button
            month_counts = get_fill_counts(category=program, selected_year=year, group_by="Month")
            # Konversi bulan ke datetime untuk pengurutan kronologis
            month_counts.index = pd.to_datetime(month_counts.index, format='%B')
            # Mengurutkan bulan
            month_counts = month_counts.sort_index()
            # Konversi kembali ke format string untuk visualisasi
            month_counts.index = month_counts.index.strftime('%B')
            # Mengurutkan bulan berdasarkan nilai Fill dari terbesar ke terkecil
            month_counts = month_counts.sort_values(ascending=False)

            # Menampilkan chart Fill by Month di Streamlit dengan Plotly
            st.subheader("Total Fill Berdasarkan Bulan")
            fig = px.bar(
                month_counts,
                x=month_counts.index,
                y=month_counts.values,
                labels={'x': 'Month', 'y': 'Total Fill'},
                title="Total Fill by Month",
                text_auto=True  # Menampilkan nilai di atas bar
            )

            # Menyesuaikan tampilan chart
            fig.update_layout(
                xaxis_title="Month",
                yaxis_title="Total Fill",
                template="plotly_white"
            )

            # Menampilkan chart di Streamlit
            st.plotly_chart(fig)

    else:
        # If "All" is selected for the year, show the view options without a month selection
        view_option = st.radio("Choose View:", ["Overview", "Location", "Batch"])

        if view_option == "Overview":
            # Mendapatkan jumlah pemesanan dan total amount paid untuk semua tahun
                        # Mendapatkan jumlah pemesanan dan total amount paid untuk semua tahun
            sales_summary_count, total_amount_paid, occupancy_mean = get_sales_summary_count_amount_paid_and_occupancy_mean(
                category=program, selected_year=year
            )
            
            # Displaying the summary in a styled format
            st.markdown(f"""
                <div style='display: flex; justify-content: center; gap: 50px; padding: 20px;'>
                    <div style='text-align: left;'>
                        <div style='font-size: 16px; color: #333333;'>Total Booking</div>
                        <div style='font-size: 48px; color: #3D3D3D;'>{sales_summary_count}</div>
                        <div style='color: #202fb2; font-size: 18px;'>Students</div>
                    </div>
                    <div style='text-align: left;'>
                        <div style='font-size: 16px; color: #333333;'>Total Amount Paid</div>
                        <div style='font-size: 48px; color: #3D3D3D;'>${total_amount_paid:,.2f}</div>
                        <div style='color: #202fb2; font-size: 18px;'>In USD (equiv)</div>
                    </div>
                    <div style='text-align: left;'>
                        <div style='font-size: 16px; color: #333333;'>Occupancy</div>
                        <div style='font-size: 48px; color: #3D3D3D;'>{occupancy_mean:.2f}%</div>
                        <div style='color: #202fb2; font-size: 18px;'>Occupancy Rate</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Menghitung site favorit untuk semua tahun
            site_counts = get_favorite_sites(category=program, selected_year=year, selected_month=month if year != "All" else None)
            
            # Menampilkan chart Site Favorit di Streamlit
            # st.subheader("Site Paling Favorit Berdasarkan Jumlah 'Fill'")
            fig = px.bar(
                site_counts,
                x=site_counts.index,
                y=site_counts.values,
                labels={'x': 'Site', 'y': 'Count'},
                title="Top Sites by Count",
                text_auto=True
            )

            # Menyesuaikan tampilan chart
            fig.update_layout(
                xaxis_title="Site",
                yaxis_title="Count",
                template="plotly_white"
            )

            st.plotly_chart(fig)

            # Menghitung total Fill berdasarkan Room
            room_counts = get_fill_by_room(category=program, selected_year=year, selected_month=month if year != "All" else None)

            # Menampilkan chart Fill by Room di Streamlit dengan Plotly
            st.subheader("Room Paling Favorit Berdasarkan Jumlah 'Fill'")
            fig = px.bar(
                room_counts,
                x=room_counts.index,
                y=room_counts.values,
                labels={'x': 'Room', 'y': 'Total Fill'},
                title="Top Rooms by Total Fill",
                text_auto=True
            )

            # Menyesuaikan tampilan chart
            fig.update_layout(
                xaxis_title="Room",
                yaxis_title="Total Fill",
                template="plotly_white"
            )

            st.plotly_chart(fig)

            #  Menghitung total Fill berdasarkan Month yang terhubung ke dropdown dan radio button
            month_counts = get_fill_counts(category=program, selected_year=year, group_by="Month")
            # Konversi bulan ke datetime untuk pengurutan kronologis
            month_counts.index = pd.to_datetime(month_counts.index, format='%B')
            # Mengurutkan bulan
            month_counts = month_counts.sort_index()
            # Konversi kembali ke format string untuk visualisasi
            month_counts.index = month_counts.index.strftime('%B')
            # Mengurutkan bulan berdasarkan nilai Fill dari terbesar ke terkecil
            month_counts = month_counts.sort_values(ascending=False)

            # Menampilkan chart Fill by Month di Streamlit dengan Plotly
            st.subheader("Total Fill Berdasarkan Bulan")
            fig = px.bar(
                month_counts,
                x=month_counts.index,
                y=month_counts.values,
                labels={'x': 'Month', 'y': 'Total Fill'},
                title="Total Fill by Month",
                text_auto=True  # Menampilkan nilai di atas bar
            )

            # Menyesuaikan tampilan chart
            fig.update_layout(
                xaxis_title="Month",
                yaxis_title="Total Fill",
                template="plotly_white"
            )

            # Menampilkan chart di Streamlit
            st.plotly_chart(fig)

#----------------------------------------------------------------------------

elif location == "RYP" and program == "200HR":
    st.write("Displaying content for RYP - 200HR")
    # Insert RYP 200HR specific content or logic here
    #------------------------------------------------------------------------

elif location == "RYP" and program == "300HR":
    st.write("Displaying content for RYP - 300HR")
    # Insert RYP 300HR specific content or logic here
    #------------------------------------------------------------------------

