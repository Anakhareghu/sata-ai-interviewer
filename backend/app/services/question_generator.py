"""
AI Question Generator Service

Generates personalized interview questions based on:
- Resume skills and projects
- Academic performance from SATA
- Difficulty level
- Question type (technical, HR, project, scenario)

Uses template-based generation with NLP enhancement for fast, lightweight operation.
"""

import random
import logging
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)


class QuestionGenerator:
    """Generate personalized interview questions."""
    
    def __init__(self):
        self._initialized = False
        self.question_templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, List[Dict]]:
        """Load question templates by type and skill."""
        return {
            "technical": {
                "python": [
                    {"q": "Explain the difference between a list and a tuple in Python.", "keywords": ["mutable", "immutable", "performance"]},
                    {"q": "What are decorators in Python and when would you use them?", "keywords": ["wrapper", "function", "reusable"]},
                    {"q": "How does Python's garbage collection work?", "keywords": ["reference counting", "memory", "gc module"]},
                    {"q": "Explain list comprehension vs generator expressions.", "keywords": ["memory", "lazy evaluation", "iteration"]},
                ],
                "javascript": [
                    {"q": "What is the difference between let, const, and var?", "keywords": ["scope", "hoisting", "block"]},
                    {"q": "Explain closures in JavaScript with an example.", "keywords": ["function", "scope", "lexical"]},
                    {"q": "What is the event loop in JavaScript?", "keywords": ["async", "callback", "queue"]},
                    {"q": "Describe the difference between == and === operators.", "keywords": ["type coercion", "strict", "comparison"]},
                ],
                "react": [
                    {"q": "What are React hooks and why were they introduced?", "keywords": ["useState", "useEffect", "functional"]},
                    {"q": "Explain the virtual DOM and its benefits.", "keywords": ["performance", "diffing", "reconciliation"]},
                    {"q": "What is the difference between state and props?", "keywords": ["mutable", "parent", "component"]},
                ],
                "sql": [
                    {"q": "What is the difference between INNER JOIN and LEFT JOIN?", "keywords": ["matching", "null", "records"]},
                    {"q": "Explain database indexing and when to use it.", "keywords": ["performance", "B-tree", "query"]},
                    {"q": "What are ACID properties in databases?", "keywords": ["atomicity", "consistency", "isolation", "durability"]},
                ],
                "machine learning": [
                    {"q": "Explain the difference between supervised and unsupervised learning.", "keywords": ["labeled", "clustering", "classification"]},
                    {"q": "What is overfitting and how do you prevent it?", "keywords": ["regularization", "validation", "generalization"]},
                    {"q": "Describe the bias-variance tradeoff.", "keywords": ["underfitting", "complexity", "error"]},
                ],
                "general": [
                    {"q": "Explain Object-Oriented Programming principles.", "keywords": ["encapsulation", "inheritance", "polymorphism"]},
                    {"q": "What is the difference between REST and GraphQL?", "keywords": ["endpoint", "query", "flexibility"]},
                    {"q": "Describe the MVC architecture pattern.", "keywords": ["model", "view", "controller", "separation"]},
                    {"q": "What are microservices and their benefits?", "keywords": ["scalability", "independent", "deployment"]},
                    {"q": "Explain version control and Git workflow.", "keywords": ["branch", "merge", "commit"]},
                ]
            },
            "hr": [
                {"q": "Tell me about yourself and your journey into tech.", "keywords": ["experience", "motivation", "goals"]},
                {"q": "Describe a challenging project you worked on and how you handled it.", "keywords": ["problem", "solution", "outcome"]},
                {"q": "Where do you see yourself in 5 years?", "keywords": ["growth", "career", "goals"]},
                {"q": "How do you handle tight deadlines and pressure?", "keywords": ["prioritize", "manage", "communicate"]},
                {"q": "Tell me about a time you worked in a team.", "keywords": ["collaboration", "conflict", "contribution"]},
                {"q": "What are your strengths and weaknesses?", "keywords": ["self-aware", "improvement", "skills"]},
                {"q": "Why do you want to work in this field?", "keywords": ["passion", "interest", "motivation"]},
                {"q": "How do you stay updated with new technologies?", "keywords": ["learning", "resources", "curiosity"]},
            ],
            "project": [
                {"q": "Walk me through the architecture of your project: {project_name}.", "keywords": ["design", "components", "flow"]},
                {"q": "What was the most challenging part of {project_name}?", "keywords": ["problem", "solution", "learning"]},
                {"q": "What technologies did you use in {project_name} and why?", "keywords": ["tools", "decision", "alternatives"]},
                {"q": "How would you improve {project_name} if given more time?", "keywords": ["features", "optimization", "scalability"]},
                {"q": "Explain the database design for {project_name}.", "keywords": ["schema", "relationships", "queries"]},
            ],
            "scenario": [
                {"q": "How would you design a URL shortening service?", "keywords": ["database", "hash", "scalability"]},
                {"q": "If a production system is running slow, how would you debug it?", "keywords": ["logs", "metrics", "profiling"]},
                {"q": "How would you handle a security vulnerability in an app?", "keywords": ["patch", "audit", "communication"]},
                {"q": "Design a simple e-commerce shopping cart system.", "keywords": ["database", "session", "inventory"]},
                {"q": "How would you scale an application to handle 10x traffic?", "keywords": ["caching", "load balancer", "database"]},
            ],
            "problem_solving": [
                {"q": "Given an array of integers, how would you find two numbers that sum to a target?", "keywords": ["hash map", "two pointer", "O(n)"]},
                {"q": "How would you check if a string is a palindrome?", "keywords": ["reverse", "two pointer", "comparison"]},
                {"q": "Explain how you would implement a basic cache.", "keywords": ["LRU", "hash map", "eviction"]},
                {"q": "How would you find the shortest path in a graph?", "keywords": ["BFS", "Dijkstra", "weighted"]},
            ]
        }
    
    async def generate_questions(
        self,
        resume_data: Dict[str, Any],
        academic_data: Optional[Dict] = None,
        difficulty: str = "medium",
        num_questions: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized interview questions.
        
        Args:
            resume_data: Parsed resume data with skills, projects, etc.
            academic_data: Optional academic performance data from SATA
            difficulty: easy, medium, or advanced
            num_questions: Number of questions to generate
            
        Returns:
            List of question dictionaries
        """
        questions = []
        
        # Extract skills from resume
        skills = resume_data.get("extracted_skills", {})
        technical_skills = skills.get("technical", [])
        projects = resume_data.get("projects", [])
        
        # Determine question distribution
        distribution = self._get_distribution(difficulty)
        
        # Generate technical questions based on skills
        tech_count = int(num_questions * distribution["technical"])
        for skill in technical_skills[:5]:
            skill_lower = skill.lower()
            skill_questions = self.question_templates["technical"].get(
                skill_lower, 
                self.question_templates["technical"]["general"]
            )
            if skill_questions and len(questions) < tech_count:
                q = random.choice(skill_questions)
                questions.append({
                    "question_text": q["q"],
                    "question_type": "technical",
                    "skill_tested": skill,
                    "difficulty": difficulty,
                    "expected_keywords": q["keywords"]
                })
        
        # Fill remaining tech questions with general
        while len(questions) < tech_count:
            q = random.choice(self.question_templates["technical"]["general"])
            questions.append({
                "question_text": q["q"],
                "question_type": "technical",
                "skill_tested": "general",
                "difficulty": difficulty,
                "expected_keywords": q["keywords"]
            })
        
        # Add project-based questions
        project_count = int(num_questions * distribution["project"])
        for project in projects[:project_count]:
            project_name = project.get("name", "your project")
            template = random.choice(self.question_templates["project"])
            questions.append({
                "question_text": template["q"].replace("{project_name}", project_name),
                "question_type": "project",
                "skill_tested": "project",
                "difficulty": difficulty,
                "expected_keywords": template["keywords"]
            })
        
        # Add HR questions
        hr_count = int(num_questions * distribution["hr"])
        for _ in range(hr_count):
            q = random.choice(self.question_templates["hr"])
            questions.append({
                "question_text": q["q"],
                "question_type": "hr",
                "skill_tested": "soft_skills",
                "difficulty": "medium",
                "expected_keywords": q["keywords"]
            })
        
        # Add scenario questions for advanced
        scenario_count = int(num_questions * distribution["scenario"])
        for _ in range(scenario_count):
            q = random.choice(self.question_templates["scenario"])
            questions.append({
                "question_text": q["q"],
                "question_type": "scenario",
                "skill_tested": "problem_solving",
                "difficulty": difficulty,
                "expected_keywords": q["keywords"]
            })
        
        # Shuffle and limit
        random.shuffle(questions)
        questions = questions[:num_questions]
        
        # Add question numbers
        for i, q in enumerate(questions):
            q["question_number"] = i + 1
        
        logger.info(f"📝 Generated {len(questions)} questions")
        return questions
    
    def _get_distribution(self, difficulty: str) -> Dict[str, float]:
        """Get question type distribution based on difficulty."""
        distributions = {
            "easy": {"technical": 0.4, "hr": 0.4, "project": 0.2, "scenario": 0.0},
            "medium": {"technical": 0.4, "hr": 0.3, "project": 0.2, "scenario": 0.1},
            "advanced": {"technical": 0.5, "hr": 0.1, "project": 0.2, "scenario": 0.2}
        }
        return distributions.get(difficulty, distributions["medium"])
    
    async def generate_followup(
        self,
        original_question: str,
        student_response: str,
        score: float
    ) -> Optional[str]:
        """Generate a follow-up question based on the response quality."""
        if score < 5:
            return "Could you elaborate more on that? Perhaps with a specific example?"
        elif score < 7:
            return "Good answer. Can you think of any edge cases or limitations?"
        return None


# Global instance
question_generator = QuestionGenerator()
