The reason your `README` looks like raw code (with the `#` and `**` symbols visible) is likely due to two small issues:

1.  **File Extension:** In your screenshot, the file is named just `README`. You must rename it to **`README.md`**. The `.md` extension tells GitHub and your code editor to render the formatting (making `#` into Big Headers and `**` into **Bold Text**).
2.  **Syntax Errors (Spaces):** In your screenshot, there are spaces between the `!` and the `[` for the images (e.g., `! [Python]`). This breaks the image display.

**Here is the corrected, clean code.** Copy this exact content and save it as **`README.md`**.

````markdown
# Agentic Task Planner with Reflexion Architecture
**Graduate Deep Learning Project | NYU MSCS**

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![AI Model](https://img.shields.io/badge/LLM-Gemini%201.5%20Flash-orange)
![Framework](https://img.shields.io/badge/UI-Streamlit-red)
![License](https://img.shields.io/badge/License-MIT-green)

## Project Overview
This project implements an **Agentic AI System** designed to autonomously plan daily schedules.

Unlike standard "zero-shot" schedulers, this system utilizes a **Reflexion Architecture** (Adversarial Planner-Critic Loop) to achieve meta-cognitive reasoning. The agent drafts a plan, critiques its own logic against energy constraints, and dynamically re-plans in real-time when the simulation environment injects "crisis" events.

### Key Objectives
1.  **Constraint Satisfaction:** Optimize task ordering based on user energy levels (circadian rhythm) rather than just time slots.
2.  **Dynamic Resilience:** Detect execution delays and autonomously drop low-priority tasks to salvage high-priority goals.
3.  **Meta-Cognition:** Use an internal "Critic" module to validate plans before execution, reducing initial failure rates.
4.  **Long-Term Learning:** Store failure modes (e.g., "Burnout") in episodic memory to improve future planning.

---

## Features

### Intelligent Architecture
-   **Planner Agent:** Uses Chain-of-Thought (CoT) prompting to decompose goals into actionable schedules.
-   **Reflexion Loop:** A secondary "Critic" agent reviews the draft plan for logical flaws.
-   **Memory Module:** Retains lessons from previous simulation episodes (RAG-lite) to avoid repeating mistakes.

### 🎮 Interactive Simulation (Streamlit UI)
-   **Live Execution:** Watch the agent execute tasks, drain energy, and react to events in real-time.
-   **Crisis Injection:** Manually trigger a "2-Hour Emergency Meeting" to test the agent's re-planning capabilities.
-   **Ablation Controls:** Toggle "Reflexion" and "Memory" on/off to perform live A/B testing.
-   **Calendar Export:** One-click export of the AI-generated schedule to `.ics` format.

### Research Analytics
-   **Headless Benchmarking:** A script (`evaluate_models.py`) that compares the Agent against a Greedy Baseline.
-   **Automated Metrics:** Tracks "Success Rate," "Energy Conservation," and "Tasks Completed."

---

## Repository Structure

```text
ai-task-planner/
├── src/
│   ├── agent.py          # Core LLM Agent
│   ├── critic.py         # Adversarial Critic module
│   ├── memory.py         # JSON-based Memory system
│   ├── llm_client.py     # API wrapper
│   └── simulation/       # Stochastic environment
├── data/                 # Generated datasets
├── app.py                # Streamlit Dashboard
├── evaluate_models.py    # Benchmark script
├── requirements.txt      # Dependencies
└── README.md             # Documentation
````

-----

##  Installation & Setup

### 1\. Clone the Repository

```bash
git clone [https://github.com/YOUR_USERNAME/ai-task-planner.git](https://github.com/YOUR_USERNAME/ai-task-planner.git)
cd ai-task-planner
```

### 2\. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3\. Configure API Key

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_MODEL_NAME=gemini-1.5-flash
```

-----

## Contributors

  - **Naman Limani**
  - **Naman Vashishta**
    *New York University, MSCS Deep Learning Course (Fall 2025)*

<!-- end list -->

```
```
