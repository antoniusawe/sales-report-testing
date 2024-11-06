import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
from datetime import datetime
from datetime import timedelta

# Sidebar dropdown for location
location = st.sidebar.selectbox("Choose a Location:", ["Bali", "India"])
