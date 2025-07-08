import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.database import get_database

st.title("📊 Progress Tracker")

if 'session_id' not in st.session_state:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())

try:
    db = get_database()
    db_loaded = True
except Exception as e:
    st.error(f"Database initialization failed: {e}")
    db_loaded = False

session_id = st.session_state.session_id

st.sidebar.markdown("### 🚀 Quick Actions")
if st.sidebar.button("📊 Add Sample Data"):
    if db_loaded:
        try:
            db.add_sample_data(session_id)
            st.sidebar.success("✅ Sample data added!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"❌ Error: {e}")
    else:
        st.sidebar.error("Database not available")

if st.sidebar.button("🗑️ Clear All Data"):
    if db_loaded:
        try:
            import sqlite3
            conn = sqlite3.connect(db.db_path)
            c = conn.cursor()
            c.execute("DELETE FROM progress WHERE session_id = ?", (session_id,))
            c.execute("DELETE FROM submissions WHERE session_id = ?", (session_id,))
            conn.commit()
            conn.close()
            st.sidebar.success("✅ Data cleared!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"❌ Error: {e}")

if db_loaded:
    try:
        progress_df = db.get_progress_data(session_id)
        user_stats = db.get_user_statistics(session_id)
    except Exception as e:
        st.error(f"Data retrieval error: {e}")
        progress_df = pd.DataFrame()
        user_stats = {}
else:
    progress_df = pd.DataFrame()
    user_stats = {}

if progress_df.empty:
    st.info("📊 No progress data yet. Click '📊 Add Sample Data' in sidebar to see demo!")
    st.subheader("🎯 What You'll See:")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### 📈 Charts & Visualizations
        - **Success Rate Over Time** - Track your improvement
        - **Problems by Category** - See which topics you've mastered  
        - **Skill Assessment Radar** - Visual skill mapping
        """)
    with col2:
        st.markdown("""
        ### 📊 Performance Metrics
        - **Total Problems Solved** - Your coding journey
        - **Success Rate Percentage** - Accuracy tracking
        - **Weekly Progress** - Recent activity
        - **Current Streak** - Consistency measurement
        """)
    st.subheader("📊 Sample Metrics Preview")
    sample_col1, sample_col2, sample_col3, sample_col4 = st.columns(4)
    with sample_col1:
        st.metric("Total Problems", "0", help="Problems you've solved")
    with sample_col2:
        st.metric("Success Rate", "0%", help="Your accuracy percentage")
    with sample_col3:
        st.metric("This Week", "0", help="Recent activity")
    with sample_col4:
        st.metric("Current Streak", "0", help="Consecutive days")
else:
    st.subheader("📈 Your Coding Progress")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Problems", user_stats.get('total_problems', 0))
    with col2:
        st.metric("Success Rate", f"{user_stats.get('success_rate', 0):.1f}%")
    with col3:
        st.metric("This Week", user_stats.get('this_week', 0))
    with col4:
        st.metric("Current Streak", user_stats.get('current_streak', 0))
    st.subheader("📈 Success Rate Over Time")
    if 'date' in progress_df.columns and 'success_rate' in progress_df.columns:
        try:
            fig = px.line(
                progress_df,
                x='date',
                y='success_rate',
                color='difficulty',
                title='Learning Progress Over Time',
                labels={'success_rate': 'Success Rate (%)', 'date': 'Date'}
            )
            fig.update_layout(xaxis_title="Date", yaxis_title="Success Rate (%)")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Chart error: {e}")
    else:
        st.warning("Required columns (date, success_rate) missing from progress data")
    st.subheader("📊 Problems Solved by Category")
    if 'topic' in progress_df.columns and 'problems_solved' in progress_df.columns:
        try:
            counts = progress_df.groupby('topic')['problems_solved'].sum().reset_index()
            if not counts.empty:
                fig2 = px.bar(
                    counts,
                    x='topic',
                    y='problems_solved',
                    title='Problems Solved by Topic',
                    labels={'problems_solved': 'Problems Solved', 'topic': 'Topic'}
                )
                fig2.update_xaxes(tickangle=45)
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No topic data available yet")
        except Exception as e:
            st.error(f"Bar chart error: {e}")
    st.subheader("⭐ Difficulty Distribution")
    if 'difficulty' in progress_df.columns:
        try:
            difficulty_counts = progress_df['difficulty'].value_counts().reset_index()
            difficulty_counts.columns = ['difficulty', 'count']
            fig3 = px.pie(
                difficulty_counts,
                values='count',
                names='difficulty',
                title='Problems by Difficulty Level'
            )
            st.plotly_chart(fig3, use_container_width=True)
        except Exception as e:
            st.error(f"Pie chart error: {e}")
    st.subheader("🎯 Topic Performance Radar")
    try:
        skill_data = progress_df.groupby('topic')['success_rate'].mean().reset_index()
        if not skill_data.empty:
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=skill_data['success_rate'].tolist(),
                theta=skill_data['topic'].tolist(),
                fill='toself',
                name='Success Rate',
                line_color='blue'
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )),
                showlegend=False,
                title="Topic Performance Overview"
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        else:
            st.info("Not enough data for radar chart")
    except Exception as e:
        st.error(f"Radar chart error: {e}")
    st.subheader("📝 Recent Activity")
    if len(progress_df) > 0:
        recent_data = progress_df.head(10)
        st.dataframe(recent_data, use_container_width=True)
    else:
        st.info("No recent activity to display")
    st.subheader("💡 Performance Insights")
    if len(progress_df) > 0:
        avg_success_rate = progress_df['success_rate'].mean()
        best_topic = progress_df.groupby('topic')['success_rate'].mean().idxmax()
        total_problems = progress_df['problems_solved'].sum()
        insight_col1, insight_col2 = st.columns(2)
        with insight_col1:
            st.info(f"🎯 **Average Success Rate**: {avg_success_rate:.1f}%")
            st.info(f"🏆 **Strongest Topic**: {best_topic}")
        with insight_col2:
            st.info(f"📊 **Total Problems**: {total_problems}")
            if avg_success_rate >= 80:
                st.success("🔥 **Excellent Performance!** Keep it up!")
            elif avg_success_rate >= 60:
                st.warning("📈 **Good Progress!** Focus on weak areas")
            else:
                st.error("💪 **Keep Practicing!** You're improving")

st.sidebar.markdown("### 📈 Quick Stats")
if user_stats:
    st.sidebar.metric("Problems Solved", user_stats.get('total_problems', 0))
    st.sidebar.metric("Success Rate", f"{user_stats.get('success_rate', 0):.1f}%")
    st.sidebar.metric("Avg Difficulty", user_stats.get('avg_difficulty', 'N/A'))
    total = user_stats.get('total_problems', 0)
    if total > 0:
        next_milestone = ((total // 10) + 1) * 10
        progress_to_milestone = (total % 10) / 10
        st.sidebar.metric("Next Milestone", f"{next_milestone} problems")
        st.sidebar.progress(progress_to_milestone)

st.sidebar.markdown("### 💡 Tips")
st.sidebar.markdown("""
- **Consistency** is key for improvement
- **Focus** on low-performing topics  
- **Challenge** yourself with harder problems
- **Review** mistakes to learn faster
""")
