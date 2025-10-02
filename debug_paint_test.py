from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio

async def main():
    """Test Paint features with debug information"""
    print("Starting Paint debug test...")
    try:
        # Create MCP server connection to debug version
        print("Establishing connection to debug MCP server...")
        server_params = StdioServerParameters(
            command="python",
            args=["example2_debug.py"]
        )

        async with stdio_client(server_params) as (read, write):
            print("Connection established, creating session...")
            async with ClientSession(read, write) as session:
                print("Session created, initializing...")
                await session.initialize()
                
                print("\n=== Testing Paint Features with Debug ===")
                
                # 1. Open Paint
                print("Opening Paint...")
                result = await session.call_tool("open_paint")
                print(result.content[0].text)

                # Wait for Paint to be fully loaded
                await asyncio.sleep(2)

                # 2. Debug Paint window structure
                print("\nDebugging Paint window...")
                result = await session.call_tool("debug_paint_window")
                print(result.content[0].text)

                # 3. Try simple rectangle drawing
                print("\nTrying simple rectangle drawing...")
                result = await session.call_tool(
                    "draw_rectangle_simple",
                    arguments={
                        "x1": 300,
                        "y1": 250,
                        "x2": 1000,
                        "y2": 700
                    }
                )
                print(result.content[0].text)

                # 4. Try text addition inside the rectangle
                print("\nTrying text addition inside the rectangle...")
                result = await session.call_tool(
                    "add_text_simple",
                    arguments={
                        "text": "Inside Rectangle!"
                    }
                )
                print(result.content[0].text)
                
                print(result.content[0].text)
                
                print("\n=== Debug test completed ===")

    except Exception as e:
        print(f"Error in debug test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())