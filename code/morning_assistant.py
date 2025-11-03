"""
Morning Assistant Multi-Agent System
LangGraph orchestration with specialized agents.

This system demonstrates a true multi-agent architecture using LangGraph:
- 4 specialized agents with distinct roles
- Conditional routing based on state
- Proper state management via StateGraph
- Error handling and retry logic
"""

import sys
import os
from typing import TypedDict, List, Optional
from datetime import datetime

# Add code directory to path
sys.path.insert(0, os.path.dirname(__file__))

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# Import agent node functions
from agents.weather_agent import weather_node
from agents.nutrition_agent import nutrition_node
from agents.activity_agent import activity_node
from agents.communication_agent import communication_node, whatsapp_node

from utils import load_config


# State definition for the multi-agent system
class MorningAssistantState(TypedDict):
    """State schema for the morning assistant workflow."""
    
    # Configuration
    city: str
    phone_number: str
    
    # Weather Agent outputs
    weather_data: Optional[dict]
    current_weather: str
    forecast: str
    weather_analysis: str
    
    # Nutrition Agent outputs
    menu_data: Optional[dict]
    menu: str
    nutrition_analysis: str
    
    # Activity Agent outputs
    activity_suggestions: str
    
    # Communication Agent outputs
    final_message: str
    whatsapp_status: Optional[dict]
    
    # System tracking
    errors: List[str]
    iteration: int


def create_initial_state(phone_number: str = None) -> MorningAssistantState:
    """
    Create initial state for the workflow.
    
    Priority order for phone number:
    1. Function parameter (command line argument)
    2. Environment variable (PHONE_NUMBER)
    3. Config file setting
    
    Args:
        phone_number: Phone number to send message to
        
    Returns:
        Initial state dictionary
        
    Raises:
        ValueError: If phone number is not configured
    """
    config = load_config()
    settings = config.get('settings', {})
    
    # Priority order: parameter > env var > config
    phone = (
        phone_number or 
        os.getenv('PHONE_NUMBER') or 
        settings.get('phone_number')
    )
    
    # Security: Require phone number to be configured (not hardcoded)
    if not phone:
        raise ValueError(
            "Phone number not configured. Please set it via:\n"
            "  1. Command line: python code/morning_assistant.py +33612345678\n"
            "  2. Environment: export PHONE_NUMBER=+33612345678 (or add to .env)\n"
            "  3. Config file: Set 'phone_number' in config/config.yaml"
        )
    
    return MorningAssistantState(
        city=settings.get('city', 'Divonne-les-Bains'),
        phone_number=phone,
        weather_data=None,
        current_weather="",
        forecast="",
        weather_analysis="",
        menu_data=None,
        menu="",
        nutrition_analysis="",
        activity_suggestions="",
        final_message="",
        whatsapp_status=None,
        errors=[],
        iteration=0
    )


def should_continue_after_weather(state: MorningAssistantState) -> str:
    """
    Decide whether to continue after weather analysis.
    
    Args:
        state: Current state
        
    Returns:
        Next node name or END
    """
    if state.get("weather_data", {}).get("success"):
        return "nutrition"
    else:
        print("[Router] Weather analysis failed, skipping to communication with limited info")
        return "communication"


def should_continue_after_nutrition(state: MorningAssistantState) -> str:
    """
    Decide whether to continue after nutrition analysis.
    
    Args:
        state: Current state
        
    Returns:
        Next node name
    """
    # Always continue to activity planning
    return "activity"


def should_continue_after_activity(state: MorningAssistantState) -> str:
    """
    Decide whether to continue after activity suggestions.
    
    Args:
        state: Current state
        
    Returns:
        Next node name
    """
    # Always continue to communication
    return "communication"


def should_send_whatsapp(state: MorningAssistantState) -> str:
    """
    Decide whether to send WhatsApp message.
    
    Args:
        state: Current state
        
    Returns:
        Next node name or END
    """
    if state.get("final_message"):
        return "whatsapp"
    else:
        print("[Router] No message created, skipping WhatsApp send")
        return END


def create_workflow() -> StateGraph:
    """
    Create the LangGraph workflow.
    
    Returns:
        Compiled StateGraph
    """
    # Create graph
    workflow = StateGraph(MorningAssistantState)
    
    # Add nodes
    workflow.add_node("weather", weather_node)
    workflow.add_node("nutrition", nutrition_node)
    workflow.add_node("activity", activity_node)
    workflow.add_node("communication", communication_node)
    workflow.add_node("whatsapp", whatsapp_node)
    
    # Define edges
    workflow.add_edge(START, "weather")
    
    # Conditional routing after weather
    workflow.add_conditional_edges(
        "weather",
        should_continue_after_weather,
        {
            "nutrition": "nutrition",
            "communication": "communication"
        }
    )
    
    # Linear flow from nutrition to activity
    workflow.add_edge("nutrition", "activity")
    
    # Linear flow from activity to communication
    workflow.add_edge("activity", "communication")
    
    # Conditional routing after communication
    workflow.add_conditional_edges(
        "communication",
        should_send_whatsapp,
        {
            "whatsapp": "whatsapp",
            END: END
        }
    )
    
    # End after WhatsApp
    workflow.add_edge("whatsapp", END)
    
    # Compile with memory
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)


def run_morning_assistant(phone_number: str = None):
    """
    Run the complete morning assistant workflow.
    
    Args:
        phone_number: Phone number to send message to (optional)
    """
    print("="*80)
    print("MORNING ASSISTANT MULTI-AGENT SYSTEM")
    print("="*80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Create workflow
    app = create_workflow()
    
    # Create initial state
    initial_state = create_initial_state(phone_number)
    
    print(f"City: {initial_state['city']}")
    print(f"Phone: {initial_state['phone_number']}")
    print()
    
    # Execute workflow
    config = {"configurable": {"thread_id": "morning_assistant_1"}}
    
    try:
        result = app.invoke(initial_state, config)
        
        print("\n" + "="*80)
        print("WORKFLOW COMPLETE")
        print("="*80)
        print(f"\nFinal Message:\n{result.get('final_message', 'No message created')}")
        print(f"\nWhatsApp Status: {result.get('whatsapp_status', 'Not sent')}")
        
        if result.get('errors'):
            print(f"\nErrors encountered: {len(result['errors'])}")
            for error in result['errors']:
                print(f"  - {error}")
        
        return result
        
    except Exception as e:
        print(f"\n[ERROR] Workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Get phone number from command line or use default
    phone = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Run the system
    run_morning_assistant(phone)
