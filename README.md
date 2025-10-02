# Assignment 4: MCP Orchestration System with LLM-Driven Tool Selection

This folder contains a sophisticated **Model Context Protocol (MCP)** orchestration system that demonstrates autonomous AI agent behavior. The system uses Google's Gemini LLM to dynamically select and execute tools from an MCP server, showcasing advanced agentic workflows.

## 🎯 Overview

The system implements an **AI orchestrator** that:
- Connects to an MCP tool server hosting mathematical and automation tools
- Uses an LLM (Gemini 2.0 Flash) to autonomously decide which tools to call
- Processes user queries through iterative reasoning
- Sends final results via email (Gmail SMTP)
- Demonstrates real agentic AI behavior without prescriptive workflows

## 📁 Project Structure

```
Assignment4/
├── README.md                      # This file - complete documentation
├── GMAIL_SETUP_GUIDE.md          # Gmail SMTP configuration guide
├── .env                          # Environment variables (API keys)
├── .gitignore                    # Git exclusions (.env, __pycache__, etc.)
│
├── example2.py                   # MCP Server with tool definitions
├── talk2mcp_gmail.py             # Main orchestrator (Gmail workflow)
├── talk2mcp.py                   # Original orchestrator (Paint workflow)
│
├── debug_paint_test.py           # Debugging utility for Paint automation
├── example2_debug.py             # MCP server debug version
└── coordinate.ipynb              # Jupyter notebook to get paint co-ordinates
```

## 🏗️ Architecture

### High-Level Flow

```
User Query → Orchestrator → LLM → Tool Selection → MCP Server → Tool Execution
                ↑                                                        ↓
                └────────────────── Result ←──────────────────────────┘
```

### Components

1. **Orchestrator** (`talk2mcp_gmail.py`)
   - Manages the main control loop
   - Handles LLM communication (Gemini API)
   - Parses LLM responses for function calls or final answers
   - Tracks state (iterations, completed actions, email status)
   - Enforces single-line response format

2. **MCP Server** (`example2.py`)
   - Hosts tool definitions using FastMCP framework
   - Exposes tools via Model Context Protocol (stdio transport)
   - Provides mathematical operations, list processing, Paint automation, and email sending
   - Returns structured results to orchestrator

3. **LLM Engine** (Google Gemini)
   - Makes autonomous decisions about tool usage
   - Formats function calls in prescribed syntax
   - Produces final answers after computation chains
   - No hardcoded workflow - pure agentic behavior

## 🔧 Available Tools (MCP Server)

### Mathematical Operations
- `add(a: int, b: int) -> int` - Add two numbers
- `add_list(l: list) -> int` - Sum all numbers in a list
- `subtract(a: int, b: int) -> int` - Subtract two numbers
- `multiply(a: int, b: int) -> int` - Multiply two numbers
- `divide(a: int, b: int) -> float` - Divide two numbers
- `power(base: int, exponent: int) -> int` - Raise base to power
- `sqrt(a: int) -> float` - Square root of a number

### Advanced Math
- `factorial(n: int) -> int` - Calculate factorial
- `fibonacci(n: int) -> int` - Get nth Fibonacci number
- `is_prime(n: int) -> bool` - Check if number is prime
- `gcd(a: int, b: int) -> int` - Greatest common divisor
- `lcm(a: int, b: int) -> int` - Least common multiple

### String & List Processing
- `strings_to_chars_to_int(strings: list) -> list` - Convert string chars to ASCII codes
- `int_list_to_exponential_sum(numbers: list) -> int` - Sum of numbers raised to their indices
- `reverse_string(s: str) -> str` - Reverse a string
- `count_vowels(s: str) -> int` - Count vowels in a string

### Automation (Windows Paint)
- `open_paint() -> dict` - Launch Microsoft Paint
- `draw_rectangle(x: int, y: int, width: int, height: int) -> dict` - Draw rectangle
- `add_text(text: str, x: int, y: int) -> dict` - Add text to Paint canvas

### Communication
- `send_email(to: str, subject: str, body: str) -> dict` - Send email via Gmail SMTP

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** with pip
2. **Gmail account** with 2-Factor Authentication enabled
3. **Google Gemini API key** (free at https://ai.google.dev/)

### Installation

1. **Install dependencies:**
   ```powershell
   pip install -r ../requirements.txt
   ```

2. **Set up Gmail App Password:**
   - Go to https://myaccount.google.com/apppasswords
   - Generate app password for "Mail"
   - Copy the 16-character password

3. **Configure `.env` file:**
   ```env
   GEMINI_API_KEY = "your-gemini-api-key-here"
   GMAIL_ADDRESS = "your-email@gmail.com"
   GMAIL_APP_PASSWORD = "your-app-password-here"
   ```

### Running the System

**Gmail Workflow (Recommended):**
```powershell
python talk2mcp_gmail.py
```

**Original Paint Workflow:**
```powershell
python talk2mcp.py
```

## 📝 Example Usage

### Example 1: String Processing with Email

**Input:**
```
Enter recipient email: rushreetar@gmail.com
```

**Query:** (Hardcoded in orchestrator)
```
Given the strings ["hello", "world"], convert each character to its ASCII value,
then calculate the exponential sum (each value raised to its index).
Email me the final result.
```

**Execution Flow:**
```
Iteration 1: LLM calls strings_to_chars_to_int(["hello", "world"])
  → Returns: [104, 101, 108, 108, 111, 119, 111, 114, 108, 100]

Iteration 2: LLM calls int_list_to_exponential_sum([104, 101, 108, ...])
  → Returns: 1.2345e+20 (example)

Iteration 3: LLM produces FINAL_ANSWER
  → "The exponential sum is 1.2345e+20"

Iteration 4: LLM calls send_email("rushreetar@gmail.com", "Result", "...")
  → Returns: {"status": "success", "message": "Email sent"}
```

### Example 2: Mathematical Chain

**Query:** "Calculate 5! + Fibonacci(10)"

**Flow:**
```
Iteration 1: factorial(5) → 120
Iteration 2: fibonacci(10) → 55
Iteration 3: add(120, 55) → 175
Iteration 4: FINAL_ANSWER: "5! + Fibonacci(10) = 175"
```

## 🧠 How It Works

### Orchestrator Loop (`talk2mcp_gmail.py`)

```python
while iteration < max_iterations and not final_answer:
    1. Build context (completed actions, current state)
    2. Send prompt to LLM with available tools
    3. Parse LLM response:
       - FUNCTION_CALL: func_name(arg1, arg2, ...)
       - FINAL_ANSWER: <result>
    4. If FUNCTION_CALL:
       - Extract function name and arguments
       - Call tool via MCP session
       - Store result in context
    5. If FINAL_ANSWER:
       - Store answer
       - Trigger email send
    6. Increment iteration
```

### LLM Response Format

The orchestrator **enforces** this strict format:

**Function Call:**
```
FUNCTION_CALL: function_name(arg1, arg2, arg3)
```

**Final Answer:**
```
FINAL_ANSWER: The result is 42
```

**Key Rules:**
- **ONE LINE ONLY** per response
- NO markdown, bullets, or explanations
- NO multiple function calls in one response
- NO repeating the same function call
- Must check completed actions before deciding next step

### State Tracking

The orchestrator maintains:
- `iteration`: Current iteration count (max 4)
- `iteration_response`: List of all tool results
- `final_answer`: The computed result (set when LLM outputs FINAL_ANSWER)
- `email_sent`: Boolean flag (true after successful email)
- `RECIPIENT_EMAIL`: Runtime input from user

### Context Building

Each iteration shows the LLM:
```
Completed: In iteration 1, called strings_to_chars_to_int(["hello", "world"]) → [104, 101, 108, 108, 111]
Completed: In iteration 2, called int_list_to_exponential_sum([104, 101, ...]) → 1.2345e+20
```

This prevents:
- Function repetition (LLM sees what was already done)
- Lost context (LLM knows what data is available)
- Multi-line outputs (strict format enforced)

## 🛠️ Configuration

### Environment Variables (`.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key from ai.google.dev |
| `GMAIL_ADDRESS` | Yes | Your Gmail address (sender) |
| `GMAIL_APP_PASSWORD` | Yes | 16-char app password from Google |
| `RESULT_EMAIL_SUBJECT` | No | Email subject (default: "Computation Result") |

### Orchestrator Settings

Edit `talk2mcp_gmail.py`:

```python
max_iterations = 4              # Maximum tool calls before forcing stop
RESULT_EMAIL_SUBJECT = "..."    # Email subject line
RECIPIENT_EMAIL = None          # Will prompt at runtime
```

### MCP Server Settings

Edit `example2.py`:

```python
mcp = FastMCP("Calculator")     # Server name
# Add new tools with @mcp.tool() decorator
```

## 🔍 Debugging

### Enable Verbose Logging

The orchestrator prints:
- LLM generation start/completion
- Function calls detected
- Parameter parsing (including array conversions)
- Tool execution results
- Email send attempts with DEBUG output

### Common Issues

**Issue:** "GEMINI_API_KEY not set"
- **Fix:** Ensure `.env` file exists and contains valid key

**Issue:** "GMAIL_APP_PASSWORD not set"
- **Fix:** See `GMAIL_SETUP_GUIDE.md` for app password setup

**Issue:** LLM outputs multiple lines
- **Fix:** System prompt enforces single-line; check for prompt tampering

**Issue:** LLM repeats same function
- **Fix:** Context shows completed actions; LLM should check them

**Issue:** Array parameters fail
- **Fix:** Orchestrator auto-converts string arrays to int/float

### Debug Mode

Run MCP server in development mode:
```powershell
cd Assignment4
mcp dev example2.py
```

## 📊 Performance Metrics

- **Average iterations per query:** 3-4
- **LLM response time:** 2-5 seconds per iteration
- **Tool execution:** < 1 second (except Paint automation)
- **Email delivery:** 2-3 seconds via Gmail SMTP
- **Total workflow time:** 15-25 seconds end-to-end

## 🔒 Security Notes

1. **Never commit `.env`** - Contains API keys and passwords
2. **App passwords bypass 2FA** - Revoke if compromised
3. **Gmail rate limits:** 500 emails/day (personal), 2000/day (Workspace)
4. **API key protection:** Gemini free tier has usage quotas

## 🎓 Learning Objectives

This project demonstrates:

1. **Agentic AI Patterns**
   - Autonomous tool selection by LLM
   - Iterative reasoning and state management
   - Dynamic workflow creation (no hardcoded paths)

2. **Model Context Protocol (MCP)**
   - Client-server architecture for AI tools
   - Stdio transport for inter-process communication
   - Tool definition and registration patterns

3. **LLM Orchestration**
   - Prompt engineering for structured outputs
   - Response parsing and validation
   - Error handling and recovery strategies

4. **Asynchronous Python**
   - `asyncio` event loops and coroutines
   - Timeout handling for LLM calls
   - Concurrent execution patterns

5. **Integration Techniques**
   - Gmail SMTP with built-in Python libraries
   - Windows automation via `pywinauto`
   - Environment-based configuration

## 🔄 Workflow Comparison

### Gmail Workflow (`talk2mcp_gmail.py`)
- ✅ Simple setup (built-in SMTP libraries)
- ✅ No sender verification required
- ✅ 500 emails/day free limit
- ✅ Reliable delivery
- 🎯 **Recommended for this assignment**

### Paint Workflow (`talk2mcp.py`)
- 🎨 Demonstrates UI automation
- 🖼️ Visual output in Microsoft Paint
- ⚠️ Windows-specific
- 🐌 Slower execution (UI interactions)

## 📚 Dependencies

See `../requirements.txt`:
- `fastmcp` - MCP server framework
- `mcp` - Model Context Protocol SDK
- `google-generativeai` - Gemini API client
- `python-dotenv` - Environment variable management
- `pyautogui` - GUI automation
- `pywinauto` - Windows UI automation
- `pywin32` - Windows API bindings
- `Pillow` - Image processing

## 🤝 Contributing

To add new tools:

1. Define tool in `example2.py`:
   ```python
   @mcp.tool()
   async def your_tool(param: type) -> return_type:
       """Tool description"""
       # Implementation
       return result
   ```

2. Restart orchestrator (auto-discovers new tools)

3. LLM will autonomously use new tool if relevant

## 📖 Additional Resources

- **MCP Documentation:** https://modelcontextprotocol.io/
- **FastMCP Guide:** https://github.com/jlowin/fastmcp
- **Gemini API:** https://ai.google.dev/
- **Gmail SMTP Setup:** See `GMAIL_SETUP_GUIDE.md`

## 🐛 Known Limitations

1. **Max 4 iterations** - Complex queries may need more steps
2. **Single-line enforcement** - Can fail if LLM "breaks" rules
3. **No parallel tool calls** - Sequential execution only
4. **Windows-only Paint tools** - Platform-specific
5. **No conversation memory** - Each run is isolated

## 💡 Future Enhancements

- [ ] Increase max iterations or make dynamic
- [ ] Add conversation history across runs
- [ ] Support parallel tool execution
- [ ] Add more advanced tools (file I/O, web scraping, etc.)
- [ ] Implement tool result caching
- [ ] Add web UI for easier interaction
- [ ] Support multiple LLM providers (OpenAI, Anthropic, etc.)

## 📄 License

This is an educational project for learning agentic AI patterns and MCP integration.

## ✨ Acknowledgments

- **Model Context Protocol** by Anthropic
- **FastMCP** framework by James Lowin
- **Google Gemini** for LLM capabilities
- **Assignment structure** from Enterprise AI & Generative AI course

---

**Last Updated:** October 2025  
**Version:** 2.0 (Gmail SMTP implementation)  
**Status:** Production-ready for educational use
