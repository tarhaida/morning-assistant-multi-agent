"""
Communication Specialist Agent
Synthesizes all information into a family-friendly message.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from typing import Dict, Any
from llm import get_llm
from utils import load_config
from prompt_builder import build_system_prompt_message
from custom_tools import send_whatsapp_tool


class CommunicationAgent:
    """Family communication specialist agent."""
    
    def __init__(self):
        """Initialize the communication agent."""
        self.config = load_config()
        self.agent_config = self.config['communication_agent']
        
        # Initialize LLM
        self.llm = get_llm(
            model_name=self.agent_config['llm'],
            temperature=self.agent_config['temperature']
        )
        
        # Build system prompt
        self.system_prompt = build_system_prompt_message(
            self.agent_config['prompt_config']
        )
    
    def create_message(
        self,
        weather_analysis: str,
        menu: str,
        nutrition_analysis: str,
        activity_suggestions: str
    ) -> Dict[str, Any]:
        """
        Create a family-friendly WhatsApp message.
        
        Args:
            weather_analysis: Weather analysis
            menu: School menu
            nutrition_analysis: Nutrition analysis
            activity_suggestions: Activity suggestions
            
        Returns:
            Dictionary with message
        """
        print(f"\n[CommunicationAgent] Creating family message...")
        
        try:
            # Create message composition prompt
            user_prompt = f"""
Create a warm, affectionate WhatsApp message in French for a mother about her child's day.

WEATHER INFORMATION:
{weather_analysis}

SCHOOL MENU:
{menu}

NUTRITION NOTES:
{nutrition_analysis}

ACTIVITY SUGGESTIONS:
{activity_suggestions}

Create a single, flowing message that:
1. Starts with "Ma chérie"
2. Includes all information naturally
3. Uses appropriate emojis
4. Has a warm, family tone
5. Is written in French
6. Is concise but comprehensive (max 200 words)
"""
            
            # Get LLM message
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = self.llm.invoke(messages)
            message = response.content if hasattr(response, 'content') else str(response)
            
            print(f"[CommunicationAgent] Message created ({len(message)} chars)")
            
            return {
                "success": True,
                "message": message
            }
            
        except Exception as e:
            print(f"[CommunicationAgent] Error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_message(self, phone_number: str, message: str) -> Dict[str, Any]:
        """
        Send WhatsApp message.
        
        Args:
            phone_number: Recipient phone number
            message: Message to send
            
        Returns:
            Send status dictionary
        """
        print(f"\n[CommunicationAgent] Sending message to {phone_number}...")
        
        try:
            result = send_whatsapp_tool.invoke({
                "phone_number": phone_number,
                "message": message
            })
            print(f"[CommunicationAgent] Send status: {result}")
            return result
        except Exception as e:
            print(f"[CommunicationAgent] Send error: {e}")
            return {"status": "error", "error": str(e)}


def communication_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node function for message creation.
    
    Args:
        state: Current state dictionary
        
    Returns:
        Updated state
    """
    agent = CommunicationAgent()
    
    # Create message
    result = agent.create_message(
        weather_analysis=state.get("weather_analysis", ""),
        menu=state.get("menu", ""),
        nutrition_analysis=state.get("nutrition_analysis", ""),
        activity_suggestions=state.get("activity_suggestions", "")
    )
    
    # Update state
    state["final_message"] = result.get("message", "")
    
    if not result.get("success"):
        state.setdefault("errors", []).append(f"Communication: {result.get('error')}")
    
    return state


def whatsapp_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node function for sending WhatsApp message.
    
    Args:
        state: Current state dictionary
        
    Returns:
        Updated state
    """
    agent = CommunicationAgent()
    
    phone_number = state.get("phone_number", "+41766757205")
    message = state.get("final_message", "")
    
    if message:
        send_result = agent.send_message(phone_number, message)
        state["whatsapp_status"] = send_result
    else:
        state["whatsapp_status"] = {"status": "error", "error": "No message to send"}
        state.setdefault("errors", []).append("WhatsApp: No message created")
    
    return state
