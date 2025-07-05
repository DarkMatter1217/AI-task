# utils/leetcode_client.py
import requests
import streamlit as st
import json
from pathlib import Path
from typing import Optional, Dict, List

class LeetCodeClient:
    def __init__(self):
        self.base_url = "https://leetcode-api-pied.vercel.app"
        self.problems_db = self._get_enhanced_problems_db()

    def _get_enhanced_problems_db(self) -> List[Dict]:
        """Comprehensive problems database"""
        return [
            # Array/String Problems
            {"id": "1", "title": "Two Sum", "difficulty": "Easy", "tags": ["array", "hash table"], "category": "Array/String Manipulation"},
            {"id": "26", "title": "Remove Duplicates from Sorted Array", "difficulty": "Easy", "tags": ["array", "two pointers"], "category": "Array/String Manipulation"},
            {"id": "27", "title": "Remove Element", "difficulty": "Easy", "tags": ["array", "two pointers"], "category": "Array/String Manipulation"},
            {"id": "283", "title": "Move Zeroes", "difficulty": "Easy", "tags": ["array", "two pointers"], "category": "Array/String Manipulation"},
            {"id": "344", "title": "Reverse String", "difficulty": "Easy", "tags": ["string", "two pointers"], "category": "Array/String Manipulation"},
            
            # Two Pointers
            {"id": "15", "title": "3Sum", "difficulty": "Medium", "tags": ["array", "two pointers"], "category": "Two Pointers"},
            {"id": "18", "title": "4Sum", "difficulty": "Medium", "tags": ["array", "two pointers"], "category": "Two Pointers"},
            {"id": "167", "title": "Two Sum II", "difficulty": "Medium", "tags": ["array", "two pointers"], "category": "Two Pointers"},
            {"id": "11", "title": "Container With Most Water", "difficulty": "Medium", "tags": ["array", "two pointers"], "category": "Two Pointers"},
            
            # Sliding Window
            {"id": "3", "title": "Longest Substring Without Repeating", "difficulty": "Medium", "tags": ["string", "sliding window"], "category": "Sliding Window"},
            {"id": "76", "title": "Minimum Window Substring", "difficulty": "Hard", "tags": ["string", "sliding window"], "category": "Sliding Window"},
            {"id": "209", "title": "Minimum Size Subarray Sum", "difficulty": "Medium", "tags": ["array", "sliding window"], "category": "Sliding Window"},
            {"id": "424", "title": "Longest Repeating Character Replacement", "difficulty": "Medium", "tags": ["string", "sliding window"], "category": "Sliding Window"},
            
            # Dynamic Programming
            {"id": "70", "title": "Climbing Stairs", "difficulty": "Easy", "tags": ["dynamic programming"], "category": "Dynamic Programming"},
            {"id": "198", "title": "House Robber", "difficulty": "Medium", "tags": ["dynamic programming"], "category": "Dynamic Programming"},
            {"id": "322", "title": "Coin Change", "difficulty": "Medium", "tags": ["dynamic programming"], "category": "Dynamic Programming"},
            {"id": "300", "title": "Longest Increasing Subsequence", "difficulty": "Medium", "tags": ["dynamic programming"], "category": "Dynamic Programming"},
            {"id": "121", "title": "Best Time to Buy and Sell Stock", "difficulty": "Easy", "tags": ["array", "dynamic programming"], "category": "Dynamic Programming"},
            
            # Linked Lists
            {"id": "206", "title": "Reverse Linked List", "difficulty": "Easy", "tags": ["linked list"], "category": "Linked Lists"},
            {"id": "21", "title": "Merge Two Sorted Lists", "difficulty": "Easy", "tags": ["linked list"], "category": "Linked Lists"},
            {"id": "141", "title": "Linked List Cycle", "difficulty": "Easy", "tags": ["linked list"], "category": "Linked Lists"},
            {"id": "19", "title": "Remove Nth Node From End", "difficulty": "Medium", "tags": ["linked list"], "category": "Linked Lists"},
            {"id": "2", "title": "Add Two Numbers", "difficulty": "Medium", "tags": ["linked list"], "category": "Linked Lists"},
            
            # Trees & Graphs
            {"id": "94", "title": "Binary Tree Inorder Traversal", "difficulty": "Easy", "tags": ["tree", "depth-first search"], "category": "Trees & Graphs"},
            {"id": "102", "title": "Binary Tree Level Order Traversal", "difficulty": "Medium", "tags": ["tree", "breadth-first search"], "category": "Trees & Graphs"},
            {"id": "104", "title": "Maximum Depth of Binary Tree", "difficulty": "Easy", "tags": ["tree", "depth-first search"], "category": "Trees & Graphs"},
            {"id": "200", "title": "Number of Islands", "difficulty": "Medium", "tags": ["array", "depth-first search"], "category": "Trees & Graphs"},
            {"id": "226", "title": "Invert Binary Tree", "difficulty": "Easy", "tags": ["tree"], "category": "Trees & Graphs"},
            
            # Binary Search
            {"id": "704", "title": "Binary Search", "difficulty": "Easy", "tags": ["array", "binary search"], "category": "Sorting & Searching"},
            {"id": "35", "title": "Search Insert Position", "difficulty": "Easy", "tags": ["array", "binary search"], "category": "Sorting & Searching"},
            {"id": "33", "title": "Search in Rotated Sorted Array", "difficulty": "Medium", "tags": ["array", "binary search"], "category": "Sorting & Searching"},
            {"id": "153", "title": "Find Minimum in Rotated Sorted Array", "difficulty": "Medium", "tags": ["array", "binary search"], "category": "Sorting & Searching"},
            
            # Backtracking
            {"id": "46", "title": "Permutations", "difficulty": "Medium", "tags": ["array", "backtracking"], "category": "Backtracking"},
            {"id": "78", "title": "Subsets", "difficulty": "Medium", "tags": ["array", "backtracking"], "category": "Backtracking"},
            {"id": "39", "title": "Combination Sum", "difficulty": "Medium", "tags": ["array", "backtracking"], "category": "Backtracking"},
            {"id": "17", "title": "Letter Combinations of Phone Number", "difficulty": "Medium", "tags": ["string", "backtracking"], "category": "Backtracking"},
            
            # Greedy
            {"id": "55", "title": "Jump Game", "difficulty": "Medium", "tags": ["array", "greedy"], "category": "Greedy Algorithms"},
            {"id": "45", "title": "Jump Game II", "difficulty": "Medium", "tags": ["array", "greedy"], "category": "Greedy Algorithms"},
            {"id": "134", "title": "Gas Station", "difficulty": "Medium", "tags": ["array", "greedy"], "category": "Greedy Algorithms"},
        ]

    @st.cache_data(ttl=3600)
    def get_problem(_self, problem_slug: str) -> Optional[Dict]:
        try:
            r = requests.get(f"{_self.base_url}/problem/{problem_slug}")
            return r.json() if r.status_code == 200 else None
        except:
            return None

    @st.cache_data(ttl=3600) 
    def search_problems(_self, query: str) -> List[Dict]:
        try:
            r = requests.get(f"{_self.base_url}/search/{query}")
            return r.json() if r.status_code == 200 else []
        except:
            return []

    def get_problems_by_category(self, category: str) -> List[Dict]:
        """Get problems filtered by category"""
        # Direct category match
        direct_matches = [p for p in self.problems_db if p.get('category') == category]
        if direct_matches:
            return direct_matches[:10]
        
        # Fallback - tag-based matching
        category_tags = {
            "Array/String Manipulation": ["array", "string", "hash table"],
            "Linked Lists": ["linked list"],
            "Trees & Graphs": ["tree", "graph", "depth-first search", "breadth-first search"],
            "Dynamic Programming": ["dynamic programming"],
            "Sorting & Searching": ["sorting", "binary search"],
            "Two Pointers": ["two pointers"],
            "Sliding Window": ["sliding window"],
            "Backtracking": ["backtracking"],
            "Greedy Algorithms": ["greedy"],
            "Divide & Conquer": ["divide and conquer"]
        }
        
        relevant_tags = category_tags.get(category, [category.lower()])
        filtered = [p for p in self.problems_db 
                   if any(tag in p.get("tags", []) for tag in relevant_tags)]
        
        return filtered[:10] if filtered else self.problems_db[:10]
