# KIW1 — The Autonomous Self-Improving Agentic Harness

> **"KIW1 notices what you keep asking for and writes itself a skill for it — and it researches its own weak spots overnight."**

*A solo entry for the **All Things Agentic Hackathon** (Google / Devpost) in **The Collaborative Partner** track.*

---

## 📊 The Measured Proof of Improvement

Every agent claims to learn. **KIW1 measured it.**

Using a fixed 20-task benchmark (`evals/`) covering planning, memory, prompt ambiguity, tool execution, and correction injection:

| Benchmark Run | Score | Percentage | Notes |
|---|---|---|---|
| **Cold Run** (Empty memory, no corrections, no forged skills) | **15 / 20** | **75%** | Baseline execution |
| **Learned Run** (Identical 20 tasks after feedback & forging) | **20 / 20** | **100%** | Post-learning execution |
| **Delta Improvement** | **+5 Tasks** | **+25% Gain** | Measurable, falsifiable self-improvement |

To reproduce the benchmark in one command:
```bash
python -m evals.runner
```

---

## 🌟 Core Architecture & Differentiators

1. **Skill Forge (PRD §6.2)**:
   - Evaluates task repetition in pure Python (zero token overhead).
   - On the **3rd occurrence in 7 days**, automatically creates, names, and registers a reusable parameterized skill.
   - Deterministic auto-retirement: Skills with `<60%` success rate over $\ge 5$ invocations are automatically disabled in code.
2. **Prompt Refinery (PRD §6.1)**:
   - Ambiguity heuristics in code classify vague prompts before execution.
   - Refuses to guess on vague pronouns or scope; asks at most 3 batched clarifying questions with options.
3. **Correction Ledger (PRD §6.5)**:
   - Corrections become durable rules stored in Firestore.
   - Rules are retrieved by context similarity and injected into future tasks *before* execution. Contradicted rules auto-retire.
4. **Overnight Research Loop (PRD §6.3)**:
   - Triggered asynchronously by Cloud Scheduler during declared sleep windows.
   - Targets the system's weakest areas, conducts research, and runs an adversarial **Gemini 3.7 Pro self-critique pass** to discard unverified claims.
   - Produces a plain-language morning report.
5. **Local Data Boundary (PRD §3.1)**:
   - Local vault notes never leave the machine. A local Vault Node answers queries on-device; only questions and synthesized answers cross the boundary.
6. **Security & Untrusted Boundary (PRD §12b)**:
   - Retrieved web content and external messages are demarcated as untrusted data in ADK callbacks, preventing prompt injection attacks.
7. **Deterministic Core (PRD §3.2)**:
   - Counting, windowing, plan scoring, risk classification, and budget enforcement are pure Python costing zero tokens. Models are invoked only for natural language comprehension and generation.

---

## 🛠️ Tech Stack & Platform Compliance

- **Reasoning Model**: **Gemini 3.7 Flash** (default) with **Gemini 3.7 Pro** escalation for deep planning and critique.
- **Effort Control**: Maps `quick` (0), `standard` (2048), and `thorough` (8192) directly to Gemini's native **thinking budget**.
- **Agent Framework**: **Google ADK (`google-adk` 2.8.0)** for agent orchestration, tools, and evaluation.
- **Google Cloud Services**:
  - **Cloud Run**: Serverless container hosting the FastAPI agent core.
  - **Cloud Firestore**: Durable store for Memory Palace (`room -> locus -> item`), skills, fingerprints, and correction rules.
  - **Cloud Pub/Sub**: Durable job queue with idempotency keys enabling crash-resilient resumption.
  - **Cloud Scheduler**: Cron triggers for autonomous overnight research loops.
  - **Cloud Trace / OpenTelemetry**: Per-step token, latency, and cost accounting.

---

## 🚀 Quickstart & Spin-Up Instructions

### Prerequisites
- Python `3.12+`
- Google Cloud SDK (`gcloud` CLI)
- Gemini API Key (from Google AI Studio: https://aistudio.google.com/apikey)

### 1. Local Setup
```bash
# Clone and enter directory
cd KIW1

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and set your GOOGLE_API_KEY
```

### 2. Run Automated Tests
```bash
pytest
```
*All 26 unit tests covering Skill Forge, Prompt Refinery, Correction Ledger, Strategic Planner, Memory Palace, Approval Layer, and Privacy Boundaries will pass.*

### 3. Start Local Web Dashboard
```bash
uvicorn app.server:app --reload --port 8080
```
Open **http://localhost:8080** to access the interactive dashboard with live chat, Skill Registry, Correction Ledger, Memory Palace, and Telemetry meters.

---

## ☁️ One-Command Google Cloud Deployment

```bash
# Authenticate and set your GCP project
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Run one-command deploy
./deploy.sh
```

`deploy.sh` automatically:
1. Enables required Cloud APIs (`run`, `firestore`, `pubsub`, `cloudscheduler`).
2. Builds and deploys the container to **Cloud Run** with `--min-instances 0` (cost ceiling protection).
3. Provisions Pub/Sub topics for durable task resumption.
4. Schedules Cloud Scheduler jobs for overnight research.

---

## 🎬 The 4 Demo Beats

1. **Beat 1 — "It made itself a skill, and I didn't ask" (≈60s)**:
   - Ask the agent three invoice auditing tasks.
   - On the 3rd turn, KIW1 announces it has forged `skill-invoice-records`.
   - Inspect `/skill` in the UI to see it registered and ready for 1-step execution.
2. **Beat 2 — "It was wrong once. It is not wrong again" (≈60s)**:
   - Provide a correction (e.g. "Always format invoices with a 15% GST breakdown").
   - Run a different invoice task — KIW1 unprompted applies the learned rule from the Correction Ledger.
3. **Beat 3 — "It worked while I slept" (≈45s)**:
   - Inspect the overnight research morning report.
   - Demonstrates target selection, web research, adversarial Pro critique, and discarded hypotheses.
4. **Beat 4 — "Here is the number" (≈30s)**:
   - The 20-task benchmark: **15/20 cold $\rightarrow$ 20/20 learned (+25% gain)** shown live on screen.

---

## 📋 Status & Deliverables Summary

| Component | Status | Verification |
|---|---|---|
| **ADK Core & Cloud Run Skeleton** | Built & Verified | `app/server.py`, `app/agent.py` |
| **Skill Forge & 3-in-7 Trigger** | Built & Verified | `app/forge.py`, `tests/test_forge.py` |
| **Prompt Refinery** | Built & Verified | `app/refinery.py`, `tests/test_refinery.py` |
| **Correction Ledger** | Built & Verified | `app/ledger.py`, `tests/test_ledger.py` |
| **Overnight Research & Pro Critique** | Built & Verified | `app/research.py`, `app/plugins/search.py` |
| **Strategic Planner (3 Candidates)** | Built & Verified | `app/planner.py`, `tests/test_planner.py` |
| **Local Vault Data Boundary** | Built & Verified | `app/boundary.py`, `app/plugins/vault.py` |
| **Untrusted Content Boundary** | Built & Verified | `app/boundary.py`, `tests/test_boundary.py` |
| **Manifest-Driven Approval Layer** | Built & Verified | `app/approval.py`, `tests/test_approval.py` |
| **20-Task Evaluation Benchmark** | Built & Verified | `evals/runner.py`, `evals/results.json` (15/20 $\rightarrow$ 20/20) |
| **Web Dashboard UI** | Built & Verified | `app/static/index.html`, `style.css`, `app.js` |
| **Deployment Automation** | Built & Verified | `Dockerfile`, `deploy.sh` |

---

## 📦 Third-Party Components

- **Thinking Orbs** (`app/static/orb/`): Dotted thought-orb loading and state indicators for AI & agent interfaces.
  - License: MIT License
  - Copyright: &copy; 2026 Jakub Antalik (with @a_brinza)
  - Upstream: [github.com/Jakubantalik/thinking-orbs](https://github.com/Jakubantalik/thinking-orbs)

