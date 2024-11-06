import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
from datetime import datetime
from datetime import timedelta

# Sidebar dropdown for location
location = st.sidebar.selectbox("Choose a Location:", ["Bali", "India"])

# Display the main image and title
st.image("https://raw.githubusercontent.com/antoniusawe/sales-report/main/images/house_of_om-removebg-preview.png",  
         use_column_width=True)
st.markdown("<h1 style='text-align: center; font-size: 50px;'>HOUSE OF OM - DASHBOARD</h1>", unsafe_allow_html=True)

if location == "Bali":
    # Sub-dropdown for specific options under "Bali"
    bali_option = st.sidebar.selectbox("Choose a Section:", ["Overview", "Location", "Batch"])
         if bali_option == "Overview":
                  if program == "200HR":
                           st.write("Ini adalah Overview untuk program 200HR")
                  elif program == "300HR":
                           st.write("Ini adalah Overview untuk program 300HR")
                           

elif location == "India":
    # Dropdown for program selection when location is "India"
    program = st.selectbox("Choose a Program:", ["200HR", "300HR"])
