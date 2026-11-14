# 🌌 SkillNova AI – Adaptive Learning & Career Intelligence Platform

> **Tagline:** *Discover Skills. Bridge Gaps. Build Your Future.*  
> **Project Title:** SkillNova AI – An AI-Powered Adaptive Learning and Career Intelligence Platform Using Collaborative Multi-Agent AI.

---

## 🌟 Executive Summary

Traditional education and online learning platforms provide one-size-fits-all course catalogs without taking into account an individual learner's verified capabilities, foundational strengths, or target career milestones.

**SkillNova AI** solves this problem through an autonomous **collaborative multi-agent system** composed of **six specialized AI agents** orchestrated by a central coordinator. The system diagnoses competencies, computes mathematically transparent readiness scores against benchmark career roles, crafts personalized multi-phase roadmaps, curates verified free resources, administers adaptive assessments, and provides contextual 24/7 AI career mentorship.

---

## 🏗️ Multi-Agent AI Architecture

SkillNova AI employs a collaborative multi-agent architecture where agents communicate using structured Python objects and real-time execution logging.

```
                  +-----------------------------------+
                  |         Learner Profile           |
                  +-----------------+-----------------+
                                    |
                                    v
                  +-----------------+-----------------+
                  |      1. Skill Analyzer Agent      |
                  +-----------------+-----------------+
                                    |
                                    v
                  +-----------------+-----------------+
                  |    2. Career Matching Agent       |
                  +-----------------+-----------------+
                                    |
                                    v
                  +-----------------+-----------------+
                  |      3. Learning Path Agent       |
                  +-----------------+-----------------+
                                    |
                                    v
                  +-----------------+-----------------+
                  |  4. Resource Recommender Agent    |
                  +-----------------+-----------------+
                                    |
                                    v
     +------------------------------+------------------------------+
     |                                                             |
     v                                                             v
+----+-----------------------------+                 +-------------+---------------------+
| 5. Assessment & Progress Agent   |  Feedback Loop  |    6. AI Career Mentor Agent       |
|    (Adaptive Diagnostic Tests)   +---------------->+ (Live Contextual Career Strategist)|
+----------------------------------+                 +-----------------------------------+
```

### The 6 Specialized AI Agents

1. **Agent 1: Skill Analyzer Agent (`agents/skill_analyzer.py`)**
   - Decomposes existing competencies into proficiency tiers (*Beginner*, *Intermediate*, *Advanced*, *Expert*).
   - Classifies competencies into **Strong Skills**, **Developing Skills**, and **Weak Skills**.
   - Produces targeted foundational reinforcement suggestions.

2. **Agent 2: Career Matching Agent (`agents/career_matcher.py`)**
   - Benchmarks learner proficiencies against role requirements for 10 premier engineering career paths.
   - Calculates a transparent, mathematically weighted career compatibility score:
     $$\text{Readiness \%} = \left(\frac{\sum \text{Earned Weighted Points}}{\sum \text{Total Possible Requirement Points}}\right) \times 100$$
   - Distinguishes matched skills, critical priority missing skills, and auxiliary strengths.

3. **Agent 3: Learning Path Agent (`agents/learning_path.py`)**
   - Synthesizes competency gaps into a chronologically staged, dependency-ordered curriculum.
   - Divides roadmap into structured milestones with learning objectives, syllabus topics, and duration estimates.
   - **Adaptive Reconfiguration**: Dynamically injects remedial review phases if test scores fall below 50%, or accelerates learners to advanced capstones when scores exceed 80%.

4. **Agent 4: Resource Recommendation Agent (`agents/resource_recommender.py`)**
   - Curates verified, 100% free learning materials matching identified skill gaps.
   - Recommends content from authoritative providers: *freeCodeCamp*, *W3Schools*, *MDN Web Docs*, *Python.org*, *SQLBolt*, *GeeksforGeeks*, *Kaggle Learn*, and *Microsoft Learn*.
   - Provides direct clickable links and filters by difficulty and media format.

5. **Agent 5: Assessment & Progress Agent (`agents/assessment_agent.py`)**
   - Generates interactive multiple-choice diagnostic tests (Python, SQL, HTML, CSS, JavaScript, React, Machine Learning, Statistics).
   - Auto-evaluates answer choices, calculates percentage scores, flags weak topics, and provides in-depth explanations for every question.
   - Updates learner proficiency level and unlocks roadmap phases upon verified mastery.

6. **Agent 6: AI Career Mentor Agent (`agents/ai_mentor.py`)**
   - Delivers personalized career mentorship, project recommendations, and technical concept breakdowns (e.g. JavaScript closures, Event Loop, React reconciliation).
   - Anchored to the learner's live profile, missing skills, readiness percentage, and test results.
   - Works fully locally without requiring paid API keys; supports optional OpenAI/Gemini LLM keys if provided.

---

## 🗄️ Relational Database Architecture (SQLite)

SkillNova AI persists all learner data across 15 relational tables:

1. `users`: Learner credentials, education, department, target role, and career goals.
2. `skills`: Master catalog of industry skills and taxonomy.
3. `user_skills`: Learner skills with verified proficiency levels.
4. `certifications`: Academic and industry certifications.
5. `projects`: Portfolio projects with tech stacks and repository links.
6. `career_roles`: Master list of 10 tech careers with industry categories.
7. `career_requirements`: Required skills, weights, and minimum proficiency levels per role.
8. `learning_roadmap`: Dynamically generated curriculum phases with statuses (*Pending*, *In Progress*, *Completed*).
9. `learning_resources`: Vetted repository of courses, documentation, and exercises.
10. `assessments`: Diagnostic test session headers and aggregate scores.
11. `assessment_questions`: MCQ bank with choices, correct answers, and explanations.
12. `assessment_results`: Question-by-question learner answer logs.
13. `learning_progress`: Historical readiness metrics and milestone completion.
14. `mentor_history`: Multi-turn conversational history with the AI Mentor.
15. `agent_activity`: Transparent execution logs recording agent names, tasks, inputs, and outputs.

---

## 📁 Project Directory Structure

```
SkillNova_AI/
│
├── app.py                      # Main Streamlit SaaS application entrypoint
├── database.py                 # SQLite database schema, seeding & CRUD utilities
├── requirements.txt            # Python dependencies (Streamlit, Pandas, NumPy, Scikit-learn, Plotly)
├── README.md                   # Comprehensive technical documentation & presentation guide
│
├── agents/                     # Multi-Agent Architecture Layer
│   ├── __init__.py
│   ├── skill_analyzer.py       # Agent 1: Skill Analyzer Agent
│   ├── career_matcher.py       # Agent 2: Career Matching Agent
│   ├── learning_path.py        # Agent 3: Learning Path Agent
│   ├── resource_recommender.py # Agent 4: Resource Recommendation Agent
│   ├── assessment_agent.py     # Agent 5: Assessment & Progress Agent
│   ├── ai_mentor.py            # Agent 6: AI Career Mentor Agent
│   └── agent_coordinator.py    # Central Multi-Agent Orchestrator
│
├── modules/                    # User Interface & View Layer
│   ├── __init__.py
│   ├── profile.py              # Profile & verified skill management
│   ├── skill_analysis.py       # Skill gap analysis, radar charts & distributions
│   ├── career_matching.py      # Career explorer & 10-role benchmark matrix
│   ├── roadmap.py              # Interactive personalized learning roadmap
│   ├── resources.py            # Learning resource catalog with clickable links
│   ├── assessment.py           # Adaptive MCQ assessment test runner
│   ├── progress.py             # Progress telemetry, readiness gauge & velocity charts
│   └── mentor.py               # AI Career Mentor conversational chat UI
│
├── data/                       # Knowledgebase & Demonstration Seed Data
│   ├── career_skills.json      # 10 career paths & skill requirements
│   ├── sample_data.json        # Demo student profile & curated resource directory
│   └── assessment_questions.json # Diagnostic question bank with explanations
│
├── assets/                     # Visual Assets & Theming
│   └── style.css               # Modern dark navy, electric blue & purple styling
│
├── .streamlit/
│   └── config.toml             # Custom theme configuration
│
└── tests/                      # Automated Unit & Adaptive Scenario Tests
    ├── test_database.py        # Database schema & query integrity
    ├── test_agents.py          # Unit tests for all 6 AI agents
    └── test_adaptive_learning.py # Tests for the 4 adaptive learning scenarios
```

---

## 🚀 Setup & Execution Guide

### Prerequisites
- Python 3.10+ (Python 3.11 recommended)
- Windows, macOS, or Linux

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
streamlit run app.py
```
The application will launch automatically in your browser at `http://localhost:8501`.

### 3. Run Automated Tests
```bash
python -m unittest discover tests/
```

---

## 🧑‍🎓 Demo Account & Hackathon Presentation Scenario

SkillNova AI includes a pre-seeded student account designed for live judging demonstrations:

- **Name:** Demo Student
- **Education:** BSc Computer Science
- **Department:** Computer Science & Engineering
- **Target Career:** Full Stack Developer
- **Initial Skills:**
  - Python: Intermediate
  - SQL: Intermediate
  - HTML: Beginner
- **Certification:** Python Basics
- **Project:** Student Management System

### 5-Step Hackathon Demonstration Script for Judges:

1. **Step 1: Dashboard Overview**
   - Show the **Dashboard** with the welcome banner, 10 metric cards, readiness percentage (38.5%), and the recommended next activity (Phase 1: HTML & CSS Fundamentals).
2. **Step 2: Skill Gap Analysis & Radar Chart**
   - Navigate to **Skill Gap Analysis** to show the interactive Plotly radar chart comparing current abilities against the Full Stack Developer benchmark.
3. **Step 3: Adaptive Assessment Engine**
   - Navigate to **Skill Assessment**. Select **JavaScript** or **HTML**, answer the questions, and submit.
   - Show the instant grading, explanations for every question, and how the score dynamically updates the learner's skill inventory and roadmap.
4. **Step 4: Dynamic Career Change Scenario**
   - Go to **Career Explorer**. Switch target career from **Full Stack Developer** to **Data Scientist**.
   - Show how the Career Matching Agent immediately recalculates readiness and the Learning Path Agent generates a brand new curriculum focusing on Statistics, Pandas, and Machine Learning.
5. **Step 5: Multi-Agent Activity Center & AI Mentor**
   - Open **Multi-Agent Activity Center** to show real-time collaboration logs between all 6 agents.
   - Open **AI Career Mentor** and ask: *"What skills am I missing?"* or click one of the quick prompt chips to show live data-grounded mentorship.
