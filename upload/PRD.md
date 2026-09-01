---
title: KIW1 — Product Requirements Document
type: prd
status: draft
project: KIW1
track: The Collaborative Partner
event: All Things Agentic Hackathon (Devpost / Google)
deadline: 2026-09-01 12:00 GMT+12
updated: 2026-08-31
---

# KIW1 — Product Requirements Document

**KIW1 is an agent that gets better at working with *you* specifically, and proves it.**

Most agents treat every request as the first one they have ever seen. KIW1 does three things
they do not: it refuses to act on a vague instruction until it has asked enough to understand
it, it notices when you have asked for the same thing repeatedly and writes itself a permanent
skill for it, and it uses the hours you are asleep to research and critique its own weak points.

---

## 1. Why this shape, and why this track

Submitted to **The Collaborative Partner**. The track brief asks for an agent that
"leads the way and takes notes… asks clarifying questions, guides the user step-by-step, and has
a clear way to capture feedback, so it constantly adapts to the user's unique way of thinking."

That is not a track KIW1 is being bent to fit. It is a description of the product.

| Track requirement | KIW1 feature |
|---|---|
| Asks clarifying questions | **Prompt Refinery** (§6.1) — mandatory pre-execution interrogation |
| Guides step-by-step | **Strategic Planner** (§6.4) — shows the candidate paths and why one won |
| Captures feedback | **Correction Ledger** (§6.5) — every correction becomes a durable rule |
| Adapts to your way of thinking | **Taste Model** (§6.6) + **Skill Forge** (§6.2) |

---

## 2. Hackathon compliance — mandatory, non-negotiable

Every project must use all three. Failure on any one is disqualifying.

| Requirement | KIW1's answer | Where |
|---|---|---|
| **Gemini 3.5+** via Gemini API or Vertex AI | Gemini 3.7 Flash as the default reasoning model; Gemini 3.7 Pro escalation for planning and critique | Model Router (§6.9) |
| **≥1 Google agent framework** | **Google ADK** as the agent runtime and tool-calling layer | Kernel (§5) |
| **≥1 Google Cloud service** | **Cloud Run** (agent + workers), **Firestore** (memory, ledgers, state), **Pub/Sub** (durable job queue), **Cloud Scheduler** (cron + overnight research) | §5, §7 |

**Bonus points** (optional, cheap, take them): publish a build write-up on dev.to or YouTube;
post on X or LinkedIn with `#AllThingsAgenticHackathon`; integrate **Gemma** as the local
fallback model — which KIW1 does anyway for the offline path (§6.10), so this is free.

**Judging weights, and what each one actually rewards:**

- **40% — Innovation & Operational Utility.** "Autonomous, high-value action over simple chat,
  with little to no hand-holding." → Skill Forge and Overnight Research are the scoring features.
  Both act without being asked.
- **30% — Architectural Discipline & Tech Stack.** "How you decouple systems, manage state and
  memory, secure credentials, and handle failures." → The plugin kernel, the data boundary, and
  durable delegation are the scoring features.
- **30% — Demo & Production Readiness.** "A live, unedited demo, a clean architecture diagram,
  reproducible setup, and visible proof it runs on Google Cloud." → Budget real time for this.
  It is worth as much as the architecture.

---

## 3. Hard constraints

### 3.1 The Local Data Boundary — the one that shapes everything

**No file from the operator's local Obsidian vaults is ever transmitted off the machine. Not to
Google, not to any API, not to any repository, not in any form.**

This is a standing rule, not a hackathon preference. It has teeth, and it costs something: it
means the naive design — "upload the vault, embed it, do RAG in the cloud" — is forbidden.

The architecture instead splits into two halves:

```
   LAPTOP (trusted)                    GOOGLE CLOUD (untrusted with vault data)
   ┌──────────────────────┐            ┌──────────────────────────────┐
   │  Vault Node          │            │  KIW1 Core (Cloud Run)       │
   │  • vault files       │            │  • Gemini 3.7 via ADK        │
   │  • local embeddings  │◄──gRPC────►│  • Firestore (no vault text) │
   │  • Gemma via Ollama  │  question   │  • Pub/Sub workers           │
   │  • answers locally   │  ──────►    │                              │
   └──────────────────────┘  ◄──────    └──────────────────────────────┘
                              answer
```

The cloud agent may **ask the Vault Node a question**. The Vault Node answers it using a local
model over locally-computed embeddings. **The question and the answer cross the boundary; the
source files never do.**

Three egress modes, selectable, defaulting to the strictest:

| Mode | What crosses | Default |
|---|---|---|
| **Sealed** | Nothing. Vault plugin disabled entirely. | — |
| **Answers-only** | Locally-generated answers. No file contents, no excerpts, no embeddings. | ✅ **Default** |
| **Excerpt** | Explicitly user-approved snippets, one approval per snippet. | Opt-in per session |

> **For the hackathon demo, use synthetic sample data, not the real vault.** The judges get a
> populated, convincing demo; your actual notes never enter the recording, the repo, or the
> cloud. Ship a `seed/` directory of realistic fake notes. This is not a compromise — it is the
> correct way to demo a privacy-boundaried product.

### 3.2 "Hardcoded" means deterministic, not prompted

You defined this precisely: *"implemented in such a way that the tokens are not wasted, it's
inexpensive and delivers a better result."*

So throughout this document, **hardcoded = written in Python, executed as code, costing zero
tokens.** The rule:

> **If a step can be done by code, it is done by code. The model is called only for the
> genuinely linguistic part — understanding intent, or writing a sentence.**

It is the single biggest lever on both cost and reliability, and it is what lets KIW1 run
acceptably on a weak or cheap model.

Concretely — these are code, never prompts: repetition counting, skill promotion thresholds,
memory decay and ranking, cost accounting, plan scoring, retry and backoff, schema validation,
approval-risk classification, tool sandboxing, context compaction triggers.

### 3.3 Other constraints

- **Solo build.** One person, limited hours. Scope accordingly.
- **Cost ceiling: the $150 Google credit.** Nothing in the design may require exceeding it.
- **No AI attribution** in commits or files (per existing repo convention).
- **Local git only** unless explicitly promoted to a private remote.

---

## 4. Design principles

1. **Everything is a plugin.** The kernel knows nothing about Gmail, memory, or voice. It knows
   how to load, sandbox, and revert a plugin.
2. **Deterministic core, linguistic edge.** §3.2.
3. **Cheap by default, expensive on demand.** Flash handles everything; Pro is escalated to
   deliberately and the escalation is logged with its reason.
4. **Every autonomous action is reversible or approved.** No exceptions.
5. **Plain language out.** Structured internally, human sentences externally. No jargon in
   anything a user reads.
6. **Fail loudly.** A degraded state that reports success is the worst outcome. Every component
   reports its actual state.

---

## 5. Architecture

### 5.1 The kernel

A small composition kernel — inspired by DeepSeek Harness and the Cordis pattern beneath it,
**written fresh, not copied**. It provides exactly five things:

| Capability | Meaning |
|---|---|
| **Load / unload** | Plugins mount and unmount at runtime, no process restart |
| **Declared dependencies** | A plugin states what it needs; the kernel resolves order or refuses |
| **Reversible effects** | Every effect registers its undo before it runs |
| **Capability grants** | A plugin gets filesystem, network, or secrets only if its manifest asks and policy allows |
| **Typed event bus** | Plugins communicate via events, never direct imports |

**The known limitation, stated honestly:** an effect that has already left the process cannot be
reverted. A sent email is sent. This is why the Approval Layer (§6.7) gates precisely the class
of actions the kernel cannot undo — the two systems are designed as a matched pair.

### 5.2 Plugin manifest

```yaml
name: gmail
version: 1.0.0
requires: [memory, approval]
provides:
  tools: [search_mail, draft_reply, send_mail]
effects:
  send_mail: { reversible: false, risk: high, approval: always }
  draft_reply: { reversible: true, risk: low, approval: never }
capabilities: [network:googleapis.com, secret:gmail_oauth]
cost_class: cheap        # cheap | standard | expensive
```

The kernel reads this and enforces it. Risk classification is **structural, from the manifest —
not a model's judgement call.** That is what makes the approval layer trustworthy.

### 5.3 Cloud topology

- **Cloud Run** — KIW1 Core (request-scoped) + Worker service (long-running, background jobs)
- **Pub/Sub** — the durable job queue; every delegated task is a message, so restarts lose nothing
- **Firestore** — memory index, correction ledger, delivery ledger, taste model, skill registry,
  job state. **Never vault file content.**
- **Cloud Scheduler** — cron jobs and the overnight research trigger
- **Secret Manager** — all OAuth tokens and API keys. Never in Firestore, never in env files.

---

## 6. Features

**P0** = built for the demo. **P1** = post-hackathon, next. **P2** = roadmap.

### 6.1 Prompt Refinery — P0

Default-on. Every incoming request passes through it before anything executes.

1. **Classify** (code, no tokens): is this ambiguous? Heuristics — missing object, undefined
   scope, unresolved pronoun, no success criterion, conflicting constraints.
2. **If clear → execute immediately.** A hands-off request must not be interrogated. This is
   the failure mode that makes clarifying agents insufferable, and it is prevented in code.
3. **If ambiguous → ask.** Maximum 3 questions, batched into one message, each with suggested
   answers. Never a wall of questions, never one at a time.
4. **Rewrite** into an explicit brief: goal, constraints, success criteria, out-of-scope.
5. **Show the rewrite and proceed.** The user can correct it; the correction feeds §6.5.

*Why it scores:* it is the track brief, executed literally.

### 6.2 Skill Forge — repetition becomes capability — P0

**The signature feature. Nobody else will have this.**

- Every completed task is fingerprinted (code, no tokens): normalised intent + tool sequence +
  parameter shape.
- A rolling 7-day window counts fingerprints. **Threshold: 3.**
- On the third occurrence, KIW1 **writes itself a skill** — a named, parameterised, reusable
  procedure capturing the tool sequence that worked.
- It then says so, plainly: *"You've asked me to do this three times this week. I've turned it
  into a skill called `weekly-invoice-chase`. Want me to run it on a schedule?"*
- Skills are versioned plugins. They can be edited, disabled, or deleted.
- `/skill` lists every available skill with its description, source, and use count.

The counting, windowing, and threshold are **pure code**. The model is called once, to write the
skill's description. Cost per promotion: one short call.

**Skills are retired the same way they are forged — in code.** Promotion is only half the loop. A
fingerprint can be correct, the three occurrences real, and the captured tool sequence still be a
*bad way to do the job*. Nothing above catches that, and since this is the signature feature it is
the first place a judge will push.

So every skill carries its own record: invocation count, and an outcome per run classified in code
— **succeeded**, **corrected** (the user amended the result), or **abandoned** (the user stopped it
or redid the task by hand). No model is asked whether a run went well; the signal is the user's own
behaviour, which is the same acceptance signal the Taste Model (§6.6) already reads.

| Condition | Behaviour |
|---|---|
| Fewer than 5 invocations | Provisional. Kept, and labelled as such in `/skill`. |
| Success rate below 60% over ≥5 invocations | **Auto-disabled**, not deleted. |
| Disabled by the system | The user is told which skill, its record, and what triggered it |
| Superseded by a corrected version | Old version retained, marked superseded — skills are versioned (above) |

A disabled skill stays in the registry with its numbers visible. Deleting it would destroy the
evidence, and the evidence is the point: *"I wrote myself this skill, then measured that it wasn't
working, and switched it off"* is a stronger claim than forging one ever was. **Retirement is
deterministic bookkeeping** — thresholds and counters, no tokens — which is §3.2 applied to the
system's judgement of itself.

This also gives §12c a second measurable number: skills forged, and skills that survived.

### 6.3 Overnight Research — P0

Inspired by Karpathy's autoresearch loop. Modes: **off / manual / auto**.

In auto, Cloud Scheduler wakes the Worker during your declared sleep window:

1. **Select a target** (code): the weakest area, chosen from failed tasks, low-confidence
   answers, repeated corrections, and stale memory.
2. **Research** it via the `agent-reach` research plugin.
3. **Critique** — a separate Gemini 3.7 Pro pass whose only job is to attack the finding. Prompted
   to refute, defaulting to "not established" under uncertainty.
4. **Keep only what survives.** Surviving findings become memory entries or skill improvements.
5. **Morning report**, in plain language: what it looked into, what it learned, what it discarded
   and why.

Hard budget cap per night, enforced in code, defaulting to a small fraction of the credit.

*Why it scores:* the hackathon's literal theme is agents that "run in the background and handle
the heavy lifting asynchronously." This is that, exactly.

### 6.4 Strategic Planner — P0

For any task above a complexity threshold:

1. Generate **3 candidate paths** to the goal, deliberately diverse (fastest / cheapest / most
   thorough).
2. **Score each in code** against the user's declared weighting of time, cost, effort, and risk.
3. **Show the comparison, state the pick and the reason**, then execute.
4. Decompose the winner into subtasks; build a dependency graph.
5. **Independent subtasks spawn parallel sub-agents** — setting: `off / on / auto`. In auto, the
   parallel path is taken only when the graph shows ≥2 independent branches *and* estimated
   savings exceed the spawn overhead. That calculation is code.

### 6.5 Memory, and the Correction Ledger — P0

Three layers:

- **Working** — current session. Compacted when the context budget is hit; compaction is
  triggered by a token count, not a model's opinion.
- **Durable (Firestore)** — facts, preferences, entities, project state. Vector + keyword hybrid
  retrieval.
- **Vault (local only)** — §3.1. Answers-only across the boundary.

**Memory Palace, hardcoded.** The method of loci made structural rather than decorative:
memories are stored in a **fixed spatial hierarchy** — `room → locus → item` (e.g.
`Projects → KIW1 → the data boundary decision`). Retrieval walks the structure first and only
falls back to vector search on a miss. This is cheaper than pure vector search, more explainable
(you can see *where* a memory lives), and gives stable addresses that survive re-embedding.
Rooms are assigned by code from the entity graph, never by asking the model.

**Correction Ledger — the self-learning loop.** Every time you correct KIW1, it records the
situation, the wrong action, the correction, and a generalised rule. Rules are retrieved by
similarity *before* acting on future tasks. A rule that prevents a repeat gains weight; one
contradicted twice is retired. **This is the mechanism by which it learns from mistakes**, and
it is deterministic bookkeeping, not prompting.

### 6.6 Taste Model — P1

A structured profile learned over time from accepted vs. rejected outputs: verbosity, formality,
directness, format preference, risk tolerance, preferred tools. Stored as explicit numeric
dimensions in Firestore, injected as a compact block into the system prompt.

Learned in code from acceptance signals — not by asking a model "what does he like?"

### 6.7 Approval Layer — P0 (thin), P1 (full)

Risk comes from the **manifest** (§5.2), not from model judgement.

| Risk | Behaviour |
|---|---|
| **None** — reversible, local, no cost | Silent |
| **Low** — reversible, external | Act, then report |
| **Medium** — costly or hard to reverse | Ask, with a default and a timeout |
| **High** — irreversible, outbound, financial | Always ask. Never defaulted. Never timed out. |

**Hands-off mode** raises the silent threshold to Medium but **can never silence High.** Sending
email, spending money, and deleting data always ask. That line is not configurable.

### 6.8 Durable delegation & the Delivery Ledger — P1

- Every delegated task is a Pub/Sub message with state in Firestore. **A restart resumes; nothing
  is lost.** Idempotency keys prevent double-execution on redelivery.
- The **Delivery Ledger** records every outbound message and its correlation ID, so an inbound
  reply is matched to what it answers. A reply is trusted only if it matches a ledger entry —
  which is what makes an untrusted inbound channel safe to act on.

### 6.9 Model Router — P0 (thin)

Chooses per task, in code, from a scored table — never by asking a model which model to use:

| Situation | Model |
|---|---|
| Default reasoning, tool calls | **Gemini 3.7 Flash** |
| Planning, critique, hard reasoning | **Gemini 3.7 Pro** |
| Bulk classification, offline | **Gemma** (local, free) |
| Voice | **Gemini Live API** |

**Effort control** — `quick / standard / thorough` — sets the token ceiling, retry count, and
escalation permission. Every call is logged with model, tokens, latency, and cost.

**Cheap tool calling on weak models:** tool schemas are compacted, only the tools relevant to
the current task are exposed (never the full catalogue), few-shot examples are attached to the
tool definition rather than the prompt, and results are cached by argument hash. This is what
lets a small model call tools reliably.

### 6.10 Local & offline execution — P1

Adapters for **Ollama, llama.cpp, and LM Studio**. On first run, KIW1 profiles the hardware — CPU,
RAM, GPU, VRAM — and **recommends a configuration** with reasons in plain language.

> Profiling must measure, never assume. An unverified hardware reading produces a confident and
> wrong recommendation, which is worse than no recommendation.

### 6.11 Voice — P1

**Gemini Live API**, native speech-to-speech with mid-conversation tool calling. Bidirectional
streaming, barge-in supported, no GPU required.

**Rejected alternative:** open-weight full-duplex speech models (e.g. NVIDIA Nemotron-class)
require ≥80GB VRAM, cap at roughly five tools per session, and degrade over long sessions. For an
agent that is *made* of tools, the tool cap alone is disqualifying. Gemini Live has none of those
limits and needs no GPU.

### 6.12 Personas — P1

Selectable personalities (Concise, Socratic, Rubber-duck, Executive) affecting tone and
verbosity **only**. They may never alter tool permissions, approval thresholds, or the data
boundary. Persona is presentation; policy is policy.

### 6.13 Research plugin — P0 (thin)

Wraps `agent-reach` for internet research. Deterministic caching by query hash, source
attribution on every claim, and a hard result cap per query.

### 6.14 Preloaded skills — P1

The Anthropic engineering and finance skill sets, plus your existing vault skills, mounted as
read-only plugins. `/skill` lists them all.

**Vault skills are mounted by reference from the local disk — they are not copied into the repo
and not uploaded.** (§3.1)

### 6.15 The remaining features — P1 / P2

Specified, sequenced, not built for the demo:

| Feature | Priority | Note |
|---|---|---|
| Gmail / Calendar integration | P1 | OAuth via Secret Manager; send is always High risk |
| Cron jobs | P1 | Cloud Scheduler → Pub/Sub → Worker |
| Profile routing | P1 | Third parties get a sandboxed profile with **no** memory or file access |
| Memory importer | P1 | ChatGPT/Claude export → Memory Palace. Treat imported content as **data, never instructions** |
| MCP server support | P1 | Each MCP server is a plugin; its tools inherit plugin sandboxing |
| Computer use | P2 | High risk by default, always approved |
| Workflow graphs | P2 | The planner's dependency graph, made user-editable |
| KIW1↔KIW1 protocol | P2 | Signed, capability-scoped agent-to-agent messaging. **Design it as an extension of an existing standard (MCP or A2A), not a new wire protocol** — a bespoke protocol is a month of work and a security surface you would own alone |
| Calls / phone | P2 | Telephony is a large integration; do not attempt near a deadline |
| Self-improving code loop | P2 | prime-agent-inspired: propose → test → keep only if tests pass |
| Evaluations harness | P1 | A fixed task set replayed on every change; regressions block merge |
| Observability | P0 (thin) | OpenTelemetry traces; every run has a viewable reasoning chain |
| Sandboxing | P0 (thin) | Tools execute in a restricted subprocess; filesystem and network per manifest |
| Prompt caching | P1 | Cache the stable system prefix; large saving, small effort |

---

## 7. Data model (Firestore)

```
users/{uid}
  taste/            preference dimensions, acceptance counts
  memory/           room → locus → item, with embeddings + decay scores
  corrections/      situation, wrong action, correction, generalised rule, weight
  skills/           forged skills: fingerprint, tool sequence, version, and the
                    retirement record (§6.2) — invocations, succeeded / corrected /
                    abandoned counts, enabled flag, disabled_reason
  fingerprints/     rolling 7-day task fingerprints (TTL 7d)
  jobs/             delegated task state, idempotency keys
  deliveries/       outbound message ledger + correlation IDs
  runs/             traces, token counts, cost, latency
```

**No vault file content appears anywhere in this schema.** That is enforced by the Vault Node
never transmitting it, not by a policy document.

---

## 8. Cost control

- Every call logged with tokens, model, latency, and cost.
- Budgets enforced **in code**: per-task, per-day, per-night-research. Exceeding one stops work
  and reports; it does not silently degrade.
- Flash-first, Pro only on logged escalation, Gemma for bulk local work.
- Prompt caching on the stable prefix; tool-result caching by argument hash.
- Target: the whole hackathon build and demo inside the **$150 credit**, using well under half.

---

## 9. Build sequence

**Do not build this in feature order. Build it in demo order** — the thing the video shows must
work first.

| Phase | Deliverable |
|---|---|
| **0** | ADK skeleton on Cloud Run, Gemini 3.7 Flash responding, Firestore connected. **Deploy on day one** — a working deploy of nothing beats a perfect local build of everything. |
| **1** | Prompt Refinery end-to-end (§6.1) |
| **2** | Skill Forge with the 3-in-7-days trigger (§6.2), `/skill` listing |
| **3** | Strategic Planner with visible path comparison (§6.4) |
| **4** | Overnight Research on Cloud Scheduler (§6.3) |
| **5** | Memory + Correction Ledger (§6.5), thin Approval Layer (§6.7) |
| **6** | **Stop building.** Architecture diagram, README spin-up steps, 4-minute demo video. |

Phase 6 is 30% of the score. Protect its time.

---

## 10. Submission checklist

- [ ] Category: **The Collaborative Partner**
- [ ] Hosted URL (optional but encouraged — Cloud Run gives you one free)
- [ ] Text description: features, technologies, data sources, findings and learnings
- [ ] Public repo URL — or private, shared with `testing@devpost.com` and `cloudhackathons@google.com`
- [ ] `README.md` with **step-by-step spin-up instructions** (explicitly judged as proof of reproducibility)
- [ ] Architecture diagram showing how Gemini connects to backend, database, frontend
- [ ] ~4-minute demo video: problem → value → **live demo** → visible proof of the Google Cloud backend (Console, Cloud Run dashboard, or Vertex AI logs on screen)
- [ ] Bonus: public write-up; social post with `#AllThingsAgenticHackathon`; Gemma integrated

---

## 11. Risks

| Risk | Severity | Mitigation |
|---|---|---|
| **Scope.** ~39 features, one person, hours not weeks | **Critical** | P0 is six features. Everything else is roadmap and is *presented* as roadmap. |
| **Nothing deployed at deadline** | **Critical** | Deploy an empty skeleton in Phase 0. Never leave deployment to the end. |
| **Demo video rushed** | High | It is 30% of the score. Reserve its time first, not last. |
| **Vault data leaking into the repo or video** | High | Synthetic seed data only. Grep the repo and re-watch the recording before submitting. |
| **Overnight research burns credit** | Medium | Hard code-enforced nightly cap. |
| **Skill Forge fires on noise** | Medium | Require exact fingerprint match plus ≥3 occurrences; user can reject a forged skill. |
| **A forged skill is valid but wrong** — real repetitions, bad captured procedure, then reused indefinitely | **High** | Per-skill outcome tracking and automatic retirement below a success threshold (§6.2). The failure mode is silent reuse, so detection must be code, not the user noticing. |
| **Free-tier rate limits during the live take** — parallel sub-agents (§6.4) against a rate-limited AI Studio key, in an unedited recording | High | Retry with backoff, degrade to sequential on 429, and rehearse the full demo run once against the real quota before recording. |
| **Opaque product name** | Low | "KIW1" carries no meaning to a judge. Lead every description with the one-line pitch, never the name. |

---

## 12. Open questions

1. What is your sleep window, for the overnight research schedule?
2. Default effort — `quick`, `standard`, or `thorough`?
3. Which Gmail/Calendar account, and is a *read-only* scope acceptable for v1? (Strongly
   recommended — it removes the entire irreversible-send risk class.)
4. Is KIW1 the shipping name, or a working title?
5. Host machine RAM and VRAM — measure before §6.10 means anything.

---

## 12a. Platform-native implementation — P0 discipline

**Anything ADK already provides is used, not reimplemented.** Hand-rolling a framework primitive
costs build time and scores badly under Architectural Discipline.

| Need | ADK native construct |
|---|---|
| Parallel sub-agents (§6.4) | Multi-agent primitives — sub-agents, agent-as-tool |
| Workflow graphs (§6.15) | Sequential / Parallel / Loop workflow agents |
| Guardrails (§6.15) | `before_model` / `after_model` and tool callbacks |
| Session state | ADK session and state services |
| Evaluations (§12c) | ADK's built-in evaluation framework |
| Tool schemas | Signature + docstring introspection |

Firestore holds only what ADK does not own: the correction ledger, skill registry, fingerprints,
and taste model.

**Gemini capabilities used deliberately, not incidentally:**

- **Thinking budget *is* the effort control** (§6.9). `quick / standard / thorough` map to Gemini's
  configurable reasoning budget — not just a token ceiling.
- **Context caching** on the stable prefix, tool definitions, and skill registry. Largest single
  cost lever available; **promoted from P1 to early build.**
- **Schema-constrained structured output** for every internal step returning data. Never parse
  JSON out of prose.
- **Long context** — measure before compacting. Compact later and less aggressively than a small
  window would require.

## 12b. Untrusted content boundary — P0

KIW1 reads web pages and, later, email. **Both are attacker-controlled**, and this is the most
likely real vulnerability in the system.

1. **Retrieved content is data, never instruction.** Fetched text is delimited and marked
   untrusted. Anything shaped like a command embedded in it is surfaced to the user, never obeyed.
2. **No tool call may be justified solely by retrieved content.** Such an action requires explicit
   approval regardless of hands-off mode.
3. **Memory poisoning is the subtle risk.** Overnight research writes to durable memory; unfiltered
   attacker text there becomes a *persistent* foothold surviving all future sessions. Every memory
   write carries provenance, and provenance is visible at retrieval.
4. Enforced as **ADK callbacks, not prompt instructions.** A guardrail in a prompt is a suggestion;
   a guardrail in a callback is a control.

## 12c. Proof of improvement — P0

The system claims to learn. **The claim must be measured, not asserted.**

A fixed benchmark of ~20 representative tasks, run twice: once against a **cold** KIW1 (empty
memory, no corrections, no forged skills), and once after a learning period. Both scores recorded,
with the delta and the methodology, using ADK's evaluation framework so it is reproducible.

This is the only falsifiable claim in the entire submission, and it is worth more than any
architecture diagram. It belongs in the README and on screen in the demo video.

### 12c.1 How a task is scored — define this before running anything

A benchmark without a stated oracle is not reproducible, and "you can rerun it" is the entire
value of the claim. **Whoever reruns it must be able to arrive at the same number without asking
us what we meant.** Decide the scoring method before the cold run, because the cold run cannot be
repeated once the system has learned anything.

Each of the ~20 tasks is one of two kinds, declared in the task file:

**Deterministic (preferred — use this wherever the task allows).** The task declares a machine
-checkable assertion: a required tool was called, a Firestore document exists with given fields, a
returned value matches, a forged skill was invoked rather than the raw tool sequence. Scored by
code. Zero ambiguity, zero cost, and it cannot drift between runs. Push tasks into this category
even when it takes rewording — a task phrased so it can be checked mechanically is worth more than
a richer task that can't.

**Rubric-judged (only where the output is genuinely open-ended).** Scored by an LLM judge under
these constraints, all of which must hold or the number is not comparable across runs:

- a **written rubric per task**, committed alongside it, with explicit pass conditions
- a **pinned judge model and version**, temperature 0 — the judge is *not* the model under test
- the judge sees the output only, **never** which run produced it, and never the other run's output
- **both runs scored in the same session against the same rubric**, so the cold and learned numbers
  share an oracle
- **every judgement logged** with its reasoning, so a disagreement can be inspected rather than
  argued about

Report the split — how many of the twenty were deterministic and how many rubric-judged. A
benchmark that is mostly deterministic is a stronger claim, and saying so is more persuasive than
a higher score with an unexplained method.

**State the limitations rather than letting a judge find them.** Twenty tasks is a small sample and
one run each is not a confidence interval; a difference of one or two tasks is noise, not learning.
If the delta is small, say so. An honestly-reported modest gain is worth more than an impressive
number that collapses under one question — and a judge who tries to poke a hole and finds it
already documented will trust everything else in the submission more.

Seed and freeze the task set before the cold run, and commit it unchanged. Editing tasks after
seeing cold results invalidates the comparison, and it is an easy mistake to make honestly.

## 12d. Interface — P0

`adk web` is a development tool, not a product. A minimal, fast, legible frontend makes the
invisible visible: the skill registry filling up as skills are forged, the correction ledger and
what triggered each rule, a live cost and latency meter, and the memory palace shown as its
`room → locus → item` structure rather than a flat list.

Observability via **Cloud Trace / OpenTelemetry**: every run has an inspectable reasoning chain
with per-step tokens, latency, and cost.

---

## 13. Reference implementations

These are **public repositories to study for design patterns. Do not copy their code.** KIW1 is
an original implementation; these establish prior art and show what has already been solved.

| Repository | Read it for | What to take |
|---|---|---|
| https://github.com/deepseek-ai/deepseek-harness | The plugin/harness architecture this project is inspired by | How a composition kernel loads, isolates, and hot-swaps plugins; the manifest shape. **Study the concept, write your own kernel.** |
| https://github.com/mempalace/mempalace | Memory palace as a working system | How loci are addressed and traversed. Informs the `room → locus → item` hierarchy in §6.5. |
| https://github.com/karpathy/autoresearch | The self-directed research loop | The propose → run → evaluate → keep cycle. Small repo — read `program.md` and `train.py`. Informs §6.3. |
| https://github.com/PrimeIntellect-ai/prime-agent | Self-improvement on coding tasks | How an agent proposes a change, tests it, and keeps it only if tests pass. Informs the P2 self-improving loop. |
| https://github.com/Panniantong/agent-reach | Internet research for agents | Search, fetch, and attribution patterns. Wrapped directly as the research plugin in §6.13. |

**Official documentation the build must follow:**

- Google ADK — https://google.github.io/adk-docs/
- ADK samples — https://github.com/google/adk-samples
- Gemini API — https://ai.google.dev/gemini-api/docs
- Gemini Live API (voice, §6.11) — https://ai.google.dev/gemini-api/docs/live
- Vertex AI Agent Builder — https://cloud.google.com/products/agent-builder
- Cloud Run — https://cloud.google.com/run/docs
- Firestore — https://cloud.google.com/firestore/docs
- Pub/Sub — https://cloud.google.com/pubsub/docs
- Cloud Scheduler — https://cloud.google.com/scheduler/docs
- Hackathon rules — https://allthingsagentichackathon.devpost.com

---

## 14. Winning strategy

See `WINNING_STRATEGY.md` — prize targeting, the demo beats that score, and the 30% most
entrants throw away.

---

## Related

- `BUILD_PROMPT.md` — the prompt to feed an AI builder alongside this document
- `WINNING_STRATEGY.md` — the competitive playbook

