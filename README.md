# 🌉 SkillBridge - CV Skill-Gap Analyzer

> AI-powered web application that analyzes your CV against job descriptions, identifies skill gaps, and recommends personalized YouTube learning resources to help you land your dream job.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.51+-red.svg)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/AI-Groq%20Llama-purple.svg)](https://groq.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**Built for:** Job seekers · Career switchers · AI product demonstrations

---

## 📖 Table of Contents

- [Features](#-features)
- [Demo](#-demo)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [How It Works](#-how-it-works)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Deployment](#-deployment)
- [Testing](#-testing)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [Author](#-author)
- [License](#-license)
- [Support](#-support)

---

## ✨ Features

### 🧠 AI-Powered CV & Job Description Comparison
- **Deep Analysis**: Uses Groq's Llama models for intelligent CV-JD matching
- **Smart Extraction**: Identifies strengths, missing skills, and generates gap narratives
- **Context-Aware**: Understands industry-specific terminology and requirements

### 📈 Comprehensive Scoring System
Get detailed breakdown across four dimensions:
- **Overall Match Score** 
- **Skills Match** 
- **Experience Match** 
- **Education Match** 

### 🧩 Detailed Skill-Gap Breakdown
- ✅ **Strengths Highlighted** 
- ⚠️ **Missing/Weak Skills** 
- 📝 **Gap Analysis Summary** 

### 🎥 Personalized Learning Recommendations
- 🔍 **Smart Search** - User selects which skill to learn and APP finds most relevant YouTube tutorials via Serper API
- 📺 **Video Cards** - Beautiful UI with thumbnails, channels, and durations


### 📤 CV PDF Upload
- 📄 **Intelligent Parser** - Extracts clean text from any PDF format
- 🔧 **Format Handling** - Manages various CV layouts and styles
- ⚡ **Fast Processing** - Instant extraction and analysis

### 📥 JSON Export
- 💾 **Full Report** - Download complete analysis with recommendations
- 🔄 **Shareable** - Easy to save and share results
- 📊 **Data-Friendly** - Structured format for further processing

### 🎨 Professional Streamlit UI
- 🖥️ **Modern Design** - Clean, intuitive interface
- ⚙️ **Sidebar Config** - Easy API key management
- 📱 **Responsive** - Works on desktop and tablets
- 🎯 **Smooth UX** - Guided workflow from upload to recommendations

---

## 🎬 Demo

![SkillBridge Demo](docs/demo.gif)
*Upload CV → Get Analysis → Learn Skills → Land Job*

**Live Demo**: [Try SkillBridge](https://your-app-url.streamlit.app) *(Coming Soon)*

---

## 🏗️ System Architecture

```
┌─────────────┐
│   User      │
│  Uploads CV │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Streamlit UI   │
│  (Frontend)     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────┐ ┌──────────────┐
│  PDF    │ │   Groq API   │
│ Parser  │ │  (Llama 4)   │
└────┬────┘ └───────┬──────┘
     │              │
     └──────┬───────┘
            ▼
    ┌───────────────┐
    │   Analysis    │
    │   Results     │
    └───────┬───────┘
            │
            ▼
    ┌───────────────┐
    │  Serper API   │
    │   (YouTube)   │
    └───────┬───────┘
            │
            ▼
    ┌───────────────┐
    │ Video Cards   │
    │ + JSON Export │
    └───────────────┘
```

*Detailed architecture diagram available in `docs/` folder*

---

## 🔧 Tech Stack

### Backend / Logic
| Component | Technology | Purpose |
|-----------|------------|---------|
| Language | Python 3.10+ | Core application logic |
| AI Engine | Groq SDK | Chat completions with Llama models |
| Video Search | Serper API | Google → YouTube search integration |
| Validation | Pydantic | Type-safe data models |
| Logging | Loguru | Professional logging |

### Frontend
| Component | Technology |
|-----------|------------|
| Framework | Streamlit |
| Styling | Custom CSS |
| UI Components | Native Streamlit widgets |

### Utilities
- **PDF Processing**: Custom text extraction engine
- **HTTP Client**: Requests library
- **Environment**: python-dotenv for config management

---

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager
- Virtual environment (recommended)

### Step-by-Step Setup

```bash
# 1. Clone the repository
git clone https://github.com/OlawumiSalaam/skillbridge.git

cd skillbridge

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set up environment variables (see Configuration section)
cp .env.example .env
# Edit .env with your API keys
```

---

## 🚀 Quick Start

### 1. Get API Keys

**Groq API Key** (Free tier available)
- Visit [console.groq.com](https://console.groq.com)
- Sign up / Log in
- Navigate to API Keys
- Create and copy your key

**Serper API Key** (2,500 free searches)
- Visit [serper.dev](https://serper.dev)
- Sign up / Log in
- Copy your API key from dashboard

### 2. Configure Environment

Create `.env` file in project root:


### 3. Run the Application

```bash
streamlit run src/cv_analyser/app.py
```

App opens at: **👉 http://localhost:8501/**

---

## 🔄 How It Works

### Step-by-Step Process

```mermaid
graph LR
A[Upload CV PDF] --> B[Extract Text]
B --> C[Paste Job Description]
C --> D[Groq AI Analysis]
D --> E[Generate Scores & Insights]
E --> F[Identify Missing Skills]
F --> G[Serper Video Search]
G --> H[Display Results + Videos]
H --> I[Export JSON Report]
```

### Detailed Workflow

1. **📄 CV Upload**
   - User uploads CV as PDF
   - Custom parser extracts clean text
   - Handles various formatting styles

2. **📝 Job Description Input**
   - User pastes target job description
   - Text is validated and sanitized

3. **🤖 AI Analysis (Groq)**
   - Sends CV + JD to Groq's Llama model
   - Model generates comprehensive analysis:
     - Match scores (overall, skills, experience, education)
     - List of matching strengths
     - List of missing/weak skills
     - Detailed gap analysis narrative

4. **🔍 Video Search (Serper)**
   - Identifies most critical missing skill
   - User selects the skill to learn
   - Queries Serper API for YouTube tutorials based on selected skill
   - Returns top 5 highest-quality videos

5. **📊 Results Display**
   - Beautiful UI cards showing:
     - Score breakdown with progress bars
     - Strengths vs gaps comparison
     - Video recommendations with thumbnails
   - Download option for JSON report

---

## 📁 Project Structure

```
SkillBridge/
│
├── src/
│   └── cv_analyser/
│       ├── app.py
│       ├── config.py
│       ├── models/
│       │   ├── schemas.py
│       │   └── __init__.py
│       ├── services/
│       │   ├── groq_service.py
│       │   ├── serper_service.py
│       │   └── __init__.py
│       ├── utils/
│       │   ├── pdf_parser.py
│       │   ├── validators.py
│       │   └── __init__.py
│       └── __init__.py
│
├── docs/
│   ├── architecture.md
│   ├── deployment.md
│   └── demo.gif
├── requirements.txt
├── README.md
├── .env   (not included in repo)
└── tests/

```

---

## ⚙️ Configuration




## 🧪 Testing

### Run Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_groq_service.py -v
```








## 👨‍💻 Author

**Olawumi Salaam**  
*AI-ML Engineer *

- 💼 LinkedIn: [olawumi-salaam](https://www.linkedin.com/in/olawumi-salaam)
- 🐙 GitHub: [@OlawumiSalaam](https://github.com/OlawumiSalaam)
- 📧 Email: olawumisalaam@gmail.com

> *Crafted with ❤️ to help job seekers level up and land their dream roles.*

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⭐ Support

If this project helps you, please:

- ⭐ **Star the repository** - It makes a big difference!
- 🐦 **Share on Twitter** - Help others discover SkillBridge
- 🐛 **Report bugs** - Open an issue on GitHub
- 💡 **Suggest features** - We love hearing your ideas!

---

## 🙏 Acknowledgments

- **Groq** - For lightning-fast AI inference
- **Serper** - For powerful search API
- **Streamlit** - For the amazing web framework
- **Open Source Community** - For inspiration and tools

---

## 📊 Stats

![GitHub stars](https://img.shields.io/github/stars/your-username/skillbridge?style=social)
![GitHub forks](https://img.shields.io/github/forks/your-username/skillbridge?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/your-username/skillbridge?style=social)

---

<div align="center">

**[⬆ Back to Top](#-skillbridge---cv-skill-gap-analyzer)**

Made with 💙 by [Olawumi Salaam](https://github.com/olawumi-salaam)

</div>