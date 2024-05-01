import streamlit as st
#import pastream
import pandas as pd
#import matplotlib.pyplot as plt

st.set_page_config(layout='wide', page_title='Players Analysis')

data = pd.read_csv('ipl_deliveries.csv')
matches = pd.read_csv('IPL_Matches_2008_2022.csv')

def player_details(player):

    played_matches = data[(data['batter'] == player) | (data['bowler'] == player)]
    total = played_matches['ID'].nunique()

    as_batsman = data[data['batter'] == player]

    total_runs = as_batsman['batsman_run'].sum()
    max_runs_as_batsman = str(as_batsman.groupby('ID')['batsman_run'].sum().sort_values(ascending=False).iloc[0])
    batter = as_batsman.groupby('ID', as_index=False)['batsman_run'].sum()
    half_centuries = batter[(batter['batsman_run'] >= 50) & (batter['batsman_run'] < 100)].shape[0]
    centuries = batter[batter['batsman_run'] >= 100].shape[0]
    fifty_hundred = f'{half_centuries}/{centuries}'

    legal_balls_data = as_batsman[as_batsman['extra_type'].isna()].groupby(['ID', 'batter'], as_index=False)
    legal_balls_faced = legal_balls_data.agg({'batsman_run': 'sum', 'ballnumber': 'count'})
    legal_balls_faced['strike_rate'] = legal_balls_faced['batsman_run'] / legal_balls_faced['ballnumber'] * 100
    season_wise_batsman_data = pd.merge(matches[['ID', 'Season']], legal_balls_faced, how='right', on='ID')
    strike_rates = season_wise_batsman_data.groupby('Season', as_index=False)['strike_rate'].mean().sort_values('Season')

    as_bowler = data[data['bowler'] == player]
    bowls = as_bowler.groupby('ID', as_index=False)['ballnumber'].max()
    overs_bowled = int(round((bowls['ballnumber'].sum()/6*10).astype(int)/10, 0))
    total_wickets = as_bowler['isWicketDelivery'].sum()
    max_wickets = as_bowler.groupby('ID')['isWicketDelivery'].sum().sort_values(ascending=False).iloc[0]

    cl1, cl2, cl3, cl4 = st.columns(4)

    with cl1:
        st.metric('Matches Played',str(total))
        st.metric('Overs bowled', str(overs_bowled))

    with cl2:
        st.metric('Total runs as a batsman', str(total_runs))
        st.metric('Total wickets as a bowler', str(total_wickets))

    with cl3:
        st.metric('Highest score as a batsman', str(max_runs_as_batsman))
        st.metric('Max wickets in a match', str(max_wickets))

    with cl4:
        st.metric('50s/100s', fifty_hundred)


    st.write(strike_rates)

st.sidebar.title('Player Analysis')
selected = st.sidebar.selectbox('Select one', ['Overall Analysis', 'Player'])
if selected == 'Overall Analysis':
    st.title('Overall Analysis')
    st.dataframe(data.describe())
else:
    player = st.sidebar.selectbox('Select Player',(sorted(data['batter'].sort_values(ascending=False).unique().tolist())))
    btn1 = st.sidebar.button('Show Player Details')
    if btn1:
        st.title(player)
        player_details(player)