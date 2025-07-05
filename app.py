import streamlit as st

# ------------------ Page Config ------------------
st.set_page_config(page_title="CodeMentorAI", layout="wide")
st.title("💡 CodeMentorAI - Your Personalized Coding Coach")

# ------------------ Sidebar ------------------
st.sidebar.header("User Preferences")
goal = st.sidebar.selectbox("Your Goal", ["Interview Prep", "Competitive Coding", "Learning Basics"])
experience = st.sidebar.selectbox("Experience Level", ["Beginner", "Intermediate", "Advanced"])

# ------------------ Code Input ------------------
st.header("📤 Upload or Paste Your Code")

code_input = st.text_area("Paste your code here (Python, C++, Java etc.)", height=300)

uploaded_file = st.file_uploader("Or upload your solution file", type=["py", "cpp", "java", "txt"])
if uploaded_file is not None:
    code_input = uploaded_file.read().decode("utf-8")

# ------------------ Load Example Code ------------------
if st.button("🔁 Load Sample Code"):
    code_input = '''def two_sum(nums, target):
    hashmap = {}
    for i, num in enumerate(nums):
        if target - num in hashmap:
            return [hashmap[target - num], i]
        hashmap[num] = i
    return []'''
    st.experimental_rerun()

# ------------------ Analyze Button ------------------
if code_input:
    st.success("✅ Code received. Ready for analysis.")
    
    if st.button("🚀 Analyze Code"):
        with st.spinner("🔍 Running AI analysis..."):

            # ---- Simulated Backend Response (Replace with actual function) ----
            def analyze_code(code, goal, experience):
                return {
                    "strengths": [
                        "Efficient use of hash map for constant time lookup",
                        "Clean and readable code structure",
                        "Correct handling of edge cases"
                    ],
                    "weaknesses": [
                        "No comments to explain logic",
                        "Could improve variable naming for clarity"
                    ],
                    "plan": [
                        {"type": "Next Problem", "title": "3Sum", "link": "https://leetcode.com/problems/3sum"},
                        {"type": "Video", "title": "NeetCode HashMap Tutorial", "link": "https://youtu.be/5WZl3MMT0Eg"},
                        {"type": "Article", "title": "Hash Map Optimization", "link": "https://www.geeksforgeeks.org/hashing-data-structure/"}
                    ]
                }

            feedback = analyze_code(code_input, goal, experience)

            # ------------------ Results ------------------
            st.subheader("✅ Strengths in Your Code")
            for s in feedback['strengths']:
                st.write(f"- {s}")

            st.subheader("⚠️ Areas for Improvement")
            for w in feedback['weaknesses']:
                st.write(f"- {w}")

            st.subheader("📘 Personalized Learning Plan")
            for item in feedback['plan']:
                st.markdown(f"- **{item['type']}**: [{item['title']}]({item['link']})")

            # ------------------ Progress Summary ------------------
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Experience Level", experience)
            with col2:
                st.metric("Goal", goal)

else:
    st.warning("⚠️ Please paste or upload your code above.")

# ------------------ Footer ------------------
st.markdown("---")
st.caption("Built with ❤️ by Team AIRebels for Rabbitt AI Hiring Show")
