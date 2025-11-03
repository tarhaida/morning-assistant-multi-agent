"""
Custom tools for the Morning Assistant.
LangChain-compatible tools for weather, menu, and messaging.
"""

import io
import contextlib
from typing import List
from langchain_core.tools import tool


@tool
def get_weather_tool(city: str) -> str:
    """
    Get the current weather for a given city.
    
    Args:
        city: The name of the city to get the weather for.
        
    Returns:
        Weather information as a string.
    """
    # Import here to avoid circular dependencies
    try:
        import weather_app
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            weather_app.get_weather(city)
        return buf.getvalue().strip()
    except ImportError:
        return f"Weather API not available. Placeholder: Sunny, 22°C in {city}"


@tool
def get_forecast_tool(city: str) -> str:
    """
    Get the weather forecast for a given city.
    
    Args:
        city: The name of the city to get the forecast for.
        
    Returns:
        Forecast information as a string.
    """
    try:
        import weather_app
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            weather_app.get_forecast(city)
        return buf.getvalue().strip()
    except ImportError:
        return f"Weather API not available. Placeholder: Forecast for {city}: Clear skies, 18-25°C"


@tool
def check_menu_tool(tool_input=None) -> str:
    """
    Check for menu updates and download new menus if available.
    
    Returns:
        Status of menu update/download.
    """
    try:
        import simple_menu_checker
        checker = simple_menu_checker.SmartMenuChecker()
        return str(checker.check_and_download_menus())
    except ImportError:
        return "Menu checker not available"


@tool
def get_menu_tool(tool_input=None) -> str:
    """
    Extract and process the current menu information.
    
    Returns:
        Processed menu details as a string.
    """
    try:
        import menu_extractor
        extractor = menu_extractor.DivonneMenuExtractor()
        return str(extractor.extract_and_process_menus())
    except ImportError:
        return "Menu extractor not available"


@tool
def process_menu_images_tool(tool_input=None) -> str:
    """
    Process menu images using DOCUPIPE OCR API to extract structured data.
    Converts menu images to CSV format with nutritional information.
    
    Returns:
        Status of OCR processing operation.
    """
    try:
        import docupipe_extractor
        from pathlib import Path
        
        # Get project paths
        project_root = Path(__file__).parent.parent
        image_folder = project_root / "data" / "final_menu_download"
        output_folder = project_root / "data" / "divonne_menu_results"
        
        print(f"[process_menu_images_tool] Processing images from: {image_folder}")
        
        # Initialize and run DOCUPIPE extractor
        extractor = docupipe_extractor.EnhancedMenuExtractor(
            image_folder=image_folder,
            output_folder=output_folder
        )
        
        extractor.process_all_menus()
        
        return f"✅ DOCUPIPE processing completed. CSV saved to {output_folder}"
        
    except ImportError:
        return "❌ DOCUPIPE extractor not available"
    except Exception as e:
        return f"❌ DOCUPIPE processing error: {str(e)}"


@tool
def send_whatsapp_tool(phone_number: str, message: str) -> dict:
    """
    Send a WhatsApp message to a specified phone number.
    
    Args:
        phone_number: The recipient's phone number.
        message: The message to send.
        
    Returns:
        Status dictionary with result of send operation.
    """
    print(f"[send_whatsapp_tool] Sending to {phone_number}")
    try:
        # Import whatsapp_simple module
        import whatsapp_simple
        whatsapp_simple.send_whatsapp(phone_number, message)
        return {"status": "sent", "phone": phone_number}
    except Exception as e:
        print(f"[send_whatsapp_tool] Error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}


def get_all_tools() -> List:
    """
    Get list of all available tools.
    
    Returns:
        List of tool functions
    """
    return [
        get_weather_tool,
        get_forecast_tool,
        check_menu_tool,
        get_menu_tool,
        process_menu_images_tool,
        send_whatsapp_tool
    ]
