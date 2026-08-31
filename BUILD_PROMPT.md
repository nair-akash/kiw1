# KIW1 — Build Prompt

Paste everything below the line into your build agent (Google Antigravity, Gemini CLI, Claude
Code, or Cursor) and attach `PRD.md`. This prompt is self-contained — it assumes the agent has no
access to any local notes.

---

You are building **KIW1**, an agentic harness, as a solo entry to the **All Things Agentic
Hackathon** (Google / Devpost). The attached `PRD.md` is the specification. Read it fully before
writing any code.

## The one-line product

> KIW1 notices what its user keeps asking for and writes itself a skill for it — and it researches
> its own weak spots overnight.

Everything you build serves that sentence. If a piece of work doesn't, it is out of scope.

## Context you should fetch yourself

You have no access to my local files, so gather your own context from these public sources before
you start. **Study them for patterns. Do not copy their code — KIW1 is an original implementation
and copied code will read as such.**

**Prior art (read the architecture, then write your own):**

- https://github.com/deepseek-ai/deepseek-harness — the plugin/harness model KIW1 is inspired by.
  Study how a composition kernel loads, isolates, and hot-swaps plugins.
- https://github.com/mempalace/mempalace — memory palace as a working system; informs the
  `room → locus → item` memory hierarchy.
- https://github.com/karpathy/autoresearch — the self-directed research loop. Small repo; read
  `program.md` and `train.py`. Informs the overnight research cycle.
- https://github.com/PrimeIntellect-ai/prime-agent — propose → test → keep-only-if-passing
  self-improvement.
- https://github.com/Panniantong/agent-reach — internet research patterns; wrap this as the
  research plugin.

**Documentation you must actually follow:**

- Google ADK — https://google.github.io/adk-docs/
- ADK samples — https://github.com/google/adk-samples
- Gemini API — https://ai.google.dev/gemini-api/docs
- Gemini Live API (voice) — https://ai.google.dev/gemini-api/docs/live
- Cloud Run — https://cloud.google.com/run/docs
- Firestore — https://cloud.google.com/firestore/docs
- Pub/Sub — https://cloud.google.com/pubsub/docs
- Cloud Scheduler — https://cloud.google.com/scheduler/docs
- Hackathon rules — https://allthingsagentichackathon.devpost.com

## Non-negotiable rules

1. **Compliance is disqualifying if missed.** The build must use **Gemini 3.5 or newer** via the
   Gemini API or Vertex AI, **Google ADK** as the agent framework, and **Google Cloud services**
   (Cloud Run, Firestore, Pub/Sub, Cloud Scheduler). Do not substitute any of the three. Do not
   use a non-Google model anywhere in the critical path.

2. **The Local Data Boundary (PRD §3.1) is absolute.** No file from the operator's local Obsidian
   vaults may be read, uploaded, embedded remotely, committed, or included in any output. **All
   development and demo work uses the synthetic `seed/` data you generate.** If a task appears to
   need real personal data, stop and ask.

3. **"Hardcoded" means written in Python, not written into a prompt** (PRD §3.2). Before adding
   any model call, ask whether code can do it. Counting, thresholds, scoring, ranking, routing,
   validation, retries, budgets, and risk classification are **always code**. The model is for
   understanding intent and writing sentences — nothing else. This is the main lever on both cost
   and reliability.

4. **Deploy first, build second.** Phase 0 is a deployed Cloud Run skeleton that answers one
   request via Gemini and writes one Firestore document. Get that live before implementing any
   feature. Never leave deployment to the end.

5. **Build in demo order, not feature order.** Build what the video shows, first. The demo is 30%
   of the score; an unbuilt feature scores zero, but so does a built feature the judge never sees.

6. **No AI attribution** in commits, comments, or files. No `Co-Authored-By` trailers, no
   generated-with links.

7. **Never report success you have not verified.** If a component is stubbed, say so. If a test
   fails, show the output. A degraded system that reports success is the worst possible outcome —
   treat it as the highest-severity class of bug.

## Use the platform properly — do not hand-roll what ADK provides

This is judged. Reimplementing a framework primitive signals you did not learn the framework, and
Architectural Discipline is 30% of the score. **Before building any of the following, read the ADK
docs and use the native construct:**

| Requirement | Use ADK's | Do NOT |
|---|---|---|
| Parallel sub-agents (PRD §6.4) | Native multi-agent primitives — sub-agents and agent-as-tool | Write your own spawner |
| Workflow graphs (§6.15) | Sequential / Parallel / Loop workflow agents | Build a custom DAG engine |
| Guardrails (§6.15) | `before_model` / `after_model` and tool callbacks | Bolt validation into prompts |
| Session state | ADK's session and state services | Invent a parallel state store |
| Evaluations (§6.15) | ADK's built-in evaluation framework | Write a bespoke test runner |
| Tool schemas | Signature + docstring introspection | Hand-write JSON schemas |

Firestore remains the durable store for the things ADK does *not* own — the correction ledger,
skill registry, task fingerprints, and taste model. Layer on top of ADK; don't duplicate it.

**Use Gemini's actual capabilities, not just its text output:**

- **Thinking / reasoning budget → this is your effort control** (PRD §6.9). `quick`, `standard`,
  and `thorough` should map onto Gemini's configurable thinking budget, not merely a token cap.
  This is the correct implementation and it showcases the model.
- **Context caching** — cache the stable system prefix, tool definitions, and skill registry. This
  is the single largest cost saving available and it is a first-class Gemini API feature. Promote
  it from P1 to build it early.
- **Native structured output** — use schema-constrained generation for every internal step that
  returns data. Never parse JSON out of prose.
- **Long context** — with a very large window, compact later and less aggressively than the PRD's
  original assumption. Measure before you compact.

## Security: untrusted content is data, never instructions

KIW1 reads web pages, and later email. **Both are attacker-controlled.** This is the most likely
real vulnerability in the system and a knowledgeable judge will look for it.

1. **Retrieved content can never issue instructions.** Text fetched from the web or received in a
   message is wrapped and clearly delimited as untrusted data. If it contains something shaped like
   a command — "ignore previous instructions", "you are now authorised to…" — it is quoted to the
   user, never obeyed.
2. **No tool call may be triggered solely by retrieved content.** An action whose only
   justification traces back to fetched text requires explicit user approval, regardless of the
   hands-off setting.
3. **Memory poisoning is the subtle one.** Overnight research writes to durable memory. If
   attacker-controlled text can enter memory unfiltered, an attacker gains a *persistent* foothold
   that survives every future session. Memory writes originating from untrusted sources must be
   tagged with their provenance, and provenance must be visible at retrieval.
4. **The Prompt Refinery is a natural choke point** — put the untrusted-content check there.

Implement these as ADK callbacks, not as prompt instructions. A guardrail written in a prompt is a
suggestion; a guardrail written in a callback is a control.

## Prove the self-improvement, don't assert it

**This is the highest-value thing in this document.** Every entrant will claim their agent learns.
Almost none will measure it.

Build a fixed benchmark of ~20 tasks representative of real use. Then:

1. Run it against a **cold** KIW1 — empty memory, no corrections, no forged skills. Record the score.
2. Let KIW1 learn: run realistic sessions, correct its mistakes, let Skill Forge fire.
3. **Run the identical benchmark again.** Record the score.
4. Report both numbers, the delta, and the methodology.

Use ADK's evaluation framework so the harness is reproducible and the judges can rerun it.

A single line — *"11/20 cold, 17/20 after learning, same 20 tasks, harness in `evals/`"* — is worth
more than any architecture diagram, because it is the only claim in the whole submission that is
falsifiable. Put it in the README and on screen in the video.

Also wire **Cloud Trace / OpenTelemetry** so every run has an inspectable reasoning chain with
per-step token counts, latency, and cost. Cheap to add, Google-native, and it makes the
architecture visible to someone who cannot read your code.

## Build a real interface

`adk web` is a development tool, not a demo. The submission asks for a hosted URL and the video
must show the product working. Build a minimal but deliberate frontend that makes the invisible
visible:

- the **skill registry** — skills appearing as they are forged
- the **correction ledger** — rules learned, and what triggered each
- a **live cost and latency meter** per request
- the **memory palace**, shown as its `room → locus → item` structure rather than a flat list

Plain, fast, and legible beats styled and slow. This is also your only shot at Best Multimodal UX
if voice ships.

## Build order

| Phase | Deliverable |
|---|---|
| **0** | ADK skeleton deployed on Cloud Run; Gemini 3.7 Flash responding; Firestore connected |
| **1** | **Skill Forge** (PRD §6.2) — the 3-occurrences-in-7-days trigger, skill generation, `/skill` listing. *The differentiator. Build it first.* |
| **2** | **Prompt Refinery** (§6.1) — clarifying questions, brief rewrite, then execute |
| **3** | **Correction Ledger** (§6.5) — corrections become durable rules retrieved before future tasks |
| **4** | **Overnight Research** (§6.3) — Cloud Scheduler trigger, research, self-critique, morning report |
| **5** | **Strategic Planner** (§6.4) — three candidate paths, code-scored, visible comparison |
| **6** | Thin Approval Layer (§6.7), Model Router (§6.9) with thinking-budget effort control, Cloud Trace |
| **7** | **The benchmark.** ~20 tasks, cold run scored, learned run scored, both numbers recorded |
| **8** | Minimal frontend: skill registry, correction ledger, cost meter |
| **9** | **Stop building.** Seed data, README with one-command deploy, architecture diagram, demo rehearsal |

After each phase: commit, deploy, verify the deployed version works, and report what you verified
and how. Do not start the next phase on an unverified one.

## Engineering standards

- **Plugin manifests are the source of truth for risk and capability** (PRD §5.2). The approval
  layer reads the manifest; it never asks a model how risky an action is.
- **Every model call is logged** with model, token counts, latency, and cost. Budget enforcement
  is code, and it hard-stops rather than degrading silently.
- **Structured internally, plain language externally.** Anything a user reads must be free of
  jargon and understandable by someone non-technical.
- **Failures are explicit.** No silent fallbacks, no empty results dressed up as success.
- **Test the deterministic core** — fingerprinting, the 3-in-7-days window, plan scoring, risk
  classification, budget enforcement. These are pure functions; they must be provably correct.
- Design so that a killed Cloud Run instance resumes its in-flight job from Pub/Sub. This will be
  demonstrated live on camera.

## When to stop and ask

Ask before: adding a dependency the PRD doesn't imply; changing anything about the data boundary;
adding a model call where code would do; deviating from the build order; or spending more than a
few minutes blocked.

Do **not** ask before routine implementation choices — file layout, naming, test structure. Make
the call and keep moving.

## Deliverables

1. A deployed Cloud Run service with a working public URL.
2. A repo with a `README.md` whose spin-up instructions someone else can actually follow —
   exact prerequisites with versions, a `.env.example` with every variable explained, one deploy
   command, and a "what you should see" section.
3. **`evals/` — the benchmark, both scores, and the methodology.** The cold number, the learned
   number, the delta, and instructions to rerun it. This is the most important artefact in the
   repository; it is the only claim a judge can verify for themselves.
4. **A working frontend** showing the skill registry, the correction ledger, and a live cost and
   latency meter. Plain and fast, not styled and slow.
5. A clean architecture diagram: Gemini → ADK → Cloud Run → Firestore / Pub/Sub, with the local
   data boundary and the untrusted-content boundary both drawn as explicit lines.
6. A `seed/` directory of realistic synthetic data sufficient to demo every built feature.
7. An accurate written list of what works, what is stubbed, and what is not built. Accurate, not
   flattering.

Begin with Phase 0. Tell me what you are about to do, then do it.
