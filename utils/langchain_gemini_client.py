import streamlit as st
import json
from typing import Dict, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import datetime
from typing import Optional
import os

load_dotenv()

class LangChainGeminiClient:
    def __init__(self, analysis_mode="balanced"):
        self.analysis_mode = analysis_mode.lower()
        self.llm = ChatGoogleGenerativeAI(
            model=st.secrets.get("GOOGLE_MODEL_NAME", "gemini-2.5-flash"),
            temperature=0.1,
            max_tokens=6000,
            timeout=30,
            max_retries=2
        )
        self.output_parser = StrOutputParser()
        self._build_prompt_templates()

    def _build_prompt_templates(self):
        self.code_analysis_prompt_fast = ChatPromptTemplate.from_template("""
You are a coding assistant. Analyze the given code briefly.

PROBLEM: {problem_name}
CODE:
{code}
INSIGHTS:
{analysis}

Respond with:
- ✅ Summary
- ⚠️ Major issues (if any)
- 💡 Quick tip
""")

        self.code_analysis_prompt_balanced = ChatPromptTemplate.from_template("""
You are an experienced coding mentor.

PROBLEM: {problem_name}
CODE:
{code}
INSIGHTS:
{analysis}

Please respond with:
## Strengths
## Improvements
## Time & Space Complexity
""")

        self.code_analysis_prompt_detailed = ChatPromptTemplate.from_template("""
You are a senior algorithm coach.

PROBLEM: {problem_name}
CODE:
{code}
INSIGHTS:
{analysis}

Respond with:
## 🧠 Category & Difficulty
## 🎯 Strengths
## 🔧 Areas for Improvement
## 📊 Complexity
## 📚 Resources
## 🎯 Next Challenge
""")

        self.pattern_recognition_prompt = ChatPromptTemplate.from_template("""
You are an expert in algorithmic design patterns.

TASK: Given the code and identified algorithmic patterns, give an in-depth breakdown.

CODE:
{code}

PATTERNS DETECTED: {detected_patterns}

Respond with:

### 🧠 1. Primary Pattern Used
Explain what algorithmic pattern is implemented, and how it's applied in the code.

### 🧪 2. Pattern Usage Quality (1-10)
Rate the clarity, correctness, and structure of implementation. Mention any critical flaws.

### 🔁 3. Alternative Patterns
Suggest any better or alternate patterns, if applicable.

### 🚀 4. Pattern-Specific Optimizations
Recommend improvements specific to the pattern used.

### 🔗 5. Related LeetCode Problems
List 2-3 LeetCode problems that use the same pattern with clickable links.
""")

    def analyze_code_with_ai(self, code: str, problem_name: str, analysis: Dict) -> str:
        try:
            prompt = {
                "fast": self.code_analysis_prompt_fast,
                "detailed": self.code_analysis_prompt_detailed
            }.get(self.analysis_mode, self.code_analysis_prompt_balanced)

            chain = prompt | self.llm | self.output_parser
            formatted = json.dumps(analysis, indent=2) if isinstance(analysis, dict) else str(analysis)
            return chain.invoke({
                "code": code.strip(),
                "problem_name": problem_name.strip(),
                "analysis": formatted
            })

        except Exception as e:
            return f"""## ❌ AI Analysis Failed
**Error:** {str(e)}
"""

    def identify_code_patterns(self, code: str, detected_patterns: List[str]) -> str:
        try:
            if not detected_patterns:
                return "No known patterns were detected. This may be a custom or unique implementation."

            chain = self.pattern_recognition_prompt | self.llm | self.output_parser
            response = chain.invoke({
                "code": code.strip(),
                "detected_patterns": ", ".join(detected_patterns)
            })

            if not response or len(response.strip()) < 200:
                return self._fallback_pattern_output(detected_patterns,error=None)

            return response

        except Exception as e:
            return self._fallback_pattern_output(detected_patterns, error=str(e))

    def _fallback_pattern_output(self, patterns: List[str], error: Optional[str] = None) -> str:
        return f"""
## 🔍 Pattern Analysis (Fallback)

**Detected Patterns:** {', '.join(patterns) if patterns else 'None'}

The system was unable to generate a full AI response.

### 📊 Basic Pattern Summary:
- These patterns suggest a known solution strategy was used.
- Review known optimizations and structure for: {', '.join(patterns)}
- Try testing your code with large inputs or edge cases.

{f"⚠️ Error: {error}" if error else "⚠️ No detailed explanation was available."}

You can retry with a simpler version of your code for better results.
"""

    def generate_learning_path(self, user_data: Dict) -> str:
        learning_prompt = ChatPromptTemplate.from_template("""
You are a coding mentor.

STUDENT PROFILE:
- Problems solved: {problems_solved}
- Strong areas: {strong_areas}
- Weak areas: {weak_areas}
- Goal: {goal}
- Daily study time: {time_per_day} minutes

RECENT PROBLEMS ATTEMPTED:
{recent_problems}

Please generate a 7-day personalized study plan:
- Focus topics per day
- 2-3 LeetCode problems with links
- Key tips or concepts for each day

Format it clearly using markdown. Use real LeetCode problem links.
""")

        try:
            chain = learning_prompt | self.llm | self.output_parser

            result = chain.invoke({
                "problems_solved": user_data.get("problems_solved", 0),
                "strong_areas": ", ".join(user_data.get("strong_areas", [])) or "None",
                "weak_areas": ", ".join(user_data.get("weak_areas", [])) or "Unknown",
                "goal": user_data.get("target_goal", "Improve coding interview skills"),
                "time_per_day": user_data.get("time_per_day", 60),
                "recent_problems": "\n".join(f"- {p.get('problem_name', 'Unknown')}" for p in user_data.get("recent_submissions", []))
            })

            return result

        except Exception as e:
            return f"""
## ❌ Learning Path Generation Failed

**Error:** {str(e)}

Please try again later or adjust the profile information.
"""

@st.cache_resource
def get_langchain_gemini_client(analysis_mode: str = "balanced") -> LangChainGeminiClient:
    return LangChainGeminiClient(analysis_mode)
