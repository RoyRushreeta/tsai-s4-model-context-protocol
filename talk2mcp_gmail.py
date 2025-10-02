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

# Email configuration (recipient will be prompted at runtime)
RECIPIENT_EMAIL = None  # will be set via input() in main()
RESULT_EMAIL_SUBJECT = os.getenv("RESULT_EMAIL_SUBJECT", "Computation Result")

# Global variables
max_iterations = 4
last_response = None
iteration = 0
iteration_response = []
final_answer = None
email_sent = False

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
    global last_response, iteration, iteration_response, final_answer, email_sent
    last_response = None
    iteration = 0
    iteration_response = []
    final_answer = None
    email_sent = False

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

                # Prompt user for recipient email once (interactive)
                global RECIPIENT_EMAIL
                if RECIPIENT_EMAIL is None:
                    entered = input("Enter recipient email for results (leave blank to use default from env or fallback): ").strip()
                    if not entered:
                        RECIPIENT_EMAIL = (
                            os.getenv("RESULT_RECIPIENT_EMAIL")
                            or os.getenv("RESULT_TO_EMAIL")
                            or os.getenv("SENDGRID_TO_EMAIL")
                            or os.getenv("DEFAULT_RESULT_EMAIL")
                            or "myaddress@gmail.com"
                        )
                        print(f"Using default recipient: {RECIPIENT_EMAIL}")
                    else:
                        RECIPIENT_EMAIL = entered
                        print(f"Using provided recipient: {RECIPIENT_EMAIL}")

                # Basic validation (very light)
                if RECIPIENT_EMAIL and "@" not in RECIPIENT_EMAIL:
                    print("WARNING: Provided recipient email may be invalid (missing @). Proceeding anyway.")

                # System prompt
                system_prompt = f"""You are an intelligent agent that performs calculations step-by-step and then sends the final result via email.

Available tools:
{tools_description}

CRITICAL RULES:
1. Output EXACTLY ONE LINE per response
2. DO NOT repeat a function call that has already been completed
3. USE the results from previous function calls as input for the next function
4. Progress forward through the workflow - never go backwards
5. When sending email, ALWAYS use this exact recipient address: {RECIPIENT_EMAIL}

RESPONSE FORMAT (EXACTLY ONE LINE):
FUNCTION_CALL: function_name|arg1|arg2|...
OR
FINAL_ANSWER: value

INSTRUCTIONS:
- Check "Completed:" section first - if you see results from a previous call, USE those results
- NEVER call the same function twice with the same arguments
- For arrays, if you see a result like "-> [[73, 78, 68, 73, 65]]", use that array in the next function
- For send_email, format must be: send_email|{RECIPIENT_EMAIL}|Subject|MessageBody
- NO explanations, NO markdown, just the single function call or answer

WORKFLOW EXAMPLE:
Step 1: FUNCTION_CALL: strings_to_chars_to_int|HELLO
  Result: [72, 69, 76, 76, 79]
Step 2: FUNCTION_CALL: add_list|72,69,76,76,79
  Result: 372
Step 3: FINAL_ANSWER: 372
Step 4: FUNCTION_CALL: send_email|{RECIPIENT_EMAIL}|Computation Result|372

DO NOT include explanations or additional text.
Your response should be a single line starting with FUNCTION_CALL: or FINAL_ANSWER:
"""

                query = """Compute the sum of ASCII values of characters in \"INDIA\" and then calculate the sum of exponentials of those values. After computing, email me the result."""
                print("Starting iteration loop...")

                # Use global iteration variables
                global iteration, last_response, final_answer, email_sent

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
                    # print(f"DEBUG - Context being sent to LLM:\n{current_query}\n")
                    try:
                        response = await generate_with_timeout(client, prompt)
                        response_text = response.text.strip()
                        print(f"LLM Response: {response_text}")
                        
                        # Find the FUNCTION_CALL or FINAL_ANSWER line in the response
                        # Handle various formats: with/without leading dash, bullet, etc.
                        for line in response_text.split("\n"):
                            line = line.strip()
                            # Strip leading markdown bullets/dashes
                            if line.startswith("- "):
                                line = line[2:].strip()
                            elif line.startswith("* "):
                                line = line[2:].strip()
                            
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

                        # (Autonomous mode) No gating after FINAL_ANSWER

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
                            
                            # Special handling: allow flexible argument counts for send_email.
                            if func_name == "send_email":
                                # Normalize params to exactly [to, subject, body]
                                if len(params) == 0:
                                    params = [RECIPIENT_EMAIL, RESULT_EMAIL_SUBJECT, "[FINAL_ANSWER]"]
                                elif len(params) == 1:
                                    # Assume provided value is body
                                    params = [RECIPIENT_EMAIL, RESULT_EMAIL_SUBJECT, params[0]]
                                elif len(params) == 2:
                                    # Assume subject, body
                                    params = [RECIPIENT_EMAIL, params[0], params[1]]
                                else:
                                    # If more than 3 provided, truncate to first 3
                                    params = params[:3]

                                # Allow email even if FINAL_ANSWER not yet emitted (autonomous mode)

                            for param_name, param_info in schema_properties.items():
                                if not params:
                                    raise ValueError(f"Not enough parameters provided for {func_name}")
                                value = params.pop(0)
                                param_type = param_info.get('type', 'string')
                                if param_type == 'integer':
                                    arguments[param_name] = int(value)
                                elif param_type == 'number':
                                    arguments[param_name] = float(value)
                                elif param_type == 'array':
                                    if isinstance(value, str):
                                        # Handle various array string formats
                                        value = value.strip('[]').strip()
                                        if ',' in value:
                                            # Split and convert to proper types (int if possible)
                                            items = value.split(',')
                                            converted = []
                                            for item in items:
                                                item = item.strip().strip("'\"")
                                                try:
                                                    converted.append(int(item))
                                                except ValueError:
                                                    try:
                                                        converted.append(float(item))
                                                    except ValueError:
                                                        converted.append(item)
                                            arguments[param_name] = converted
                                        else:
                                            # Single item or empty
                                            arguments[param_name] = [int(value)] if value and value.isdigit() else []
                                    elif isinstance(value, list):
                                        arguments[param_name] = value
                                else:
                                    # Replace placeholder [FINAL_ANSWER] if present
                                    if str(value) == '[FINAL_ANSWER]' and final_answer is not None:
                                        arguments[param_name] = str(final_answer)
                                    else:
                                        arguments[param_name] = str(value)

                            # Final safety: auto-fill missing 'to' for send_email if absent
                            if func_name == "send_email" and 'to' not in arguments:
                                arguments['to'] = RECIPIENT_EMAIL
                            if func_name == "send_email" and 'subject' not in arguments:
                                arguments['subject'] = RESULT_EMAIL_SUBJECT
                            if func_name == "send_email" and 'body' not in arguments and final_answer is not None:
                                arguments['body'] = str(final_answer)

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
                            print(f"Result captured: {iteration_result}")

                            # Mark completion heuristically if email sent and body has meaningful content
                            if func_name == "send_email":
                                body_sample = str(arguments.get('body', '')).strip()
                                if not final_answer and body_sample:
                                    # Treat body as implicit final answer if plausible (keep both states)
                                    final_answer = final_answer or body_sample
                                if body_sample:
                                    email_sent = True
                                    print("\n=== WORKFLOW COMPLETED: Email dispatched (body captured result). ===")
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
                        # Model may optionally choose to send email next

                    else:
                        # Handle any other response format
                        print(f"Unexpected response format: {response_text}")
                        iteration_response.append(f"Unexpected response in iteration {iteration+1}: {response_text}")

                    iteration += 1
                    if email_sent:
                        break
                    time.sleep(10)  # Shorter pause now that flow is simpler

    except Exception as e:
        import traceback
        print(f"Error in main execution: {e}")
        print(f"Error type: {type(e).__name__}")
        print("Full traceback:")
        traceback.print_exc()
    finally:
        reset_state()

if __name__ == "__main__":
    asyncio.run(main())