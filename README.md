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

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate

### 3. Install dependencies
```bash
pip install requests
pip install dotenv

### 4. Run the project
```bash
python conversational_agent.py
