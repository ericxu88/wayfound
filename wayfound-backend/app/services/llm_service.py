# app/services/llm_service.py
import os
import json
from typing import Dict, List, Optional
from openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class MilestoneModel(BaseModel):
    id: str = Field(description="Unique identifier for the milestone")
    day: int = Field(description="Day number when this milestone should be completed")
    title: str = Field(description="Clear, actionable title for the milestone")
    description: str = Field(description="Detailed description of what to accomplish")
    tasks: List[str] = Field(description="List of specific tasks to complete")
    resources: List[str] = Field(description="List of recommended resources (YouTube channels, books, tools, etc.)")

class RoadmapModel(BaseModel):
    domain: str = Field(description="Classified domain (cooking, fitness, programming, language, art, general)")
    estimated_hours_total: int = Field(description="Total estimated hours needed")
    difficulty_level: str = Field(description="Beginner, Intermediate, or Advanced")
    milestones: List[MilestoneModel] = Field(description="List of milestones for the roadmap")

class RoadmapGenerator:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠️  OPENAI_API_KEY not found in environment variables")
            print("   Add it to your .env file: OPENAI_API_KEY=sk-your-key-here")
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)
            print("✅ OpenAI client initialized successfully")
        
        self.parser = PydanticOutputParser(pydantic_object=RoadmapModel)
        
    def classify_domain(self, goal_text: str) -> str:
        """Use AI to classify the domain of the goal"""
        
        if not self.client:
            return self._classify_domain_simple(goal_text)
        
        prompt = f"""
        Classify this learning goal into one of these domains: cooking, fitness, programming, language, art, general
        
        Goal: "{goal_text}"
        
        Respond with only the domain name (lowercase).
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.1
            )
            
            domain = response.choices[0].message.content.strip().lower()
            valid_domains = ["cooking", "fitness", "programming", "language", "art", "general"]
            
            return domain if domain in valid_domains else "general"
            
        except Exception as e:
            print(f"Error classifying domain: {e}")
            return self._classify_domain_simple(goal_text)
    
    def _classify_domain_simple(self, goal_text: str) -> str:
        """Simple keyword-based domain classification (fallback)"""
        goal_lower = goal_text.lower()
        
        if any(word in goal_lower for word in ["cook", "recipe", "bake", "food", "kitchen", "chef", "ramen"]):
            return "cooking"
        elif any(word in goal_lower for word in ["fit", "gym", "workout", "muscle", "weight", "exercise"]):
            return "fitness"
        elif any(word in goal_lower for word in ["code", "program", "python", "javascript", "app", "software"]):
            return "programming"
        elif any(word in goal_lower for word in ["language", "spanish", "french", "italian", "speak"]):
            return "language"
        elif any(word in goal_lower for word in ["paint", "draw", "art", "sketch", "canvas"]):
            return "art"
        else:
            return "general"
    
    def generate_roadmap(self, goal_text: str, timeline_days: int, survey_data: Dict = None) -> Dict:
        """Generate personalized roadmap using OpenAI"""
        
        # Check if OpenAI client is available
        if not self.client:
            print("🔄 OpenAI not available, using fallback generation")
            domain = self._classify_domain_simple(goal_text)
            return self._generate_fallback_roadmap(goal_text, timeline_days, domain)
        
        # Classify domain first
        domain = self.classify_domain(goal_text)
        
        # Build the prompt
        prompt = self._build_roadmap_prompt(goal_text, timeline_days, domain, survey_data)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",  # Use GPT-4 for better roadmap quality
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
                temperature=0.7
            )
            
            # Parse the JSON response
            roadmap_data = json.loads(response.choices[0].message.content)
            
            # Validate and structure the response
            return self._validate_roadmap(roadmap_data, domain, timeline_days)
            
        except Exception as e:
            print(f"Error generating roadmap: {e}")
            # Fall back to mock generation if AI fails
            return self._generate_fallback_roadmap(goal_text, timeline_days, domain)
    
    def _build_roadmap_prompt(self, goal_text: str, timeline_days: int, domain: str, survey_data: Dict = None) -> str:
        """Build the prompt for roadmap generation"""
        
        # Base context
        user_context = ""
        if survey_data:
            user_context = f"""
User Context:
- Skill Level: {survey_data.get('skill_level', 'Beginner')}
- Available Time: {survey_data.get('time_per_day', '30 minutes')} per day
- Learning Style: {survey_data.get('learning_style', 'Mixed')}
- Timeline Preference: {survey_data.get('timeline_preference', 'Flexible')}
"""
        
        # Domain-specific instructions
        domain_instructions = self._get_domain_instructions(domain)
        
        prompt = f"""
Create a detailed {timeline_days}-day learning roadmap for: "{goal_text}"

{user_context}

Domain: {domain}
{domain_instructions}

Requirements:
1. Create {max(2, min(8, timeline_days // 7))} milestones spread across {timeline_days} days
2. Each milestone should be achievable and build on previous ones
3. Include specific, actionable tasks for each milestone
4. Provide relevant resources (YouTube channels, websites, books, tools)
5. Make it practical and realistic for the given timeline

Respond with a JSON object in this exact format:
{{
  "domain": "{domain}",
  "estimated_hours_total": <number>,
  "difficulty_level": "Beginner|Intermediate|Advanced",
  "milestones": [
    {{
      "id": "milestone_1",
      "day": <day_number>,
      "title": "<milestone_title>",
      "description": "<detailed_description>",
      "tasks": ["<task1>", "<task2>", "<task3>"],
      "resources": ["<resource1>", "<resource2>", "<resource3>"]
    }}
  ]
}}

Ensure the JSON is valid and complete.
"""
        
        return prompt
    
    def _get_domain_instructions(self, domain: str) -> str:
        """Get domain-specific instructions for roadmap generation"""
        
        instructions = {
            "cooking": """
Focus on:
- Knife skills and kitchen safety
- Basic cooking techniques (sautéing, roasting, etc.)
- Understanding ingredients and flavors
- Recipe progression from simple to complex
- Kitchen equipment and organization
""",
            "fitness": """
Focus on:
- Proper form and injury prevention
- Progressive overload principles
- Nutrition fundamentals
- Rest and recovery
- Goal-specific training (strength, cardio, etc.)
""",
            "programming": """
Focus on:
- Development environment setup
- Core programming concepts
- Hands-on project building
- Version control and best practices
- Problem-solving and debugging skills
""",
            "language": """
Focus on:
- Practical conversation skills
- Grammar fundamentals
- Vocabulary building strategies
- Cultural context and phrases
- Speaking and listening practice
""",
            "art": """
Focus on:
- Basic techniques and materials
- Fundamental principles (composition, color, etc.)
- Practice exercises and studies
- Style development and creativity
- Building a portfolio of work
""",
            "general": """
Focus on:
- Breaking down the goal into learnable components
- Building foundational knowledge first
- Practical application and practice
- Community and resource discovery
- Continuous improvement and adaptation
"""
        }
        
        return instructions.get(domain, instructions["general"])
    
    def _validate_roadmap(self, roadmap_data: Dict, domain: str, timeline_days: int) -> Dict:
        """Validate and clean up the AI-generated roadmap"""
        
        # Ensure required fields exist
        validated = {
            "domain": roadmap_data.get("domain", domain),
            "estimated_hours_total": roadmap_data.get("estimated_hours_total", timeline_days * 2),
            "difficulty_level": roadmap_data.get("difficulty_level", "Beginner"),
            "milestones": []
        }
        
        # Validate milestones
        milestones = roadmap_data.get("milestones", [])
        for i, milestone in enumerate(milestones):
            validated_milestone = {
                "id": milestone.get("id", f"milestone_{i+1}"),
                "day": milestone.get("day", (i * (timeline_days // len(milestones))) + 1),
                "title": milestone.get("title", f"Milestone {i+1}"),
                "description": milestone.get("description", ""),
                "tasks": milestone.get("tasks", []),
                "resources": milestone.get("resources", []),
                "completed": False
            }
            validated["milestones"].append(validated_milestone)
        
        return validated
    
    def _generate_fallback_roadmap(self, goal_text: str, timeline_days: int, domain: str) -> Dict:
        """Generate a simple fallback roadmap if AI fails"""
        
        num_milestones = max(2, min(4, timeline_days // 7))
        days_per_milestone = timeline_days // num_milestones
        
        milestones = []
        titles = ["Getting Started", "Building Foundation", "Skill Development", "Mastery & Practice"]
        
        for i in range(num_milestones):
            milestone = {
                "id": f"milestone_{i+1}",
                "day": (i * days_per_milestone) + 1,
                "title": titles[min(i, len(titles)-1)],
                "description": f"Focus on {goal_text} fundamentals",
                "tasks": [
                    "Research and plan your approach",
                    "Practice basic skills",
                    "Apply what you've learned"
                ],
                "resources": [
                    "YouTube tutorials",
                    "Online courses",
                    "Community forums"
                ],
                "completed": False
            }
            milestones.append(milestone)
        
        return {
            "domain": domain,
            "estimated_hours_total": timeline_days * 2,
            "difficulty_level": "Beginner",
            "milestones": milestones
        }

# Create a global instance
roadmap_generator = RoadmapGenerator()