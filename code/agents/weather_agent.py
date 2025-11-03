"""
Weather Specialist Agent
Analyzes weather data and provides actionable insights.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from typing import Dict, Any
from llm import get_llm
from utils import load_config
from prompt_builder import build_system_prompt_message
from custom_tools import get_weather_tool, get_forecast_tool


class WeatherAgent:
    """Weather analysis specialist agent."""
    
    def __init__(self):
        """Initialize the weather agent."""
        self.config = load_config()
        self.agent_config = self.config['weather_agent']
        
        # Initialize LLM
        self.llm = get_llm(
            model_name=self.agent_config['llm'],
            temperature=self.agent_config['temperature']
        )
        
        # Build system prompt
        self.system_prompt = build_system_prompt_message(
            self.agent_config['prompt_config']
        )
    
    def analyze(self, city: str) -> Dict[str, Any]:
        """
        Analyze weather for a city and provide insights.
        
        Args:
            city: City name
            
        Returns:
            Dictionary with weather analysis
        """
        print(f"\n[WeatherAgent] Analyzing weather for {city}...")
        
        try:
            # Get weather data
            current_weather = get_weather_tool.invoke({"city": city})
            forecast = get_forecast_tool.invoke({"city": city})
            
            # Create analysis prompt
            user_prompt = f"""
Analyze the following weather information and provide actionable insights:

CURRENT WEATHER:
{current_weather}

FORECAST:
{forecast}

Provide a brief, actionable summary with clothing and activity recommendations.
"""
            
            # Get LLM analysis
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = self.llm.invoke(messages)
            analysis = response.content if hasattr(response, 'content') else str(response)
            
            print(f"[WeatherAgent] Analysis complete")
            
            return {
                "success": True,
                "current_weather": current_weather,
                "forecast": forecast,
                "analysis": analysis,
                "city": city
            }
            
        except Exception as e:
            print(f"[WeatherAgent] Error: {e}")
            return {
                "success": False,
                "error": str(e),
                "city": city
            }


def weather_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node function for weather analysis.
    
    Args:
        state: Current state dictionary
        
    Returns:
        Updated state
    """
    agent = WeatherAgent()
    city = state.get("city", "Divonne-les-Bains")
    
    result = agent.analyze(city)
    
    # Update state
    state["weather_data"] = result
    state["current_weather"] = result.get("current_weather", "")
    state["forecast"] = result.get("forecast", "")
    state["weather_analysis"] = result.get("analysis", "")
    
    if not result.get("success"):
        state.setdefault("errors", []).append(f"Weather: {result.get('error')}")
    
    return state
