import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

st.set_page_config(
    page_title="AI Coding Mentor",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils.database import get_database
from utils.langchain_gemini_client import get_langchain_gemini_client

if 'session_id' not in st.session_state:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())

st.title("🤖 AI Coding Mentor")
st.markdown("Your Personalized AI Coach for Coding Interview Success")

st.markdown("""
## Welcome to Your AI Coding Mentor! 

Use the sidebar to navigate between different features:

- **📝 Code Analysis**: Submit your solutions for AI-powered feedback
- **📊 Progress Tracker**: Monitor your learning progress  
- **🎯 Recommendations**: Get personalized learning plans
- **⚙️ Settings**: Configure your preferences

### Getting Started
1. Navigate to **Code Analysis** to submit your first solution
2. Get instant AI feedback on your coding patterns
3. Track your progress and get personalized recommendations

Ready to level up your coding skills? Let's begin! 🚀
""")

try:
    db = get_database()
    st.success("✅ Database connection ready")
except Exception as e:
    st.error(f"❌ Database error: {e}")

try:
    llm_client = get_langchain_gemini_client()
    st.success("✅ AI model connection ready")
except Exception as e:
    st.error(f"❌ AI model error: {e}")
