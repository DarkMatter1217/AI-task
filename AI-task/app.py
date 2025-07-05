import streamlit as st
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
import json

# ------------------ Configuration ------------------
load_dotenv()

# Initialize session state
if 'code_input' not in st.session_state:
    st.session_state.code_input = ''

# ------------------ Page Config ------------------
st.set_page_config(page_title="CodeMentorAI", layout="wide")
st.title("💡 CodeMentorAI - Your Personalized Coding Coach")

# ------------------ AI Analysis Backend ------------------
class LearningResources(BaseModel):
    youtube_links: List[str] = Field(description="List of relevant YouTube tutorial links")
    articles: List[str] = Field(description="List of relevant article links")
    practice_problems: List[str] = Field(description="List of recommended practice problems")

class LearningRecommendation(BaseModel):
    problem_type: str = Field(description="Identified problem category")
    difficulty: str = Field(description="Estimated difficulty level")
    strengths: List[str] = Field(description="List of coding strengths")
    weaknesses: List[str] = Field(description="List of improvements needed")
    next_challenge: str = Field(description="Recommended next problem")
    study_plan: List[str] = Field(description="Personalized action plan")
    resources: LearningResources = Field(description="Recommended learning resources")

def analyze_code(user_code: str):
    try:
        llm = HuggingFaceEndpoint(
            repo_id="meta-llama/Llama-3.1-8B-Instruct",
            task="text-generation",
            temperature=0.3
        )
        model = ChatHuggingFace(llm=llm)

        parser = PydanticOutputParser(pydantic_object=LearningRecommendation)
        
        template = """Analyze this code and provide detailed recommendations including specific learning resources:
        
        {user_code}
        
        Provide:
        1. Problem type and difficulty
        2. Key strengths/weaknesses
        3. Next recommended challenge
        4. 3-step study plan
        5. Specific resources including:
           - 2 YouTube tutorial links
           - 2 article links
           - 3 practice problems
        
        {format_instructions}"""
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["user_code"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )

        chain = prompt | model | parser
        return chain.invoke({"user_code": user_code})
    
    except Exception as e:
        st.error(f"Analysis failed: {str(e)}")
        return None

# ------------------ Streamlit UI ------------------
st.sidebar.header("User Preferences")
goal = st.sidebar.selectbox("Your Goal", ["Interview Prep", "Competitive Coding", "Learning Basics"])
experience = st.sidebar.selectbox("Experience Level", ["Beginner", "Intermediate", "Advanced"])

st.header("📤 Upload or Paste Your Code")
code_input = st.text_area(
    "Paste your code here", 
    value=st.session_state.code_input, 
    height=300
)

if st.button("🔁 Load Sample Code"):
    st.session_state.code_input = '''def two_sum(nums, target):
    hashmap = {}
    for i, num in enumerate(nums):
        if target - num in hashmap:
            return [hashmap[target - num], i]
        hashmap[num] = i
    return []'''
    st.rerun()

if st.session_state.code_input:
    if st.button("🚀 Analyze Code"):
        with st.spinner("🔍 Analyzing your code..."):
            analysis = analyze_code(st.session_state.code_input)
            
            if analysis:
                st.subheader("🔍 Analysis Results")
                
                # Problem Info
                cols = st.columns(3)
                cols[0].info(f"**Problem Type**: {analysis.problem_type}")
                cols[1].info(f"**Difficulty**: {analysis.difficulty}")
                cols[2].info(f"**Next Challenge**: {analysis.next_challenge}")
                
                # Strengths/Weaknesses
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("✅ Strengths")
                    for strength in analysis.strengths:
                        st.markdown(f"- {strength}")
                with col2:
                    st.subheader("⚠️ Areas for Improvement")
                    for weakness in analysis.weaknesses:
                        st.markdown(f"- {weakness}")
                
                # Study Plan
                st.subheader("📝 Study Plan")
                for i, step in enumerate(analysis.study_plan, 1):
                    st.markdown(f"{i}. {step}")
                
                # Resources
                st.subheader("🎓 Recommended Resources")
                
                tab1, tab2, tab3 = st.tabs(["🎥 Videos", "📚 Articles", "💻 Practice"])
                
                with tab1:
                    for link in analysis.resources.youtube_links:
                        st.markdown(f"- [{link.split('=')[-1]}]({link})")
                
                with tab2:
                    for link in analysis.resources.articles:
                        st.markdown(f"- [{link.split('/')[-1]}]({link})")
                
                with tab3:
                    for problem in analysis.resources.practice_problems:
                        st.markdown(f"- {problem}")
                
                # Progress Tracking
                st.divider()
                st.subheader("📊 Progress Tracking")
                st.select_slider("Rate your understanding", options=["Beginner", "Intermediate", "Advanced"])

# Footer
st.markdown("---")
st.caption("Built with ❤️ by Team AIRebels")