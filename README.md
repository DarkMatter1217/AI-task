
# 🧠 AI Mentor – Code Analysis & Learning Platform

An AI-powered coding assistant built with Streamlit and Gemini 2.5 Flash, designed to provide intelligent feedback on code solutions, recognize algorithmic patterns, track user progress, and recommend personalized learning paths.

---

## 📁 Project Structure

```
.
├── .streamlit/
│   └── secrets.toml            # API keys & config
├── assets/
│   └── styles/
│       └── main.css            # Optional custom styling
├── data/
│   ├── patterns/               # Pattern embeddings
│   └── mentor.db               # SQLite database for user submissions
├── pages/
│   ├── Code_Analysis.py        # Main AI Code Analysis page
│   ├── Home.py                 # Landing/Home screen
│   ├── Progress_Tracker.py     # Shows past submission history & progress
│   ├── Recommendations.py      # Personalized 7-day or 14-day learning paths
│   └── Settings.py             # Configurable app options
├── utils/
│   ├── code_analyzer.py        # Static analysis + pattern detection
│   ├── database.py             # Database operations
│   ├── langchain_gemini_client.py # Gemini prompt chaining
│   ├── leetcode_client.py      # (Optional) LeetCode integration
│   ├── recommendation_engine.py# Generates learning paths
│   └── vector_store.py         # Embedding similarity search
├── .env                        # Local env config (optional)
├── app.py                      # Main entrypoint to launch Streamlit app
├── requirements.txt            # All required Python dependencies
```

---

## 🚀 Features

- 🧠 AI Code Review: Smart GPT-based insights, complexity, improvements.
- 🔍 Pattern Analysis: Detects patterns like BFS, DFS, Sliding Window, etc.
- 📊 Complexity & Metrics: Estimates time/space complexity, lines, structure.
- 🔗 Similar Solutions: Finds similar codes using vector similarity.
- 📚 Personalized Roadmap: Adaptive 7/14-day learning plans with LeetCode links.
- ⏳ Progress Tracker: Recent history and code attempts saved with feedback.

---

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/ai-mentor.git
cd ai-mentor
```

2. Create a virtual environment:
```bash
conda create -n aimentor python=3.11
conda activate aimentor
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set your Gemini API key in `.streamlit/secrets.toml`:
```toml
GOOGLE_API_KEY = "your-gemini-api-key"
GOOGLE_MODEL_NAME = "gemini-2.5-flash"
```

Or use a `.env` file for development.

5. Run the app:
```bash
streamlit run app.py
```

---

## 🧪 Example Workflow

1. Paste your code (Python/C++/Java)
2. Enter problem name (and optional LeetCode URL)
3. Choose analysis mode: Fast / Balanced / Comprehensive
4. Get:
   - 🤖 AI Feedback
   - 📊 Complexity + Structure
   - 🔍 Pattern Breakdown
   - 🔗 Similar Solutions
   - 📚 Learning Path (optional)

---

## 📌 Future Improvements

- [ ] OAuth login + persistent progress
- [ ] Export feedback to PDF/Markdown
- [ ] Live code autocomplete
- [ ] Model selector (Gemini / Claude / Perplexity)

---
