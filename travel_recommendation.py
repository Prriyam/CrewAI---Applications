import sys
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
from typing import Dict, List
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
from typing import Dict, List
from typing import Type


load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_MODEL_NAME"] = "gpt-4"

class TravelPreferencesInput(BaseModel):
    destination: str = Field(
        ..., 
        description="Desired travel destination"
    )
    budget: float = Field(
        ...,
        description="Available budget for the trip"
    )
    duration: str = Field(
        ...,
        description="Duration of the trip (e.g., '7 days')"
    )
    interests: List[str] = Field(
        default_factory=list,  # Default to empty list if not provided
        description="List of travel interests"
    )

class TravelRecommendationTool(BaseTool):
    """Travel recommendation tool that processes user preferences and suggests destinations."""
    name: str = "Travel Recommendation Tool"
    description: str = "Provides personalized travel recommendations based on user preferences."
    args_schema: Type[BaseModel] = TravelPreferencesInput  # This is the key fix

    def _run(self, destination: str, budget: float, duration: str, interests: List[str]) -> Dict:
        destinations = {
            "paris": {
                "name": "Paris",
                "budget_range": (1500, 3000),
                "activities": [
                    "Visit the Louvre Museum",
                    "Climb the Eiffel Tower",
                    "Explore Notre-Dame Cathedral",
                    "Walk through Montmartre",
                    "Shop on Champs-Élysées"
                ],
                "best_season": ["Spring", "Fall"],
                "cuisine": ["French pastries", "Fine dining", "Wine tasting"]
            },
            "tokyo": {
                "name": "Tokyo",
                "budget_range": (2000, 4000),
                "activities": [
                    "Visit Senso-ji Temple",
                    "Explore Shibuya Crossing",
                    "Tour the Imperial Palace",
                    "Shop in Akihabara",
                    "Experience teamLab Borderless"
                ],
                "best_season": ["Spring", "Fall"],
                "cuisine": ["Sushi", "Ramen", "Street food"]
            },
            "bangkok": {
                "name": "1000",
                "budget_range": (800, 2000),
                "activities": [
                    "Visit Grand Palace",
                    "Explore Wat Arun",
                    "Shop at Chatuchak Market",
                    "Take a river cruise",
                    "Visit floating markets"
                ],
                "best_season": ["November", "February"],
                "cuisine": ["Street food", "Thai curries", "Seafood"]
            },
            "rome": {
                "name": "Rome",
                "budget_range": (1200, 3000),
                "activities": [
                    "Visit the Colosseum",
                    "Explore Vatican Museums",
                    "Throw coins in Trevi Fountain",
                    "Walk through Roman Forum",
                    "Visit Pantheon"
                ],
                "best_season": ["Spring", "Fall"],
                "cuisine": ["Pizza", "Pasta", "Gelato", "Wine"]
            },
            "barcelona": {
                "name": "Barcelona",
                "budget_range": (1000, 2500),
                "activities": [
                    "Visit Sagrada Familia",
                    "Explore Park Güell",
                    "Walk Las Ramblas",
                    "Visit Casa Batlló",
                    "Beach day at Barceloneta"
                ],
                "best_season": ["Spring", "Early Summer"],
                "cuisine": ["Tapas", "Paella", "Seafood"]
            }
        }

        def find_alternatives(target_budget: float, target_interests: List[str]) -> List[Dict]:
            """Helper function to find alternative destinations within budget."""
            alternatives = []
            for key, info in destinations.items():
                if info["budget_range"][0] <= target_budget <= info["budget_range"][1]:
                    matching_activities = [
                        activity for activity in info["activities"]
                        if not target_interests or any(interest.lower() in activity.lower() 
                        for interest in target_interests)
                    ]
                    
                    if matching_activities:
                        alternatives.append({
                            "name": info["name"],
                            "budget_range": info["budget_range"],
                            "matching_activities": matching_activities,
                            "best_season": info["best_season"],
                            "cuisine": info["cuisine"]
                        })
            
            alternatives.sort(key=lambda x: len(x["matching_activities"]), reverse=True)
            return alternatives

        destination_key = destination.lower()
        if destination_key not in destinations:
            return {
                "match": False,
                "message": f"Destination '{destination}' not found in our database",
                "available_destinations": sorted([info["name"] for info in destinations.values()]),
                "suggestion": "Please choose from our available destinations"
            }

        dest_info = destinations[destination_key]
        
        if dest_info["budget_range"][0] <= budget <= dest_info["budget_range"][1]:
            matching_activities = [
                activity for activity in dest_info["activities"]
                if not interests or any(interest.lower() in activity.lower() for interest in interests)
            ]

            return {
                "match": True,
                "destination": dest_info["name"],
                "recommended_activities": matching_activities,
                "best_season": dest_info["best_season"],
                "budget_range": dest_info["budget_range"],
                "cuisine": dest_info["cuisine"]
            }
        

        alternative_destinations = find_alternatives(budget, interests)
        
        return {
            "match": False,
            "message": f"Budget constraint not met for {dest_info['name']}",
            "required_budget": dest_info["budget_range"][0],
            "current_budget": budget,
            "budget_difference": dest_info["budget_range"][0] - budget,
            "alternatives": alternative_destinations,
            "suggestion": "Consider these alternative destinations within your budget"
        }
    
tool = TravelRecommendationTool()

travel_advisor = Agent(
    role='Travel Advisor',
    goal='Provide detailed, personalized travel recommendations based on user preferences',
    backstory=
    """
        You are an experienced travel advisor with extensive knowledge of global 
        destinations. You excel at matching travelers with their perfect destinations while 
        considering their interests, budget, and preferences.
    """,
        tools=[tool],
        verbose=True,
        allow_delegation=False
    )

user_preferences = {
    "destination": "tokyo",
    "budget": 2500,
    "duration": "10 days",
    "interests": ["art", "food", "history"]
    }

def create_vacation_tasks(destination, budget, duration, interests):
    recommendation_task = Task(
        description=f"""Analyze travel preferences and provide detailed recommendations for:
        Destination: {destination}
        Budget: ${budget}
        Duration: {duration}
        Interests: {', '.join(interests)}
        
        Provide a comprehensive travel plan including:
        1. Confirmation of budget feasibility
        2. Recommended activities based on interests
        3. Best time to visit
        4. Local cuisine recommendations""",
        expected_output="""A detailed travel recommendation including:
        - Destination analysis and budget feasibility
        - List of recommended activities matching user interests
        - Best seasons to visit
        - Local cuisine recommendations
        - Any relevant travel tips or warnings""",
        agent=travel_advisor
    )

    # Create a Crew instance
    crew = Crew(
        agents=[travel_advisor],
        tasks=[recommendation_task],
        process=Process.sequential,
        verbose=True,
        max_rpm=1000,
        share_crew=True
    )

    return crew


#result=crew.kickoff(inputs={"destination": "tokyo",
#                            "budget": 2500,
#                           "duration": "10 days",
#                            "interests": ["art", "food", "history"]})
