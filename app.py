import streamlit as st
import pandas as pd
import plotly.express as px

# Load your dataset
@st.cache_data
def load_data():
    return pd.read_csv('data/dataset.csv')

df = load_data()

# Creating sidebar with filters
st.sidebar.header("Filters:")

social_options = ['TG gMembers', 'TG gMessages', 'TG cMembers', 'TG cPosts', 'TG cViews', 'X Followers', 'X Views', 'X Tweets', 'X Likes',
                  'X Retweets', 'X Comments']
web_options = ['Web Users', 'Web New Users', 'Web Time', 'Web Clicks', 'LinkTree Clicks', 'LinkTree Views', 'LinkTree CTR']
kol_options = ['KOL Budget X','KOL Budget YT']
tokens_options = ['BTC', 'ETH', 'USDT']

# Displaying 3 main filters in sidebar
social_filter = st.sidebar.multiselect("Social Chart:", options=social_options, default=social_options)
web_filter = st.sidebar.multiselect("Web Chart:", options=web_options, default=web_options)
kol_filter = st.sidebar.multiselect("KOL Chart:", options=kol_options, default=kol_options)
tokens_filter = st.sidebar.multiselect("Tokens Chart:", options=tokens_options, default=['USDT'])

filtered_df = df[['Date'] + social_filter + web_filter + kol_filter + tokens_filter]

# Social Chart
social_melted_df = pd.melt(filtered_df, id_vars=['Date'], value_vars=social_filter, var_name='Social', value_name='Value')
social_fig = px.line(social_melted_df, x='Date', y='Value', color='Social', title='Social Metrics Over Time')

# Web Chart
web_melted_df = pd.melt(filtered_df, id_vars=['Date'], value_vars=web_filter, var_name='Web', value_name='Value')
web_fig = px.line(web_melted_df, x='Date', y='Value', color='Web', title='Web Metrics Over Time')

# KOL Chart
kol_melted_df = pd.melt(filtered_df, id_vars=['Date'], value_vars=kol_filter, var_name='KOL', value_name='Value')
kol_fig = px.line(kol_melted_df, x='Date', y='Value', color='KOL', title='KOL Metrics Over Time')

# Tokens Chart
tokens_melted_df = pd.melt(filtered_df, id_vars=['Date'], value_vars=tokens_filter, var_name='Tokens', value_name='Value')
tokens_fig = px.line(tokens_melted_df, x='Date', y='Value', color='Tokens', title='Tokens Metrics Over Time')

st.plotly_chart(social_fig, use_container_width=True)
st.plotly_chart(web_fig, use_container_width=True)
st.plotly_chart(kol_fig, use_container_width=True)
st.plotly_chart(tokens_fig, use_container_width=True)