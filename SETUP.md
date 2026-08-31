# KIW1 — Google Cloud setup, and how not to spend the $150

**You will almost certainly spend under $5.** Everything in the PRD's architecture sits inside
permanent free tiers, and the Gemini API's free tier already satisfies the hackathon's "Gemini 3.5
or newer via Gemini API or Vertex AI" requirement. Treat the credit as insurance against a
mistake, not as a budget to consume.

---

## Step 1 — Claim the credit

Two separate things, in this order:

1. **Sign up for the no-cost Google Cloud trial** at https://cloud.google.com/free — this is its
   own credit (typically $300 over 90 days) and requires a card, though it does not auto-charge
   when the trial ends.
2. **Then claim the hackathon's $150** using the credit form on the **Resources tab** of
   https://allthingsagentichackathon.devpost.com — you must be registered for the hackathon first.

While you're there, register for the **GEAR (Gemini Enterprise Agent Ready) programme** from the
Devpost to-do list. Free, and it signals platform engagement.

---

## Step 2 — Project and billing

```bash
gcloud auth login
gcloud projects create kiw1-agent --name="KIW1"
gcloud config set project kiw1-agent
```

Link billing (list your accounts first, then link the one holding the credit):

```bash
gcloud billing accounts list
gcloud billing projects link kiw1-agent --billing-account=YOUR_ACCOUNT_ID
```

**Region: use `us-central1`.** It has the broadest Gemini and Vertex AI model availability. Latency
is irrelevant for a demo, so don't optimise for geography — optimise for "the model I need is
actually there."

---

## Step 3 — Set a budget alarm before you write any code

This is the step people skip and regret. Do it now.

**Console → Billing → Budgets & alerts → Create budget.** Set the amount to **$20**, with email
alerts at 50%, 90%, and 100%.

Twenty dollars is deliberately far below your credit. If you ever get that email, something is
wrong and you want to know within hours — not after the credit is gone. A budget alert does not
cap spending; it warns you. The real caps are in Step 8.

---

## Step 4 — Enable the APIs

```bash
gcloud services enable \
  run.googleapis.com \
  firestore.googleapis.com \
  pubsub.googleapis.com \
  cloudscheduler.googleapis.com \
  secretmanager.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  aiplatform.googleapis.com \
  generativelanguage.googleapis.com
```

Enabling an API costs nothing. You only pay for use.

---

## Step 5 — Get a free Gemini key and develop against it

Go to https://aistudio.google.com/apikey and create an API key.

**This is the single biggest money-saver: do all development against the AI Studio free tier.** It
has rate limits but no cost, and — importantly — **it still satisfies the hackathon requirement**,
which accepts "Gemini API *or* Vertex AI." You do not need Vertex AI to be compliant.

```bash
export GOOGLE_API_KEY="your-key-here"
```

Never commit this. Put `GOOGLE_API_KEY=` in `.env.example` with an empty value, and put `.env` in
`.gitignore`. For the deployed service, use Secret Manager (Step 7).

---

## Step 6 — Local ADK loop

```bash
python -m venv .venv && source .venv/bin/activate
pip install google-adk google-cloud-firestore google-cloud-pubsub
```

ADK ships a local dev UI, which is the fastest way to iterate:

```bash
adk web
```

Build and test everything here first. Local iteration is free; every deploy costs a build minute.

> Verify command names against https://google.github.io/adk-docs/ — the ADK CLI is young and its
> surface moves. If `adk web` or `adk deploy` differs from what's documented, trust the docs.

---

## Step 7 — Deploy to Cloud Run

Store the key as a secret first:

```bash
echo -n "your-key-here" | gcloud secrets create gemini-api-key --data-file=-
```

Then deploy from source — Cloud Build containerises it for you, no Dockerfile needed:

```bash
gcloud run deploy kiw1 \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 3 \
  --set-secrets GOOGLE_API_KEY=gemini-api-key:latest
```

**`--min-instances 0` is the important flag.** It means the service scales to zero when idle and
costs nothing between demos. `--max-instances 3` caps the blast radius if something loops.

That command returns your public URL — which is the "hosted project URL" the submission asks for.
Take it; it's free and it's explicitly encouraged.

ADK also offers `adk deploy cloud_run` as a wrapper. Either is fine.

---

## Step 8 — The remaining services

```bash
# Firestore — pick Native mode
gcloud firestore databases create --location=us-central1

# Pub/Sub — the durable job queue
gcloud pubsub topics create kiw1-jobs
gcloud pubsub subscriptions create kiw1-jobs-sub --topic kiw1-jobs

# Cloud Scheduler — the overnight research trigger
gcloud scheduler jobs create http kiw1-overnight \
  --schedule "0 3 * * *" \
  --uri "YOUR_CLOUD_RUN_URL/research/run" \
  --http-method POST \
  --location us-central1
```

Adjust `0 3 * * *` to your actual sleep window.

---

## What will actually bill you

Roughly, and directionally — check the current pricing pages, these change:

| Service | Free allowance | Your usage | Risk |
|---|---|---|---|
| **Gemini API (AI Studio)** | Free tier with rate limits | All development | **None** |
| **Cloud Run** | ~2M requests/month, scales to zero | A demo and some testing | **None** with `--min-instances 0` |
| **Firestore** | ~1 GiB, ~50k reads / 20k writes per day | Ledgers and memory — tiny | **None** |
| **Pub/Sub** | ~10 GiB/month | A handful of messages | **None** |
| **Cloud Scheduler** | 3 jobs/month free | One job | **None** |
| **Cloud Build** | Free daily build minutes | A few deploys | Low |
| **Vertex AI** | No free tier | Only if you switch to it | ⚠️ **This is the one that bills** |
| **Overnight research** | — | Unbounded if uncapped | ⚠️ **The other one** |

**Only two things can meaningfully spend your credit:** Vertex AI calls, and an uncapped overnight
research loop. Both are controllable:

1. **Stay on the AI Studio key** unless you have a specific reason to need Vertex. You are
   compliant either way.
2. **Hard-cap the nightly research budget in code**, as the PRD requires (§6.3, §8) — a token
   ceiling per run, enforced before the call, that stops rather than degrades.
3. **Never set `--min-instances` above 0** until after judging.

---

## Before you submit

- [ ] Cloud Run URL loads and responds
- [ ] `--min-instances 0`, so it costs nothing while judges are looking at other entries
- [ ] Secrets in Secret Manager — **not** in the repo, not in env vars in the deploy command
- [ ] `.env` gitignored; `.env.example` committed with every variable named and explained
- [ ] Billing dashboard checked once — confirm the number is what you expect
- [ ] Screenshot or screen-record the Cloud Run dashboard and a Firestore document for the video;
      the rules require visible proof the backend runs on Google Cloud

The rules also say your app **does not** need to be live at the moment of judging — so if anything
starts costing money after you submit, turn it off. Keep the video as the proof.
