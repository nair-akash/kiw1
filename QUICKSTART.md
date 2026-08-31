# KIW1 — From empty folder to deployed agent

Follow `SETUP.md` first (project, billing, budget alarm, APIs, API key). This picks up from there
and gets you to a live URL, then to the feature that wins.

---

## The model decision, settled

| Where | Model | Why |
|---|---|---|
| **Writing the code** | Claude Opus 5, Cursor, Copilot — anything | **No rule governs your tooling.** Use whatever writes the best code. |
| **Inside the agent (default)** | **Gemini 3.5 Flash** | Named explicitly in the rules: *"an AI Agent leveraging Gemini 3.5 Flash."* Cheapest tier, free quota. |
| **Inside the agent (escalation)** | **Gemini 3.5 Pro** | Planning and overnight self-critique only. Logged every time. |
| **Bulk / local / offline** | **Gemma** | Free, runs locally, and earns a bonus point for integrating a Google open model. |
| **Voice** | **Gemini Live API** | Native speech-to-speech with tool calling. |

**Claude cannot be the agent's runtime model.** "Gemini 3.5 or newer *accessed through* Gemini API
or Vertex AI" makes Vertex the permitted access path — not permission for any model hosted there.
Anthropic models are in Vertex Model Garden, which makes this an easy and expensive mistake.

Don't add Claude to the model router either. It gains nothing the Flash/Pro/Gemma tiers don't
already demonstrate, it costs real money, and to a panel of Google judges it reads as hedging away
from their platform.

> **Verify the exact model string before you paste it.** Copy it from AI Studio or Vertex Model
> Garden rather than trusting any string written here — Gemini identifiers change and a wrong one
> fails at runtime, not at review.

---

## Step 1 — Scaffold

```bash
mkdir -p ~/kiw1/app && cd ~/kiw1
python -m venv .venv && source .venv/bin/activate
pip install google-adk google-cloud-firestore google-cloud-pubsub
pip freeze > requirements.txt
```

```bash
printf '.venv/\n.env\n__pycache__/\n*.pyc\n' > .gitignore
printf 'GOOGLE_API_KEY=\nGOOGLE_CLOUD_PROJECT=\n' > .env.example
git init
```

`.gitignore` before your first commit, not after. A key in git history is a key you have to rotate.

---

## Step 2 — The smallest agent that counts as compliant

`app/__init__.py`:

```python
from . import agent
```

`app/agent.py`:

```python
from google.adk.agents import Agent

MODEL = "gemini-3.5-flash"   # verify this string against AI Studio

def remember(fact: str) -> dict:
    """Store a durable fact about the user.

    Args:
        fact: The fact to remember, as a short sentence.
    """
    from .store import save_fact
    save_fact(fact)
    return {"status": "saved", "fact": fact}

root_agent = Agent(
    name="kiw1",
    model=MODEL,
    instruction=(
        "You are KIW1, a personal agent. Be direct and use plain language. "
        "Never use jargon with the user. If a request is ambiguous, ask at most "
        "three clarifying questions in a single message, then proceed."
    ),
    tools=[remember],
)
```

ADK reads a tool's signature and docstring to build its schema — so the docstring *is* the tool
description the model sees. Write it for the model, not for a human reader.

Run it locally:

```bash
export GOOGLE_API_KEY="your-key"
adk web
```

You now have a working Gemini agent. **Deploy it before adding anything else.**

---

## Step 3 — Firestore

`app/store.py`:

```python
import os
from datetime import datetime, timezone
from google.cloud import firestore

_db = None
UID = "demo-user"          # single-user for the hackathon

def db():
    global _db
    if _db is None:
        _db = firestore.Client(project=os.environ["GOOGLE_CLOUD_PROJECT"])
    return _db

def user():
    return db().collection("users").document(UID)

def save_fact(fact: str):
    user().collection("memory").add({
        "text": fact,
        "created": datetime.now(timezone.utc),
    })
```

---

## Step 4 — Deploy

```bash
gcloud run deploy kiw1 \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 3 \
  --set-secrets GOOGLE_API_KEY=gemini-api-key:latest \
  --set-env-vars GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project)
```

That URL is your submission's hosted link. **You are now compliant on all three mandatory
requirements** — Gemini 3.5, Google ADK, Google Cloud. Everything after this is score, not
eligibility.

Commit here. This is your safe fallback if the rest goes wrong.

---

## Step 5 — Skill Forge, the feature that wins

Build this next, before anything else. It is the only thing on your list nobody else will have,
and it is almost entirely free code — one short model call per promotion.

`app/forge.py`:

```python
import hashlib, re
from datetime import datetime, timedelta, timezone
from google.cloud.firestore_v1.base_query import FieldFilter
from .store import user

THRESHOLD = 3          # occurrences that trigger promotion
WINDOW_DAYS = 7

_STOP = {"the","a","an","please","can","you","my","me","i","to","for","of","and","is","it"}

def fingerprint(intent: str, tools_used: list[str]) -> str:
    """Stable id for 'the same kind of task'. Pure code, zero tokens."""
    words = re.sub(r"[^a-z ]", " ", intent.lower()).split()
    keywords = sorted(w for w in words if w not in _STOP and len(w) > 2)
    basis = "|".join(keywords) + "::" + "|".join(sorted(set(tools_used)))
    return hashlib.sha256(basis.encode()).hexdigest()[:16]

def record(intent: str, tools_used: list[str]) -> str:
    fp = fingerprint(intent, tools_used)
    user().collection("fingerprints").add({
        "fp": fp,
        "intent": intent,
        "tools": tools_used,
        "ts": datetime.now(timezone.utc),
    })
    return fp

def count_recent(fp: str) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(days=WINDOW_DAYS)
    hits = (user().collection("fingerprints")
            .where(filter=FieldFilter("fp", "==", fp))
            .where(filter=FieldFilter("ts", ">=", cutoff))
            .stream())
    return sum(1 for _ in hits)

def already_forged(fp: str) -> bool:
    return any(user().collection("skills")
               .where(filter=FieldFilter("fp", "==", fp)).limit(1).stream())

def should_promote(fp: str) -> bool:
    return count_recent(fp) >= THRESHOLD and not already_forged(fp)
```

**Read what that does and does not do.** Counting, normalising, windowing, and the threshold are
all plain Python costing zero tokens. The model is called exactly once — to name and describe the
skill after the code has already decided it deserves to exist. That is the "hardcoded" principle
from PRD §3.2, and it is why KIW1 stays cheap.

Wire it into your agent loop: after each completed task, call `record(...)`, then check
`should_promote(...)`. When it returns true, make one Flash call to write a name and description,
save it to `users/{uid}/skills`, and tell the user in plain language:

> *"You've asked me to do this three times this week. I've written myself a skill for it called
> `weekly-invoice-chase`. Want me to run it on a schedule?"*

Add a `/skill` command that lists everything in that collection with its description and use count.

**Test the pure functions.** `fingerprint` and `should_promote` decide whether your headline
feature fires on camera. They must be right.

```python
def test_fingerprint_is_stable_across_phrasing():
    a = fingerprint("chase the unpaid invoices", ["search_mail"])
    b = fingerprint("Please chase my unpaid invoices!", ["search_mail"])
    assert a == b
```

---

## Step 6 — Then the rest

Follow the build order in `BUILD_PROMPT.md`: Prompt Refinery → Correction Ledger →
Overnight Research → Strategic Planner. Deploy and verify after each one.

**Stop building at hour 12** and switch to the README, the diagram, and the video. That's 30% of
the score and it is the part people run out of time for.

---

## If something doesn't match

The ADK CLI and API surface move fast, and the exact Gemini model strings change. Where anything
here disagrees with https://google.github.io/adk-docs/ or https://ai.google.dev/gemini-api/docs,
**the docs are right and this file is stale.** The architecture holds regardless; only the syntax
drifts.
