# Debug version with enhanced error reporting
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
import time
import pyautogui
from pywinauto.application import Application
import win32gui
import win32con
from win32api import GetSystemMetrics

# instantiate an MCP server client
mcp = FastMCP("Calculator")

# Global variable for Paint application
paint_app = None

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
async def draw_rectangle_simple(x1: int, y1: int, x2: int, y2: int) -> dict:
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
async def add_text_simple(text: str) -> dict:
    """Simple text addition using pyautogui as fallback - places text at center of last rectangle (300,250,600,450)"""
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
        
        # Calculate center of the last rectangle (300,250,600,450)
        center_x = (300 + 600) // 2  # 450
        center_y = (250 + 450) // 2  # 350
        
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

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()
    else:
        mcp.run(transport="stdio")