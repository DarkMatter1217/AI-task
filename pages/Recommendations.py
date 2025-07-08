import streamlit as st
from utils.langchain_gemini_client import get_langchain_gemini_client
from utils.database import get_database
from utils.leetcode_client import LeetCodeClient
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
import datetime
import hashlib
import os
st.title("🎯 Personalized Learning Recommendations")

if 'session_id' not in st.session_state:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())

if 'learning_plan' not in st.session_state:
    st.session_state.learning_plan = None
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}
if 'problem_shuffle_seed' not in st.session_state:
    st.session_state.problem_shuffle_seed = None
if 'plan_generated_date' not in st.session_state:
    st.session_state.plan_generated_date = None

def get_week_seed():
    today = datetime.date.today()
    year, week, _ = today.isocalendar()
    return week

def get_daily_seed():
    today = datetime.date.today()
    return int(today.strftime("%Y%m%d"))

def get_session_seed(session_id):
    return int(hashlib.md5(session_id.encode()).hexdigest()[:8], 16)

def get_random_problems(problem_list, n=5, seed=None, shuffle_override=False):
    if not problem_list:
        return []
    
    if shuffle_override and st.session_state.get('problem_shuffle_seed'):
        seed = st.session_state.problem_shuffle_seed
    elif seed is None:
        seed = get_week_seed()
    
    random.seed(seed)
    
    if len(problem_list) <= n:
        shuffled = problem_list.copy()
        random.shuffle(shuffled)
        return shuffled
    
    return random.sample(problem_list, n)

def shuffle_problems():
    st.session_state.problem_shuffle_seed = random.randint(1, 1000000)
    st.rerun()

try:
    llm_client = get_langchain_gemini_client()
    db = get_database()
    leetcode_client = LeetCodeClient()
    services_loaded = True
except Exception as e:
    st.error(f"Service initialization failed: {e}")
    services_loaded = False

st.sidebar.markdown("### 🔧 Quick Actions")
col1, col2 = st.sidebar.columns(2)

with col1:
    if st.button("🚀 Add Sample Data"):
        try:
            db.add_sample_data(st.session_state.session_id)
            st.sidebar.success("Sample data added!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error: {e}")

with col2:
    if st.button("🔄 Reset Data"):
        try:
            import sqlite3
            conn = sqlite3.connect("data/mentor.db")
            c = conn.cursor()
            c.execute("DELETE FROM submissions WHERE session_id = ?", (st.session_state.session_id,))
            c.execute("DELETE FROM progress WHERE session_id = ?", (st.session_state.session_id,))
            conn.commit()
            conn.close()
            st.sidebar.success("Data reset!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error: {e}")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎲 Problem Randomization")

current_week = get_week_seed()
st.sidebar.metric("Current Week", f"Week {current_week}")

if st.sidebar.button("🔀 Shuffle This Week's Problems"):
    shuffle_problems()

if st.sidebar.button("🗓️ Reset to Weekly Default"):
    st.session_state.problem_shuffle_seed = None
    st.rerun()

if st.session_state.get('problem_shuffle_seed'):
    st.sidebar.info("🎲 Using shuffled problems")
else:
    st.sidebar.info("📅 Using weekly default problems")

st.subheader("👤 Your Learning Profile")
profile_col1, profile_col2 = st.columns(2)

with profile_col1:
    st.markdown("### 📊 Current Status")
    
    try:
        user_stats = db.get_user_statistics(st.session_state.session_id)
    except Exception as e:
        st.error(f"Database error: {e}")
        user_stats = {
            'total_problems': 0,
            'success_rate': 0.0,
            'avg_difficulty': 'N/A', 
            'this_week': 0,
            'current_streak': 0
        }
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Problems Solved", user_stats.get('total_problems', 0))
    with col2:
        st.metric("Success Rate", f"{user_stats.get('success_rate', 0):.1f}%")
    with col3:
        st.metric("Avg. Difficulty", user_stats.get('avg_difficulty', 'N/A'))

with profile_col2:
    st.markdown("### 🎯 Learning Goals")
    primary_goal = st.selectbox("Primary Goal", [
        "FAANG Interview Preparation",
        "Competitive Programming", 
        "Algorithm Mastery",
        "Data Structure Proficiency",
        "System Design Interview",
        "General Programming Skills"
    ])
    time_per_day = st.slider("Daily Study Time (minutes)", 15, 120, 60)
    target_timeline = st.selectbox("Target Timeline", [
        "1 month", "3 months", "6 months", "1 year"
    ])

st.subheader("🔍 Skill Assessment")
skill_areas = [
    "Array/String Manipulation", "Linked Lists", "Trees & Graphs",
    "Dynamic Programming", "Sorting & Searching", "Two Pointers", 
    "Sliding Window", "Backtracking", "Greedy Algorithms", "Divide & Conquer"
]

st.markdown("Rate your current proficiency in each area:")
skill_ratings = {}
skill_cols = st.columns(2)

for i, skill in enumerate(skill_areas):
    with skill_cols[i % 2]:
        skill_ratings[skill] = st.slider(
            skill, 1, 5, 3, key=f"skill_{i}", help="1=Beginner, 5=Expert"
        )

strong_areas = [s for s, r in skill_ratings.items() if r >= 4]
weak_areas = [s for s, r in skill_ratings.items() if r <= 2]

def collect_enhanced_user_data():
    
    try:
        recent_submissions = db.get_recent_submissions(st.session_state.session_id, 5)
    except:
        recent_submissions = pd.DataFrame()
    
    problems_solved = user_stats.get('total_problems', 0)
    
    if problems_solved == 0:
        st.info("👋 **New to coding interviews?** Don't worry! Our AI will create a beginner-friendly plan.")
        experience_note = "Complete beginner - will start with fundamentals"
    elif problems_solved < 20:
        st.info("🌱 **Building foundations!** Your plan will focus on core concepts.")
        experience_note = "Beginner level - building core skills"
    elif problems_solved < 50:
        st.info("📈 **Making progress!** Time to tackle intermediate challenges.")
        experience_note = "Intermediate beginner - ready for more challenges"
    else:
        st.info("🚀 **Experienced problem solver!** Advanced techniques ahead.")
        experience_note = "Advanced level - complex problem solving"
    
    return {
        'problems_solved': problems_solved,
        'strong_areas': strong_areas,
        'weak_areas': weak_areas,
        'target_goal': primary_goal,
        'time_per_day': time_per_day,
        'target_timeline': target_timeline,
        'recent_submissions': recent_submissions.to_dict('records') if not recent_submissions.empty else [],
        'experience_note': experience_note,
        'success_rate': user_stats.get('success_rate', 0),
        'user_id': st.session_state.session_id
    }

def generate_enhanced_fallback_plan(user_data):
    problems_solved = user_data.get('problems_solved', 0)
    weak_areas = user_data.get('weak_areas', [])
    target_goal = user_data.get('target_goal', 'Interview Preparation')
    time_per_day = user_data.get('time_per_day', 60)
    
    is_beginner = problems_solved < 10
    
    current_week = get_week_seed()
    
    if is_beginner:
        return f"""
# 📚 Week {current_week} AI Learning Plan (Beginner Track)
**🎯 Goal**: {target_goal} | **⏰ Daily Time**: {time_per_day} minutes | **📊 Level**: Beginner

## 📅 This Week's Schedule

### 🌟 Day 1 (Monday) - Programming Fundamentals
**🎯 Focus**: Basic problem-solving approach
**📖 Theory (20 min)**: How to approach coding problems step by step
**💻 Practice Problems**:
- [Two Sum](https://leetcode.com/problems/two-sum/) - Easy ⭐
- [Running Sum of 1d Array](https://leetcode.com/problems/running-sum-of-1d-array/) - Easy ⭐
**🎯 Daily Goal**: Understand problem breakdown and testing

### 💪 Day 2 (Tuesday) - Array Basics
**🎯 Focus**: Array traversal and manipulation
**📖 Theory (20 min)**: Array indexing, loops, and common patterns
**💻 Practice Problems**:
- [Best Time to Buy and Sell Stock](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/) - Easy ⭐
- [Find Numbers with Even Number of Digits](https://leetcode.com/problems/find-numbers-with-even-number-of-digits/) - Easy ⭐
**🎯 Daily Goal**: Master single-pass array algorithms

### 🎯 Day 3 (Wednesday) - String Fundamentals
**🎯 Focus**: String processing and manipulation
**📖 Theory (20 min)**: String methods, character comparison, palindromes
**💻 Practice Problems**:
- [Valid Palindrome](https://leetcode.com/problems/valid-palindrome/) - Easy ⭐
- [Reverse String](https://leetcode.com/problems/reverse-string/) - Easy ⭐
**🎯 Daily Goal**: Understand string traversal patterns

### 🚀 Day 4 (Thursday) - Hash Tables Introduction
**🎯 Focus**: Using dictionaries/maps for lookups
**📖 Theory (20 min)**: Hash table concept, O(1) lookups, counting
**💻 Practice Problems**:
- [Contains Duplicate](https://leetcode.com/problems/contains-duplicate/) - Easy ⭐
- [Valid Anagram](https://leetcode.com/problems/valid-anagram/) - Easy ⭐
**🎯 Daily Goal**: Learn when and how to use hash tables

### ⚡ Day 5 (Friday) - Two Pointers Technique
**🎯 Focus**: Efficient array/string traversal
**📖 Theory (20 min)**: Two pointers concept, when to use
**💻 Practice Problems**:
- [Remove Duplicates from Sorted Array](https://leetcode.com/problems/remove-duplicates-from-sorted-array/) - Easy ⭐
- [Move Zeroes](https://leetcode.com/problems/move-zeroes/) - Easy ⭐
**🎯 Daily Goal**: Master two-pointer technique basics

### 🏆 Day 6 (Saturday) - Practice Mixed Problems
**🎯 Focus**: Applying learned concepts
**📖 Theory (15 min)**: Review week's patterns
**💻 Practice Problems**:
- [Plus One](https://leetcode.com/problems/plus-one/) - Easy ⭐
- [Remove Element](https://leetcode.com/problems/remove-element/) - Easy ⭐
**🎯 Daily Goal**: Solve problems without hints

### 🔄 Day 7 (Sunday) - Review and Consolidation
**🎯 Focus**: Understanding and documenting progress
**📖 Theory (30 min)**: Review all solutions, note patterns
**💻 Practice**: Redo any difficult problems from the week
**🎯 Daily Goal**: Solidify understanding before next week

## 🎯 Weekly Objectives
- ✅ **Complete 10+ Easy problems** with understanding
- ✅ **Master basic patterns**: Arrays, strings, hash tables, two pointers
- ✅ **Build confidence** in problem-solving approach
- ✅ **Prepare for intermediate concepts** next week

## 📊 Progress Tracking
- ✅ Problems completed: ___/10+
- ✅ Patterns understood: Arrays, Strings, Hash Tables, Two Pointers
- ✅ Confidence level: Rate 1-10

## 🚀 Next Week Preview
Once you complete this week comfortably:
- 🔗 Linked List fundamentals
- 🔄 Basic recursion
- 💰 Elementary dynamic programming
- 🌳 Tree traversal basics

*🎓 This plan is specifically designed for coding beginners. Focus on understanding over speed!*
"""
    else:
        focus_area = weak_areas[0] if weak_areas else "Dynamic Programming"
        
        return f"""
# 📚 Week {current_week} AI Learning Plan (Intermediate Track)
**🎯 Goal**: {target_goal} | **⏰ Daily Time**: {time_per_day} minutes | **🎯 Focus**: {focus_area}

## 📅 This Week's Schedule

### 🌟 Day 1 (Monday) - {focus_area} Fundamentals
**🎯 Focus**: Core concepts and basic patterns
**📖 Theory (15 min)**: {focus_area} key principles and approach
**💻 Practice Problems**:
- [Climbing Stairs](https://leetcode.com/problems/climbing-stairs/) - Easy ⭐
- [House Robber](https://leetcode.com/problems/house-robber/) - Medium ⭐⭐
**🎯 Daily Goal**: Understand basic {focus_area} patterns

### 💪 Day 2 (Tuesday) - Pattern Recognition
**🎯 Focus**: Identifying {focus_area} problems
**📖 Theory (15 min)**: How to recognize when to use {focus_area}
**💻 Practice Problems**:
- [Coin Change](https://leetcode.com/problems/coin-change/) - Medium ⭐⭐
- [Longest Increasing Subsequence](https://leetcode.com/problems/longest-increasing-subsequence/) - Medium ⭐⭐
**🎯 Daily Goal**: Master pattern recognition

### 🎯 Day 3 (Wednesday) - Advanced Applications
**🎯 Focus**: Complex {focus_area} scenarios
**📖 Theory (15 min)**: Advanced techniques and optimizations
**💻 Practice Problems**:
- [Word Break](https://leetcode.com/problems/word-break/) - Medium ⭐⭐
- [Unique Paths](https://leetcode.com/problems/unique-paths/) - Medium ⭐⭐
**🎯 Daily Goal**: Handle multi-dimensional problems

### 🚀 Day 4 (Thursday) - Mixed Practice
**🎯 Focus**: Combining {focus_area} with other concepts
**📖 Theory (10 min)**: Integration with other algorithms
**💻 Practice Problems**:
- [Palindromic Substrings](https://leetcode.com/problems/palindromic-substrings/) - Medium ⭐⭐
- [Decode Ways](https://leetcode.com/problems/decode-ways/) - Medium ⭐⭐
**🎯 Daily Goal**: Apply concepts in varied contexts

### ⚡ Day 5 (Friday) - Challenging Problems
**🎯 Focus**: Push your {focus_area} skills
**📖 Theory (10 min)**: Advanced optimization techniques
**💻 Practice Problems**:
- [Edit Distance](https://leetcode.com/problems/edit-distance/) - Hard ⭐⭐⭐
- [Maximum Product Subarray](https://leetcode.com/problems/maximum-product-subarray/) - Medium ⭐⭐
**🎯 Daily Goal**: Tackle harder problems confidently

### 🏆 Day 6 (Saturday) - Speed and Accuracy
**🎯 Focus**: Timed practice and optimization
**💻 Practice**: Review and optimize all week's solutions
**⚡ Challenge**: Solve 3 random {focus_area} problems in 1 hour
**🎯 Daily Goal**: Improve solving speed

### 🔄 Day 7 (Sunday) - Review and Analysis
**🎯 Focus**: Deep understanding and pattern documentation
**📝 Activity**: 
- Document all patterns learned
- Create personal {focus_area} cheat sheet
- Plan next week's focus area
**🎯 Daily Goal**: Consolidate knowledge for long-term retention

## 🎯 Weekly Objectives
- ✅ **Master {focus_area}** fundamentals and advanced patterns
- ✅ **Solve 12-15 problems** across Easy to Hard difficulty
- ✅ **Improve solving speed** by 25%
- ✅ **Identify next improvement area**

## 📊 Progress Tracking
- Problems completed: ___/15
- Average time per problem: ___ minutes
- Accuracy rate: ___%
- Confidence in {focus_area}: ___/10

## 🚀 Next Week Preview
- Advanced {focus_area} optimizations
- System design concepts
- Mock interview practice
- Complex algorithm combinations

*🎓 This plan adapts to your current skill level. Adjust difficulty as needed!*
"""

if st.button("🚀 Generate My AI Learning Plan", type="primary"):
    with st.spinner("🧠 AI is analyzing your data and creating a personalized plan with question links..."):
        
        user_data = collect_enhanced_user_data()
        
        with st.expander("🔍 Data Being Used for AI Plan Generation"):
            st.markdown(f"**Experience Level**: {user_data['experience_note']}")
            st.markdown(f"**Problems Solved**: {user_data['problems_solved']}")
            st.markdown(f"**Strong Areas**: {', '.join(user_data['strong_areas']) if user_data['strong_areas'] else 'Will be identified'}")
            st.markdown(f"**Weak Areas**: {', '.join(user_data['weak_areas']) if user_data['weak_areas'] else 'Will be assessed'}")
            st.markdown(f"**Goal**: {user_data['target_goal']}")
            st.markdown(f"**Daily Time**: {user_data['time_per_day']} minutes")
        
        try:
            if services_loaded:
                learning_plan = llm_client.generate_learning_path(user_data)
                st.session_state.learning_plan = learning_plan
                st.session_state.user_profile = user_data
                st.session_state.plan_generated_date = pd.Timestamp.now().strftime('%Y-%m-%d')
                st.success("✅ Your personalized AI learning plan with question links is ready!")
            else:
                learning_plan = generate_enhanced_fallback_plan(user_data)
                st.session_state.learning_plan = learning_plan
                st.session_state.user_profile = user_data
                st.session_state.plan_generated_date = pd.Timestamp.now().strftime('%Y-%m-%d')
                st.success("✅ Enhanced fallback learning plan generated!")
                
        except Exception as e:
            st.warning(f"AI service error: {e}")
            learning_plan = generate_enhanced_fallback_plan(user_data)
            st.session_state.learning_plan = learning_plan
            st.session_state.user_profile = user_data
            st.session_state.plan_generated_date = pd.Timestamp.now().strftime('%Y-%m-%d')
            st.success("✅ Backup plan generated with your preferences!")

if st.session_state.learning_plan:
    st.subheader("📚 Your Personalized Learning Plan")
    st.markdown(st.session_state.learning_plan)
    
    st.markdown("---")
    st.info("💡 **Weekly Tip**: Generate a new plan every Monday for fresh problems and updated difficulty!")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("💾 Save Plan"):
            try:
                db.save_learning_plan(st.session_state.session_id, st.session_state.learning_plan)
                st.success("Plan saved!")
            except Exception as e:
                st.error(f"Save failed: {e}")
    with c2:
        if st.button("📅 Generate Next Week"):
            st.session_state.learning_plan = None
            st.session_state.plan_generated_date = None
            st.rerun()
    with c3:
        if st.button("🔄 Regenerate Current"):
            st.session_state.learning_plan = None
            st.rerun()
    with c4:
        if st.button("📥 Export Plan"):
            plan_text = f"""AI Coding Mentor - Learning Plan
Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
Goal: {st.session_state.user_profile.get('target_goal', 'Not specified')}
Timeline: {st.session_state.user_profile.get('target_timeline', 'Not specified')}

{st.session_state.learning_plan}"""
            
            st.download_button(
                "Download Plan",
                data=plan_text,
                file_name=f"learning_plan_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    if st.session_state.plan_generated_date:
        st.caption(f"📅 Generated on: {st.session_state.plan_generated_date}")

def get_all_fallback_problems():
    return [
        {"id": "1", "title": "Two Sum", "difficulty": "Easy", "category": "Array/String", "url": "https://leetcode.com/problems/two-sum/"},
        {"id": "26", "title": "Remove Duplicates from Sorted Array", "difficulty": "Easy", "category": "Array/String", "url": "https://leetcode.com/problems/remove-duplicates-from-sorted-array/"},
        {"id": "27", "title": "Remove Element", "difficulty": "Easy", "category": "Array/String", "url": "https://leetcode.com/problems/remove-element/"},
        {"id": "283", "title": "Move Zeroes", "difficulty": "Easy", "category": "Array/String", "url": "https://leetcode.com/problems/move-zeroes/"},
        {"id": "121", "title": "Best Time to Buy and Sell Stock", "difficulty": "Easy", "category": "Array/String", "url": "https://leetcode.com/problems/best-time-to-buy-and-sell-stock/"},
        
        {"id": "122", "title": "Best Time to Buy and Sell Stock II", "difficulty": "Medium", "category": "Array/String", "url": "https://leetcode.com/problems/best-time-to-buy-and-sell-stock-ii/"},
        {"id": "53", "title": "Maximum Subarray", "difficulty": "Medium", "category": "Array/String", "url": "https://leetcode.com/problems/maximum-subarray/"},
        {"id": "15", "title": "3Sum", "difficulty": "Medium", "category": "Array/String", "url": "https://leetcode.com/problems/3sum/"},
        {"id": "238", "title": "Product of Array Except Self", "difficulty": "Medium", "category": "Array/String", "url": "https://leetcode.com/problems/product-of-array-except-self/"},
        {"id": "11", "title": "Container With Most Water", "difficulty": "Medium", "category": "Array/String", "url": "https://leetcode.com/problems/container-with-most-water/"},
        
        {"id": "70", "title": "Climbing Stairs", "difficulty": "Easy", "category": "Dynamic Programming", "url": "https://leetcode.com/problems/climbing-stairs/"},
        {"id": "746", "title": "Min Cost Climbing Stairs", "difficulty": "Easy", "category": "Dynamic Programming", "url": "https://leetcode.com/problems/min-cost-climbing-stairs/"},
        
        {"id": "198", "title": "House Robber", "difficulty": "Medium", "category": "Dynamic Programming", "url": "https://leetcode.com/problems/house-robber/"},
        {"id": "213", "title": "House Robber II", "difficulty": "Medium", "category": "Dynamic Programming", "url": "https://leetcode.com/problems/house-robber-ii/"},
        {"id": "322", "title": "Coin Change", "difficulty": "Medium", "category": "Dynamic Programming", "url": "https://leetcode.com/problems/coin-change/"},
        {"id": "300", "title": "Longest Increasing Subsequence", "difficulty": "Medium", "category": "Dynamic Programming", "url": "https://leetcode.com/problems/longest-increasing-subsequence/"},
        {"id": "139", "title": "Word Break", "difficulty": "Medium", "category": "Dynamic Programming", "url": "https://leetcode.com/problems/word-break/"},
        {"id": "62", "title": "Unique Paths", "difficulty": "Medium", "category": "Dynamic Programming", "url": "https://leetcode.com/problems/unique-paths/"},
        {"id": "72", "title": "Edit Distance", "difficulty": "Hard", "category": "Dynamic Programming", "url": "https://leetcode.com/problems/edit-distance/"},
        
        {"id": "206", "title": "Reverse Linked List", "difficulty": "Easy", "category": "Linked Lists", "url": "https://leetcode.com/problems/reverse-linked-list/"},
        {"id": "21", "title": "Merge Two Sorted Lists", "difficulty": "Easy", "category": "Linked Lists", "url": "https://leetcode.com/problems/merge-two-sorted-lists/"},
        {"id": "141", "title": "Linked List Cycle", "difficulty": "Easy", "category": "Linked Lists", "url": "https://leetcode.com/problems/linked-list-cycle/"},
        {"id": "142", "title": "Linked List Cycle II", "difficulty": "Medium", "category": "Linked Lists", "url": "https://leetcode.com/problems/linked-list-cycle-ii/"},
        {"id": "2", "title": "Add Two Numbers", "difficulty": "Medium", "category": "Linked Lists", "url": "https://leetcode.com/problems/add-two-numbers/"},
        {"id": "19", "title": "Remove Nth Node From End of List", "difficulty": "Medium", "category": "Linked Lists", "url": "https://leetcode.com/problems/remove-nth-node-from-end-of-list/"},
        
        {"id": "94", "title": "Binary Tree Inorder Traversal", "difficulty": "Easy", "category": "Trees & Graphs", "url": "https://leetcode.com/problems/binary-tree-inorder-traversal/"},
        {"id": "104", "title": "Maximum Depth of Binary Tree", "difficulty": "Easy", "category": "Trees & Graphs", "url": "https://leetcode.com/problems/maximum-depth-of-binary-tree/"},
        {"id": "226", "title": "Invert Binary Tree", "difficulty": "Easy", "category": "Trees & Graphs", "url": "https://leetcode.com/problems/invert-binary-tree/"},
        {"id": "102", "title": "Binary Tree Level Order Traversal", "difficulty": "Medium", "category": "Trees & Graphs", "url": "https://leetcode.com/problems/binary-tree-level-order-traversal/"},
        {"id": "200", "title": "Number of Islands", "difficulty": "Medium", "category": "Trees & Graphs", "url": "https://leetcode.com/problems/number-of-islands/"},
        {"id": "133", "title": "Clone Graph", "difficulty": "Medium", "category": "Trees & Graphs", "url": "https://leetcode.com/problems/clone-graph/"},
        
        {"id": "125", "title": "Valid Palindrome", "difficulty": "Easy", "category": "Two Pointers", "url": "https://leetcode.com/problems/valid-palindrome/"},
        {"id": "167", "title": "Two Sum II - Input Array Is Sorted", "difficulty": "Medium", "category": "Two Pointers", "url": "https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/"},
        {"id": "42", "title": "Trapping Rain Water", "difficulty": "Hard", "category": "Two Pointers", "url": "https://leetcode.com/problems/trapping-rain-water/"},
        
        {"id": "3", "title": "Longest Substring Without Repeating Characters", "difficulty": "Medium", "category": "Sliding Window", "url": "https://leetcode.com/problems/longest-substring-without-repeating-characters/"},
        {"id": "76", "title": "Minimum Window Substring", "difficulty": "Hard", "category": "Sliding Window", "url": "https://leetcode.com/problems/minimum-window-substring/"},
        {"id": "209", "title": "Minimum Size Subarray Sum", "difficulty": "Medium", "category": "Sliding Window", "url": "https://leetcode.com/problems/minimum-size-subarray-sum/"},
        {"id": "424", "title": "Longest Repeating Character Replacement", "difficulty": "Medium", "category": "Sliding Window", "url": "https://leetcode.com/problems/longest-repeating-character-replacement/"},
        
        {"id": "704", "title": "Binary Search", "difficulty": "Easy", "category": "Sorting & Searching", "url": "https://leetcode.com/problems/binary-search/"},
        {"id": "35", "title": "Search Insert Position", "difficulty": "Easy", "category": "Sorting & Searching", "url": "https://leetcode.com/problems/search-insert-position/"},
        {"id": "33", "title": "Search in Rotated Sorted Array", "difficulty": "Medium", "category": "Sorting & Searching", "url": "https://leetcode.com/problems/search-in-rotated-sorted-array/"},
        {"id": "153", "title": "Find Minimum in Rotated Sorted Array", "difficulty": "Medium", "category": "Sorting & Searching", "url": "https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/"},
        
        {"id": "46", "title": "Permutations", "difficulty": "Medium", "category": "Backtracking", "url": "https://leetcode.com/problems/permutations/"},
        {"id": "78", "title": "Subsets", "difficulty": "Medium", "category": "Backtracking", "url": "https://leetcode.com/problems/subsets/"},
        {"id": "39", "title": "Combination Sum", "difficulty": "Medium", "category": "Backtracking", "url": "https://leetcode.com/problems/combination-sum/"},
        {"id": "17", "title": "Letter Combinations of a Phone Number", "difficulty": "Medium", "category": "Backtracking", "url": "https://leetcode.com/problems/letter-combinations-of-a-phone-number/"},
        
        {"id": "55", "title": "Jump Game", "difficulty": "Medium", "category": "Greedy Algorithms", "url": "https://leetcode.com/problems/jump-game/"},
        {"id": "45", "title": "Jump Game II", "difficulty": "Medium", "category": "Greedy Algorithms", "url": "https://leetcode.com/problems/jump-game-ii/"},
        {"id": "134", "title": "Gas Station", "difficulty": "Medium", "category": "Greedy Algorithms", "url": "https://leetcode.com/problems/gas-station/"},
    ]

def get_fallback_problems(category):
    all_problems = get_all_fallback_problems()
    
    if category == "general":
        easy_problems = [p for p in all_problems if p["difficulty"] == "Easy"]
        return get_random_problems(easy_problems, n=8, shuffle_override=True)
    
    category_problems = [p for p in all_problems if p["category"] == category]
    return get_random_problems(category_problems, n=6, shuffle_override=True)

st.subheader("💡 Recommended Problems")

current_seed = st.session_state.get('problem_shuffle_seed', get_week_seed())
if st.session_state.get('problem_shuffle_seed'):
    st.info(f"🎲 Showing shuffled problems (Seed: {current_seed})")
else:
    st.info(f"📅 Showing problems for Week {current_seed}")

col_shuffle1, col_shuffle2, col_shuffle3 = st.columns([1, 1, 2])
with col_shuffle1:
    if st.button("🔀 Shuffle Problems"):
        shuffle_problems()
        
with col_shuffle2:
    if st.button("🗓️ Reset to Weekly"):
        st.session_state.problem_shuffle_seed = None
        st.rerun()

if weak_areas and len(weak_areas) > 0:
    st.markdown("### 🎯 Focus Areas (Based on your weak areas)")
    for i, area in enumerate(weak_areas[:3]):
        with st.expander(f"📝 Problems for {area}", expanded=(i==0)):
            problems = get_fallback_problems(area)
            
            if problems:
                for j, problem in enumerate(problems):
                    col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
                    
                    with col1:
                        st.markdown(f"**#{problem['id']}**")
                    with col2:
                        st.markdown(f"**{problem['title']}**")
                    with col3:
                        difficulty_color = {
                            'Easy': '🟢',
                            'Medium': '🟡', 
                            'Hard': '🔴'
                        }
                        st.markdown(f"{difficulty_color.get(problem['difficulty'], '⚪')} {problem['difficulty']}")
                    with col4:
                        if 'url' in problem:
                            st.markdown(f"[🔗 Solve]({problem['url']})")
                
                st.markdown("---")
                col_action1, col_action2 = st.columns(2)
                with col_action1:
                    st.button(f"🚀 Start {area} Practice", key=f"practice_{area}")
                with col_action2:
                    st.button(f"📊 View {area} Progress", key=f"progress_{area}")
else:
    st.markdown("### 🎯 Popular Practice Problems")
    with st.expander("📝 Essential Coding Problems", expanded=True):
        general_problems = get_fallback_problems("general")
        
        for problem in general_problems:
            col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
            
            with col1:
                st.markdown(f"**#{problem['id']}**")
            with col2:
                st.markdown(f"**{problem['title']}**")
            with col3:
                difficulty_color = {
                    'Easy': '🟢',
                    'Medium': '🟡', 
                    'Hard': '🔴'
                }
                st.markdown(f"{difficulty_color.get(problem['difficulty'], '⚪')} {problem['difficulty']}")
            with col4:
                if 'url' in problem:
                    st.markdown(f"[🔗 Solve]({problem['url']})")

st.subheader("📅 This Week's Study Schedule")

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_icons = ['🌟', '💪', '🎯', '🚀', '⚡', '🏆', '🔄']

st.markdown("**✨ Personalized Weekly Study Plan**")

for i, day in enumerate(days):
    with st.expander(f"{day_icons[i]} {day}", expanded=(i==0)):
        
        if weak_areas:
            topic = weak_areas[i % len(weak_areas)]
            difficulty = ["Easy", "Easy", "Medium", "Medium", "Medium", "Hard", "Review"][i]
        else:
            topics = ["Arrays", "Strings", "Linked Lists", "Trees", "Graphs", "DP", "Mixed Review"]
            topic = topics[i]
            difficulty = ["Easy", "Easy", "Medium", "Medium", "Medium", "Hard", "Review"][i]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if day == 'Sunday':
                st.markdown(f"🔄 **Weekly Review Day**")
                st.markdown(f"⏰ **Time:** {time_per_day} minutes")
                st.markdown("📝 **Tasks:**")
                st.markdown("- 📊 Review this week's progress")
                st.markdown("- 🔍 Identify patterns in solved problems")
                st.markdown("- 📝 Note down key learnings")
                st.markdown("- 📋 Plan for next week's focus areas")
            else:
                st.markdown(f"🎯 **Focus Topic:** {topic}")
                st.markdown(f"⭐ **Target Difficulty:** {difficulty}")
                st.markdown(f"⏰ **Study Time:** {time_per_day//7} minutes")
                
                st.markdown("📝 **Daily Tasks:**")
                st.markdown(f"- 📖 Review {topic} theory (10-15 min)")
                st.markdown(f"- 💻 Solve 2-3 {difficulty.lower()} problems")
                st.markdown(f"- 📝 Document solution patterns")
                
                if difficulty == "Hard":
                    st.markdown(f"- 🎯 **Challenge Day:** Push your limits!")
                elif day == 'Wednesday':
                    st.markdown(f"- 🚀 **Mid-week Boost:** Extra practice session")
        
        with col2:
            st.markdown("**📊 Progress**")
            completion_key = f"day_{day}_completed"
            completed = st.checkbox("✅ Completed", key=completion_key)
            
            if completed:
                st.success("🎉 Great job!")
            else:
                st.info("⏳ Pending")
            
            if topic != "Mixed Review":
                st.markdown("**🔗 Quick Start**")
                topic_problems = get_fallback_problems(topic)
                if topic_problems:
                    first_problem = topic_problems[0]
                    st.markdown(f"[🚀 {first_problem['title']}]({first_problem.get('url', '#')})")

st.sidebar.markdown("### 📈 Quick Stats")
st.sidebar.metric("Total Problems", user_stats.get('total_problems', 0))
st.sidebar.metric("This Week", user_stats.get('this_week', 0)) 
current_streak = user_stats.get('current_streak', 0)
if isinstance(current_streak, (int, float)):
    st.sidebar.metric("Current Streak", f"{int(current_streak)} days")
else:
    st.sidebar.metric("Current Streak", "0 days")

total_problems = user_stats.get('total_problems', 0)
if total_problems > 0:
    next_milestone = ((total_problems // 10) + 1) * 10
    st.sidebar.metric("Next Milestone", f"{next_milestone} problems")
    
    progress_to_milestone = (total_problems % 10) / 10
    st.sidebar.progress(progress_to_milestone)

st.sidebar.markdown("### 💡 Daily Tips")
st.sidebar.markdown("""
- **🌅 Morning**: Review concepts
- **🎯 Afternoon**: Solve problems  
- **🌙 Evening**: Analyze solutions
- **📊 Track**: Log your progress
- **🔄 Adapt**: Adjust based on results
""")
