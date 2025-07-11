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
            print(f"🔄 Calling OpenAI GPT-4 for roadmap generation...")
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use GPT-3.5 for better compatibility
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000,
                temperature=0.7
            )
            
            print(f"✅ OpenAI response received")
            response_content = response.choices[0].message.content
            print(f"📝 Response length: {len(response_content)} characters")
            
            # Parse the JSON response
            roadmap_data = json.loads(response_content)
            print(f"🎯 Parsed roadmap with {len(roadmap_data.get('milestones', []))} milestones")
            
            # Validate and structure the response
            return self._validate_roadmap(roadmap_data, domain, timeline_days)
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"🔍 Raw response: {response_content[:500]}...")
            return self._generate_fallback_roadmap(goal_text, timeline_days, domain)
        except Exception as e:
            print(f"❌ Error generating roadmap: {e}")
            print(f"🔄 Falling back to mock generation")
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
4. **CRITICAL: Provide SPECIFIC, HIGH-QUALITY resources for each milestone:**
   - Exact YouTube channel names (e.g., "Joshua Weissman", "Bon Appétit")
   - Specific online courses (e.g., "MasterClass: Gordon Ramsay Teaches Cooking")
   - Actual book titles and authors
   - Specific tools, apps, or websites
   - Real blogs, articles, or documentation
   - NO generic phrases like "YouTube tutorials" or "online courses"

5. Make it practical and realistic for the given timeline

Example of good resources:
- "Joshua Weissman's Ramen series on YouTube"
- "Ivan Ramen cookbook by Ivan Orkin"
- "Ramen_Lord's comprehensive guide on Reddit r/ramen"
- "Kansui (alkaline mineral water) for noodle making"

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
      "tasks": ["<specific_task1>", "<specific_task2>", "<specific_task3>"],
      "resources": ["<specific_resource1>", "<specific_resource2>", "<specific_resource3>"]
    }}
  ]
}}

Ensure the JSON is valid and complete. Focus on providing REAL, SPECIFIC resources that actually exist.
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

Suggest SPECIFIC resources like:
- Exact YouTube channels: "Joshua Weissman", "Bon Appétit", "Babish Culinary Universe"
- Specific cookbooks: "Salt Fat Acid Heat by Samin Nosrat"
- Cooking schools: "Rouxbe Online Culinary School"
- Equipment brands: "Victorinox knives", "Lodge cast iron"
""",
            "fitness": """
Focus on:
- Proper form and injury prevention
- Progressive overload principles
- Nutrition fundamentals
- Rest and recovery
- Goal-specific training (strength, cardio, etc.)

Suggest SPECIFIC resources like:
- YouTube channels: "AthleanX", "Jeff Nippard", "Calisthenic Movement"
- Apps: "MyFitnessPal", "Strong (iOS)", "Jefit"
- Programs: "StrongLifts 5x5", "Starting Strength"
- Books: "Bigger Leaner Stronger by Michael Matthews"
""",
            "programming": """
Focus on:
- Development environment setup
- Core programming concepts
- Hands-on project building
- Version control and best practices
- Problem-solving and debugging skills

Suggest SPECIFIC resources like:
- Platforms: "FreeCodeCamp", "The Odin Project", "Codecademy"
- YouTube channels: "Traversy Media", "Net Ninja", "Programming with Mosh"
- Documentation: "MDN Web Docs", "React official docs"
- Tools: "VS Code", "Git/GitHub", "Stack Overflow"
""",
            "language": """
Focus on:
- Practical conversation skills
- Grammar fundamentals
- Vocabulary building strategies
- Cultural context and phrases
- Speaking and listening practice

Suggest SPECIFIC resources like:
- Apps: "Duolingo", "Babbel", "HelloTalk"
- YouTube channels: "SpanishDict", "Français avec Pierre"
- Websites: "conjuguemos.com", "News in Slow Spanish"
- Books: "Madrigal's Magic Key to Spanish Words"
""",
            "art": """
Focus on:
- Basic techniques and materials
- Fundamental principles (composition, color, etc.)
- Practice exercises and studies
- Style development and creativity
- Building a portfolio of work

Suggest SPECIFIC resources like:
- YouTube channels: "Proko", "Marco Bucci", "Sinix Design"
- Online courses: "Schoolism", "New Masters Academy"
- Books: "Drawing on the Right Side of the Brain by Betty Edwards"
- Software: "Photoshop", "Procreate", "Clip Studio Paint"
""",
            "general": """
Focus on:
- Breaking down the goal into learnable components
- Building foundational knowledge first
- Practical application and practice
- Community and resource discovery
- Continuous improvement and adaptation

Always suggest SPECIFIC, real resources rather than generic ones.
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
        """Generate a smart fallback roadmap if AI fails"""
        
        print(f"🔄 Generating smart fallback for domain: {domain}")
        
        num_milestones = max(2, min(6, timeline_days // 7))
        days_per_milestone = timeline_days // num_milestones
        
        milestones = []
        
        # Domain-specific milestone templates
        domain_templates = {
            "cooking": {
                "titles": ["Kitchen Setup & Basics", "Fundamental Techniques", "Recipe Mastery", "Advanced Skills", "Flavor Perfection", "Presentation & Style"],
                "descriptions": [
                    "Set up your kitchen workspace and learn essential knife skills and safety",
                    "Master fundamental cooking techniques like sautéing, boiling, and seasoning",
                    "Practice core recipes and build confidence with timing and ingredients",
                    "Learn advanced techniques and tackle more complex preparations",
                    "Develop your palate and perfect flavor balancing",
                    "Focus on plating, presentation, and developing your personal style"
                ],
                "tasks": [
                    ["Organize kitchen tools and workspace", "Learn basic knife cuts and safety", "Practice proper posture and grip", "Stock essential ingredients"],
                    ["Master sautéing and heat control", "Practice seasoning techniques", "Learn timing for multiple dishes", "Understand ingredient interactions"],
                    ["Cook 3-5 foundational recipes", "Document cooking notes and adjustments", "Practice mise en place", "Taste and adjust seasoning"],
                    ["Try complex multi-step recipes", "Learn sauce-making techniques", "Practice temperature control", "Experiment with ingredient substitutions"],
                    ["Develop signature flavor combinations", "Practice balancing sweet, salty, umami", "Learn wine/sake pairing basics", "Create recipe variations"],
                    ["Master plating techniques", "Practice food photography", "Develop presentation style", "Share dishes with others for feedback"]
                ]
            },
            "fitness": {
                "titles": ["Foundation & Assessment", "Form & Technique", "Building Strength", "Progressive Training", "Performance Optimization", "Long-term Success"],
                "descriptions": [
                    "Assess current fitness level and establish proper foundation",
                    "Learn correct form for all exercises and movement patterns", 
                    "Focus on building base strength with progressive overload",
                    "Advance to intermediate techniques and specialized training",
                    "Optimize performance through advanced programming",
                    "Develop sustainable long-term fitness habits"
                ],
                "tasks": [
                    ["Complete fitness assessment", "Set realistic goals", "Learn basic movements", "Establish workout schedule"],
                    ["Master bodyweight exercises", "Learn proper lifting form", "Practice mobility routines", "Focus on breathing techniques"],
                    ["Implement progressive overload", "Track weights and reps", "Maintain consistent schedule", "Focus on compound movements"],
                    ["Add advanced exercises", "Implement periodization", "Optimize nutrition timing", "Monitor recovery metrics"],
                    ["Fine-tune programming", "Track performance metrics", "Optimize sleep and recovery", "Consider specialized coaching"],
                    ["Develop maintenance routine", "Set new challenges", "Help others with fitness", "Celebrate achievements"]
                ]
            },
            "programming": {
                "titles": ["Environment Setup", "Programming Fundamentals", "Project Building", "Advanced Concepts", "Best Practices", "Professional Development"],
                "descriptions": [
                    "Set up development environment and learn basic programming concepts",
                    "Master fundamental programming concepts and syntax",
                    "Build real projects to apply your knowledge practically",
                    "Learn advanced programming patterns and concepts",
                    "Adopt industry best practices and clean code principles",
                    "Develop professional skills and contribute to the community"
                ],
                "tasks": [
                    ["Install development tools and IDE", "Learn version control basics", "Write your first 'Hello World'", "Understand basic syntax"],
                    ["Master variables and data types", "Learn control flow and loops", "Practice with functions", "Debug simple programs"],
                    ["Build a small personal project", "Learn to break down problems", "Practice iterative development", "Add features gradually"],
                    ["Learn object-oriented programming", "Understand design patterns", "Practice with APIs", "Work with databases"],
                    ["Learn code review practices", "Write unit tests", "Follow style guides", "Optimize for performance"],
                    ["Contribute to open source", "Build a portfolio", "Network with developers", "Continue learning new technologies"]
                ]
            }
        }
        
        # Get templates for domain or use general
        if domain in domain_templates:
            templates = domain_templates[domain]
        else:
            templates = {
                "titles": ["Getting Started", "Building Foundation", "Skill Development", "Advanced Practice", "Mastery Focus", "Continuous Growth"],
                "descriptions": [
                    f"Begin your journey with {goal_text} by establishing fundamentals",
                    "Build a solid foundation of knowledge and basic skills",
                    "Develop intermediate capabilities through focused practice",
                    "Apply advanced techniques and tackle challenging projects",
                    "Refine your skills and develop personal mastery",
                    "Continue growing and helping others in your journey"
                ],
                "tasks": [
                    ["Research your goal thoroughly", "Gather necessary resources", "Create a detailed learning plan", "Set up your workspace"],
                    ["Study fundamental concepts", "Practice basic skills daily", "Join relevant communities", "Find mentors or guides"],
                    ["Apply knowledge practically", "Seek feedback regularly", "Overcome initial challenges", "Build confidence"],
                    ["Take on complex challenges", "Experiment with variations", "Develop problem-solving skills", "Share your progress"],
                    ["Perfect your technique", "Develop signature style", "Teach others your skills", "Set higher standards"],
                    ["Pursue advanced opportunities", "Mentor newcomers", "Continue learning", "Set new challenges"]
                ]
            }
        
        # Generate milestones
        for i in range(num_milestones):
            day = (i * days_per_milestone) + 1
            index = min(i, len(templates["titles"]) - 1)
            
            # Customize for specific goal if possible
            title = templates["titles"][index]
            if domain == "cooking" and "ramen" in goal_text.lower():
                ramen_titles = ["Ramen Fundamentals", "Broth Mastery", "Noodle Perfection", "Toppings & Assembly", "Regional Styles", "Personal Signature"]
                if i < len(ramen_titles):
                    title = ramen_titles[i]
            
            milestone = {
                "id": f"milestone_{i+1}",
                "day": day,
                "title": title,
                "description": templates["descriptions"][index],
                "tasks": templates["tasks"][index],
                "resources": self._get_domain_resources(domain),
                "completed": False
            }
            milestones.append(milestone)
        
        return {
            "domain": domain,
            "estimated_hours_total": timeline_days * 2,
            "difficulty_level": "Intermediate",
            "milestones": milestones
        }
    
    def _get_domain_resources(self, domain: str) -> List[str]:
        """Get domain-specific resources"""
        domain_resources = {
            "cooking": [
                "Joshua Weissman YouTube channel",
                "Salt Fat Acid Heat by Samin Nosrat", 
                "Serious Eats website",
                "Bon Appétit YouTube channel"
            ],
            "fitness": [
                "AthleanX YouTube channel",
                "MyFitnessPal app for tracking",
                "StrongLifts 5x5 program",
                "Starting Strength book by Mark Rippetoe"
            ],
            "programming": [
                "FreeCodeCamp curriculum",
                "The Odin Project",
                "Traversy Media YouTube channel",
                "MDN Web Docs for reference"
            ],
            "language": [
                "Duolingo app for daily practice",
                "HelloTalk for language exchange",
                "News in Slow [Language] podcasts",
                "Anki flashcard app for vocabulary"
            ],
            "art": [
                "Proko YouTube channel",
                "Drawing on the Right Side of the Brain book",
                "Procreate app for digital art",
                "Schoolism online courses"
            ]
        }
        
        return domain_resources.get(domain, [
            "Khan Academy for fundamentals",
            "YouTube channel searches for your topic",
            "Reddit communities for advice",
            "Local classes or workshops"
        ])

# Create a global instance
roadmap_generator = RoadmapGenerator()