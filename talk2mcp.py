import os
import time
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import asyncio
from google import genai
from concurrent.futures import TimeoutError

# Load environment variables from .env file
load_dotenv()

# Access your API key and initialize Gemini client
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# Global variables
max_iterations = 8
last_response = None
iteration = 0
iteration_response = []
final_answer = None
last_rectangle_coords = None  # store rectangle coordinates dynamically
paint_opened = False
rectangle_drawn = False
text_added = False

async def generate_with_timeout(client, prompt, timeout=10):
    """Generate content with a timeout"""
    print("Starting LLM generation...")
    try:
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None, 
                lambda: client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
            ),
            timeout=timeout
        )
        print("LLM generation completed")
        return response
    except TimeoutError:
        print("LLM generation timed out!")
        raise
    except Exception as e:
        print(f"Error in LLM generation: {e}")
        raise

def reset_state():
    """Reset all global variables to their initial state"""
    global last_response, iteration, iteration_response, final_answer, last_rectangle_coords, paint_opened, rectangle_drawn, text_added
    last_response = None
    iteration = 0
    iteration_response = []
    final_answer = None
    last_rectangle_coords = None
    paint_opened = False
    rectangle_drawn = False
    text_added = False

async def main():
    reset_state()
    print("Starting main execution...")
    try:
        # MCP server connection
        server_params = StdioServerParameters(
            command="python",
            args=["example2.py"]
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Get available tools
                tools_result = await session.list_tools()
                tools = tools_result.tools
                print(f"Retrieved {len(tools)} tools")

                # Build tools description
                tools_description = []
                for i, tool in enumerate(tools):
                    try:
                        # Get tool properties
                        params = tool.inputSchema
                        desc = getattr(tool, 'description', 'No description available')
                        name = getattr(tool, 'name', f'tool_{i}')

                        # Format the input schema in a more readable way
                        if 'properties' in params:
                            param_details = []
                            for param_name, param_info in params['properties'].items():
                                param_type = param_info.get('type', 'unknown')
                                param_details.append(f"{param_name}: {param_type}")
                            params_str = ', '.join(param_details)
                        else:
                            params_str = 'no parameters'
                        tools_description.append(f"{i+1}. {name}({params_str}) - {desc}")
                    except Exception as e:
                        tools_description.append(f"{i+1}. Error processing tool")

                tools_description = "\n".join(tools_description)

                # System prompt
                system_prompt = f"""You are an intelligent agent that can perform mathematical calculations and create visual representations.

Available tools:
{tools_description}

GENERAL WORKFLOW:
1. Solve mathematical problems using the available calculation tools
2. Provide FINAL_ANSWER when calculations are complete
3. After computing results, create visual representations using appropriate graphics tools

RESPONSE FORMAT:
You must respond with EXACTLY ONE function call or final answer per response:
- FUNCTION_CALL: function_name|param1|param2|...
- FINAL_ANSWER: [your_computed_result]

IMPORTANT GUIDELINES:
- Study the available tools and their descriptions carefully
- Choose appropriate tools based on their documentation and purpose
- When drawing in Paint, use these co-ordinates: (x1, y1, x2, y2) as (300, 250, 1000, 700)
- Follow logical sequences (e.g., open applications before using them)
- Use reasonable parameter values based on tool descriptions
- Only provide ONE function call or FINAL_ANSWER per response
- After FINAL_ANSWER, continue with visualization if needed

Examples:
- FUNCTION_CALL: add|5|3
- FUNCTION_CALL: strings_to_chars_to_int|HELLO
- FINAL_ANSWER: 42

DO NOT include explanations or additional text.
Your response should be a single line starting with FUNCTION_CALL: or FINAL_ANSWER:
"""

                query = """Compute the sum of ASCII values of characters in "INDIA" and then calculate the sum of exponentials of those values. After getting the final mathematical result, create a visual representation by displaying the result in a graphics application."""
                print("Starting iteration loop...")

                # Use global iteration variables
                global iteration, last_response, final_answer, last_rectangle_coords, paint_opened, rectangle_drawn, text_added

                while iteration < max_iterations:
                    print(f"\n--- Iteration {iteration + 1} ---")
                    
                    # # Build context with current workflow status
                    # workflow_status = []
                    # if final_answer is not None:
                    #     workflow_status.append(f"✓ Mathematical computation complete: {final_answer}")
                    # if paint_opened:
                    #     workflow_status.append("✓ Paint opened")
                    # if rectangle_drawn:
                    #     workflow_status.append("✓ Rectangle drawn")
                    # if text_added:
                    #     workflow_status.append("✓ Text added to Paint")
                    
                    # status_text = "\n".join(workflow_status) if workflow_status else "No steps completed yet"
                    
                    # if final_answer is not None and not paint_opened:
                    #     next_step_hint = "\nSuggestion: Consider using graphics tools to visualize the result"
                    # elif paint_opened and not rectangle_drawn:
                    #     next_step_hint = "\nSuggestion: Create shapes or boundaries for your visualization"
                    # elif rectangle_drawn and not text_added:
                    #     next_step_hint = f"\nSuggestion: Display your computed result in the graphics"
                    # else:
                    #     next_step_hint = ""
                    
                    # context = f"{query}\n\nWorkflow Status:\n{status_text}{next_step_hint}"
                    # if iteration_response:
                    #     context += f"\n\nPrevious results:\n" + "\n".join(iteration_response[-3:])  # Last 3 results only
                    
                    # current_query = context
                    if last_response is None:
                        current_query = query
                    else:
                        current_query = current_query + "\n\n" + " ".join(iteration_response)
                        current_query = current_query + "  What should I do next?"

                    # Get model's response with timeout
                    print("Preparing to generate LLM response...")
                    prompt = f"{system_prompt}\n\nQuery: {current_query}"
                    try:
                        response = await generate_with_timeout(client, prompt)
                        response_text = response.text.strip()
                        print(f"LLM Response: {response_text}")
                        
                        # Find the FUNCTION_CALL line in the response
                        for line in response_text.split("\n"):
                            line = line.strip()
                            if line.startswith("FUNCTION_CALL:") or line.startswith("FINAL_ANSWER:"):
                                response_text = line
                                break

                    except Exception as e:
                        print(f"Failed to get LLM response: {e}")
                        break

                    if response_text.startswith("FUNCTION_CALL:"):
                        _, function_info = response_text.split(":", 1)
                        parts = [p.strip() for p in function_info.split("|")]
                        func_name, params = parts[0], parts[1:]
                        print(f"Executing FUNCTION_CALL: {func_name} with params {params}")

                        try:
                            # Find the matching tool to get its input schema
                            tool = next((t for t in tools if t.name == func_name), None)
                            if not tool:
                                print(f"DEBUG: Available tools: {[t.name for t in tools]}")
                                raise ValueError(f"Unknown tool: {func_name}")
                            
                            print(f"DEBUG: Found tool: {tool.name}")
                            print(f"DEBUG: Tool schema: {tool.inputSchema}")

                            # Prepare arguments according to the tool's input schema
                            arguments = {}
                            schema_properties = tool.inputSchema.get('properties', {})
                            print(f"DEBUG: Schema properties: {schema_properties}")
                            
                            # Special handling for open_paint - allow no parameters
                            if func_name == "open_paint" and not params:
                                # Use default parameters for open_paint
                                pass  # arguments will be set below in the state tracking section
                            else:
                                for param_name, param_info in schema_properties.items():
                                    if not params:  # Check if we have enough parameters
                                        raise ValueError(f"Not enough parameters provided for {func_name}")
                                    
                                    value = params.pop(0)  # Get and remove the first parameter
                                    param_type = param_info.get('type', 'string')

                                    print(f"DEBUG: Converting parameter {param_name} with value {value} to type {param_type}")
                                        
                                    # Special handling for add_text_in_paint rect_coords parameter
                                    if func_name == "add_text_in_paint" and param_name == "rect_coords":
                                        # Keep as string for special processing later
                                        arguments[param_name] = str(value)
                                    elif param_type == 'integer':
                                        arguments[param_name] = int(value)
                                    elif param_type == 'number':
                                        arguments[param_name] = float(value)
                                    elif param_type == 'array':
                                        if isinstance(value, str):
                                            # Handle both formats: [1,2,3] and ['1','2','3']
                                            value = value.strip('[]').split(',')
                                            # Remove quotes and whitespace from each element
                                            arguments[param_name] = [int(x.strip().strip("'\"")) for x in value]
                                    else:
                                        arguments[param_name] = str(value)

                            # Track workflow state and handle parameters
                            if func_name == "open_paint":
                                paint_opened = True
                                # Handle open_paint parameters - ensure valid values
                                if 'monitor' in arguments:
                                    # Convert monitor parameter and ensure it's valid (1 or 2)
                                    monitor_val = int(arguments['monitor'])
                                    arguments['monitor'] = 1 if monitor_val <= 0 else monitor_val
                                else:
                                    arguments['monitor'] = 1
                                if 'maximize' not in arguments:
                                    arguments['maximize'] = True
                            
                            elif func_name == "draw_rectangle":
                                rectangle_drawn = True
                                last_rectangle_coords = arguments

                            elif func_name == "add_text_in_paint":
                                text_added = True
                                # Use final_answer as text if available
                                if "text" in arguments and final_answer is not None:
                                    if arguments["text"] == final_answer or arguments["text"] == "[FINAL_ANSWER]":
                                        arguments["text"] = str(final_answer)
                                
                                # Handle rect_coords parameter - convert from tuple format if needed
                                if "rect_coords" in arguments and isinstance(arguments["rect_coords"], str):
                                    try:
                                        # Parse string like "(100,100,400,200)" or "(100, 100, 400, 200)" into tuple
                                        coord_str = arguments["rect_coords"].strip().strip('()')
                                        # Split by comma and clean up each coordinate
                                        coord_parts = [part.strip() for part in coord_str.split(',')]
                                        coords = [int(part) for part in coord_parts if part.isdigit() or (part.startswith('-') and part[1:].isdigit())]
                                        if len(coords) == 4:
                                            arguments["rect_coords"] = tuple(coords)
                                        else:
                                            raise ValueError(f"Expected 4 coordinates, got {len(coords)}")
                                    except Exception as parse_error:
                                        print(f"Error parsing rect_coords: {parse_error}")
                                        # Use last rectangle coordinates as fallback
                                        if last_rectangle_coords:
                                            arguments["rect_coords"] = (
                                                last_rectangle_coords.get('x1', 100),
                                                last_rectangle_coords.get('y1', 100), 
                                                last_rectangle_coords.get('x2', 400),
                                                last_rectangle_coords.get('y2', 200)
                                            )
                                elif "rect_coords" not in arguments and last_rectangle_coords:
                                    # Use last drawn rectangle coordinates if not specified
                                    arguments["rect_coords"] = (
                                        last_rectangle_coords.get('x1', 100),
                                        last_rectangle_coords.get('y1', 100), 
                                        last_rectangle_coords.get('x2', 400),
                                        last_rectangle_coords.get('y2', 200)
                                    )

                            result = await session.call_tool(func_name, arguments=arguments)
                            iteration_result = []

                            # Get the full result content
                            if hasattr(result, 'content'):
                                if isinstance(result.content, list):
                                    iteration_result = [item.text if hasattr(item, 'text') else str(item) for item in result.content]
                                else:
                                    iteration_result = [str(result.content)]
                            else:
                                iteration_result = [str(result)]

                            iteration_response.append(f"In iteration {iteration+1}, called {func_name}({arguments}) -> {iteration_result}")
                            last_response = iteration_result

                            # Check if we've completed the Paint workflow
                            if func_name == "add_text_in_paint" and final_answer is not None and paint_opened and rectangle_drawn:
                                print("\n=== WORKFLOW COMPLETED: Paint visualization created successfully! ===")
                                print(f"Final answer '{final_answer}' has been added to Paint rectangle.")
                                break

                        except Exception as e:
                            print(f"Error executing function call: {e}")
                            iteration_response.append(f"Error in iteration {iteration+1}: {str(e)}")
                            break

                    elif response_text.startswith("FINAL_ANSWER:"):
                        final_answer = response_text.split(":",1)[1].strip()
                        iteration_response.append(f"FINAL_ANSWER: {final_answer}")
                        last_response = final_answer
                        print(f"\n=== FINAL ANSWER COMPUTED: {final_answer} ===")
                        
                        # Now automatically continue to have LLM call Paint functions
                        # The LLM will continue in next iterations to open Paint, draw rectangle, and add text

                    else:
                        # Handle any other response format
                        print(f"Unexpected response format: {response_text}")
                        iteration_response.append(f"Unexpected response in iteration {iteration+1}: {response_text}")

                    iteration += 1
                    time.sleep(60)  # Brief pause between iterations

    except Exception as e:
        print(f"Error in main execution: {e}")
    finally:
        reset_state()

if __name__ == "__main__":
    asyncio.run(main())