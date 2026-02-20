"""
AI Question Generator Service

Generates personalized interview questions based on:
- Resume skills and projects
- Interview type (technical, HR, mixed, project_viva)
- Auto-mixed difficulty (easy, medium, advanced)

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
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load question templates by type and skill."""
        return {
            "technical": {
                "python": [
                    {"q": "Explain the difference between a list and a tuple in Python.", "keywords": ["mutable", "immutable", "performance"], "level": "easy"},
                    {"q": "What are decorators in Python and when would you use them?", "keywords": ["wrapper", "function", "reusable"], "level": "medium"},
                    {"q": "How does Python's garbage collection work?", "keywords": ["reference counting", "memory", "gc module"], "level": "advanced"},
                    {"q": "Explain list comprehension vs generator expressions.", "keywords": ["memory", "lazy evaluation", "iteration"], "level": "medium"},
                    {"q": "What is the difference between a shallow copy and a deep copy?", "keywords": ["reference", "nested", "copy module"], "level": "easy"},
                    {"q": "Explain Python's Global Interpreter Lock (GIL) and its impact on multithreading.", "keywords": ["threading", "concurrency", "CPU-bound"], "level": "advanced"},
                ],
                "javascript": [
                    {"q": "What is the difference between let, const, and var?", "keywords": ["scope", "hoisting", "block"], "level": "easy"},
                    {"q": "Explain closures in JavaScript with an example.", "keywords": ["function", "scope", "lexical"], "level": "medium"},
                    {"q": "What is the event loop in JavaScript?", "keywords": ["async", "callback", "queue"], "level": "medium"},
                    {"q": "Describe the difference between == and === operators.", "keywords": ["type coercion", "strict", "comparison"], "level": "easy"},
                    {"q": "Explain prototypal inheritance in JavaScript.", "keywords": ["prototype chain", "object", "__proto__"], "level": "advanced"},
                ],
                "react": [
                    {"q": "What are React hooks and why were they introduced?", "keywords": ["useState", "useEffect", "functional"], "level": "easy"},
                    {"q": "Explain the virtual DOM and its benefits.", "keywords": ["performance", "diffing", "reconciliation"], "level": "medium"},
                    {"q": "What is the difference between state and props?", "keywords": ["mutable", "parent", "component"], "level": "easy"},
                    {"q": "How does React's reconciliation algorithm work?", "keywords": ["fiber", "diffing", "keys"], "level": "advanced"},
                ],
                "sql": [
                    {"q": "What is the difference between INNER JOIN and LEFT JOIN?", "keywords": ["matching", "null", "records"], "level": "easy"},
                    {"q": "Explain database indexing and when to use it.", "keywords": ["performance", "B-tree", "query"], "level": "medium"},
                    {"q": "What are ACID properties in databases?", "keywords": ["atomicity", "consistency", "isolation", "durability"], "level": "medium"},
                    {"q": "Explain database normalization and its different forms.", "keywords": ["1NF", "2NF", "3NF", "redundancy"], "level": "advanced"},
                ],
                "machine learning": [
                    {"q": "Explain the difference between supervised and unsupervised learning.", "keywords": ["labeled", "clustering", "classification"], "level": "easy"},
                    {"q": "What is overfitting and how do you prevent it?", "keywords": ["regularization", "validation", "generalization"], "level": "medium"},
                    {"q": "Describe the bias-variance tradeoff.", "keywords": ["underfitting", "complexity", "error"], "level": "advanced"},
                ],
                "general": [
                    {"q": "Explain Object-Oriented Programming principles.", "keywords": ["encapsulation", "inheritance", "polymorphism"], "level": "easy"},
                    {"q": "What is the difference between REST and GraphQL?", "keywords": ["endpoint", "query", "flexibility"], "level": "medium"},
                    {"q": "Describe the MVC architecture pattern.", "keywords": ["model", "view", "controller", "separation"], "level": "medium"},
                    {"q": "What are microservices and their benefits?", "keywords": ["scalability", "independent", "deployment"], "level": "advanced"},
                    {"q": "Explain version control and Git workflow.", "keywords": ["branch", "merge", "commit"], "level": "easy"},
                    {"q": "What is the difference between a stack and a queue?", "keywords": ["LIFO", "FIFO", "push", "pop"], "level": "easy"},
                    {"q": "Explain the concept of API rate limiting.", "keywords": ["throttle", "token bucket", "quota"], "level": "medium"},
                    {"q": "What is CI/CD and why is it important?", "keywords": ["continuous integration", "deployment", "automation"], "level": "medium"},
                ]
            },
            "hr": [
                {"q": "Tell me about yourself and your journey into tech.", "keywords": ["experience", "motivation", "goals"], "level": "easy"},
                {"q": "Describe a challenging project you worked on and how you handled it.", "keywords": ["problem", "solution", "outcome"], "level": "medium"},
                {"q": "Where do you see yourself in 5 years?", "keywords": ["growth", "career", "goals"], "level": "easy"},
                {"q": "How do you handle tight deadlines and pressure?", "keywords": ["prioritize", "manage", "communicate"], "level": "medium"},
                {"q": "Tell me about a time you worked in a team.", "keywords": ["collaboration", "conflict", "contribution"], "level": "easy"},
                {"q": "What are your strengths and weaknesses?", "keywords": ["self-aware", "improvement", "skills"], "level": "easy"},
                {"q": "Why do you want to work in this field?", "keywords": ["passion", "interest", "motivation"], "level": "easy"},
                {"q": "How do you stay updated with new technologies?", "keywords": ["learning", "resources", "curiosity"], "level": "easy"},
                {"q": "Describe a time when you had a conflict with a colleague. How did you resolve it?", "keywords": ["communication", "compromise", "empathy"], "level": "medium"},
                {"q": "Tell me about a time you failed. What did you learn from it?", "keywords": ["accountability", "growth", "reflection"], "level": "medium"},
                {"q": "How do you prioritize tasks when you have multiple deadlines?", "keywords": ["time management", "organization", "priority"], "level": "medium"},
                {"q": "What motivates you to do your best work?", "keywords": ["drive", "passion", "achievement"], "level": "easy"},
                {"q": "How would you handle a situation where you disagree with your manager's decision?", "keywords": ["respect", "communication", "professionalism"], "level": "advanced"},
                {"q": "Describe a situation where you took the initiative without being asked.", "keywords": ["proactive", "leadership", "ownership"], "level": "medium"},
                {"q": "How do you handle constructive criticism?", "keywords": ["openness", "improvement", "maturity"], "level": "easy"},
                {"q": "Tell me about a time you had to learn something quickly. How did you approach it?", "keywords": ["adaptability", "learning", "resourceful"], "level": "medium"},
                {"q": "What is your approach to work-life balance?", "keywords": ["boundaries", "productivity", "wellbeing"], "level": "easy"},
                {"q": "How do you handle ambiguity or unclear requirements in a project?", "keywords": ["clarification", "assumptions", "communication"], "level": "advanced"},
                {"q": "Describe a time when you went above and beyond in your work.", "keywords": ["dedication", "effort", "impact"], "level": "medium"},
                {"q": "What kind of work environment do you thrive in?", "keywords": ["culture", "collaboration", "preferences"], "level": "easy"},
            ],
            "project": [
                {"q": "Walk me through the architecture of your project: {project_name}.", "keywords": ["design", "components", "flow"], "level": "medium"},
                {"q": "What was the most challenging part of {project_name}?", "keywords": ["problem", "solution", "learning"], "level": "medium"},
                {"q": "What technologies did you use in {project_name} and why?", "keywords": ["tools", "decision", "alternatives"], "level": "easy"},
                {"q": "How would you improve {project_name} if given more time?", "keywords": ["features", "optimization", "scalability"], "level": "medium"},
                {"q": "Explain the database design for {project_name}.", "keywords": ["schema", "relationships", "queries"], "level": "advanced"},
                {"q": "How did you test {project_name}? What testing approach did you follow?", "keywords": ["unit tests", "integration", "manual"], "level": "medium"},
                {"q": "What were the key design decisions you made in {project_name}?", "keywords": ["tradeoffs", "architecture", "patterns"], "level": "advanced"},
                {"q": "How did you handle errors and edge cases in {project_name}?", "keywords": ["validation", "error handling", "edge cases"], "level": "medium"},
            ],
            "scenario": [
                {"q": "How would you design a URL shortening service?", "keywords": ["database", "hash", "scalability"], "level": "advanced"},
                {"q": "If a production system is running slow, how would you debug it?", "keywords": ["logs", "metrics", "profiling"], "level": "medium"},
                {"q": "How would you handle a security vulnerability in an app?", "keywords": ["patch", "audit", "communication"], "level": "medium"},
                {"q": "Design a simple e-commerce shopping cart system.", "keywords": ["database", "session", "inventory"], "level": "advanced"},
                {"q": "How would you scale an application to handle 10x traffic?", "keywords": ["caching", "load balancer", "database"], "level": "advanced"},
                {"q": "How would you design a notification system for a mobile app?", "keywords": ["push", "queue", "preferences"], "level": "medium"},
            ],
            "problem_solving": [
                {"q": "Given an array of integers, how would you find two numbers that sum to a target?", "keywords": ["hash map", "two pointer", "O(n)"], "level": "medium"},
                {"q": "How would you check if a string is a palindrome?", "keywords": ["reverse", "two pointer", "comparison"], "level": "easy"},
                {"q": "Explain how you would implement a basic cache.", "keywords": ["LRU", "hash map", "eviction"], "level": "advanced"},
                {"q": "How would you find the shortest path in a graph?", "keywords": ["BFS", "Dijkstra", "weighted"], "level": "advanced"},
                {"q": "How would you reverse a linked list?", "keywords": ["iterative", "pointers", "prev"], "level": "medium"},
            ]
        }
    
    def _assign_difficulty(self) -> str:
        """Randomly assign a difficulty level with a balanced distribution."""
        # ~30% easy, ~40% medium, ~30% advanced
        return random.choices(
            ["easy", "medium", "advanced"],
            weights=[30, 40, 30],
            k=1
        )[0]
    
    async def generate_questions(
        self,
        resume_data: Dict[str, Any],
        interview_type: str = "mixed",
        num_questions: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized interview questions.
        
        Args:
            resume_data: Parsed resume data with skills, projects, etc.
            interview_type: 'technical', 'hr', 'mixed', or 'project_viva'
            num_questions: Number of questions to generate
            
        Returns:
            List of question dictionaries
        """
        questions = []
        
        # Extract skills from resume
        skills = resume_data.get("extracted_skills", {})
        technical_skills = skills.get("technical", [])
        projects = resume_data.get("projects", [])
        
        if interview_type == "hr":
            questions = self._generate_hr_questions(num_questions)
        elif interview_type == "technical":
            questions = self._generate_technical_questions(technical_skills, num_questions)
        elif interview_type == "project_viva":
            questions = self._generate_project_questions(projects, technical_skills, num_questions)
        else:
            # mixed (default)
            questions = self._generate_mixed_questions(technical_skills, projects, num_questions)
        
        # Shuffle and limit
        random.shuffle(questions)
        questions = questions[:num_questions]
        
        # Add question numbers
        for i, q in enumerate(questions):
            q["question_number"] = i + 1
        
        logger.info(f"📝 Generated {len(questions)} {interview_type} questions")
        return questions
    
    def _generate_hr_questions(self, count: int) -> List[Dict[str, Any]]:
        """Generate only HR/behavioral questions."""
        questions = []
        available = list(self.question_templates["hr"])
        random.shuffle(available)
        
        for q in available[:count]:
            questions.append({
                "question_text": q["q"],
                "question_type": "hr",
                "skill_tested": "soft_skills",
                "difficulty": q.get("level", self._assign_difficulty()),
                "expected_keywords": q["keywords"]
            })
        
        return questions
    
    def _generate_technical_questions(self, technical_skills: List[str], count: int) -> List[Dict[str, Any]]:
        """Generate only technical, scenario, and problem-solving questions."""
        questions = []
        used_questions = set()
        
        # 1) Skill-based technical questions (~50% of count)
        skill_count = max(1, int(count * 0.5))
        for skill in technical_skills[:8]:
            skill_lower = skill.lower()
            skill_questions = self.question_templates["technical"].get(
                skill_lower,
                self.question_templates["technical"]["general"]
            )
            for q in skill_questions:
                if q["q"] not in used_questions and len(questions) < skill_count:
                    used_questions.add(q["q"])
                    questions.append({
                        "question_text": q["q"],
                        "question_type": "technical",
                        "skill_tested": skill,
                        "difficulty": q.get("level", self._assign_difficulty()),
                        "expected_keywords": q["keywords"]
                    })
        
        # Fill remaining skill slots with general technical
        while len(questions) < skill_count:
            q = random.choice(self.question_templates["technical"]["general"])
            if q["q"] not in used_questions:
                used_questions.add(q["q"])
                questions.append({
                    "question_text": q["q"],
                    "question_type": "technical",
                    "skill_tested": "general",
                    "difficulty": q.get("level", self._assign_difficulty()),
                    "expected_keywords": q["keywords"]
                })
        
        # 2) Scenario questions (~25% of count)
        scenario_count = max(1, int(count * 0.25))
        scenario_templates = list(self.question_templates["scenario"])
        random.shuffle(scenario_templates)
        for q in scenario_templates[:scenario_count]:
            if q["q"] not in used_questions:
                used_questions.add(q["q"])
                questions.append({
                    "question_text": q["q"],
                    "question_type": "scenario",
                    "skill_tested": "system_design",
                    "difficulty": q.get("level", self._assign_difficulty()),
                    "expected_keywords": q["keywords"]
                })
        
        # 3) Problem-solving questions (~25% of count)
        ps_count = max(1, int(count * 0.25))
        ps_templates = list(self.question_templates["problem_solving"])
        random.shuffle(ps_templates)
        for q in ps_templates[:ps_count]:
            if q["q"] not in used_questions:
                used_questions.add(q["q"])
                questions.append({
                    "question_text": q["q"],
                    "question_type": "problem_solving",
                    "skill_tested": "problem_solving",
                    "difficulty": q.get("level", self._assign_difficulty()),
                    "expected_keywords": q["keywords"]
                })
        
        return questions
    
    def _generate_project_questions(self, projects: List[Dict], technical_skills: List[str], count: int) -> List[Dict[str, Any]]:
        """Generate project-based questions (for Project Viva mode)."""
        questions = []
        used_questions = set()
        
        # Generate questions for each project
        for project in projects[:5]:
            project_name = project.get("name", "your project")
            templates = list(self.question_templates["project"])
            random.shuffle(templates)
            
            for template in templates[:3]:  # Up to 3 questions per project
                q_text = template["q"].replace("{project_name}", project_name)
                if q_text not in used_questions and len(questions) < count:
                    used_questions.add(q_text)
                    questions.append({
                        "question_text": q_text,
                        "question_type": "project",
                        "skill_tested": "project",
                        "difficulty": template.get("level", self._assign_difficulty()),
                        "expected_keywords": template["keywords"]
                    })
        
        # If we don't have enough project questions, fill with technical questions
        if len(questions) < count:
            remaining = count - len(questions)
            tech_questions = self._generate_technical_questions(technical_skills, remaining)
            questions.extend(tech_questions)
        
        return questions
    
    def _generate_mixed_questions(self, technical_skills: List[str], projects: List[Dict], count: int) -> List[Dict[str, Any]]:
        """Generate a balanced mix of all question types."""
        questions = []
        used_questions = set()
        
        # Distribution: 40% technical, 30% HR, 20% project, 10% scenario
        tech_count = max(1, int(count * 0.4))
        hr_count = max(1, int(count * 0.3))
        project_count = max(1, int(count * 0.2))
        scenario_count = max(1, count - tech_count - hr_count - project_count)
        
        # Technical questions based on skills
        for skill in technical_skills[:5]:
            skill_lower = skill.lower()
            skill_questions = self.question_templates["technical"].get(
                skill_lower,
                self.question_templates["technical"]["general"]
            )
            if skill_questions and len(questions) < tech_count:
                q = random.choice(skill_questions)
                if q["q"] not in used_questions:
                    used_questions.add(q["q"])
                    questions.append({
                        "question_text": q["q"],
                        "question_type": "technical",
                        "skill_tested": skill,
                        "difficulty": q.get("level", self._assign_difficulty()),
                        "expected_keywords": q["keywords"]
                    })
        
        # Fill remaining tech with general
        while len(questions) < tech_count:
            q = random.choice(self.question_templates["technical"]["general"])
            if q["q"] not in used_questions:
                used_questions.add(q["q"])
                questions.append({
                    "question_text": q["q"],
                    "question_type": "technical",
                    "skill_tested": "general",
                    "difficulty": q.get("level", self._assign_difficulty()),
                    "expected_keywords": q["keywords"]
                })
        
        # HR questions
        hr_templates = list(self.question_templates["hr"])
        random.shuffle(hr_templates)
        for q in hr_templates[:hr_count]:
            questions.append({
                "question_text": q["q"],
                "question_type": "hr",
                "skill_tested": "soft_skills",
                "difficulty": q.get("level", self._assign_difficulty()),
                "expected_keywords": q["keywords"]
            })
        
        # Project questions
        for project in projects[:project_count]:
            project_name = project.get("name", "your project")
            template = random.choice(self.question_templates["project"])
            q_text = template["q"].replace("{project_name}", project_name)
            if q_text not in used_questions:
                used_questions.add(q_text)
                questions.append({
                    "question_text": q_text,
                    "question_type": "project",
                    "skill_tested": "project",
                    "difficulty": template.get("level", self._assign_difficulty()),
                    "expected_keywords": template["keywords"]
                })
        
        # Scenario questions
        scenario_templates = list(self.question_templates["scenario"])
        random.shuffle(scenario_templates)
        for q in scenario_templates[:scenario_count]:
            questions.append({
                "question_text": q["q"],
                "question_type": "scenario",
                "skill_tested": "problem_solving",
                "difficulty": q.get("level", self._assign_difficulty()),
                "expected_keywords": q["keywords"]
            })
        
        return questions
    
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
