import streamlit as st
from utils.database import get_database

def main():
    st.title("⚙️ Settings")

    st.markdown("### API & Model Configuration")
    secrets = st.secrets
    openai_key = secrets.get("GOOGLE_API_KEY", "")
    model = secrets.get("GOOGLE_MODEL_NAME", "gemini-2.5-flash")
    thinking_budget = int(secrets.get("THINKING_BUDGET", 1024))

    st.text_input("Google API Key", value=openai_key, disabled=True)
    st.text_input("Model Name", value=model, disabled=True)
    st.slider("Thinking Budget", 0, 2048, thinking_budget, disabled=True)

    st.markdown("---")
    st.markdown("### Data & Storage")
    st.checkbox("Enable local SQLite persistence", value=True)
    st.markdown("Database path: `data/mentor.db` (read-only display)")

if __name__ == "__main__":
    main()
