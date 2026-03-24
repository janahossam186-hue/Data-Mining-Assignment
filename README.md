# Data-Mining-Assignment
#  Weather Conversational Agent

A conversational AI agent that provides weather information using external APIs and supports advanced reasoning like comparisons and calculations.


##  Features

- Get current weather for any location
- Get weather forecast for multiple days
- Compare temperatures between cities
- Calculate averages (e.g., average temperature)
- Multiple agent types:
  - Basic Agent
  - Chain-of-Thought Agent
  - Advanced Agent (multi-step reasoning)


## Technologies Used

- Python
- OpenAI-compatible API (Groq - LLaMA 3)
- WeatherAPI
- dotenv
- requests


## 📂 Project Structure
Assignment2/
│
├── conversational_agent.py
├── .env
├── README.md
└── venv/


## Setup Instructions

### 1. Clone the repository

```bash
git clone <your-repo-link>
cd Assignment2
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install requests
pip install dotenv
```

### 4. Run the project
```bash
python conversational_agent.py
```

## 2. Implementation Overview

The assistant supports three reasoning strategies:

### Basic Agent:
Directly answers weather questions using the provided weather API.
Single-step responses without multi-step reasoning.
### Chain of Thought Agent:
Breaks down questions into smaller parts.
Uses intermediate steps and calculations before giving a final answer.
### Advanced Agent:
Supports multi-step workflows and parallel tool usage.
Can handle complex comparisons between multiple cities.
Returns structured JSON output if needed.

## Tools Implemented:

get_current_weather(location) – fetches current weather.
get_weather_forecast(location, days) – fetches weather forecast.
calculator(expression) – evaluates mathematical expressions.

## Orchestration:

The assistant checks if a tool call is needed.
Tool outputs are appended to the conversation and can be used for further reasoning.
Advanced agent supports parallel execution of independent tool calls.


## 3. Example Conversations
### basic agent:
```bash
You: What is the weather in Cairo?
Assistant: The current weather in Cairo is 16.1°C (61.0°F) with patchy rain nearby, 59% humidity, and a wind speed of 18.7 km/h.
```
### chain of thought agent:
```bash
You: What is the weather in Jordan?
Assistant: First, I check the current weather in Amman, Jordan. It's 9.4°C (48.9°F), clear, and 87% humidity. The wind is 4.3 km/h.
```
### advanced agent
```bash
You: What is the temperature difference between Cairo and London right now?
Assistant: I fetched the current temperatures: Cairo: 16.1°C, London: 12.0°C.
The temperature difference is 4.1°C.
```

## Observations:

Using Chain of Thought improved correctness for queries involving multiple steps.
Advanced Agent is better for comparing multiple locations and performing calculations in parallel.
Tool orchestration and safe execution prevent errors even when some tool calls fail.
## 5. Challenges and Solutions
#### Handling tool failures:
Sometimes weather API calls failed or returned unexpected formats.
Solution: Added validation, error handling, and safe execution of tool calls.
#### Parallel execution:
Needed for Advanced Agent to handle multiple independent tool calls.
Solution: Implemented ThreadPoolExecutor for parallel tool calls.
#### Structured JSON output:
Ensuring valid keys and format from model responses.
Solution: Added validation functions to parse and check structured outputs.
#### API Key management:
Needed a secure way to store API keys.
Solution:The solution was to create .env file and python-dotenv to load keys dynamically, but that didn't work for me, the file just couldn't read the data although I used loadotenv()
