import os
import json
from openai import OpenAI
from dotenv import load_dotenv

API_KEY="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"
BASE_URL="https://api.groq.com/openai/v1"
LLM_MODEL="llama-3.3-70b-versatile"
WEATHER_API_KEY="ecbb81695c5f41a58db222301262303"

system_message = """You are a weather assistant.

IMPORTANT RULES:
- You MUST use the provided tools to answer weather questions.
- Do NOT answer from your own knowledge.
- If the user asks about weather, ALWAYS call the weather tool.
"""

print("API_KEY:", API_KEY)
print("BASE_URL:", BASE_URL)
print("LLM_MODEL:", LLM_MODEL) 

# Initialize the OpenAI client with custom base URL
# Replace with your API key or set it as an environment variable

client = OpenAI(
api_key=API_KEY,
base_url=BASE_URL,
)

import requests

def get_current_weather(location):
    """Get the current weather for a location."""
    api_key = WEATHER_API_KEY
    url = url = f"https://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={location}&aqi=no"
    response = requests.get(url)
    data = response.json()
    if "error" in data:
        return f"Error: {data['error']['message']}"
    weather_info = data["current"]
    
    print("WEATHER DEBUG:", data)
    return json.dumps(
        {
            "location": data["location"]["name"],
            "temperature_c": weather_info["temp_c"],
            "temperature_f": weather_info["temp_f"],
            "condition": weather_info["condition"]["text"],
            "humidity": weather_info["humidity"],
            "wind_kph": weather_info["wind_kph"],
        }
    )
    
def get_weather_forecast(location, days=3):
    """Get a weather forecast for a location for a specified number of days."""
    api_key = WEATHER_API_KEY
    url = url = f"https://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={location}&aqi=no"
    response = requests.get(url)
    data = response.json()
    if "error" in data:
        return f"Error: {data['error']['message']}"
    forecast_days = data["forecast"]["forecastday"]
    forecast_data = []
    for day in forecast_days:
        forecast_data.append(
            {
                "date": day["date"],
                "max_temp_c": day["day"]["maxtemp_c"],
                "min_temp_c": day["day"]["mintemp_c"],
                "condition": day["day"]["condition"]["text"],
                "chance_of_rain": day["day"]["daily_chance_of_rain"],
            }
        )
    return json.dumps(
        {
            "location": data["location"]["name"],
            "forecast": forecast_data,
        }
    )
    
    
weather_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": (
                            "The city and state, e.g., San Francisco, CA, "
                            "or a country, e.g., France"
                            ),
                        }
                    },
                    "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather_forecast",
            "description": (
                "Get the weather forecast for a location for a specific "
                "number of days"
                ),
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": (
                            "The city and state, e.g., San Francisco, CA, "
                            "or a country, e.g., France"
                            ),
                        },
                        "days": {
                            "type": "integer",
                            "description": "The number of days to forecast (1-10)",
                            "minimum": 1,
                            "maximum": 10,
                        },
                    },
                    "required": ["location"],
                },
            },
        },
    ]
# Create a lookup dictionary
available_functions = {
    "get_current_weather": get_current_weather,
    "get_weather_forecast": get_weather_forecast,
}


def process_messages(client, messages, tools=None, available_functions=None):
    """
    Process messages and invoke tools as needed.
    Args:
    client: The OpenAI client
    messages: The conversation history
    tools: The available tools
    available_functions: A dictionary mapping tool names to functions
    Returns:
    The list of messages with new additions
    """
    tools = tools or []
    available_functions = available_functions or {}
    
    # Step 1: Send the messages to the model with the tool definitions
    
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        tools=tools,
    )
    response_message = response.choices[0].message
    print("DEBUG:", response_message)
    # Step 2: Append the model's response to the conversation

    messages.append({
        "role": response_message.role,
        "content": response_message.content,
        "tool_calls": response_message.tool_calls,
    })
    
    # Step 3: Check if the model wanted to use a tool
    
    if response_message.tool_calls:

        # Step 4: Extract tool invocation and make evaluation

        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(**function_args)

            # Step 5: Extend conversation with function response

            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )
            
        second_response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
    )

    final_message = second_response.choices[0].message

    messages.append({
        "role": "assistant",
        "content": final_message.content or "Here is the result based on the tool output."
    })
    return messages


def run_conversation(client, system_message="You are a helpful weather assistant."):
    """
    Run a conversation with the user, processing their messages and handling
    tool calls.
    Args:
    client: The OpenAI client
    system_message: The system message to initialize the conversation
    Returns:
    The final conversation history
    """
    messages = [
        {
            "role": "system",
            "content": system_message,
        }
    ]
    print("Weather Assistant: Hello! I can help you with weather information.")
    print("Ask me about the weather anywhere!")
    print("(Type 'exit' to end the conversation)\n")
    
    while True:

        # Request user input and append to messages
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nWeather Assistant: Goodbye! Have a great day!")
            break
        messages.append(
            {
            "role": "user",
            "content": user_input,
            }
        )
        # Process the messages and get tool calls if any
        messages = process_messages(
            client,
            messages,
            weather_tools,
            available_functions,
        )
        # Check the last message to see if it's from the assistant
        last_message = messages[-1]
        # If the last message has content, print it
        if last_message["role"] == "assistant" and last_message.get("content"):
            print(f"\nWeather Assistant: {last_message['content']}\n")
    return messages
if __name__ == "__main__":
    # Make sure to set WEATHER_API_KEY in your .env file
    run_conversation(client)
    
    
    #################################### TASK 2 ########################################
def calculator(expression):
    """
    Evaluate a mathematical expression.
    Args:
    expression: A mathematical expression as a string
    Returns:
    The result of the evaluation
    """
    try:
        # Safely evaluate the expression
        # Note: This is not completely safe for production use
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"
    
    
calculator_tool = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Evaluate a mathematical expression",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": (
                        "The mathematical expression to evaluate, "
                        "e.g., '2 + 2' or '5 * (3 + 2)'"
                    ),
                }
            },
            "required": ["expression"],
        },
    },
}
# Add calculator to weather tools and available functions
cot_tools = weather_tools + [calculator_tool]
available_functions["calculator"] = calculator

cot_system_message = """You are a helpful assistant that can answer questions
about weather and perform calculations.

When responding to complex questions, please follow these steps:
1. Think step-by-step about what information you need.
2. Break down the problem into smaller parts.
3. Use the appropriate tools to gather information.
4. Explain your reasoning clearly.
5. Provide a clear final answer.
For example, if someone asks about temperature conversions or
comparisons between cities, first get the weather data, then use the
calculator if needed, showing your work.
"""
if __name__ == "__main__":
    # Test the Chain of Thought agent
    print("Testing Chain of Thought Agent:")
    run_conversation(client, cot_system_message)


def execute_tool_safely(tool_call, available_functions):
    """
    Execute a tool call with validation and error handling.
    Args:
    tool_call: The tool call object returned by the model
    available_functions: A dictionary mapping tool names to functions
    Returns:
    A JSON string describing either a success result or an error
    """
    
    function_name= tool_call.function.name
    if function_name not in available_functions:
        return json.dumps(
            {
                "success": False,
                "error": f"Unknown function: {function_name}",
            }
        )
    try:
        function_args = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError as e:
        return json.dumps(
            {
                "success": False,
                "error": f"Invalid JSON arguments: {str(e)}",
            }
        )
    
    try:
        function_response = available_functions[function_name](**function_args)
        return json.dumps(
            {
                "success": True,
                "function_name": function_name,
                "result": function_response,
            }
        )
    except TypeError as e:
        return json.dumps(
            {
                "success": False,
                "error": f"Invalid arguments: {str(e)}",
            }
        )
    except Exception as e:
        return json.dumps(
            {
                "success": False,
                "error": f"Tool execution failed: {str(e)}",
            }
        )

from concurrent.futures import ThreadPoolExecutor
import time
def execute_tools_sequential(tool_calls, available_functions):
    """
    Execute tool calls one after another.
    Args:
    tool_calls: A list of tool call objects returned by the model.
    available_functions: A dictionary mapping function names to functions.
    Returns:
    A list of tool result messages ready to append to the conversation.
    """
    results = []
    for tool_call in tool_calls:
        # TODO: Execute the current tool call safely.
        # Hint: use execute_tool_safely(tool_call, available_functions)
        safe_result = execute_tool_safely(tool_call, available_functions)
        tool_message = {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": tool_call.function.name,
            "content": safe_result,
        }
    results.append(tool_message)
    return results
    
def execute_tools_parallel(tool_calls, available_functions, max_workers=4):
    """ Execute independent tool calls in parallel"""
    def run_single_tool(tool_call):
        return {
            "tool_call_id": tool_call.id,
            "role":"tool",
            "name": tool_call.function.name,
            "content": execute_tool_safely(tool_call, available_functions),
        }
    with ThreadPoolExecutor(
        max_workers=min(max_workers, len(tool_calls))
    ) as executor:
        return list(executor.map(run_single_tool, tool_calls))
def compare_parallel_vs_sequential(tool_calls, available_functions):
    """
    Measure the timing difference between sequential and parallel execution.
    Args:
    tool_calls: A list of independent tool calls to evaluate.
    available_functions: A dictionary mapping function names to functions
    
    Returns:
    A dictionary containing sequential results, parallel results, timing,
    and speedup.
    """
    start = time.perf_counter()
    sequential_results = None # TODO
    sequential_time = time.perf_counter() - start
    start = time.perf_counter()
    parallel_results = None # TODO
    parallel_time = time.perf_counter() - start
    speedup = (
        sequential_time / parallel_time if parallel_time > 0 else None
    )
    return {
        "sequential_results": sequential_results,
        "parallel_results": parallel_results,
        "sequential_time": sequential_time,
        "parallel_time": parallel_time,
        "speedup": speedup,
    }
    
advanced_tools = cot_tools
advanced_system_message = """You are a helpful weather assistant that can use
weather tools and a calculator to solve multi-step problems.
Guidelines:
1. If the user asks about several independent locations, use multiple weather
tool calls in parallel when appropriate.
2. If a question requires several steps, continue using tools until the task is
completed.
3. If a tool fails, explain the issue clearly and continue safely when possible.
4. For complex comparison or calculation queries, prepare a structured final
response.
"""
def process_messages_advanced(client, messages, tools=None, available_functions=None):
    """Send messages to the model and execute any returned tools in parallel."""
    tools = tools or []
    available_functions = available_functions or {}
    response = client.chat.completions.create(
        model=LLM_MODEL,
    messages=messages,
    tools=tools,
    )
    response_message = response.choices[0].message
    messages.append(response_message)
    if response_message.tool_calls:
        tool_results = execute_tools_parallel(
            response_message.tool_calls,
            available_functions,
        )
        messages.extend(tool_results)
    return messages, response_message
    
    
def run_conversation_advanced(client, system_message=advanced_system_message, max_iterations=5,):
    """
    Run a conversation that supports multi-step tool workflows.
    Args:
    client: The OpenAI client.
    system_message: The system message for the advanced agent.
    max_iterations: Maximum number of tool rounds for each user turn.
    Returns:
    The final conversation history.
    """
    messages = [
        {
            "role": "system",
            "content": system_message,
        }
    ]
    print("Advanced Weather Assistant: Hello! Ask me complex weather questions.")
    print("I can compare cities, perform calculations, and return structured outputs.")
    print("(Type 'exit' to end the conversation)\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nAdvanced Weather Assistant: Goodbye! Have a great day!")
            break
        messages.append(
            {
                "role": "user",
                "content": user_input,
            }
        )
        for _ in range(max_iterations):
            # TODO: Process the current conversation state using the advanced
            # tool workflow. Pass client, messages, advanced_tools, and
            # available_functions to process_messages_advanced(...).
            messages, response_message = process_messages_advanced(
                client,
                messages,
                advanced_tools,
                available_functions,
            )
            
            if messages is None:
                print("ERROR: process_messages_advanced returned None")
                break
            # TODO: If the model is done calling tools, print the final answer
            if not response_message.tool_calls:
                if response_message.content:
                    print(f"\nAdvanced Weather Assistant: {response_message.content}\n")
            # and break out of the loop.
                    break
        else:
            print(
                "\nAdvanced Weather Assistant: I stopped after reaching the"
                " maximum number of tool iterations.\n"
            )
    return messages

required_output_keys = [
    "query_type",
    "locations",
    "summary",
    "tool_calls_used",
    "final_answer",
]
structured_output_prompt = """For complex comparison or calculation queries,
return the final answer as a valid JSON object with exactly these keys:
- query_type
- locations
- summary
- tool_calls_used
- final_answer
Do not include markdown fences.
"""
    
def validate_structured_output(response_text):
    """Validate the final structured JSON response."""
    try:
        parsed = json.loads(response_text)
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON output: {str(e)}")
    
    for key in required_output_keys:
        if key not in parsed:
            raise ValueError(f"Missing required key: {key}")
        
    if not isinstance(parsed["locations"], list):
        raise ValueError("'locations' must be a list")
    
    if not isinstance(parsed["tool_calls_used"], list):
        raise ValueError("'tool_calls_used' must be a list")
    return parsed

def get_structured_final_response(client, messages):
    """
    Request a structured final response in JSON mode and validate it.
    Args:
    client: The OpenAI client.
    messages: The full conversation history including tool results.
    Returns:
    A validated Python dictionary representing the final structured output.
    """
    structured_messages = messages + [
        {
            "role": "system",
            "content": structured_output_prompt,
        }
    ]
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=structured_messages,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content
    # TODO: Validate the JSON string before returning it.
    # Hint: use validate_structured_output(content)
    return validate_structured_output(content)

if __name__ == "__main__":
    choice = input(
        "Choose an agent type (1: Basic, 2: Chain of Thought, 3: Advanced): "
    )
    if choice == "1":
        run_conversation(client, "You are a helpful weather assistant.")
    elif choice == "2":
        run_conversation(client, cot_system_message)
    elif choice == "3":
        run_conversation_advanced(client, advanced_system_message)
    else:
        print("Invalid choice. Defaulting to Basic agent.")
        run_conversation(client, "You are a helpful weather assistant.")
