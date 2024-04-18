import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta

st.set_page_config(layout="wide")

# Load your dataset
@st.cache_data
def load_data():
    df = pd.read_csv('data/dataset.csv')
    df['Date'] = pd.date_range(start='2024-01-01', end='2024-02-01')

    print(df.shape)
    return df

df = load_data()

# Creating sidebar with filters
st.sidebar.header("Filters:")

timeframes = ['1d', '7d', '1M']

st.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: center;} </style>', unsafe_allow_html=True)
selected_timeframe = st.sidebar.radio("Choose Timeframe", timeframes, index=0, key="timeframe")

# Options
social_options = ['X', 'TG', 'Website', 'LinkTree']
kol_options = ['Token Holders', 'NCDT/USDT']
token_options = ['NCDT/USDT', 'NCDT/BTC', 'NCDT/ETH']

# Displaying filters in sidebar
social_filter = st.sidebar.multiselect("Social Chart:", options=social_options, default=social_options)
col1, col2 = st.sidebar.columns(2)
with col1:
    kol_option = st.radio('Choose a KOL:', ['X', 'YT'])
with col2:
    kol_filter = st.multiselect("KOL Chart:", options=kol_options, default=kol_options)
token_filter = st.sidebar.multiselect("Token Chart:", options=token_options, default=['NCDT/USDT'])

# Social Metrics
social_metrics = []
if 'X' in social_filter:
    for metric in ['X Followers', 'X Views', 'X Tweets', 'X Likes', 'X Retweets', 'X Comments']:
        social_metrics.append(metric)
if 'TG' in social_filter:
    for metric in ['TG Group Members', 'TG Group Messages', 'TG Channel Members', 'TG Channel Posts', 'TG Channel Views']:
        social_metrics.append(metric)
if 'Website' in social_filter:
    for metric in ['Web Users', 'Web New Users', 'Web Time', 'Web Clicks']:
        social_metrics.append(metric)
if 'LinkTree' in social_filter:
    for metric in ['LinkTree Clicks', 'LinkTree Views', 'LinkTree CTR']:
        social_metrics.append(metric)

# KOL Metric
if kol_option == 'X':
    kol_column = 'KOL Budget X'
elif kol_option == 'YT':
    kol_column = 'KOL Budget YT'


# Specify dataframes
social_df = df[['Date'] + social_metrics]
kol_df = df[['KOL Budget X', 'KOL Budget YT'] + kol_filter]
token_df = df[['Date'] + token_filter]

if selected_timeframe == '1d':
    social_tf_df = social_df
    kol_tf_df = kol_df
    token_tf_df = token_df
elif selected_timeframe == '7d':
    social_tf_df = social_df.iloc[::7]
    kol_tf_df = kol_df.iloc[::7]
    token_tf_df = token_df.iloc[::7]
elif selected_timeframe == '1M':
    social_tf_df = social_df.iloc[::30]
    kol_tf_df = kol_df.iloc[::30]
    token_tf_df = token_df.iloc[::30]

# Social Chart
social_melted_df = pd.melt(social_tf_df, id_vars=['Date'], value_vars=social_metrics, var_name='Social', value_name='Value')
social_fig = px.line(social_melted_df, x='Date', y='Value', color='Social', title='Social Metrics Over Time')

# KOL Chart
kol_melted_df = pd.melt(kol_tf_df, id_vars=[kol_column], value_vars=kol_filter, var_name='KOL', value_name='Value')
kol_fig = px.line(kol_melted_df, x=kol_column, y='Value', color='KOL', title='KOL Metrics')

# Tokens Chart
token_melted_df = pd.melt(token_tf_df, id_vars=['Date'], value_vars=token_df, var_name='Tokens', value_name='Value')
token_fig = px.line(token_melted_df, x='Date', y='Value', color='Tokens', title='Tokens Price Over Time')

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(social_fig, use_container_width=True)
with col2:
    st.plotly_chart(kol_fig, use_container_width=True)
st.plotly_chart(token_fig, use_container_width=True)
