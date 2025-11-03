"""
Simple WhatsApp automation for macOS.
Sends WhatsApp messages using AppleScript automation.
"""

import subprocess
import urllib.parse
import time


def send_whatsapp(phone, message):
    """
    Send WhatsApp message automatically on macOS.
    
    Args:
        phone: Phone number with country code (e.g., +41766757205)
        message: Message text to send
    """
    # Clean phone number
    clean_phone = phone.replace("+", "").replace(" ", "").replace("-", "")
    
    # Create WhatsApp URL
    url = f"whatsapp://send?phone={clean_phone}&text={urllib.parse.quote(message)}"
    
    print("📱 Sending WhatsApp message...")
    print(f"   To: {phone}")
    print(f"   Message length: {len(message)} chars")
    
    try:
        # Open WhatsApp
        subprocess.run(["open", url], check=True)
        
        # Wait for WhatsApp to open
        time.sleep(4)
        
        # Auto-send with Enter key (key code 36)
        subprocess.run([
            "osascript", 
            "-e", 
            'tell application "System Events" to tell process "WhatsApp" to key code 36'
        ], check=True)
        
        print("✅ WhatsApp message sent!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error sending WhatsApp: {e}")
        raise
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise


if __name__ == "__main__":
    # Test function
    phone = input("Phone (+country code): ")
    message = input("Message: ")
    send_whatsapp(phone, message)
