# pages/02_📝_Code_Analysis.py
import streamlit as st
import json
import pandas as pd
import uuid

from utils.code_analyzer import analyze_code
from utils.database import get_database
from utils.vector_store import get_vector_store
from utils.langchain_gemini_client import get_langchain_gemini_client

st.title("📝 Code Analysis with AI Mentor")

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

# UI: Input form
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📋 Submit Your Code")
    code_input = st.text_area(
        "Paste your Python/C++/Java solution here:",
        height=300,
        placeholder="Paste your code here..."
    )

with col2:
    st.subheader("📊 Problem Details")
    problem_name = st.text_input("Problem Name", placeholder="e.g., Two Sum")
    problem_url = st.text_input("Problem URL (optional)")
    analysis_mode = st.selectbox("Analysis Mode", ["Fast", "Balanced", "Comprehensive"])

# Analysis config
st.subheader("🔧 Analysis Options")
a1, a2, a3 = st.columns(3)
with a1: enable_pattern_detection = st.checkbox("🔍 Pattern Detection", value=True)
with a2: enable_complexity_analysis = st.checkbox("📊 Complexity Analysis", value=True)
with a3: enable_similarity_search = st.checkbox("🔗 Similar Solutions", value=True)

# 🧠 AI Reasoning Depth (Fixed for quality)
thinking_budget = 2048  # Always use max for full detailed output

# Load services
try:
    db = get_database()
    vector_store = get_vector_store()
    llm_client = get_langchain_gemini_client(analysis_mode=analysis_mode)
    services_loaded = True
except Exception as e:
    st.error(f"❌ Error loading services: {e}")
    services_loaded = False

# MAIN BUTTON
if st.button("🚀 Analyze Code", type="primary", use_container_width=True):
    if not services_loaded:
        st.error("❌ Services failed to load. Refresh and try again.")
        st.stop()

    if not code_input.strip() or not problem_name.strip():
        st.error("❌ Code and Problem Name are required!")
        st.stop()

    st.info(f"🔍 Analyzing: **{problem_name}**")
    progress_bar = st.progress(0)
    status = st.empty()

    try:
        # Step 1: Technical analysis
        status.text("Step 1/4: Technical analysis...")
        progress_bar.progress(25)
        technical_analysis = analyze_code(code_input)

        if 'error' in technical_analysis:
            st.warning(f"⚠️ Static analysis failed: {technical_analysis['error']}")
            technical_analysis.update({
                'complexity': {'time_complexity': 'O(?)', 'space_complexity': 'O(?)'},
                'patterns': ['general_algorithm'],
                'quality_metrics': {'lines': len(code_input.splitlines()), 'characters': len(code_input)}
            })

        # Step 2: Pattern Detection
        pattern_analysis = ""
        if enable_pattern_detection:
            status.text("Step 2/4: Detecting patterns...")
            progress_bar.progress(50)
            try:
                patterns = technical_analysis.get('patterns', [])
                if patterns:
                    pattern_analysis = llm_client.identify_code_patterns(code_input, patterns)
                else:
                    pattern_analysis = "⚠️ No patterns detected in static analysis."
            except Exception as e:
                st.warning(f"⚠️ Pattern analysis failed: {e}")
                pattern_analysis = f"⚠️ Could not analyze patterns. Exception: {str(e)}"

        # Step 3: Similarity Search
        similar_solutions = []
        if enable_similarity_search:
            status.text("Step 3/4: Finding similar solutions...")
            progress_bar.progress(75)
            try:
                similar_solutions = vector_store.find_similar_patterns(code_input, k=3)
            except Exception as e:
                st.warning(f"Similarity search failed: {e}")

        # Step 4: AI Feedback
        status.text("Step 4/4: Generating AI feedback...")
        progress_bar.progress(90)

        try:
            ai_response = llm_client.analyze_code_with_ai(
                code=code_input,
                problem_name=problem_name,
                analysis=technical_analysis
            )

            try:
                ai_result = json.loads(ai_response)
                ai_feedback = ai_result.get("feedback", ai_response)
                category = ai_result.get("category", "Unknown")
            except json.JSONDecodeError:
                ai_feedback = ai_response
                category = "Unknown"

        except Exception as e:
            ai_feedback = f"⚠️ Failed to generate feedback: {e}"
            category = "Unknown"

        progress_bar.progress(100)
        status.text("✅ Analysis complete!")
        progress_bar.empty()
        status.empty()
        st.success("✅ Code analyzed successfully!")

        # Save to DB
        try:
            db.save_submission(
                st.session_state.session_id,
                problem_name.strip(),
                code_input.strip(),
                technical_analysis,
                ai_feedback
            )
        except Exception as e:
            st.warning(f"DB save failed: {e}")

        # DISPLAY TABS
        tab1, tab2, tab3, tab4 = st.tabs(["🎯 AI Feedback", "📊 Technical", "🔍 Patterns", "🔗 Similar"])

        with tab1:
            st.markdown("### 🤖 AI Mentor Feedback")
            st.markdown(ai_feedback)

        with tab2:
            st.markdown("### 📊 Static Code Metrics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Time", technical_analysis.get('complexity', {}).get('time_complexity', 'N/A'))
            with col2:
                st.metric("Space", technical_analysis.get('complexity', {}).get('space_complexity', 'N/A'))
            with col3:
                st.metric("Lines", technical_analysis.get('quality_metrics', {}).get('lines', len(code_input.splitlines())))
            if 'code_structure' in technical_analysis:
                st.json(technical_analysis['code_structure'])
        with tab3:
            st.markdown("## 🧠 Pattern Analysis")

            if pattern_analysis:
                import re

                # Split by custom headers or markers like "###"
                sections = re.split(r"(###.*)", pattern_analysis)
                rendered = []

                for i in range(1, len(sections), 2):
                    header = sections[i].strip()
                    body = sections[i+1].strip() if i+1 < len(sections) else ""

                    # Assign emoji + header formatting
                    if "Primary Pattern" in header:
                        emoji = "🔍"
                    elif "Usage Quality" in header:
                        emoji = "🧪"
                    elif "Alternative" in header:
                        emoji = "🔁"
                    elif "Optimizations" in header:
                        emoji = "🚀"
                    elif "Related" in header:
                        emoji = "🔗"
                    else:
                        emoji = "🔸"

                    st.markdown(f"### {emoji} {header.replace('###', '').strip()}")
                    st.markdown(body)

            else:
                st.info("No pattern feedback generated.")

        with tab4:
            st.markdown("### 🔗 Similar Solutions")
            if similar_solutions:
                for i, (sol, score) in enumerate(similar_solutions):
                    with st.expander(f"Solution {i+1} (Score: {score:.2f})"):
                        st.code(sol.get("code", ""), language="python")
                        st.markdown(f"**Description:** {sol.get('description', 'N/A')}")
                        st.markdown(f"**Use Cases:** {', '.join(sol.get('use_cases', []))}")
            else:
                st.info("No similar solutions found.")

        # History
        st.session_state.analysis_history.append({
            "problem_name": problem_name.strip(),
            "code_preview": code_input[:100] + "..." if len(code_input) > 100 else code_input,
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ai_feedback": ai_feedback,
            "category": category,
        })

    except Exception as e:
        st.error(f"❌ Full analysis failed: {e}")

# History
if st.session_state.analysis_history:
    st.markdown("---")
    st.subheader("📚 Recent Analyses")
    for entry in reversed(st.session_state.analysis_history[-5:]):
        with st.expander(f"{entry['problem_name']} ({entry.get('category', 'Unknown')})"):
            st.markdown(f"**🕒 Date:** {entry['timestamp']}")
            st.code(entry['code_preview'], language="python")
            st.markdown(entry["ai_feedback"][:300] + "..." if len(entry["ai_feedback"]) > 300 else entry["ai_feedback"])
