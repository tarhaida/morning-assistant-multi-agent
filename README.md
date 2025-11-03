# 🌅 Morning Assistant Multi-Agent System

> **A LangGraph-powered multi-agent AI system that prepares personalized morning briefings for families**

[![Module](https://img.shields.io/badge/Module-Project%202-blue)](https://app.readytensor.ai/certifications/agentic-ai-cert-U7HxeL7a)
[![Framework](https://img.shields.io/badge/Framework-LangGraph-green)](https://github.com/langchain-ai/langgraph)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success)]()

> 📖 **[Read the full publication on Ready Tensor](https://app.readytensor.ai/publications/morning-assistant-multi-agent-system-o492tNLs2qZk)**

---

## 📋 Overview

The **Morning Assistant** is a sophisticated multi-agent AI system built with LangGraph that transforms your family's morning routine. It autonomously gathers weather data, analyzes school menus, suggests activities, and delivers a personalized WhatsApp message - all coordinated by intelligent agent orchestration.

**Built for:** Ready Tensor Agentic AI Developer Certification - Project 2

---

## 🎯 Key Features

### Multi-Agent Architecture
- ✅ **4 Specialized Autonomous Agents**
  - Weather Specialist - Analyzes conditions and provides recommendations
  - Nutrition Specialist - Evaluates school menus and dietary insights
  - Activity Planner - Suggests weather-appropriate activities
  - Communication Specialist - Synthesizes everything into a warm message

### Intelligent Orchestration
- ✅ **LangGraph StateGraph** for workflow management
- ✅ **Conditional Routing** based on agent results
- ✅ **State Management** across agent interactions
- ✅ **Error Handling** with graceful degradation
- ✅ **Memory Persistence** via MemorySaver

### Real-World Integration
- ✅ **Live Weather API** integration
- ✅ **Web Scraping** for school cafeteria menus
- ✅ **DOCUPIPE OCR API** for image-to-CSV conversion
- ✅ **WhatsApp Messaging** for delivery
- ✅ **Configurable** via YAML

### 🔍 DOCUPIPE OCR Integration
The Nutrition Agent includes automatic **DOCUPIPE API** integration for processing menu images:

**Data Pipeline:**
1. **Web Scraping** → Download menu images from school website
2. **DOCUPIPE OCR** → Extract table data from images (automatic)
3. **CSV Generation** → Create structured menu database
4. **AI Analysis** → LLM-powered nutrition insights

**Key Features:**
- 🤖 Automatic OCR processing when images are detected
- 📊 Converts unstructured images to structured CSV
- 🔄 Idempotent operations (won't re-process existing data)
- ⚡ Async processing with status polling
- 📝 Detailed logging and error handling

**See**: `DOCUPIPE_INTEGRATION.md` for complete technical documentation

---

## 🏗️ System Architecture

```
                    ┌─────────────────┐
                    │   START         │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Weather Agent  │
                    │  (Analysis)     │
                    └────────┬────────┘
                             │
                    ┌────────▼─────────┐
                    │ Nutrition Agent  │
                    │ (Menu Analysis)  │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │ Activity Agent   │
                    │ (Suggestions)    │
                    └────────┬─────────┘
                             │
                    ┌────────▼──────────┐
                    │ Communication     │
                    │ Agent (Synthesis) │
                    └────────┬──────────┘
                             │
                    ┌────────▼────────┐
                    │  WhatsApp Send  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │     END         │
                    └─────────────────┘
```

### Agent Responsibilities

| Agent | Role | Tools | Output |
|-------|------|-------|--------|
| **Weather** | Weather analysis | Weather API, Forecast API | Current conditions + recommendations |
| **Nutrition** | Menu evaluation | Menu scraper, Nutrition DB | Dietary insights |
| **Activity** | Activity planning | None (reasoning-based) | Activity suggestions |
| **Communication** | Message synthesis | WhatsApp API | Final personalized message |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- API keys for:
  - Google Gemini (recommended)
  - OpenWeather API (for weather)
  - Twilio (for WhatsApp)

### Installation

```bash
# Clone repository
cd /Users/tarikhaida/Documents/Python/ai-agent-morning-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. **Create `.env` file:**
```bash
cp .env.example .env
```

2. **Add your API keys:**
```env
GOOGLE_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_key_here  # Optional
ANTHROPIC_API_KEY=your_claude_key_here  # Optional
GROQ_API_KEY=your_groq_key_here  # Optional
```

3. **Configure settings in `config/config.yaml`:**
```yaml
settings:
  city: "Your-City-Name"
  phone_number: "+1234567890"
```

### Run the System

```bash
# Basic run (uses config defaults)
python code/morning_assistant.py

# With custom phone number
python code/morning_assistant.py +1234567890
```

---

## 📁 Project Structure

```
ai-agent-morning-assistant/
├── code/
│   ├── agents/
│   │   ├── weather_agent.py      # Weather analysis specialist
│   │   ├── nutrition_agent.py    # Menu analysis specialist
│   │   ├── activity_agent.py     # Activity planning specialist
│   │   └── communication_agent.py # Message synthesis specialist
│   ├── morning_assistant.py      # Main LangGraph orchestrator
│   ├── llm.py                    # LLM provider management
│   ├── prompt_builder.py         # Prompt construction
│   ├── utils.py                  # Utility functions
│   ├── langgraph_utils.py        # LangGraph helpers
│   ├── custom_tools.py           # LangChain tools
│   └── paths.py                  # Path configurations
├── config/
│   ├── config.yaml               # Agent configurations
│   └── reasoning.yaml            # Reasoning strategies
├── data/                         # Input data (if needed)
├── outputs/                      # Generated outputs
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── LICENSE                       # MIT License
├── .env.example                  # Environment template
└── .gitignore                    # Git exclusions
```

---

## 🔧 Configuration Guide

### Agent Configuration (`config/config.yaml`)

Each agent is independently configured:

```yaml
weather_agent:
  llm: "gemini-2.5-flash"
  temperature: 0.1
  prompt_config:
    role: "Weather Analysis Specialist"
    instruction: "Analyze weather and provide actionable insights..."
    reasoning_strategy: "CoT"
```

### Reasoning Strategies (`config/reasoning.yaml`)

Agents use different reasoning approaches:
- **CoT** (Chain of Thought) - Step-by-step logical reasoning
- **ReAct** - Reasoning + Acting cycle
- **Self-Ask** - Question-driven exploration

---

## 🧪 Testing

```bash
# Test with mock data (no API calls)
python code/morning_assistant.py --mock

# Test individual agents
python -c "from agents.weather_agent import WeatherAgent; agent = WeatherAgent(); print(agent.analyze('Paris'))"
```

---

## 📊 Example Output

```
================================================================================
MORNING ASSISTANT MULTI-AGENT SYSTEM
================================================================================
Started at: 2025-01-15 07:00:00

City: Paris
Phone: +1234567890

[WeatherAgent] Analyzing weather for Divonne-les-Bains...
[WeatherAgent] Analysis complete

[NutritionAgent] Analyzing school menu...
[NutritionAgent] Analysis complete

[ActivityAgent] Generating activity suggestions...
[ActivityAgent] Suggestions generated

[CommunicationAgent] Creating family message...
[CommunicationAgent] Message created (245 chars)

[CommunicationAgent] Sending message to +1234567890...
[CommunicationAgent] Send status: {'status': 'sent', 'phone': '+1234567890'}

================================================================================
WORKFLOW COMPLETE
================================================================================

Final Message:
Ma chérie ❤️,

Aujourd'hui il fait beau ☀️ avec 18°C. Parfait pour jouer dehors après l'école ! 

Le menu de la cantine : salade, poulet rôti, riz, et yaourt aux fruits 🍗🍚🍓

Ce soir, peut-être une soupe de légumes pour équilibrer ? 

Bisous ! 💕

WhatsApp Status: {'status': 'sent'}
```

---

## 🎯 Ready Tensor Project 2 Compliance

This project meets all Project 2 requirements:

✅ **Multi-Agent System (4 agents minimum - EXCEEDS)**
- Weather Specialist
- Nutrition Specialist
- Activity Planner
- Communication Specialist

✅ **Tool Integration**
- Weather API
- Menu web scraper
- WhatsApp messaging

✅ **LangGraph Orchestration**
- StateGraph with typed state
- Conditional routing
- Memory persistence
- Error handling

✅ **Agent Collaboration**
- Sequential coordination
- State sharing
- Result synthesis
- Graceful degradation

✅ **Meaningful Problem**
- Real family use case
- Saves time daily
- Actionable insights
- Production-ready

---

## 🔐 Security & Privacy

- ✅ API keys stored in `.env` (git-ignored)
- ✅ No sensitive data in code
- ✅ WhatsApp E2E encryption
- ✅ Local data processing
- ✅ GDPR-compliant

---

## 🚧 Known Limitations

1. **Language**: Currently French-only for final messages
2. **Menu Source**: Specific to Divonne-les-Bains cafeteria
3. **Weather API**: Requires valid API key
4. **WhatsApp**: Requires Twilio configuration

---

## 🔮 Future Enhancements

- [ ] Multi-language support
- [ ] Configurable menu sources
- [ ] Email delivery option
- [ ] Historical analytics
- [ ] Mobile app interface
- [ ] Voice message generation
- [ ] Calendar integration

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file

---

## 👤 Author

**Tarik Haida, CFA**
- Ready Tensor: [Profile](https://app.readytensor.ai/)
- GitHub: [@tarikhaida](https://github.com/tarikhaida)
- Email: tarik.haida@gmail.com

---

## 🙏 Acknowledgments

- **Ready Tensor** - Agentic AI Developer Certification Program
- **LangChain/LangGraph** - Multi-agent orchestration framework
- **Google Gemini** - LLM provider

---

## 📚 Documentation

For detailed documentation, see:
- [Agent Design Patterns](docs/AGENT_PATTERNS.md)
- [Configuration Guide](docs/CONFIGURATION.md)
- [API Reference](docs/API_REFERENCE.md)

---

**Built with ❤️ for families using LangGraph multi-agent orchestration**
