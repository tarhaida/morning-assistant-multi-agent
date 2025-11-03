"""
Activity Planning Specialist Agent
Suggests activities based on weather and menu.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from typing import Dict, Any
from llm import get_llm
from utils import load_config
from prompt_builder import build_system_prompt_message


class ActivityAgent:
    """Activity planning specialist agent."""
    
    def __init__(self):
        """Initialize the activity agent."""
        self.config = load_config()
        self.agent_config = self.config['activity_agent']
        
        # Initialize LLM
        self.llm = get_llm(
            model_name=self.agent_config['llm'],
            temperature=self.agent_config['temperature']
        )
        
        # Build system prompt
        self.system_prompt = build_system_prompt_message(
            self.agent_config['prompt_config']
        )
    
    def suggest_activities(
        self, 
        weather_analysis: str, 
        menu: str
    ) -> Dict[str, Any]:
        """
        Suggest activities based on weather and menu.
        
        Args:
            weather_analysis: Weather analysis from weather agent
            menu: Menu information from nutrition agent
            
        Returns:
            Dictionary with activity suggestions
        """
        print(f"\n[ActivityAgent] Generating activity suggestions...")
        
        try:
            # Create suggestion prompt
            user_prompt = f"""
Based on the following information, suggest 2-3 appropriate activities for a child:

WEATHER CONDITIONS:
{weather_analysis}

TODAY'S LUNCH MENU:
{menu}

Consider:
- Weather appropriateness (indoor vs outdoor)
- Energy levels after lunch
- Time of day (afternoon/evening)
- Safety and fun balance

Provide creative, practical activity suggestions.
"""
            
            # Get LLM suggestions
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = self.llm.invoke(messages)
            suggestions = response.content if hasattr(response, 'content') else str(response)
            
            print(f"[ActivityAgent] Suggestions generated")
            
            return {
                "success": True,
                "suggestions": suggestions
            }
            
        except Exception as e:
            print(f"[ActivityAgent] Error: {e}")
            return {
                "success": False,
                "error": str(e)
            }


def activity_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node function for activity suggestions.
    
    Args:
        state: Current state dictionary
        
    Returns:
        Updated state
    """
    agent = ActivityAgent()
    
    weather_analysis = state.get("weather_analysis", "")
    menu = state.get("menu", "")
    
    result = agent.suggest_activities(weather_analysis, menu)
    
    # Update state
    state["activity_suggestions"] = result.get("suggestions", "")
    
    if not result.get("success"):
        state.setdefault("errors", []).append(f"Activity: {result.get('error')}")
    
    return state
