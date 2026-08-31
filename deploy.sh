#!/usr/bin/env bash
set -e

# KIW1 One-Command Deployment Script
# Deploys KIW1 to Google Cloud Run with Firestore, Pub/Sub, and Cloud Scheduler

echo "========================================================"
echo "          KIW1 Google Cloud Deployment Script           "
echo "========================================================"

# Check gcloud CLI
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI is not installed. Please install gcloud before deploying."
    exit 1
fi

PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "(unset)" ]; then
    echo "Error: No active GCP project configured. Run 'gcloud config set project YOUR_PROJECT_ID'."
    exit 1
fi

REGION="us-central1"
SERVICE_NAME="kiw1"

echo "Deploying KIW1 to project '$PROJECT_ID' in region '$REGION'..."

# 1. Enable Required Services
echo "[1/4] Enabling Google Cloud services..."
gcloud services enable \
  run.googleapis.com \
  firestore.googleapis.com \
  pubsub.googleapis.com \
  cloudscheduler.googleapis.com \
  secretmanager.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com

# 2. Deploy Cloud Run Service
echo "[2/4] Deploying to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
  --source . \
  --region "$REGION" \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 3 \
  --update-env-vars GOOGLE_CLOUD_PROJECT="$PROJECT_ID",GOOGLE_CLOUD_REGION="$REGION",GOOGLE_GENAI_USE_VERTEXAI="true",KIW1_DEFAULT_EFFORT="standard"

# Get Service URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --platform managed --region "$REGION" --format 'value(status.url)')
echo "Service live at: $SERVICE_URL"

# 3. Setup Pub/Sub Topic and Subscription
echo "[3/4] Ensuring Pub/Sub topic and subscription exist..."
gcloud pubsub topics create kiw1-jobs 2>/dev/null || true
gcloud pubsub subscriptions create kiw1-jobs-sub --topic kiw1-jobs 2>/dev/null || true

# 4. Setup Cloud Scheduler for Overnight Research
echo "[4/4] Configuring Cloud Scheduler for overnight research..."
gcloud scheduler jobs create http kiw1-overnight-trigger \
  --schedule "0 3 * * *" \
  --uri "$SERVICE_URL/research/run" \
  --http-method POST \
  --location "$REGION" 2>/dev/null || true

echo "========================================================"
echo " Deployment Complete!"
echo " Public Hosted URL: $SERVICE_URL"
echo " Open $SERVICE_URL to access the KIW1 Dashboard."
echo "========================================================"
