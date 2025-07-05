# utils/database.py
import sqlite3
import streamlit as st
import pandas as pd
import json
from typing import Dict, Any
from datetime import datetime, timedelta
import random

DB_PATH = "data/mentor.db"

class DatabaseManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database with proper schema"""
        import os
        os.makedirs("data", exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Create user_sessions table
        c.execute("""
        CREATE TABLE IF NOT EXISTS user_sessions (
            session_id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_data TEXT
        )""")
        
        # Create submissions table (without difficulty column)
        c.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            problem_name TEXT,
            code TEXT,
            analysis TEXT,
            feedback TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        
        # Create progress table (with difficulty column)
        c.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            topic TEXT,
            difficulty TEXT,
            success_rate REAL,
            problems_solved INTEGER,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        
        # Create learning_plans table
        c.execute("""
        CREATE TABLE IF NOT EXISTS learning_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            plan_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        
        conn.commit()
        conn.close()

    def save_submission(self, session_id: str, problem_name: str,
                        code: str, analysis: Dict[str, Any], feedback: str):
        """Save code submission and analysis"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
        INSERT INTO submissions (session_id, problem_name, code, analysis, feedback)
        VALUES (?, ?, ?, ?, ?)""",
                  (session_id, problem_name, code,
                   json.dumps(analysis), feedback))
        conn.commit()
        conn.close()

    def get_recent_submissions(self, session_id: str, limit: int = 5) -> pd.DataFrame:
        """Get recent submissions"""
        conn = sqlite3.connect(self.db_path)
        try:
            df = pd.read_sql_query("""
            SELECT problem_name, code, analysis, feedback, submitted_at
            FROM submissions WHERE session_id = ?
            ORDER BY submitted_at DESC LIMIT ?""",
                                   conn, params=(session_id, limit))
            conn.close()
            return df
        except Exception:
            conn.close()
            return pd.DataFrame()

    def get_progress_data(self, session_id: str) -> pd.DataFrame:
        """Get progress data with proper date formatting"""
        conn = sqlite3.connect(self.db_path)
        try:
            df = pd.read_sql_query("""
            SELECT 
                topic, 
                difficulty, 
                success_rate, 
                problems_solved, 
                DATE(updated_at) as date,
                updated_at
            FROM progress 
            WHERE session_id = ?
            ORDER BY updated_at DESC""",
            conn, params=(session_id,))
            conn.close()
            return df
        except Exception:
            conn.close()
            return pd.DataFrame()

    def get_user_statistics(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive user statistics - FIXED VERSION"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            # Get total problems solved
            c.execute("SELECT COUNT(*) FROM submissions WHERE session_id = ?", (session_id,))
            total_problems = c.fetchone()[0]
            
            # Get success rate (simulate improvement based on submissions)
            if total_problems > 0:
                success_rate = min(100.0, 60 + (total_problems * 3))  # Simulate improvement
            else:
                success_rate = 0.0
            
            # Get average difficulty from PROGRESS table (not submissions)
            c.execute("""
            SELECT difficulty, COUNT(*) as count 
            FROM progress 
            WHERE session_id = ? 
            GROUP BY difficulty""", (session_id,))
            
            difficulty_counts = c.fetchall()
            if difficulty_counts:
                # Get most common difficulty
                avg_difficulty = max(difficulty_counts, key=lambda x: x[1])[0]
            else:
                avg_difficulty = "N/A"
            
            # Get this week's submissions
            c.execute("""
            SELECT COUNT(*) FROM submissions 
            WHERE session_id = ? AND submitted_at >= date('now', '-7 days')""", (session_id,))
            this_week = c.fetchone()[0]
            
            # Calculate current streak (simplified)
            current_streak = min(total_problems, this_week + 2)  # Simulate streak
            
            conn.close()
            
            return {
                'total_problems': total_problems,
                'success_rate': success_rate,
                'avg_difficulty': avg_difficulty,
                'this_week': this_week,
                'current_streak': current_streak
            }
            
        except Exception as e:
            conn.close()
            # Return default values if any error
            return {
                'total_problems': 0,
                'success_rate': 0.0,
                'avg_difficulty': 'N/A',
                'this_week': 0,
                'current_streak': 0
            }

    def save_learning_plan(self, session_id: str, plan_text: str):
        """Save a learning plan for the user"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
        INSERT INTO learning_plans (session_id, plan_text)
        VALUES (?, ?)""", (session_id, plan_text))
        conn.commit()
        conn.close()

    def add_sample_data(self, session_id: str):
        """Add comprehensive sample data with proper schema"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Clear existing data
        c.execute("DELETE FROM submissions WHERE session_id = ?", (session_id,))
        c.execute("DELETE FROM progress WHERE session_id = ?", (session_id,))
        
        # Sample submissions (without difficulty)
        sample_submissions = [
            ("Two Sum", "def twoSum(nums, target):\n    d = {}\n    for i, n in enumerate(nums):\n        if target - n in d:\n            return [d[target - n], i]\n        d[n] = i"),
            ("Three Sum", "def threeSum(nums):\n    nums.sort()\n    result = []\n    # implementation\n    return result"),
            ("Maximum Subarray", "def maxSubArray(nums):\n    max_sum = nums[0]\n    curr_sum = nums[0]\n    # Kadane's algorithm\n    return max_sum"),
            ("Climbing Stairs", "def climbStairs(n):\n    if n <= 2: return n\n    # DP solution\n    return dp[n]"),
            ("Reverse Linked List", "def reverseList(head):\n    prev = None\n    curr = head\n    # iterative reversal\n    return prev"),
            ("Binary Tree Inorder", "def inorderTraversal(root):\n    result = []\n    # DFS traversal\n    return result"),
            ("Valid Parentheses", "def isValid(s):\n    stack = []\n    # stack validation\n    return True"),
            ("Merge Two Lists", "def mergeTwoLists(l1, l2):\n    dummy = ListNode(0)\n    # merge logic\n    return dummy.next")
        ]
        
        # Insert submissions
        for i, (problem, code) in enumerate(sample_submissions):
            timestamp = (datetime.now() - timedelta(days=i)).isoformat()
            c.execute("""
            INSERT INTO submissions (session_id, problem_name, code, analysis, feedback, submitted_at)
            VALUES (?, ?, ?, ?, ?, ?)""", 
            (session_id, problem, code, 
             '{"complexity": {"time_complexity": "O(n)", "space_complexity": "O(1)"}, "patterns": ["algorithm"]}',
             f"Great solution for {problem}! Your implementation shows good understanding.", timestamp))
        
        # Sample progress data (with difficulty)
        sample_progress = [
            ('Array/String Manipulation', 'Easy', 85.0, 8, 1),
            ('Array/String Manipulation', 'Medium', 70.0, 4, 2),
            ('Dynamic Programming', 'Easy', 90.0, 3, 3),
            ('Dynamic Programming', 'Medium', 60.0, 2, 4),
            ('Linked Lists', 'Easy', 95.0, 4, 5),
            ('Trees & Graphs', 'Easy', 80.0, 2, 6),
            ('Trees & Graphs', 'Medium', 75.0, 3, 7),
            ('Two Pointers', 'Easy', 88.0, 3, 8),
            ('Two Pointers', 'Medium', 65.0, 2, 9),
            ('Sliding Window', 'Medium', 72.0, 2, 10),
            ('Binary Search', 'Easy', 92.0, 2, 11),
            ('Backtracking', 'Medium', 58.0, 1, 12)
        ]
        
        for topic, difficulty, success_rate, problems_solved, days_ago in sample_progress:
            timestamp = (datetime.now() - timedelta(days=days_ago)).isoformat()
            c.execute("""
            INSERT INTO progress (session_id, topic, difficulty, success_rate, problems_solved, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)""", 
            (session_id, topic, difficulty, success_rate, problems_solved, timestamp))
        
        conn.commit()
        conn.close()

@st.cache_resource
def get_database() -> DatabaseManager:
    return DatabaseManager()
