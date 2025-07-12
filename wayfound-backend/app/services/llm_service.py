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
        """Generate personalized roadmap using OpenAI with survey data"""
        
        # Check if OpenAI client is available
        if not self.client:
            print("🔄 OpenAI not available, using fallback generation")
            domain = self._classify_domain_simple(goal_text)
            return self._generate_fallback_roadmap(goal_text, timeline_days, domain, survey_data)
        
        # Classify domain first
        domain = self.classify_domain(goal_text)
        
        # Build the prompt with survey data
        prompt = self._build_roadmap_prompt(goal_text, timeline_days, domain, survey_data)
        
        try:
            print(f"🔄 Calling OpenAI GPT-3.5 for roadmap generation...")
            print(f"📋 Survey data: {survey_data}")
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3500,  # Increased for more detailed responses
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
            return self._generate_fallback_roadmap(goal_text, timeline_days, domain, survey_data)
        except Exception as e:
            print(f"❌ Error generating roadmap: {e}")
            print(f"🔄 Falling back to smart generation")
            return self._generate_fallback_roadmap(goal_text, timeline_days, domain, survey_data)
    
    def _build_roadmap_prompt(self, goal_text: str, timeline_days: int, domain: str, survey_data: Dict = None) -> str:
        """Build the prompt for roadmap generation with survey data"""
        
        # Build user context from survey data
        user_context = ""
        if survey_data:
            skill_level = survey_data.get('skillLevel', 'Beginner')
            time_per_day = survey_data.get('timePerDay', '30 minutes')
            learning_style = survey_data.get('learningStyle', 'Mixed')
            timeline_pref = survey_data.get('timelinePreference', 'Flexible')
            
            user_context = f"""
User Profile:
- Skill Level: {skill_level}
- Available Time: {time_per_day} per day
- Learning Style: {learning_style}
- Timeline Preference: {timeline_pref}
- Estimated total hours available: {self._calculate_total_hours(time_per_day, timeline_days)}

IMPORTANT: Adapt the roadmap intensity and content based on these preferences:
- For "Complete Beginner": Start with absolute basics, explain everything
- For "Advanced": Skip basics, focus on nuanced techniques and mastery
- For "15 minutes" daily: Create micro-learning sessions with quick wins
- For "2+ hours" daily: Include deep-dive sessions and complex projects
- For "Watch Videos" preference: Prioritize video resources and visual learning
- For "Hands-on Practice" preference: Focus on projects and practical exercises
"""
        
        # Domain-specific instructions
        domain_instructions = self._get_domain_instructions(domain)
        
        # Adjust milestone count based on timeline and daily time
        time_per_day = survey_data.get('timePerDay', '30 minutes') if survey_data else '30 minutes'
        milestone_count = self._calculate_milestone_count(timeline_days, time_per_day)
        
        prompt = f"""
Create a detailed {timeline_days}-day learning roadmap for: "{goal_text}"

{user_context}

Domain: {domain}
{domain_instructions}

Requirements:
1. Create {milestone_count} milestones spread strategically across {timeline_days} days
2. Each milestone should build progressively on previous ones
3. Include specific, actionable tasks for each milestone
4. **CRITICAL: Provide SPECIFIC, HIGH-QUALITY resources for each milestone:**
   - Exact YouTube channel names (e.g., "Joshua Weissman", "Bon Appétit")
   - Specific online courses (e.g., "MasterClass: Gordon Ramsay Teaches Cooking")
   - Actual book titles and authors
   - Specific tools, apps, or websites
   - Real blogs, articles, or documentation
   - NO generic phrases like "YouTube tutorials" or "online courses"

5. Make it practical and realistic for the given timeline and user preferences
6. Adapt difficulty and pacing based on skill level and available time

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
    
    def _calculate_total_hours(self, time_per_day: str, timeline_days: int) -> int:
        """Calculate total available hours based on daily commitment"""
        time_mapping = {
            '15 minutes': 0.25,
            '30 minutes': 0.5,
            '1 hour': 1.0,
            '2+ hours': 2.5
        }
        daily_hours = time_mapping.get(time_per_day, 0.5)
        return int(daily_hours * timeline_days)
    
    def _calculate_milestone_count(self, timeline_days: int, time_per_day: str) -> int:
        """Calculate appropriate number of milestones based on timeline and daily time"""
        if time_per_day == '15 minutes':
            # More frequent, smaller milestones for short sessions
            return max(3, min(8, timeline_days // 4))
        elif time_per_day == '2+ hours':
            # Fewer, more substantial milestones for longer sessions
            return max(2, min(6, timeline_days // 10))
        else:
            # Standard milestone cadence
            return max(3, min(7, timeline_days // 7))
    
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
    
    def _generate_fallback_roadmap(self, goal_text: str, timeline_days: int, domain: str, survey_data: Dict = None) -> Dict:
        """Generate a smart fallback roadmap if AI fails, incorporating survey data"""
        
        print(f"🔄 Generating smart fallback for domain: {domain} with survey data")
        
        # Adapt milestone count based on survey data
        if survey_data:
            time_per_day = survey_data.get('timePerDay', '30 minutes')
            num_milestones = self._calculate_milestone_count(timeline_days, time_per_day)
        else:
            num_milestones = max(2, min(6, timeline_days // 7))
            
        days_per_milestone = timeline_days // num_milestones
        
        milestones = []
        
        # Get domain-specific templates adapted for survey data
        templates = self._get_domain_templates(domain, survey_data)
        
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
        
        # Determine difficulty level based on survey data
        difficulty_level = "Intermediate"
        if survey_data and survey_data.get('skillLevel'):
            skill_mapping = {
                'Complete Beginner': 'Beginner',
                'Some Experience': 'Beginner',
                'Intermediate': 'Intermediate',
                'Advanced': 'Advanced'
            }
            difficulty_level = skill_mapping.get(survey_data['skillLevel'], 'Intermediate')
        
        return {
            "domain": domain,
            "estimated_hours_total": self._calculate_total_hours(
                survey_data.get('timePerDay', '30 minutes') if survey_data else '30 minutes',
                timeline_days
            ),
            "difficulty_level": difficulty_level,
            "milestones": milestones
        }
    
    def _get_domain_templates(self, domain: str, survey_data: Dict = None):
        """Get domain-specific milestone templates, adapted for survey data"""
        
        # Adapt complexity based on skill level
        skill_level = survey_data.get('skillLevel', 'Some Experience') if survey_data else 'Some Experience'
        is_beginner = skill_level == 'Complete Beginner'
        is_advanced = skill_level == 'Advanced'
        
        domain_templates = {
            "cooking": {
                "titles": [
                    "Kitchen Fundamentals" if is_beginner else ("Advanced Techniques" if is_advanced else "Kitchen Setup & Basics"),
                    "Essential Cooking Methods" if is_beginner else ("Complex Flavor Building" if is_advanced else "Fundamental Techniques"),
                    "Recipe Practice" if is_beginner else ("Culinary Innovation" if is_advanced else "Recipe Mastery"),
                    "Advanced Skills" if not is_advanced else "Mastery & Teaching Others"
                ],
                "descriptions": [
                    "Learn absolute kitchen basics and safety" if is_beginner else ("Master advanced culinary techniques" if is_advanced else "Set up your kitchen workspace and learn essential knife skills"),
                    "Master basic cooking methods step by step" if is_beginner else ("Develop complex flavor profiles and techniques" if is_advanced else "Master fundamental cooking techniques like sautéing and seasoning"),
                    "Practice with very simple recipes" if is_beginner else ("Create innovative dishes and techniques" if is_advanced else "Practice core recipes and build confidence"),
                    "Learn intermediate techniques" if is_beginner else ("Teach others and perfect your craft" if is_advanced else "Learn advanced techniques and develop your style")
                ],
                "tasks": [
                    ["Learn kitchen safety rules", "Identify basic tools", "Practice holding a knife safely", "Understand ingredient storage"] if is_beginner else 
                    (["Master knife techniques", "Understand advanced equipment", "Learn professional kitchen organization", "Study ingredient science"] if is_advanced else
                     ["Organize kitchen tools and workspace", "Learn basic knife cuts and safety", "Practice proper posture and grip", "Stock essential ingredients"]),
                    
                    ["Learn to boil water safely", "Practice basic seasoning", "Understand heat levels", "Try simple sautéing"] if is_beginner else
                    (["Master sauce-making", "Perfect temperature control", "Understand flavor chemistry", "Create signature techniques"] if is_advanced else
                     ["Master sautéing and heat control", "Practice seasoning techniques", "Learn timing for multiple dishes", "Understand ingredient interactions"]),
                     
                    ["Cook 1-2 very simple recipes", "Focus on following instructions exactly", "Taste and learn", "Document what you tried"] if is_beginner else
                    (["Develop original recipes", "Master complex multi-course meals", "Innovate with ingredients", "Perfect presentation techniques"] if is_advanced else
                     ["Cook 3-5 foundational recipes", "Document cooking notes and adjustments", "Practice mise en place", "Taste and adjust seasoning"])
                ]
            },
            "fitness": {
                "titles": [
                    "Fitness Basics & Safety" if is_beginner else ("Performance Optimization" if is_advanced else "Foundation & Assessment"),
                    "Basic Movement Patterns" if is_beginner else ("Advanced Training Methods" if is_advanced else "Form & Technique"),
                    "Simple Exercise Routine" if is_beginner else ("Competition Preparation" if is_advanced else "Building Strength"),
                    "Building Consistency" if is_beginner else ("Coaching Others" if is_advanced else "Progressive Training")
                ],
                "descriptions": [
                    "Learn basic fitness concepts and safety" if is_beginner else ("Optimize performance for competition" if is_advanced else "Assess current fitness level and establish foundation"),
                    "Master basic bodyweight movements" if is_beginner else ("Master advanced training techniques" if is_advanced else "Learn correct form for all exercises"),
                    "Establish a simple, consistent routine" if is_beginner else ("Prepare for competitive events" if is_advanced else "Focus on building base strength"),
                    "Build the habit of regular exercise" if is_beginner else ("Learn to coach and teach others" if is_advanced else "Advance to intermediate techniques")
                ],
                "tasks": [
                    ["Learn proper posture", "Understand basic anatomy", "Practice breathing techniques", "Learn warm-up basics"] if is_beginner else
                    (["Analyze biomechanics", "Optimize training periodization", "Master recovery protocols", "Study sports science"] if is_advanced else
                     ["Complete fitness assessment", "Set realistic goals", "Learn basic movements", "Establish workout schedule"])
                ]
            },
            "programming": {
                "titles": [
                    "Computer Basics" if is_beginner else ("System Architecture" if is_advanced else "Environment Setup"),
                    "Programming Fundamentals" if is_beginner else ("Advanced Algorithms" if is_advanced else "Programming Fundamentals"),
                    "First Simple Project" if is_beginner else ("Complex System Design" if is_advanced else "Project Building"),
                    "Learning to Debug" if is_beginner else ("Open Source Contribution" if is_advanced else "Advanced Concepts")
                ],
                "descriptions": [
                    "Learn basic computer operation and concepts" if is_beginner else ("Master system design and architecture" if is_advanced else "Set up development environment and learn basics"),
                    "Understand what programming is and basic concepts" if is_beginner else ("Implement complex algorithms and data structures" if is_advanced else "Master fundamental programming concepts"),
                    "Build your very first simple program" if is_beginner else ("Design and build complex distributed systems" if is_advanced else "Build real projects to apply knowledge"),
                    "Learn to find and fix simple errors" if is_beginner else ("Contribute to major open source projects" if is_advanced else "Learn advanced patterns and best practices")
                ],
                "tasks": [
                    ["Learn to use a computer efficiently", "Understand files and folders", "Learn basic typing", "Understand what code is"] if is_beginner else
                    (["Design scalable architectures", "Optimize system performance", "Implement security best practices", "Master DevOps practices"] if is_advanced else
                     ["Install development tools and IDE", "Learn version control basics", "Write your first 'Hello World'", "Understand basic syntax"])
                ]
            }
        }
        
        # Use general template if domain not found
        if domain not in domain_templates:
            return {
                "titles": ["Getting Started", "Building Foundation", "Skill Development", "Advanced Practice"],
                "descriptions": [
                    f"Begin your journey with {goal_text if 'goal_text' in locals() else 'your goal'}",
                    "Build a solid foundation of knowledge and skills",
                    "Develop intermediate capabilities through practice",
                    "Apply advanced techniques and master your craft"
                ],
                "tasks": [
                    ["Research your goal", "Gather resources", "Create learning plan", "Set up workspace"],
                    ["Study fundamentals", "Practice basic skills", "Join communities", "Find mentors"],
                    ["Apply knowledge practically", "Seek feedback", "Overcome challenges", "Build confidence"],
                    ["Master advanced techniques", "Teach others", "Continue learning", "Set new challenges"]
                ]
            }
        
        return domain_templates[domain]
    
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