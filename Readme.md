
**Agentic Task Planner with Reflexion Architecture**
**Deep Learning Project | NYU MSCS**

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![AI Model](https://img.shields.io/badge/LLM-Gemini%201.5%20Flash-orange)
![Framework](https://img.shields.io/badge/UI-Streamlit-red)
![License](https://img.shields.io/badge/License-MIT-green)

**Project Overview**
This project implements an **Agentic AI System** designed to autonomously plan daily schedules under realistic, stochastic constraints (e.g., user fatigue, unexpected interruptions, time limits). 

Unlike standard "zero-shot" schedulers, this system utilizes a **Reflexion Architecture** (Adversarial Planner-Critic Loop) to achieve meta-cognitive reasoning. The agent drafts a plan, critiques its own logic against energy constraints, and dynamically re-plans in real-time when the simulation environment injects "crisis" events.

**Key Objectives**
1.  **Constraint Satisfaction:** Optimize task ordering based on user energy levels (circadian rhythm) rather than just time slots.
2.  **Dynamic Resilience:** Detect execution delays and autonomously drop low-priority tasks to salvage high-priority goals.
3.  **Meta-Cognition:** Use an internal "Critic" module to validate plans before execution, reducing initial failure rates.
4.  **Long-Term Learning:** Store failure modes (e.g., "Burnout") in episodic memory to improve future planning.

---

**Features**

**Intelligent Architecture**
-   **Planner Agent:** Uses Chain-of-Thought (CoT) prompting to decompose goals into actionable schedules.
-   **Reflexion Loop:** A secondary "Critic" agent reviews the draft plan for logical flaws (e.g., "Scheduling complex coding tasks at 5 PM when fatigue is high") and forces a revision.
-   **Memory Module:** Retains lessons from previous simulation episodes (RAG-lite) to avoid repeating mistakes.

**Interactive Simulation (Streamlit UI)**
-   **Live Execution:** Watch the agent execute tasks, drain energy, and react to events in real-time.
-   **Crisis Injection:** Manually trigger a "2-Hour Emergency Meeting" to test the agent's re-planning capabilities.
-   **Ablation Controls:** Toggle "Reflexion" and "Memory" on/off to perform live A/B testing of the architecture.
-   **Calendar Export:** One-click export of the AI-generated schedule to `.ics` format (compatible with Apple/Google Calendar).

**Research Analytics**
-   **Headless Benchmarking:** A script (`evaluate_models.py`) that compares the Agent against a Greedy Baseline (Shortest-Job-First).
-   **Automated Metrics:** Tracks "Success Rate," "Energy Conservation," and "Tasks Completed" across hundreds of episodes.

---

**Repository Structure**

```text

ai-task-planner/
├── src/
│   ├── agent.py          # Core LLM Agent (Planner & Refiner logic)
│   ├── critic.py         # Adversarial Critic module
│   ├── memory.py         # JSON-based Episodic Memory system
│   ├── llm_client.py     # Robust API wrapper with error handling
│   └── simulation/       # Stochastic environment (Fatigue/Delay logic)
├── data/                 # Generated datasets & logs (Included in Repo)
│   ├── evaluation_results.csv  # Benchmark comparison data
│   ├── agent_memory.json       # Learned lessons from past runs
│   └── simulation_v1.csv       # Synthetic training data
├── app.py                # Main Streamlit Dashboard (UI)
├── evaluate_models.py    # CLI script for quantitative benchmarks
├── run_agentic_loop.py   # CLI script for qualitative testing
├── requirements.txt      # Project dependencies
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

This project requires a Google Gemini API key.

1.  Create a file named `.env` in the root directory.
2.  Add your key :



```env
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_MODEL_NAME=gemini-1.5-flash
```

-----

##  Usage

### Option 1: The Interactive Dashboard (Recommended)

This launches the full research UI with simulation controls and real-time visualization.

```bash
streamlit run app.py
```

  * **Controls:** Use the sidebar to adjust "Chaos Level" (Procrastination) or toggle Research Controls (Ablation study).
  * **Export:** Click "Download .ics Calendar" after a plan is generated to save it to your device.

### Option 2: Run Quantitative Benchmarks

To reproduce the research metrics (Agent vs. Greedy Baseline), run the headless script:

```bash
python evaluate_models.py
```

  * This generates `data/evaluation_results.csv` and prints a summary table to the console.

-----

##  How It Works (The Pipeline)

1.  **User Intent:** The user sets goals (e.g., "Complete 6 tasks") and constraints (Work hours: 9-5).
2.  **Drafting (System 1):** The LLM generates an initial schedule based on task duration estimates.
3.  **Reflexion (System 2):** The **Critic** module scans the draft.
      * *If Flawed:* It returns feedback (e.g., "Too ambitious"). The Planner refines the schedule.
      * *If Approved:* The plan moves to execution.
4.  **Simulation & Perception:** The plan runs through a stochastic environment.
      * *Fatigue Check:* If Energy \< 30, tasks take 1.5x longer.
      * *Interruption:* Random events (p=0.15) add delays.
5.  **Re-Planning:** If the Agent detects a significant drift (Actual Time \> Planned Time), it triggers a **Re-Plan Event**, dropping low-priority tasks to satisfy the hard deadline.
6.  **Learning:** At the end of the episode, the outcome is stored in `data/agent_memory.json` to inform the next run's prompt.

-----

##  Results

*See the "Research Analytics" tab in the app for live visualization.*

Our evaluation compares the **Reflexion Agent** against a **Greedy Baseline** (Shortest-Job-First).

  - **Baseline:** High burnout rate (Energy \< 20) and rigid adherence to impossible plans.
  - **Agent:** Lower raw completion rate but significantly higher **Energy Conservation** and **Robustness**. The Agent successfully drops tasks to prevent burnout, mimicking human-like prudence.

-----

##  Contributors

  - **Naman Limani**
  - **Naman Vashishta**

    *New York University, MSCS Deep Learning Course (Fall 2025)*

```
```
