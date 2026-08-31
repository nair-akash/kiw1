#!/usr/bin/env bash
# KIW1 — one-shot Google Cloud bootstrap.
#
#   ./bootstrap.sh
#
# Takes an authenticated gcloud and a GOOGLE_API_KEY in .env, and leaves you with a
# deployed Cloud Run service and its public URL. Safe to re-run: every step checks
# before it creates, so a half-finished run resumes rather than erroring.
set -euo pipefail

PROJECT="${KIW1_PROJECT:-kiw1-agent}"
REGION="${KIW1_REGION:-us-central1}"
SERVICE="kiw1"
SECRET="gemini-api-key"
TOPIC="kiw1-jobs"

say() { printf '\n\033[1;34m==>\033[0m %s\n' "$1"; }
ok()  { printf '    \033[0;32mok\033[0m %s\n' "$1"; }

# ---------------------------------------------------------------- preflight ---
say "Preflight"
command -v gcloud >/dev/null || { echo "gcloud not found"; exit 1; }
gcloud auth list --format='value(account)' | grep -q . || { echo "Run: gcloud auth login"; exit 1; }
ok "authenticated as $(gcloud auth list --format='value(account)' | head -1)"

[ -f .env ] || { echo ".env missing"; exit 1; }
API_KEY="$(grep '^GOOGLE_API_KEY=' .env | cut -d= -f2-)"
[ -n "$API_KEY" ] || { echo "GOOGLE_API_KEY is empty in .env"; exit 1; }
ok "api key present (${#API_KEY} chars)"

# ------------------------------------------------------------------ project ---
say "Project: $PROJECT"
if gcloud projects describe "$PROJECT" >/dev/null 2>&1; then
  ok "already exists"
else
  gcloud projects create "$PROJECT" --name="KIW1"
  ok "created"
fi
gcloud config set project "$PROJECT" >/dev/null
gcloud config set run/region "$REGION" >/dev/null

# ------------------------------------------------------------------ billing ---
say "Billing"
if gcloud billing projects describe "$PROJECT" --format='value(billingEnabled)' 2>/dev/null | grep -qi true; then
  ok "already linked"
else
  ACCT="$(gcloud billing accounts list --filter='open=true' --format='value(name)' | head -1)"
  [ -n "$ACCT" ] || { echo "No open billing account. Claim your credit first."; exit 1; }
  gcloud billing projects link "$PROJECT" --billing-account="$ACCT"
  ok "linked to $ACCT"
fi

# --------------------------------------------------------------------- apis ---
say "Enabling APIs (slow the first time)"
gcloud services enable \
  run.googleapis.com firestore.googleapis.com pubsub.googleapis.com \
  cloudscheduler.googleapis.com secretmanager.googleapis.com \
  artifactregistry.googleapis.com cloudbuild.googleapis.com \
  generativelanguage.googleapis.com --quiet
ok "enabled"

# ---------------------------------------------------------------- firestore ---
say "Firestore"
if gcloud firestore databases describe --database='(default)' >/dev/null 2>&1; then
  ok "already exists"
else
  gcloud firestore databases create --location="$REGION" --quiet
  ok "created (Native mode)"
fi

# ------------------------------------------------------------------- pubsub ---
say "Pub/Sub"
gcloud pubsub topics describe "$TOPIC" >/dev/null 2>&1 \
  || gcloud pubsub topics create "$TOPIC" --quiet
gcloud pubsub subscriptions describe "${TOPIC}-sub" >/dev/null 2>&1 \
  || gcloud pubsub subscriptions create "${TOPIC}-sub" --topic "$TOPIC" --quiet
ok "topic and subscription ready"

# ------------------------------------------------------------------- secret ---
# The key goes in Secret Manager, never in --set-env-vars: env vars are visible to
# anyone who can describe the service, secrets are not.
say "Secret Manager"
if gcloud secrets describe "$SECRET" >/dev/null 2>&1; then
  printf '%s' "$API_KEY" | gcloud secrets versions add "$SECRET" --data-file=- >/dev/null
  ok "added new version"
else
  printf '%s' "$API_KEY" | gcloud secrets create "$SECRET" --data-file=- >/dev/null
  ok "created"
fi

PROJNUM="$(gcloud projects describe "$PROJECT" --format='value(projectNumber)')"
gcloud secrets add-iam-policy-binding "$SECRET" \
  --member="serviceAccount:${PROJNUM}-compute@developer.gserviceaccount.com" \
  --role=roles/secretmanager.secretAccessor --quiet >/dev/null
ok "runtime service account can read it"

# ------------------------------------------------------------------- deploy ---
say "Deploying to Cloud Run (a few minutes on the first build)"
gcloud run deploy "$SERVICE" \
  --source . \
  --region "$REGION" \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 3 \
  --set-secrets "GOOGLE_API_KEY=${SECRET}:latest" \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=${PROJECT},GOOGLE_CLOUD_REGION=${REGION}" \
  --quiet

URL="$(gcloud run services describe "$SERVICE" --region "$REGION" --format='value(status.url)')"
ok "deployed"

# ---------------------------------------------------------------- scheduler ---
say "Cloud Scheduler (overnight research, 03:00 daily)"
if gcloud scheduler jobs describe kiw1-overnight --location "$REGION" >/dev/null 2>&1; then
  ok "already exists"
else
  gcloud scheduler jobs create http kiw1-overnight \
    --schedule "0 3 * * *" --uri "${URL}/research/run" \
    --http-method POST --location "$REGION" --quiet
  ok "created"
fi

# ------------------------------------------------------------------- verify ---
say "Verifying the deployed service"
CODE="$(curl -s -o /dev/null -w '%{http_code}' "$URL" || echo 000)"
[ "$CODE" = "200" ] && ok "GET / -> 200" || echo "    GET / -> $CODE (check: gcloud run services logs read $SERVICE --region $REGION)"

cat <<EOF

────────────────────────────────────────────────────────────
  Hosted URL : $URL
  Project    : $PROJECT
  Console    : https://console.cloud.google.com/run?project=$PROJECT

  That URL is the "hosted project URL" for the Devpost form.
  Scales to zero, so it costs nothing between demos.
────────────────────────────────────────────────────────────
EOF
