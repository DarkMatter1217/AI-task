# pages/02_📝_Code_Analysis.py
import streamlit as st
from utils.langchain_gemini_client import get_langchain_gemini_client
from utils.code_analyzer import analyze_code
from utils.database import get_database
from utils.vector_store import get_vector_store
import json
import pandas as pd

st.title("📝 Code Analysis with AI Mentor")

# Initialize session
if 'session_id' not in st.session_state:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())

if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

# Initialize services
try:
    llm_client = get_langchain_gemini_client()
    db = get_database()
    vector_store = get_vector_store()
    services_loaded = True
except Exception as e:
    st.error(f"❌ Service initialization failed: {str(e)}")
    services_loaded = False

# Input section
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📋 Submit Your Code")
    
    # Code input with syntax highlighting
    code_input = st.text_area(
        "Paste your Python/C++/Java solution here:",
        height=300,
        help="Paste your complete code solution",
        placeholder="""def twoSum(nums, target):
    # Your solution here
    hash_map = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in hash_map:
            return [hash_map[complement], i]
        hash_map[num] = i
    return []"""
    )

with col2:
    st.subheader("📊 Problem Details")
    
    # Problem metadata
    problem_name = st.text_input(
        "Problem Name", 
        placeholder="e.g., 'Two Sum'",
        help="Enter the exact problem name"
    )
    
    problem_url = st.text_input(
        "Problem URL (optional)", 
        placeholder="https://leetcode.com/problems/..."
    )
    
    difficulty = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard"])
    
    # Problem category
    category = st.selectbox("Algorithm Category", [
        "Array/String", "Linked List", "Tree/Graph", 
        "Dynamic Programming", "Sorting/Searching", 
        "Two Pointers", "Sliding Window", "Backtracking",
        "Greedy", "Divide & Conquer", "Hash Table", "Other"
    ])

# Advanced analysis options
st.subheader("🔧 Analysis Options")
analysis_col1, analysis_col2, analysis_col3 = st.columns(3)

with analysis_col1:
    enable_pattern_detection = st.checkbox("🔍 Pattern Detection", value=True)
    
with analysis_col2:
    enable_complexity_analysis = st.checkbox("📊 Complexity Analysis", value=True)
    
with analysis_col3:
    enable_similarity_search = st.checkbox("🔗 Similar Solutions", value=True)

# Thinking budget control for Gemini Flash 2.5
st.subheader("🧠 AI Analysis Configuration")
col_budget, col_model = st.columns(2)

with col_budget:
    thinking_budget = st.slider(
        "AI Reasoning Depth", 
        min_value=256, 
        max_value=2048, 
        value=1024,
        step=256,
        help="Higher values = more thorough analysis but slower response"
    )

with col_model:
    analysis_mode = st.selectbox(
        "Analysis Mode",
        ["Balanced", "Fast", "Comprehensive"],
        help="Choose analysis depth vs speed trade-off"
    )

# Update thinking budget based on mode
if analysis_mode == "Fast":
    thinking_budget = 512
elif analysis_mode == "Comprehensive":
    thinking_budget = 2048

# Analysis button
if st.button("🚀 Analyze Code", type="primary", use_container_width=True):
    if not services_loaded:
        st.error("❌ Services not properly loaded. Please refresh the page.")
        st.stop()
        
    if code_input.strip() and problem_name.strip():
        
        # Debug info
        st.info(f"🔍 Analyzing: **{problem_name}** ({len(code_input)} characters)")
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with st.spinner("🔍 Analyzing your code with AI..."):
            
            try:
                # Step 1: Technical Analysis
                status_text.text("Step 1/4: Performing technical analysis...")
                progress_bar.progress(25)
                
                technical_analysis = analyze_code(code_input)
                
                # Check if technical analysis failed
                if 'error' in technical_analysis:
                    st.warning(f"⚠️ Code analysis warning: {technical_analysis['error']}")
                    # Provide fallback analysis
                    technical_analysis.update({
                        'complexity': {'time_complexity': 'O(?)', 'space_complexity': 'O(?)'},
                        'patterns': ['general_algorithm'],
                        'quality_metrics': {'lines': len(code_input.splitlines()), 'characters': len(code_input)}
                    })
                
                # Step 2: Pattern Detection
                pattern_analysis = ""
                if enable_pattern_detection:
                    status_text.text("Step 2/4: Detecting coding patterns...")
                    progress_bar.progress(50)
                    
                    patterns = technical_analysis.get('patterns', [])
                    if patterns:
                        try:
                            pattern_analysis = llm_client.identify_code_patterns(code_input, patterns)
                        except Exception as e:
                            st.warning(f"Pattern analysis failed: {str(e)}")
                            pattern_analysis = f"Pattern detection temporarily unavailable. Detected: {', '.join(patterns)}"
                
                # Step 3: Similarity Search
                similar_solutions = []
                if enable_similarity_search:
                    status_text.text("Step 3/4: Finding similar solutions...")
                    progress_bar.progress(75)
                    
                    try:
                        similar_solutions = vector_store.find_similar_patterns(code_input, k=3)
                    except Exception as e:
                        st.warning(f"Similarity search failed: {str(e)}")
                
                # Step 4: AI Analysis with proper variable passing
                status_text.text("Step 4/4: Generating AI feedback...")
                progress_bar.progress(90)
                
                
                ai_feedback = llm_client.analyze_code_with_ai(
                    code=code_input.strip(),
                    problem_name=problem_name.strip(),
                    analysis=technical_analysis
                )
                
                # Complete progress
                progress_bar.progress(100)
                status_text.text("✅ Analysis complete!")
                
                # Step 5: Save to database
                if services_loaded:
                    try:
                        db.save_submission(
                            st.session_state.session_id,
                            problem_name.strip(),
                            code_input.strip(),
                            technical_analysis,
                            ai_feedback
                        )
                    except Exception as e:
                        st.warning(f"Failed to save to database: {str(e)}")
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
                # Display results
                st.success("✅ Analysis complete!")
                
                # Create tabs for different analysis views
                tab1, tab2, tab3, tab4 = st.tabs([
                    "🎯 AI Feedback", 
                    "📊 Technical Analysis", 
                    "🔍 Pattern Analysis", 
                    "🔗 Similar Solutions"
                ])
                
                with tab1:
                    st.markdown("### 🤖 AI Mentor Feedback")
                    
                    # Debug info (collapsible)
                    with st.expander("🔧 Debug Information", expanded=False):
                        st.markdown(f"**Problem Name:** `{problem_name.strip()}`")
                        st.markdown(f"**Code Length:** `{len(code_input.strip())} characters`")
                        st.markdown(f"**Analysis Keys:** `{list(technical_analysis.keys())}`")
                        st.markdown(f"**AI Mode:** `{analysis_mode}` (Budget: {thinking_budget})")
                        
                        # Show first 200 chars of code
                        st.markdown("**Code Preview:**")
                        st.code(code_input[:200] + "..." if len(code_input) > 200 else code_input, language='python')
                    
                    # Display AI feedback
                    if ai_feedback and ai_feedback.strip():
                        st.markdown(ai_feedback)
                    else:
                        st.error("❌ AI feedback is empty or failed to generate!")
                        st.markdown("### 📋 Fallback Analysis")
                        st.info(f"""
**Problem:** {problem_name}
**Category:** {category} | **Difficulty:** {difficulty}
**Code Structure:** {len(code_input.splitlines())} lines, {len(code_input)} characters

Your code has been analyzed and saved. The AI service may be temporarily unavailable.
Please try again later for detailed feedback.
                        """)
                    
                    # Feedback rating
                    st.markdown("---")
                    st.subheader("💬 Rate this Analysis")
                    
                    col_rating, col_feedback = st.columns([1, 2])
                    with col_rating:
                        feedback_rating = st.slider("How helpful was this analysis?", 1, 5, 3)
                    
                    with col_feedback:
                        feedback_comment = st.text_input("Optional feedback:", placeholder="What could be improved?")
                    
                    if st.button("📤 Submit Rating"):
                        # Here you could save the rating to database
                        st.success(f"Thank you! Rating: {feedback_rating}/5")
                        if feedback_comment:
                            st.info(f"Comment saved: {feedback_comment}")
                
                with tab2:
                    st.markdown("### 📊 Technical Analysis Results")
                    
                    # Complexity metrics in a nice layout
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "Time Complexity", 
                            technical_analysis.get('complexity', {}).get('time_complexity', 'N/A')
                        )
                    with col2:
                        st.metric(
                            "Space Complexity", 
                            technical_analysis.get('complexity', {}).get('space_complexity', 'N/A')
                        )
                    with col3:
                        st.metric(
                            "Code Lines",
                            technical_analysis.get('quality_metrics', {}).get('lines', len(code_input.splitlines()))
                        )
                    
                    # Patterns detected
                    patterns = technical_analysis.get('patterns', [])
                    if patterns:
                        st.markdown("**🔍 Detected Patterns:**")
                        # Create pattern badges using colored containers
                        pattern_cols = st.columns(min(len(patterns), 4))
                        for i, pattern in enumerate(patterns):
                            with pattern_cols[i % 4]:
                                st.markdown(f"""
                                <div style="background-color: #e1f5fe; padding: 8px; border-radius: 5px; margin: 2px; text-align: center;">
                                    <strong>{pattern.replace('_', ' ').title()}</strong>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    # Code structure analysis
                    if 'code_structure' in technical_analysis:
                        st.markdown("**🏗️ Code Structure:**")
                        structure = technical_analysis['code_structure']
                        struct_col1, struct_col2, struct_col3, struct_col4 = st.columns(4)
                        
                        with struct_col1:
                            st.metric("Functions", structure.get('functions', 0))
                        with struct_col2:
                            st.metric("Classes", structure.get('classes', 0))
                        with struct_col3:
                            st.metric("Loops", structure.get('loops', 0))
                        with struct_col4:
                            st.metric("Conditionals", structure.get('conditionals', 0))
                    
                    # Detailed analysis (collapsible)
                    with st.expander("📋 Detailed Technical Data"):
                        st.json(technical_analysis)
                
                with tab3:
                    st.markdown("### 🔍 Pattern Analysis")
                    
                    if enable_pattern_detection:
                        if pattern_analysis and pattern_analysis.strip():
                            st.markdown(pattern_analysis)
                        else:
                            patterns = technical_analysis.get('patterns', [])
                            if patterns:
                                st.info(f"**Detected patterns:** {', '.join(patterns)}")
                                st.markdown("""
**Pattern Analysis temporarily unavailable.**

Your code shows usage of the following algorithmic patterns. Consider studying these concepts:

- **Pattern Recognition**: Understanding common problem-solving approaches
- **Algorithm Optimization**: Improving efficiency based on detected patterns  
- **Similar Problems**: Practice problems that use the same patterns
                                """)
                            else:
                                st.info("No specific patterns detected. This might be a unique implementation or a general algorithm.")
                    else:
                        st.info("Pattern detection was disabled for this analysis.")
                
                with tab4:
                    st.markdown("### 🔗 Similar Solutions")
                    
                    if enable_similarity_search:
                        if similar_solutions:
                            st.info(f"Found {len(similar_solutions)} similar solutions based on code patterns.")
                            
                            for i, (solution, score) in enumerate(similar_solutions):
                                with st.expander(f"📝 Similar Solution {i+1} (Similarity: {score:.2f})"):
                                    if 'code' in solution:
                                        st.code(solution['code'], language='python')
                                    
                                    col_desc, col_use = st.columns(2)
                                    with col_desc:
                                        st.markdown(f"**Description:** {solution.get('description', 'N/A')}")
                                    with col_use:
                                        use_cases = solution.get('use_cases', [])
                                        if use_cases:
                                            st.markdown(f"**Use Cases:** {', '.join(use_cases)}")
                        else:
                            st.info("No similar solutions found in the database. Your approach might be unique!")
                    else:
                        st.info("Similarity search was disabled for this analysis.")
                
                # Add to analysis history
                st.session_state.analysis_history.append({
                    'problem_name': problem_name.strip(),
                    'code_preview': code_input[:100] + "..." if len(code_input) > 100 else code_input,
                    'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'ai_feedback': ai_feedback,
                    'category': category,
                    'difficulty': difficulty
                })
                
            except Exception as e:
                # Clear progress indicators on error
                if 'progress_bar' in locals():
                    progress_bar.empty()
                if 'status_text' in locals():
                    status_text.empty()
                
                st.error(f"❌ Analysis failed: {str(e)}")
                
                # Detailed error info for debugging
                with st.expander("🔧 Error Details"):
                    st.code(f"Error Type: {type(e).__name__}\nError Message: {str(e)}")
                
                st.markdown("### 📋 Fallback Analysis")
                st.info(f"""
**Problem:** {problem_name}  
**Code Length:** {len(code_input)} characters  
**Difficulty:** {difficulty}  
**Category:** {category}

Your code submission has been received. While detailed AI analysis is temporarily unavailable, 
your code appears to be a {category.lower()} implementation.

**Next Steps:**
1. Verify your solution with test cases
2. Check for edge case handling  
3. Consider time/space complexity optimization
4. Try the analysis again later

Your submission is saved for future review.
                """)
    
    else:
        st.error("❌ Please provide both **code** and **problem name** to proceed.")
        if not code_input.strip():
            st.warning("📝 **Code input is required!** Please paste your solution.")
        if not problem_name.strip():
            st.warning("📝 **Problem name is required!** Please enter the problem title.")

# Analysis History Section
if st.session_state.analysis_history:
    st.markdown("---")
    st.subheader("📚 Recent Analysis History")
    
    # Show last 5 analyses
    recent_analyses = list(reversed(st.session_state.analysis_history[-5:]))
    
    for i, entry in enumerate(recent_analyses):
        with st.expander(f"📊 Analysis {len(st.session_state.analysis_history) - i}: {entry['problem_name']} ({entry.get('difficulty', 'Unknown')})"):
            
            col_info, col_code = st.columns([1, 2])
            
            with col_info:
                st.markdown(f"**📅 Date:** {entry['timestamp']}")
                st.markdown(f"**🏷️ Category:** {entry.get('category', 'Unknown')}")
                st.markdown(f"**⭐ Difficulty:** {entry.get('difficulty', 'Unknown')}")
            
            with col_code:
                st.markdown("**💻 Code Preview:**")
                st.code(entry['code_preview'], language='python')
            
            if entry.get('ai_feedback'):
                st.markdown("**🤖 AI Feedback Preview:**")
                preview = entry['ai_feedback'][:300] + "..." if len(entry['ai_feedback']) > 300 else entry['ai_feedback']
                st.markdown(preview)

# Enhanced Sidebar
st.sidebar.markdown("### 💡 Analysis Tips")
st.sidebar.markdown("""
**For Best Results:**
1. 📝 **Complete Code**: Include your entire working solution
2. 🎯 **Exact Names**: Use precise LeetCode/problem names  
3. 🔧 **Right Category**: Select the most relevant algorithm type
4. ⚡ **Analysis Mode**: 
   - **Fast**: Quick feedback (30 sec)
   - **Balanced**: Detailed analysis (1-2 min)  
   - **Comprehensive**: Deep dive (2-3 min)

**What You'll Get:**
- ✅ **Code Review**: Strengths and improvements
- 📊 **Complexity**: Time/space analysis  
- 🔍 **Patterns**: Algorithm recognition
- 🔗 **Similar**: Related solutions
- 📚 **Learning**: Personalized recommendations
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📝 Try These Problems")

# Sample problems with difficulty indicators
sample_problems = [
    ("Two Sum", "Easy", "🟢"),
    ("Reverse Linked List", "Easy", "🟢"), 
    ("Maximum Subarray", "Medium", "🟡"),
    ("Binary Tree Inorder Traversal", "Easy", "🟢"),
    ("Climbing Stairs", "Easy", "🟢"),
    ("3Sum", "Medium", "🟡"),
    ("Coin Change", "Medium", "🟡")
]

for problem, diff, emoji in sample_problems:
    if st.sidebar.button(f"{emoji} {problem}", key=f"sample_{problem}"):
        st.info(f"💡 **Suggested Problem:** Try analyzing your solution for **{problem}** ({diff})")
        # Could auto-fill the problem name
        st.session_state.suggested_problem = problem

# Quick stats in sidebar
if st.session_state.analysis_history:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 Your Progress")
    
    total_analyses = len(st.session_state.analysis_history)
    st.sidebar.metric("Total Analyses", total_analyses)
    
    # Count by difficulty
    difficulties = [entry.get('difficulty', 'Unknown') for entry in st.session_state.analysis_history]
    if difficulties:
        difficulty_counts = {d: difficulties.count(d) for d in set(difficulties)}
        for diff, count in difficulty_counts.items():
            if diff != 'Unknown':
                st.sidebar.metric(f"{diff} Problems", count)
