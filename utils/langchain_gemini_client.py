# utils/langchain_gemini_client.py

import streamlit as st
import json
from typing import Dict, List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
load_dotenv()
class LangChainGeminiClient:
    """
    LangChain + Google Gemini Flash 2.5 client for AI-powered code analysis
    and personalized learning path generation.
    """

    def __init__(self):

        # Initialize the Gemini Flash 2.5 model via LangChain
        self.llm = ChatGoogleGenerativeAI(
            model=st.secrets.get("GOOGLE_MODEL_NAME", "gemini-2.5-flash"),
            temperature=0.1,
            max_tokens=2000,
            timeout=30,
            max_retries=2
        )

        # Output parser to ensure string output
        self.output_parser = StrOutputParser()

        # Build reusable prompt templates
        self._build_prompt_templates()

    def _build_prompt_templates(self):
        """Define and compile prompt templates for different tasks."""

        # 1. Code Analysis Prompt - COMPLETELY FIXED
        self.code_analysis_prompt = ChatPromptTemplate.from_template("""
You are an expert coding mentor specializing in algorithm analysis and interview preparation.

PROBLEM: {problem_name}

CODE TO ANALYZE:
{code}

TECHNICAL ANALYSIS:
{analysis}

Please provide detailed feedback in this exact format:

## 🎯 Strengths
- List specific things implemented well
- Highlight good coding practices

## 🔧 Areas for Improvement  
- Specific suggestions with examples
- Code optimization opportunities

## 📊 Complexity Analysis
- Time complexity: Explain the Big O notation
- Space complexity: Explain memory usage

## 📚 Learning Resources
- Specific concepts to study next
- Recommended practice topics

## 🎯 Next Challenge
- Suggest a similar but slightly harder problem

Keep feedback constructive, educational, and encouraging.
""")

        # 2. Learning Path Generation Prompt
        self.learning_path_prompt = ChatPromptTemplate.from_template("""
You are an AI learning coach for coding interview preparation.

STUDENT PROFILE:
- Problems solved: {problems_solved}
- Strong areas: {strong_areas}
- Weak areas: {weak_areas}
- Target goal: {target_goal}
- Daily time (min): {time_per_day}

RECENT SUBMISSIONS:
{recent_submissions}

Create a structured 14-day learning plan with:
1. Daily study topics (specific concepts)
2. Recommended problems to solve
3. Key resources and materials
4. Progress milestones

Format as a clear, actionable roadmap.
""")

        # 3. Pattern Recognition Prompt
        self.pattern_recognition_prompt = ChatPromptTemplate.from_template("""
You are an expert in coding patterns and algorithms.

CODE TO ANALYZE:
{code}

DETECTED PATTERNS: {detected_patterns}

Provide:
1. Primary algorithmic pattern used
2. Implementation quality score (1-10)
3. Alternative patterns that could work
4. Pattern-specific optimizations
5. Related problems using same pattern

Focus on educational insights about algorithmic patterns.
""")

    def analyze_code_with_ai(self, code: str, problem_name: str, analysis: Dict) -> str:
        """
        Analyze a single code submission and return structured feedback.
        """
        try:
            # Create the chain
            chain = self.code_analysis_prompt | self.llm | self.output_parser
            
            # Format analysis data
            formatted_analysis = json.dumps(analysis, indent=2) if isinstance(analysis, dict) else str(analysis)
            
            # Execute the chain with proper variable substitution
            result = chain.invoke({
                "code": code.strip(),
                "problem_name": problem_name.strip(),
                "analysis": formatted_analysis
            })
            
            return result
            
        except Exception as e:
            # Comprehensive fallback response
            return f"""
## ❌ AI Analysis Temporarily Unavailable

**Error:** {str(e)}

## 📋 Manual Analysis for: {problem_name}

### 🎯 Basic Assessment
Your code submission has been received and saved successfully.

**Code Length:** {len(code)} characters  
**Lines of Code:** {len(code.splitlines())} lines

### 📊 Quick Analysis
- **Problem Type:** {problem_name}
- **Implementation:** Code structure appears complete
- **Next Steps:** Review algorithm efficiency and edge cases

### 📚 General Recommendations
1. **Test with sample inputs** to verify correctness
2. **Consider edge cases** like empty inputs or boundary conditions  
3. **Analyze time/space complexity** for optimization opportunities
4. **Review similar problems** for pattern recognition

### 🔄 Try Again
The AI service may be temporarily busy. Please try analyzing again in a moment for detailed feedback.

**Your code has been saved and you can continue practicing!**
"""

    def generate_learning_path(self, user_data: Dict) -> str:
        """
        Generate a personalized 14-day learning plan based on the user profile.
        """
        try:
            # Create the chain
            chain = self.learning_path_prompt | self.llm | self.output_parser
            
            # Execute the chain
            result = chain.invoke({
                "problems_solved": user_data.get("problems_solved", 0),
                "strong_areas": ", ".join(user_data.get("strong_areas", [])),
                "weak_areas": ", ".join(user_data.get("weak_areas", [])),
                "target_goal": user_data.get("target_goal", "General improvement"),
                "time_per_day": user_data.get("time_per_day", 30),
                "recent_submissions": json.dumps(user_data.get("recent_submissions", []), indent=2)
            })
            
            return result
            
        except Exception as e:
            # Fallback learning plan
            weak_areas = user_data.get("weak_areas", ["Arrays", "Dynamic Programming"])
            target_goal = user_data.get("target_goal", "Interview Preparation")
            time_per_day = user_data.get("time_per_day", 60)
            
            return f"""
# 📚 Your Personalized Learning Plan

## 🎯 Goal: {target_goal}
**Daily Time Commitment:** {time_per_day} minutes

## Week 1: Foundation Building

### Days 1-3: Core Concepts
**Focus:** {weak_areas[0] if weak_areas else 'Array Fundamentals'}
- **Day 1:** Basic array operations and traversal
- **Day 2:** Two-pointer technique introduction  
- **Day 3:** Practice problems (Easy level)

### Days 4-7: Pattern Recognition
**Focus:** {weak_areas[1] if len(weak_areas) > 1 else 'Problem Solving Patterns'}
- **Day 4:** Sliding window technique
- **Day 5:** Hash table applications
- **Day 6:** String manipulation methods
- **Day 7:** Weekly review and practice

## Week 2: Advanced Applications

### Days 8-10: Intermediate Concepts
- **Day 8:** Dynamic programming basics
- **Day 9:** Tree traversal methods
- **Day 10:** Graph algorithms introduction

### Days 11-14: Integration & Practice
- **Day 11:** Mixed problem solving
- **Day 12:** Time complexity optimization
- **Day 13:** Mock interview practice
- **Day 14:** Progress review and next steps

## 📝 Daily Structure ({time_per_day} minutes)
1. **Theory Review (20%):** Concept understanding
2. **Coding Practice (60%):** Hands-on problem solving
3. **Review & Notes (20%):** Solution analysis

## 🎯 Weekly Goals
- **Week 1:** Solve 15-20 easy to medium problems
- **Week 2:** Focus on 10-15 medium to hard problems

## 📚 Recommended Resources
- LeetCode problem sets by topic
- Algorithm visualization tools
- Coding interview preparation books

**Note:** AI service temporarily unavailable. This is a general plan - customize based on your specific needs!
"""

    def identify_code_patterns(self, code: str, detected_patterns: List[str]) -> str:
        """
        Evaluate detected code patterns and suggest improvements.
        """
        try:
            # Create the chain
            chain = self.pattern_recognition_prompt | self.llm | self.output_parser
            
            # Execute the chain
            result = chain.invoke({
                "code": code.strip(),
                "detected_patterns": ", ".join(detected_patterns)
            })
            
            return result
            
        except Exception as e:
            return f"""
## 🔍 Pattern Analysis for Detected Patterns

**Detected Patterns:** {', '.join(detected_patterns)}

### 📊 Pattern Assessment
Your code demonstrates use of: **{', '.join(detected_patterns)}**

### 💡 General Pattern Insights
- **Primary Pattern:** {detected_patterns[0] if detected_patterns else 'Basic Implementation'}
- **Complexity:** Depends on specific implementation details
- **Use Cases:** Applicable to similar algorithmic problems

### 🎯 Optimization Opportunities
1. **Review algorithm efficiency** for the detected patterns
2. **Consider alternative approaches** that might be more optimal
3. **Practice similar problems** to reinforce pattern recognition

### 📚 Pattern-Specific Resources
- Study algorithmic pattern collections
- Practice problems grouped by pattern type
- Review optimal implementations for each pattern

**Error:** {str(e)}
**Note:** Detailed AI analysis temporarily unavailable.
"""

@st.cache_resource
def get_langchain_gemini_client() -> LangChainGeminiClient:
    """
    Cached factory for the LangChainGeminiClient to reuse resources across Streamlit sessions.
    """
    return LangChainGeminiClient()
# utils/langchain_gemini_client.py - Add this enhanced method

def _build_prompt_templates(self):
    """Enhanced prompt templates with question links"""
    
    # Enhanced Learning Path Generation Prompt with Question Links
    self.learning_path_prompt = ChatPromptTemplate.from_template("""
You are an expert coding interview coach specializing in personalized learning plans.

STUDENT PROFILE:
- Problems solved: {problems_solved}
- Strong areas: {strong_areas}
- Weak areas: {weak_areas}
- Target goal: {target_goal}
- Daily time (min): {time_per_day}
- Experience level: {experience_level}
- Recent submissions: {recent_submissions}

CURRENT WEEK: Week {current_week}

Generate a detailed 7-day learning plan for THIS WEEK with the following requirements:

1. **Daily Schedule**: Specific daily tasks and time allocation
2. **Targeted Problems**: Include EXACT LeetCode problem names and URLs
3. **Progressive Difficulty**: Start easier, build up complexity
4. **Focus Areas**: Prioritize weak areas, maintain strong areas
5. **Practical Goals**: Achievable daily targets

For each day, provide:
- **Day X (Date)**: Clear daily theme
- **Focus Topic**: Specific algorithm/data structure
- **Theory (15-20 min)**: Key concepts to review
- **Practice Problems**: 2-3 specific LeetCode problems with URLs
- **Daily Goal**: What to achieve by end of day

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:

# 📚 Week {current_week} Learning Plan
**Goal**: {target_goal} | **Daily Time**: {time_per_day} minutes

## 📅 This Week's Schedule

### 🌟 Day 1 (Monday) - Array Fundamentals
**Focus**: Basic Array Operations
**Theory (15 min)**: Array traversal and indexing patterns
**Practice Problems**:
- [Two Sum](https://leetcode.com/problems/two-sum/) - Easy
- [Best Time to Buy and Sell Stock](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/) - Easy
**Daily Goal**: Master single-pass array algorithms

### 💪 Day 2 (Tuesday) - String Manipulation
**Focus**: String processing techniques
**Theory (15 min)**: String methods and character manipulation
**Practice Problems**:
- [Valid Palindrome](https://leetcode.com/problems/valid-palindrome/) - Easy
- [Longest Common Prefix](https://leetcode.com/problems/longest-common-prefix/) - Easy
**Daily Goal**: Understand string traversal patterns

[Continue for all 7 days with actual LeetCode URLs]

## 🎯 Weekly Objectives
- Solve 15-20 problems total
- Master [specific topic] fundamentals
- Improve [weak area] by 20%

## 📊 Progress Tracking
- Daily: Track problems completed
- Weekly: Assess improvement in weak areas
- Next Week: Plan advanced topics

Include REAL LeetCode URLs for all recommended problems. Adapt difficulty based on user's experience level.
""")

def generate_learning_path(self, user_data: Dict) -> str:
    """Enhanced learning path generation with user data analysis"""
    try:
        # Analyze user experience level
        problems_solved = user_data.get('problems_solved', 0)
        strong_areas = user_data.get('strong_areas', [])
        weak_areas = user_data.get('weak_areas', [])
        
        # Determine experience level
        if problems_solved == 0:
            experience_level = "Complete Beginner"
        elif problems_solved < 20:
            experience_level = "Beginner" 
        elif problems_solved < 50:
            experience_level = "Intermediate Beginner"
        elif problems_solved < 100:
            experience_level = "Intermediate"
        else:
            experience_level = "Advanced"
        
        # Set beginner defaults if no data
        if not strong_areas and not weak_areas:
            if experience_level in ["Complete Beginner", "Beginner"]:
                strong_areas = ["Basic Programming"]
                weak_areas = ["Array/String Manipulation", "Problem Solving", "Algorithm Thinking"]
            else:
                strong_areas = ["Arrays", "Basic Algorithms"]
                weak_areas = ["Dynamic Programming", "Graph Algorithms"]
        
        # Get current week number
        import datetime
        current_week = datetime.date.today().isocalendar()[1]
        
        # Create the chain
        chain = self.learning_path_prompt | self.llm | self.output_parser
        
        # Execute with enhanced data
        result = chain.invoke({
            "problems_solved": problems_solved,
            "strong_areas": ", ".join(strong_areas) if strong_areas else "None identified",
            "weak_areas": ", ".join(weak_areas) if weak_areas else "Basic fundamentals",
            "target_goal": user_data.get("target_goal", "General Programming Skills"),
            "time_per_day": user_data.get("time_per_day", 60),
            "experience_level": experience_level,
            "recent_submissions": self._format_recent_submissions(user_data.get("recent_submissions", [])),
            "current_week": current_week
        })
        
        return result
        
    except Exception as e:
        # Enhanced fallback with question links
        return self._generate_enhanced_fallback_plan(user_data)

def _format_recent_submissions(self, submissions: List[Dict]) -> str:
    """Format recent submissions for AI context"""
    if not submissions:
        return "No recent submissions (new user)"
    
    formatted = []
    for sub in submissions[:3]:  # Last 3 submissions
        problem = sub.get('problem_name', 'Unknown')
        formatted.append(f"- {problem}")
    
    return "\n".join(formatted)

def _generate_enhanced_fallback_plan(self, user_data: Dict) -> str:
    """Enhanced fallback plan with actual question links"""
    problems_solved = user_data.get('problems_solved', 0)
    weak_areas = user_data.get('weak_areas', [])
    target_goal = user_data.get('target_goal', 'Interview Preparation')
    time_per_day = user_data.get('time_per_day', 60)
    
    # Determine if beginner
    is_beginner = problems_solved < 10
    
    # Get current week
    import datetime
    current_week = datetime.date.today().isocalendar()[1]
    
    if is_beginner:
        return f"""
# 📚 Week {current_week} Learning Plan (Beginner Track)
**Goal**: {target_goal} | **Daily Time**: {time_per_day} minutes | **Level**: Beginner

## 📅 This Week's Schedule

### 🌟 Day 1 (Monday) - Programming Fundamentals
**Focus**: Basic problem-solving approach
**Theory (20 min)**: How to approach coding problems step by step
**Practice Problems**:
- [Two Sum](https://leetcode.com/problems/two-sum/) - Easy
- [Running Sum of 1d Array](https://leetcode.com/problems/running-sum-of-1d-array/) - Easy
**Daily Goal**: Understand problem breakdown and testing

### 💪 Day 2 (Tuesday) - Array Basics
**Focus**: Array traversal and manipulation
**Theory (20 min)**: Array indexing, loops, and common patterns
**Practice Problems**:
- [Best Time to Buy and Sell Stock](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/) - Easy
- [Maximum Subarray](https://leetcode.com/problems/maximum-subarray/) - Easy (try simple approach)
**Daily Goal**: Master single-pass array algorithms

### 🎯 Day 3 (Wednesday) - String Fundamentals
**Focus**: String processing and manipulation
**Theory (20 min)**: String methods, character comparison, palindromes
**Practice Problems**:
- [Valid Palindrome](https://leetcode.com/problems/valid-palindrome/) - Easy
- [Reverse String](https://leetcode.com/problems/reverse-string/) - Easy
**Daily Goal**: Understand string traversal patterns

### 🚀 Day 4 (Thursday) - Hash Tables Introduction
**Focus**: Using dictionaries/maps for lookups
**Theory (20 min)**: Hash table concept, O(1) lookups, counting
**Practice Problems**:
- [Contains Duplicate](https://leetcode.com/problems/contains-duplicate/) - Easy
- [Valid Anagram](https://leetcode.com/problems/valid-anagram/) - Easy
**Daily Goal**: Learn when and how to use hash tables

### ⚡ Day 5 (Friday) - Two Pointers Technique
**Focus**: Efficient array/string traversal
**Theory (20 min)**: Two pointers concept, when to use
**Practice Problems**:
- [Remove Duplicates from Sorted Array](https://leetcode.com/problems/remove-duplicates-from-sorted-array/) - Easy
- [Move Zeroes](https://leetcode.com/problems/move-zeroes/) - Easy
**Daily Goal**: Master two-pointer technique basics

### 🏆 Day 6 (Saturday) - Practice Mixed Problems
**Focus**: Applying learned concepts
**Theory (15 min)**: Review week's patterns
**Practice Problems**:
- [Plus One](https://leetcode.com/problems/plus-one/) - Easy
- [Remove Element](https://leetcode.com/problems/remove-element/) - Easy
**Daily Goal**: Solve problems without hints

### 🔄 Day 7 (Sunday) - Review and Consolidation
**Focus**: Understanding and documenting progress
**Theory (30 min)**: Review all solutions, note patterns
**Practice**: Redo any difficult problems from the week
**Daily Goal**: Solidify understanding before next week

## 🎯 Weekly Objectives
- **Complete 10+ Easy problems** with understanding
- **Master basic patterns**: Arrays, strings, hash tables, two pointers
- **Build confidence** in problem-solving approach
- **Prepare for intermediate concepts** next week

## 📊 Progress Tracking
- ✅ Problems completed: ___/10+
- ✅ Patterns understood: Arrays, Strings, Hash Tables, Two Pointers
- ✅ Confidence level: Rate 1-10

## 🚀 Next Week Preview
Once you complete this week comfortably:
- Linked List fundamentals
- Basic recursion
- Elementary dynamic programming
- Tree traversal basics

*This plan is specifically designed for coding beginners. Focus on understanding over speed!*
"""
    else:
        # Intermediate plan with more advanced problems
        focus_area = weak_areas[0] if weak_areas else "Dynamic Programming"
        
        return f"""
# 📚 Week {current_week} Learning Plan (Intermediate Track)
**Goal**: {target_goal} | **Daily Time**: {time_per_day} minutes | **Focus**: {focus_area}

## 📅 This Week's Schedule

### 🌟 Day 1 (Monday) - {focus_area} Fundamentals
**Focus**: Core concepts and basic patterns
**Theory (15 min)**: {focus_area} key principles and approach
**Practice Problems**:
- [Climbing Stairs](https://leetcode.com/problems/climbing-stairs/) - Easy
- [House Robber](https://leetcode.com/problems/house-robber/) - Medium
**Daily Goal**: Understand basic {focus_area} patterns

### 💪 Day 2 (Tuesday) - Pattern Recognition
**Focus**: Identifying {focus_area} problems
**Theory (15 min)**: How to recognize when to use {focus_area}
**Practice Problems**:
- [Coin Change](https://leetcode.com/problems/coin-change/) - Medium
- [Longest Increasing Subsequence](https://leetcode.com/problems/longest-increasing-subsequence/) - Medium
**Daily Goal**: Master pattern recognition

### 🎯 Day 3 (Wednesday) - Advanced Applications
**Focus**: Complex {focus_area} scenarios
**Theory (15 min)**: Advanced techniques and optimizations
**Practice Problems**:
- [Word Break](https://leetcode.com/problems/word-break/) - Medium
- [Unique Paths](https://leetcode.com/problems/unique-paths/) - Medium
**Daily Goal**: Handle multi-dimensional problems

### 🚀 Day 4 (Thursday) - Mixed Practice
**Focus**: Combining {focus_area} with other concepts
**Theory (10 min)**: Integration with other algorithms
**Practice Problems**:
- [Palindromic Substrings](https://leetcode.com/problems/palindromic-substrings/) - Medium
- [Decode Ways](https://leetcode.com/problems/decode-ways/) - Medium
**Daily Goal**: Apply concepts in varied contexts

### ⚡ Day 5 (Friday) - Challenging Problems
**Focus**: Push your {focus_area} skills
**Theory (10 min)**: Advanced optimization techniques
**Practice Problems**:
- [Edit Distance](https://leetcode.com/problems/edit-distance/) - Hard
- [Maximum Product Subarray](https://leetcode.com/problems/maximum-product-subarray/) - Medium
**Daily Goal**: Tackle harder problems confidently

### 🏆 Day 6 (Saturday) - Speed and Accuracy
**Focus**: Timed practice and optimization
**Practice**: Review and optimize all week's solutions
**Challenge**: Solve 3 random {focus_area} problems in 1 hour
**Daily Goal**: Improve solving speed

### 🔄 Day 7 (Sunday) - Review and Analysis
**Focus**: Deep understanding and pattern documentation
**Activity**: 
- Document all patterns learned
- Create personal {focus_area} cheat sheet
- Plan next week's focus area
**Daily Goal**: Consolidate knowledge for long-term retention

## 🎯 Weekly Objectives
- **Master {focus_area}** fundamentals and advanced patterns
- **Solve 12-15 problems** across Easy to Hard difficulty
- **Improve solving speed** by 25%
- **Identify next improvement area**

## 📊 Progress Tracking
- Problems completed: ___/15
- Average time per problem: ___ minutes
- Accuracy rate: ___%
- Confidence in {focus_area}: ___/10

*This plan adapts to your current skill level. Adjust difficulty as needed!*
"""
