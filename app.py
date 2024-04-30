import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

@st.cache_data
def load_data():
    stats_df = pd.read_csv('data/dataset.csv')
    stats_df['Date'] = stats_df['Date'].apply(lambda x: datetime.strptime(f"2024-{x}", "%Y-%d/%m"))
    stats_df['X Views AVG'] = stats_df['X Views'] // stats_df['X Tweets']
    stats_df['X Likes AVG'] = stats_df['X Likes'] // stats_df['X Tweets']
    stats_df['X Retweets AVG'] = stats_df['X Retweets'] // stats_df['X Tweets']
    stats_df['X Comments AVG'] = stats_df['X Comments'] // stats_df['X Tweets']
    stats_df['TG Channel Views AVG'] = stats_df['TG Channel Views'] // stats_df['TG Channel Posts']
    stats_df = stats_df.drop(columns=['X Tweets', 'TG Channel Posts'])

    ncdt_usdt_df = pd.read_csv('data/ncdt-usd-max.csv')
    ncdt_usdt_df['snapped_at'] = pd.to_datetime(ncdt_usdt_df['snapped_at'])
    ncdt_usdt_df['snapped_at'] = ncdt_usdt_df['snapped_at'].apply(lambda x: x.strftime("%Y-%m-%d"))

    eth_usdt_df = pd.read_csv('data/eth-usd-max.csv')
    eth_usdt_df['snapped_at'] = pd.to_datetime(eth_usdt_df['snapped_at'])
    eth_usdt_df['snapped_at'] = eth_usdt_df['snapped_at'].apply(lambda x: x.strftime("%Y-%m-%d"))

    btc_usdt_df = pd.read_csv('data/btc-usd-max.csv')
    btc_usdt_df['snapped_at'] = pd.to_datetime(btc_usdt_df['snapped_at'])
    btc_usdt_df['snapped_at'] = btc_usdt_df['snapped_at'].apply(lambda x: x.strftime("%Y-%m-%d"))

    ncdt_price_df = ncdt_usdt_df.rename(columns={'price': 'NCDT/USDT', 'market_cap': 'MarketCap', 'total_volume': 'Volume'})

    eth_usdt_df = eth_usdt_df[eth_usdt_df['snapped_at'] >= ncdt_price_df['snapped_at'].min()][['snapped_at', 'price']]
    ncdt_price_df = pd.merge(ncdt_price_df, eth_usdt_df, on='snapped_at', how='outer')
    ncdt_price_df = ncdt_price_df.rename(columns={'price': 'ETH/USDT'})

    btc_usdt_df = btc_usdt_df[btc_usdt_df['snapped_at'] >= ncdt_price_df['snapped_at'].min()][['snapped_at', 'price']]
    ncdt_price_df = pd.merge(ncdt_price_df, btc_usdt_df, on='snapped_at', how='outer')
    ncdt_price_df = ncdt_price_df.rename(columns={'snapped_at': 'Date', 'price': 'BTC/USDT'})

    ncdt_price_df['NCDT/ETH'] = ncdt_price_df['NCDT/USDT'] / ncdt_price_df['ETH/USDT']
    ncdt_price_df['NCDT/BTC'] = ncdt_price_df['NCDT/USDT'] / ncdt_price_df['BTC/USDT']
    ncdt_price_df = ncdt_price_df[['Date', 'NCDT/USDT', 'NCDT/ETH', 'NCDT/BTC', 'MarketCap', 'Volume']]
    ncdt_price_df = ncdt_price_df.dropna(subset=['NCDT/USDT', 'MarketCap', 'Volume'], how='all')

    ncdt_price_df['NCDT/USDT'] = ncdt_price_df['NCDT/USDT'].apply(lambda x: round(x, 2))
    ncdt_price_df['Date'] = pd.to_datetime(ncdt_price_df['Date'])

    return stats_df, ncdt_price_df

def scale_values(group, floor=5, ceil=95):
    min_value = group.min()
    max_value = group.max()
    if min_value != max_value:
        scaled_values = ((group - min_value) / (max_value - min_value)) * (ceil - floor) + floor
    else:
        scaled_values = group / max_value * 50

    return scaled_values

def main():
    st.set_page_config(layout="wide")
    stats_df, ncdt_price_df = load_data()

    # Splitted columns in stats_df
    x_columns = ['X Followers', 'X Views AVG', 'X Likes AVG', 'X Retweets AVG', 'X Comments AVG']
    tg_colums = ['TG Group Members', 'TG Group Messages', 'TG Channel Members', 'TG Channel Views AVG']
    web_columns = ['Web Users', 'Web New Users', 'Web Time', 'Web Clicks']
    linktree_columns = ['LinkTree Clicks', 'LinkTree Views', 'LinkTree CTR']
    kol_columns = ['KOL Budget X', 'KOL Budget YT']

    # Creating sidebar with filters
    st.sidebar.header("Filters:")

    # Options
    timeframes = ['1d', '7d', '1M', '3M', '1Y']
    kol_options_xaxis = ['X', 'YT']
    kol_options_yaxis = ['Holders', 'Price']
    token_options = ['NCDT/USDT', 'NCDT/ETH', 'NCDT/BTC']

    # Selecting timeframe option
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: center;} </style>', unsafe_allow_html=True)
    selected_timeframe = st.sidebar.radio("Choose a Timeframe:", timeframes, index=0, key="timeframe")

    # Date range slider option
    min_ncdt_price_date = ncdt_price_df['Date'].min()
    max_ncdt_price_date = ncdt_price_df['Date'].max()
    thirtieth_from_end = ncdt_price_df.iloc[-90]['Date'] if ncdt_price_df.shape[0] > 90 else min_ncdt_price_date  # get only last 90 days
    start_date_range, end_date_range = st.sidebar.select_slider(
        label='Choose a Date Range:',
        options=pd.date_range(min_ncdt_price_date, max_ncdt_price_date, freq='D'),
        value=(thirtieth_from_end, max_ncdt_price_date),
        format_func=lambda x: '',
        label_visibility='visible'
    )

    # Date range two dates text
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.write(f'<div style="text-align: center;">{start_date_range.strftime("%d-%m-%Y")}</div>', unsafe_allow_html=True)
    with col2:
        st.write(f'<div style="text-align: center;">{end_date_range.strftime("%d-%m-%Y")}</div>', unsafe_allow_html=True)
    st.sidebar.write("")

    # KOL options
    col1, col2 = st.sidebar.columns(2)
    with col1:
        kol_option = st.radio('Choose a KOL:', kol_options_xaxis)
        kol_column = 'KOL Budget X' if kol_option == 'X' else 'KOL Budget YT'
    with col2:
        kol_raw_filter = st.multiselect("KOL Chart:", options=kol_options_yaxis, default=kol_options_yaxis)
        kol_filter = []
        if 'Holders' in kol_raw_filter:
            kol_filter.append('Token Holders')
        if 'Price' in kol_raw_filter:
            kol_filter.append('NCDT/USDT')

    # Token option
    token_filter = st.sidebar.selectbox("Token Chart:", options=token_options, index=0)

    # Specify dataframes
    stats_range_df = stats_df[(stats_df['Date'] >= start_date_range) & (stats_df['Date'] <= end_date_range)]
    ncdt_price_range_df = ncdt_price_df[(ncdt_price_df['Date'] >= start_date_range) & (ncdt_price_df['Date'] <= end_date_range)]
    social_df = stats_df[['Date'] + x_columns + tg_colums + web_columns + linktree_columns]
    kol_df = pd.merge(stats_df[['Date', 'Token Holders'] + kol_columns], ncdt_price_df[['Date', 'NCDT/USDT']], on='Date', how='outer')[kol_columns + kol_filter]
    token_df = ncdt_price_range_df[['Date', token_filter]]

    if selected_timeframe == '1d':
        social_tf_df = social_df
        kol_tf_df = kol_df
        token_tf_df = token_df
    elif selected_timeframe == '7d':
        # social_tf_df = social_df.iloc[::7]
        # kol_tf_df = kol_df.iloc[::7]
        social_tf_df = social_df
        kol_tf_df = kol_df
        token_tf_df = token_df.iloc[::7]
    elif selected_timeframe == '1M':
        # social_tf_df = social_df.iloc[::30]
        # kol_tf_df = kol_df.iloc[::30]
        social_tf_df = social_df
        kol_tf_df = kol_df
        token_tf_df = token_df.iloc[::30]
    elif selected_timeframe == '3M':
        # social_tf_df = social_df.iloc[::90]
        # kol_tf_df = kol_df.iloc[::90]
        social_tf_df = social_df
        kol_tf_df = kol_df
        token_tf_df = token_df.iloc[::90]
    elif selected_timeframe == '1Y':
        # social_tf_df = social_df.iloc[::365]
        # kol_tf_df = kol_df.iloc[::365]
        social_tf_df = social_df
        kol_tf_df = kol_df
        token_tf_df = token_df.iloc[::365]

    # X Chart
    x_melted_df = pd.melt(social_tf_df, id_vars='Date', value_vars=x_columns, var_name='X', value_name='Value')
    x_melted_df['Original Value'] = x_melted_df['Value']
    x_melted_df['Scaled Value'] = x_melted_df.groupby('X')['Value'].transform(scale_values)
    x_fig = px.line(x_melted_df, x='Date', y='Scaled Value', color='X', title='X Metrics Over Time', hover_data={'Original Value': True, 'Scaled Value': False})

    # TG Chart
    tg_melted_df = pd.melt(social_tf_df, id_vars='Date', value_vars=tg_colums, var_name='TG', value_name='Value')
    tg_melted_df['Original Value'] = tg_melted_df['Value']
    tg_melted_df['Scaled Value'] = tg_melted_df.groupby('TG')['Value'].transform(scale_values)
    tg_fig = px.line(tg_melted_df, x='Date', y='Scaled Value', color='TG', title='Telegram Metrics Over Time', hover_data={'Original Value': True, 'Scaled Value': False})

    # Web Chart
    web_melted_df = pd.melt(social_tf_df, id_vars='Date', value_vars=web_columns, var_name='Website', value_name='Value')
    web_melted_df['Original Value'] = web_melted_df['Value']
    web_melted_df['Scaled Value'] = web_melted_df.groupby('Website')['Value'].transform(scale_values)
    web_fig = px.line(web_melted_df, x='Date', y='Scaled Value', color='Website', title='Website Metrics Over Time', hover_data={'Original Value': True, 'Scaled Value': False})

    # TG Chart
    linktree_melted_df = pd.melt(social_tf_df, id_vars='Date', value_vars=linktree_columns, var_name='LinkTree', value_name='Value')
    linktree_melted_df['Original Value'] = linktree_melted_df['Value']
    linktree_melted_df['Scaled Value'] = linktree_melted_df.groupby('LinkTree')['Value'].transform(scale_values)
    linktree_fig = px.line(linktree_melted_df, x='Date', y='Scaled Value', color='LinkTree', title='LinkTree Metrics Over Time', hover_data={'Original Value': True, 'Scaled Value': False})

    # KOL Chart
    kol_melted_df = pd.melt(kol_tf_df, id_vars=kol_column, value_vars=kol_filter, var_name='KOL', value_name='Value')
    kol_size_df = kol_melted_df.groupby([kol_column, 'Value', 'KOL']).size().reset_index(name='Size')
    kol_size_df['Original Value'] = kol_size_df['Value']
    kol_size_df['Scaled Value'] = kol_size_df.groupby('KOL')['Value'].transform(scale_values)
    kol_size_df['Formatted Size'] = kol_size_df['Size'].apply(lambda x: f'<b>Size:</b> {x}')
    kol_fig = px.scatter(kol_size_df, x=kol_column, y='Scaled Value', color='KOL', size='Size', title='KOL Metrics', hover_name='Formatted Size', hover_data={'Original Value': True, 'Scaled Value': False, 'KOL': True, 'Size': False}, log_x=True, size_max=20)

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

if __name__ == '__main__':
    main()