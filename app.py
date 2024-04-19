import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta
from datetime import datetime


st.set_page_config(layout="wide")

# Load your dataset
@st.cache_data
def load_data():
    df = pd.read_csv('data/dataset.csv')
    df['Date'] = pd.date_range(start='2023-01-01', periods=df.shape[0], freq='D')
    df['Date'] = pd.to_datetime(df['Date'])

    return df

df = load_data()

# Creating sidebar with filters
st.sidebar.header("Filters:")

# Options
timeframes = ['1d', '7d', '1M', '3M', '1Y']
kol_options = ['Token Holders', 'NCDT/USDT']
token_options = ['NCDT/USDT', 'BTC/NCDT', 'ETH/NCDT']

x_columns = ['X Followers', 'X Views', 'X Tweets', 'X Likes', 'X Retweets', 'X Comments']
tg_colums = ['TG Group Members', 'TG Group Messages', 'TG Channel Members', 'TG Channel Posts', 'TG Channel Views']
web_columns = ['Web Users', 'Web New Users', 'Web Time', 'Web Clicks']
linktree_columns = ['LinkTree Clicks', 'LinkTree Views', 'LinkTree CTR']

# Displaying filters in sidebar
st.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: center;} </style>', unsafe_allow_html=True)
selected_timeframe = st.sidebar.radio("Choose a Timeframe:", timeframes, index=0, key="timeframe")

thirtieth_from_end = df.iloc[-90]['Date']
date_range = st.sidebar.select_slider(
    'Choose a Time Range:',
    options=pd.date_range(df['Date'].min(), df['Date'].max(), freq='D'),
    value=(thirtieth_from_end, df['Date'].max()),
    format_func=lambda x: '',
)
start_date_range, end_date_range = date_range

col1, col2 = st.sidebar.columns(2)
with col1:
    st.write(f'<div style="text-align: center;">{start_date_range.strftime("%d-%m-%Y")}</div>', unsafe_allow_html=True)
with col2:
    st.write(f'<div style="text-align: center;">{end_date_range.strftime("%d-%m-%Y")}</div>', unsafe_allow_html=True)

st.sidebar.write("")

col1, col2 = st.sidebar.columns(2)
with col1:
    kol_option = st.radio('Choose a KOL:', ['X', 'YT'])
with col2:
    kol_filter = st.multiselect("KOL Chart:", options=kol_options, default=kol_options)
token_filter = st.sidebar.selectbox("Token Chart:", options=token_options, index=0)

# KOL Metric
if kol_option == 'X':
    kol_column = 'KOL Budget X'
elif kol_option == 'YT':
    kol_column = 'KOL Budget YT'

# Specify dataframes
df = df[(df['Date'] >= start_date_range) & (df['Date'] <= end_date_range)]
social_df = df[['Date'] + x_columns + tg_colums + web_columns + linktree_columns]
kol_df = df[['KOL Budget X', 'KOL Budget YT'] + kol_filter]
token_df = df[['Date', token_filter]]

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
elif selected_timeframe == '3M':
    social_tf_df = social_df.iloc[::90]
    kol_tf_df = kol_df.iloc[::90]
    token_tf_df = token_df.iloc[::90]
elif selected_timeframe == '1Y':
    social_tf_df = social_df.iloc[::365]
    kol_tf_df = kol_df.iloc[::365]
    token_tf_df = token_df.iloc[::365]

# X Chart
x_melted_df = pd.melt(social_tf_df, id_vars='Date', value_vars=x_columns, var_name='X', value_name='Value')
x_fig = px.line(x_melted_df, x='Date', y='Value', color='X', title='X Metrics Over Time')

# TG Chart
tg_melted_df = pd.melt(social_tf_df, id_vars='Date', value_vars=tg_colums, var_name='TG', value_name='Value')
tg_fig = px.line(tg_melted_df, x='Date', y='Value', color='TG', title='Telegram Metrics Over Time')

# Web Chart
web_melted_df = pd.melt(social_tf_df, id_vars='Date', value_vars=web_columns, var_name='Website', value_name='Value')
web_fig = px.line(web_melted_df, x='Date', y='Value', color='Website', title='Website Metrics Over Time')

# TG Chart
linktree_melted_df = pd.melt(social_tf_df, id_vars='Date', value_vars=linktree_columns, var_name='LinkTree', value_name='Value')
linktree_fig = px.line(linktree_melted_df, x='Date', y='Value', color='LinkTree', title='LinkTree Metrics Over Time')

# KOL Chart
kol_melted_df = pd.melt(kol_tf_df, id_vars=kol_column, value_vars=kol_filter, var_name='KOL', value_name='Value')
size_df = kol_melted_df.groupby([kol_column, 'Value', 'KOL']).size().reset_index(name='Size')
kol_fig = px.scatter(size_df, x=kol_column, y='Value', color='KOL', size='Size', title='KOL Metrics', hover_name='KOL', log_x=True, size_max=20)

# Token Chart
token_melted_df = pd.melt(token_tf_df, id_vars='Date', value_vars=token_df, var_name='Tokens', value_name='Value')
token_fig = px.line(token_melted_df, x='Date', y='Value', color='Tokens', title='Tokens Price Over Time')

# Plotting
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(x_fig, use_container_width=True, scroll_zoom='x')
with col2:
    st.plotly_chart(tg_fig, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(web_fig, use_container_width=True)
with col2:
    st.plotly_chart(linktree_fig, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(kol_fig, use_container_width=True)
with col2:
    st.plotly_chart(token_fig, use_container_width=True)
