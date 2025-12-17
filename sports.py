import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

st.set_page_config(page_title="IPL Data Analysis", layout="wide")

st.title("📊 IPL Data Analysis Dashboard")
st.markdown("""
<div style='font-size:16px;'>Upload your IPL match and delivery CSV files in the sidebar to explore statistics and visualizations.</div>
""", unsafe_allow_html=True)


st.sidebar.header("Data Upload")
st.sidebar.markdown("""
**Instructions:**
1. Upload the IPL Matches CSV file (match-level data).
2. Upload the Deliveries CSV file (ball-by-ball data).
""")
match_file = st.sidebar.file_uploader("Upload IPL Matches CSV", type="csv")
delivery_file = st.sidebar.file_uploader("Upload Deliveries CSV", type="csv")

if match_file and delivery_file:
    df = pd.read_csv(match_file)
    deliveries = pd.read_csv(delivery_file)
    df.columns = df.columns.str.strip().str.lower()
    deliveries.columns = deliveries.columns.str.strip().str.lower()

    st.write('Deliveries DataFrame columns:', deliveries.columns.tolist())

    df.drop_duplicates(inplace=True)
    df.fillna(0, inplace=True)
    deliveries.drop_duplicates(inplace=True)
    num_cols = deliveries.select_dtypes(include=['number']).columns
    deliveries[num_cols] = deliveries[num_cols].fillna(0)
    required_cols = ['batsman', 'batsman_runs']
    missing = [c for c in required_cols if c not in deliveries.columns]
    if missing:
        st.error(f"Deliveries file is missing required columns: {missing}. Available columns: {deliveries.columns.tolist()}")
        st.stop()

    with st.expander("First 5 Rows of IPL Matches Data", expanded=False):
        st.dataframe(df.head())

    with st.expander("Dataset Info", expanded=False):
        buffer = io.StringIO()
        df.info(buf=buffer)
        s = buffer.getvalue()
        st.text(s)

    st.sidebar.header("Navigation")
    section = st.sidebar.radio(
        "Go to section:",
        (
            "Dashboard Overview",
            "Player Statistics",
            "Team Analysis",
            "Season-wise Trends",
            "Bowler Analysis",
            "Match Outcome Insights",
            "Interactive Visualizations",
            "Downloadable Reports",
            "Advanced Analytics"
        )
    )

    if section == "Dashboard Overview":
      
        top_runs = deliveries.groupby("batsman")["batsman_runs"].sum().sort_values(ascending=False).head(10)
        st.subheader("🏏 Top 10 Run Scorers")
        fig, ax = plt.subplots(figsize=(10,5))
        top_runs.plot(kind="bar", color="orange", ax=ax)
        ax.set_ylabel("Total Runs")
        ax.set_xlabel("Batsman")
        ax.set_title("Top 10 Run Scorers")
        st.pyplot(fig)

        top_teams = df["winner"].value_counts().head(10)
        st.subheader("🏆 Top Winning Teams")
        fig, ax = plt.subplots(figsize=(10,5))
        sns.barplot(x=top_teams.index, y=top_teams.values, palette="viridis", ax=ax)
        ax.set_ylabel("Matches Won")
        ax.set_xlabel("Team")
        ax.set_title("Top Winning Teams")
        plt.xticks(rotation=45)
        st.pyplot(fig)

        st.subheader("🎲 Toss Decision Distribution")
        fig, ax = plt.subplots(figsize=(6,4))
        sns.countplot(x="toss_decision", data=df, palette="Set2", ax=ax)
        ax.set_title("Toss Decision Distribution")
        st.pyplot(fig)

        st.subheader("🎯 Effect of Toss Decision on Match Outcome")
        fig, ax = plt.subplots(figsize=(10,6))
        sns.countplot(x="toss_decision", hue="winner", data=df, palette="coolwarm", ax=ax)
        ax.set_title("Effect of Toss Decision on Match Outcome")
        plt.xticks(rotation=45)
        st.pyplot(fig)

        if "over" in deliveries.columns and "total_runs" in deliveries.columns:
            avg_runs_over = deliveries.groupby("over")["total_runs"].mean()
            st.subheader("📈 Average Runs Per Over")
            fig, ax = plt.subplots(figsize=(8,4))
            avg_runs_over.plot(marker="o", color="green", ax=ax)
            ax.set_xlabel("Over")
            ax.set_ylabel("Average Runs")
            ax.set_title("Average Runs Per Over")
            ax.grid(True)
            st.pyplot(fig)

        st.subheader("📌 Key Insights")
        st.write(f"Total Matches in Dataset: {df.shape[0]}")
        st.write(f"Most Successful Team: {df['winner'].mode()[0]}")
        st.write(f"Top Batsman: {top_runs.index[0]} with {top_runs.iloc[0]} runs")

    elif section == "Player Statistics":
        st.header("Player Statistics")
        player_list = sorted(deliveries['batsman'].unique())
        selected_player = st.selectbox("Select a player:", player_list)
        player_data = deliveries[deliveries['batsman'] == selected_player]
        total_runs = player_data['batsman_runs'].sum()
        balls_faced = player_data.shape[0]
        outs = player_data['player_dismissed'].eq(selected_player).sum()
        average = total_runs / outs if outs > 0 else total_runs
        strike_rate = (total_runs / balls_faced) * 100 if balls_faced > 0 else 0

        st.markdown(f"**Total Runs:** {total_runs}")
        st.markdown(f"**Balls Faced:** {balls_faced}")
        st.markdown(f"**Average:** {average:.2f}")
        st.markdown(f"**Strike Rate:** {strike_rate:.2f}")

    elif section == "Team Analysis":
        st.header("Team Analysis")
        team_list = sorted(df['team1'].unique())
        selected_team = st.selectbox("Select a team:", team_list)
        matches_played = df[(df['team1'] == selected_team) | (df['team2'] == selected_team)]
        total_matches = matches_played.shape[0]
        
        total_wins = df['winner'].eq(selected_team).sum()
        win_pct = (total_wins / total_matches * 100) if total_matches > 0 else 0
        st.markdown(f"**Total Matches Played:** {total_matches}")
        st.markdown(f"**Total Wins:** {total_wins}")
        st.markdown(f"**Win Percentage:** {win_pct:.2f}%")

        st.subheader("Head-to-Head Wins vs Other Teams")
        head_to_head = df[df['winner'] == selected_team]['loser'] if 'loser' in df.columns else df[df['winner'] == selected_team]['team2']
        if 'loser' in df.columns:
            h2h_counts = head_to_head.value_counts().reset_index()
            h2h_counts.columns = ['Opponent', 'Wins Against']
        else:
            def get_opponent(row):
                if row['winner'] == row['team1']:
                    return row['team2']
                else:
                    return row['team1']
            h2h = df[df['winner'] == selected_team].copy()
            h2h['Opponent'] = h2h.apply(get_opponent, axis=1)
            h2h_counts = h2h['Opponent'].value_counts().reset_index()
            h2h_counts.columns = ['Opponent', 'Wins Against']
        st.dataframe(h2h_counts)

    elif section == "Season-wise Trends":
        st.header("Season-wise Trends")
        if 'season' in df.columns:
            season_list = sorted(df['season'].unique())
            selected_season = st.selectbox("Select a season:", season_list)
            season_df = df[df['season'] == selected_season]
            st.markdown(f"**Total Matches:** {season_df.shape[0]}")
            if 'winner' in season_df.columns:
                top_team = season_df['winner'].mode()[0]
                st.markdown(f"**Most Successful Team:** {top_team}")
            if 'id' in season_df.columns and 'batsman' in deliveries.columns:
                match_ids = season_df['id'].unique()
                season_deliveries = deliveries[deliveries['match_id'].isin(match_ids)]
                top_batsman = season_deliveries.groupby('batsman')['batsman_runs'].sum().sort_values(ascending=False).head(1)
                if not top_batsman.empty:
                    st.markdown(f"**Top Run Scorer:** {top_batsman.index[0]} ({top_batsman.iloc[0]} runs)")
        else:
            st.info("Season data not available in matches file.")

    elif section == "Bowler Analysis":
        st.header("Bowler Analysis")
        bowler_list = sorted(deliveries['bowler'].unique())
        selected_bowler = st.selectbox("Select a bowler:", bowler_list)
        bowler_data = deliveries[deliveries['bowler'] == selected_bowler]
        wickets = bowler_data['player_dismissed'].notna().sum()
        balls = bowler_data.shape[0]
        runs = bowler_data['total_runs'].sum()
        overs = balls // 6 + (balls % 6) / 6
        economy = (runs / overs) if overs > 0 else 0
        st.markdown(f"**Total Wickets:** {wickets}")
        st.markdown(f"**Economy Rate:** {economy:.2f}")

        if 'match_id' in bowler_data.columns:
            best = bowler_data.groupby('match_id')['player_dismissed'].apply(lambda x: x.notna().sum()).max()
            st.markdown(f"**Best Bowling (Wickets in a Match):** {best}")

    elif section == "Match Outcome Insights":
        st.header("Match Outcome Insights")
        win_by_runs = df[df['win_by_runs'] > 0].shape[0] if 'win_by_runs' in df.columns else 0
        win_by_wickets = df[df['win_by_wickets'] > 0].shape[0] if 'win_by_wickets' in df.columns else 0
        ties = df[df['result'].str.lower() == 'tie'].shape[0] if 'result' in df.columns else 0
        no_result = df[df['result'].str.lower() == 'no result'].shape[0] if 'result' in df.columns else 0
        st.markdown(f"**Matches Won by Runs:** {win_by_runs}")
        st.markdown(f"**Matches Won by Wickets:** {win_by_wickets}")
        st.markdown(f"**Tied Matches:** {ties}")
        st.markdown(f"**No Result Matches:** {no_result}")

    elif section == "Interactive Visualizations":
        st.header("Interactive Visualizations")
        st.markdown("Select a team and season to view their run distribution:")
        team_list = sorted(df['team1'].unique())
        season_list = sorted(df['season'].unique()) if 'season' in df.columns else []
        team = st.selectbox("Team:", team_list)
        season = st.selectbox("Season:", season_list) if season_list else None
        if season:
            match_ids = df[(df['season'] == season) & ((df['team1'] == team) | (df['team2'] == team))]['id'].unique()
            team_deliveries = deliveries[(deliveries['match_id'].isin(match_ids)) & (deliveries['batting_team'] == team)]
        else:
            team_deliveries = deliveries[deliveries['batting_team'] == team]
        if not team_deliveries.empty:
            runs_by_match = team_deliveries.groupby('match_id')['total_runs'].sum()
            st.bar_chart(runs_by_match)
        else:
            st.info("No data for selected filters.")

    elif section == "Downloadable Reports":
        st.header("Downloadable Reports")
        st.markdown("Download the IPL matches or deliveries data as CSV:")
        st.download_button("Download Matches CSV", df.to_csv(index=False), file_name="ipl_matches.csv")
        st.download_button("Download Deliveries CSV", deliveries.to_csv(index=False), file_name="deliveries.csv")

    elif section == "Advanced Analytics":
        st.header("Advanced Analytics")
        st.info("Predict match outcomes and advanced stats. [ML models can be added here].")

else:
    st.warning("Please upload both IPL Matches and Deliveries CSV files to continue.")