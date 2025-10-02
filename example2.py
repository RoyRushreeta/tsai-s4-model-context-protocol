# basic import 
from mcp.server.fastmcp import FastMCP, Image
from mcp.server.fastmcp.prompts import base
from mcp.types import TextContent
from mcp import types
from PIL import Image as PILImage
import math
import sys
from pywinauto.application import Application
import win32gui
import win32con
import time
from win32api import GetSystemMetrics
import pyautogui
import os
from dotenv import load_dotenv

# Load environment variables (for SENDGRID_API_KEY, etc.)
load_dotenv()

# instantiate an MCP server client
mcp = FastMCP("Calculator")

# Global variable for Paint application
paint_app = None

def ensure_paint_focused():
    """Utility function to ensure Paint window is focused and in foreground"""
    global paint_app
    if paint_app:
        try:
            paint_window = paint_app.window(class_name='MSPaintApp')
            win32gui.SetForegroundWindow(paint_window.handle)
            win32gui.BringWindowToTop(paint_window.handle)
            paint_window.set_focus()
            time.sleep(0.3)
            return True
        except Exception as e:
            print(f"Error focusing Paint: {e}")
            return False
    return False

def select_rectangle_tool_alternative():
    """Alternative method to select rectangle tool using keyboard"""
    global paint_app
    if paint_app:
        try:
            paint_window = paint_app.window(class_name='MSPaintApp')
            
            # Ensure window is focused first
            ensure_paint_focused()
            
            # Method 1: Simple 'r' shortcut (most reliable)
            paint_window.type_keys('r')
            time.sleep(0.3)
            
            # Method 2: If that doesn't work, try Home tab approach
            paint_window.type_keys('%h')  # Alt+H for Home tab
            time.sleep(0.2)
            paint_window.type_keys('sh')  # Shapes dropdown
            time.sleep(0.3)
            paint_window.type_keys('r')   # Rectangle
            time.sleep(0.3)
            
            print("Rectangle tool selection completed")
            return True
            
        except Exception as e:
            print(f"Alternative rectangle selection failed: {e}")
            return False
    return False

# DEFINE TOOLS

#addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    print("CALLED: add(a: int, b: int) -> int:")
    return int(a + b)

@mcp.tool()
def add_list(l: list) -> int:
    """Add all numbers in a list"""
    print("CALLED: add(l: list) -> int:")
    return sum(l)

# subtraction tool
@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    print("CALLED: subtract(a: int, b: int) -> int:")
    return int(a - b)

# multiplication tool
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    print("CALLED: multiply(a: int, b: int) -> int:")
    return int(a * b)

#  division tool
@mcp.tool() 
def divide(a: int, b: int) -> float:
    """Divide two numbers"""
    print("CALLED: divide(a: int, b: int) -> float:")
    return float(a / b)

# power tool
@mcp.tool()
def power(a: int, b: int) -> int:
    """Power of two numbers"""
    print("CALLED: power(a: int, b: int) -> int:")
    return int(a ** b)

# square root tool
@mcp.tool()
def sqrt(a: int) -> float:
    """Square root of a number"""
    print("CALLED: sqrt(a: int) -> float:")
    return float(a ** 0.5)

# cube root tool
@mcp.tool()
def cbrt(a: int) -> float:
    """Cube root of a number"""
    print("CALLED: cbrt(a: int) -> float:")
    return float(a ** (1/3))

# factorial tool
@mcp.tool()
def factorial(a: int) -> int:
    """factorial of a number"""
    print("CALLED: factorial(a: int) -> int:")
    return int(math.factorial(a))

# log tool
@mcp.tool()
def log(a: int) -> float:
    """log of a number"""
    print("CALLED: log(a: int) -> float:")
    return float(math.log(a))

# remainder tool
@mcp.tool()
def remainder(a: int, b: int) -> int:
    """remainder of two numbers divison"""
    print("CALLED: remainder(a: int, b: int) -> int:")
    return int(a % b)

# sin tool
@mcp.tool()
def sin(a: int) -> float:
    """sin of a number"""
    print("CALLED: sin(a: int) -> float:")
    return float(math.sin(a))

# cos tool
@mcp.tool()
def cos(a: int) -> float:
    """cos of a number"""
    print("CALLED: cos(a: int) -> float:")
    return float(math.cos(a))

# tan tool
@mcp.tool()
def tan(a: int) -> float:
    """tan of a number"""
    print("CALLED: tan(a: int) -> float:")
    return float(math.tan(a))

# mine tool
@mcp.tool()
def mine(a: int, b: int) -> int:
    """special mining tool"""
    print("CALLED: mine(a: int, b: int) -> int:")
    return int(a - b - b)

@mcp.tool()
def create_thumbnail(image_path: str) -> Image:
    """Create a thumbnail from an image"""
    print("CALLED: create_thumbnail(image_path: str) -> Image:")
    img = PILImage.open(image_path)
    img.thumbnail((100, 100))
    return Image(data=img.tobytes(), format="png")

@mcp.tool()
def strings_to_chars_to_int(string: str) -> list[int]:
    """Return the ASCII values of the characters in a word"""
    print("CALLED: strings_to_chars_to_int(string: str) -> list[int]:")
    return [int(ord(char)) for char in string]

@mcp.tool()
def int_list_to_exponential_sum(int_list: list) -> float:
    """Return sum of exponentials of numbers in a list"""
    print("CALLED: int_list_to_exponential_sum(int_list: list) -> float:")
    return sum(math.exp(i) for i in int_list)

@mcp.tool()
def fibonacci_numbers(n: int) -> list:
    """Return the first n Fibonacci Numbers"""
    print("CALLED: fibonacci_numbers(n: int) -> list:")
    if n <= 0:
        return []
    fib_sequence = [0, 1]
    for _ in range(2, n):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return fib_sequence[:n]


@mcp.tool()
async def open_paint(monitor: int = 1, maximize: bool = True) -> dict:
    """Open Microsoft Paint application for drawing and graphics."""
    global paint_app
    try:
        paint_app = Application().start('mspaint.exe')
        time.sleep(0.2)  # Give more time to load
        
        # Get the Paint window
        paint_window = paint_app.window(class_name='MSPaintApp')
        
        # Wait for Paint to fully load
        time.sleep(0.2)
        
        # Maximize the window always for best visibility
        win32gui.ShowWindow(paint_window.handle, win32con.SW_MAXIMIZE)
        
        # Bring Paint to foreground and ensure it has focus
        win32gui.SetForegroundWindow(paint_window.handle)
        win32gui.BringWindowToTop(paint_window.handle)
        paint_window.set_focus()
        
        # Additional time to ensure Paint is ready and visible
        time.sleep(2.0)  # More time for Paint to be ready
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Paint opened successfully on monitor {monitor}, maximized: {maximize}, focused: {paint_window.has_focus()}"
                ),
                {"handle": paint_window.handle}
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error opening Paint: {str(e)}"
                )
            ]
        }

@mcp.tool()
async def draw_rectangle(x1: int, y1: int, x2: int, y2: int) -> dict:
    """Draw a rectangle in Paint using pyautogui with canvas-relative coordinates"""
    global paint_app
    try:
        if not paint_app:
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Paint is not open. Please call open_paint first."
                    )
                ]
            }

        # Get the Paint window
        paint_window = paint_app.window(class_name='MSPaintApp')

        # Ensure Paint window is active
        if not paint_window.has_focus():
            paint_window.set_focus()
            time.sleep(0.5)

        import pyautogui

        # Click on rectangle tool (approximate position)
        pyautogui.click(658, 107)  # Rectangle tool in toolbar
        time.sleep(0.5)

        # Get window position to calculate canvas offsets
        rect = paint_window.rectangle()  # left, top, right, bottom of window
        canvas_left = rect.left + 8      # approximate left offset to canvas
        canvas_top = rect.top + 80       # approximate top offset to canvas

        # Convert canvas-relative coordinates to screen coordinates
        screen_x1 = canvas_left + x1
        screen_y1 = canvas_top + y1
        screen_x2 = canvas_left + x2
        screen_y2 = canvas_top + y2

        # Draw rectangle
        pyautogui.mouseDown(screen_x1, screen_y1)
        pyautogui.dragTo(screen_x2, screen_y2, duration=0.5)
        pyautogui.mouseUp()

        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Rectangle drawn from ({x1},{y1}) to ({x2},{y2}) inside canvas"
                )
            ]
        }

    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error drawing rectangle: {str(e)}"
                )
            ]
        }

@mcp.tool()
async def add_text_in_paint(text: str, x1: int, y1: int, x2: int, y2: int) -> dict:
    """Add text at the center of the specified rectangle coordinates"""
    global paint_app
    try:
        if not paint_app:
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Paint is not open. Please call open_paint first."
                    )
                ]
            }
        
        # Get the Paint window
        paint_window = paint_app.window(class_name='MSPaintApp')
        
        # Ensure Paint window is active
        if not paint_window.has_focus():
            paint_window.set_focus()
            time.sleep(0.5)
        
        # Use pyautogui as a more reliable alternative
        import pyautogui
        
        # Click on text tool (approximate position)
        pyautogui.click(421, 110)  # Text tool position
        time.sleep(0.5)
        
        # Calculate center of the specified rectangle
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        
        ## Drag a small text box inside the rectangle
        pyautogui.mouseDown(center_x - 50, center_y - 20)
        pyautogui.dragTo(center_x + 50, center_y + 20, duration=0.5)
        pyautogui.mouseUp()
        time.sleep(1.5)  # Wait longer for text input box to activate
        
        # Type the text
        pyautogui.write(text)  # Use write instead of typewrite for better reliability
        time.sleep(1.0)  # Wait for text to be fully typed
        
        # Finalize text by clicking outside the text box
        pyautogui.click(center_x + 150, center_y + 150)  # adjust so it's outside
        time.sleep(0.5)
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Text '{text}' added at rectangle center ({center_x}, {center_y})"
                )
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error adding text: {str(e)}"
                )
            ]
        }

# DEFINE RESOURCES

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    print("CALLED: get_greeting(name: str) -> str:")
    return f"Hello, {name}!"


# DEFINE AVAILABLE PROMPTS
@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"
    print("CALLED: review_code(code: str) -> str:")


@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]

@mcp.tool()
async def send_email(to: str, subject: str, body: str) -> dict:
    """Send an email using Gmail SMTP.

    Parameters:
      to: Recipient email address
      subject: Subject line of the email
      body: Plain text body content (will also be wrapped in minimal HTML)

    Behavior:
      - Loads GMAIL_ADDRESS and GMAIL_APP_PASSWORD from environment (.env)
      - Uses Gmail's SMTP server (smtp.gmail.com:587) with TLS
      - Sends both plain text and HTML version
      - Returns a dict with status and any error message
    """
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
    except Exception as e:
        return {"status": "error", "error": f"Failed to import email libraries: {e}"}

    # Get and clean Gmail credentials (remove quotes and spaces)
    gmail_address = os.getenv("GMAIL_ADDRESS", "").strip().strip('"').strip("'")
    gmail_app_password = os.getenv("GMAIL_APP_PASSWORD", "").strip().strip('"').strip("'")
    
    if not gmail_address:
        return {"status": "error", "error": "GMAIL_ADDRESS not set in environment"}
    if not gmail_app_password:
        return {"status": "error", "error": "GMAIL_APP_PASSWORD not set in environment"}
    
    if "@" not in gmail_address:
        return {"status": "error", "error": f"Invalid GMAIL_ADDRESS: {gmail_address}"}

    print(f"DEBUG send_email: from={gmail_address}, to={to}")

    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = gmail_address
        msg['To'] = to

        # Add plain text and HTML versions
        part1 = MIMEText(body, 'plain')
        part2 = MIMEText(f"<pre style='font-family: monospace'>{body}</pre>", 'html')
        msg.attach(part1)
        msg.attach(part2)

        # Connect to Gmail SMTP server
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Secure the connection
            server.login(gmail_address, gmail_app_password)
            server.send_message(msg)
        
        return {
            "status": "success",
            "message": f"Email sent to {to} from {gmail_address}"
        }
    except Exception as e:
        # Provide detailed error information
        error_msg = str(e)
        return {"status": "error", "error": error_msg, "from": gmail_address, "to": to}

if __name__ == "__main__":
    # Check if running with mcp dev command
    print("STARTING")
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()  # Run without transport for dev server
    else:
        mcp.run(transport="stdio")  # Run with stdio for direct execution
