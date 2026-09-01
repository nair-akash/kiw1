# GCP Billing Safety, Free Tier Limits & Debit Card Removal Guide

## 1. Zero-Cost Operation Safeguards
- **Cloud Run Concurrency & Min/Max Instances:**
  Ensure `--min-instances=0` (scales to zero when idle = $0.00) and `--max-instances=1` (prevents auto-scaling spikes).
  ```bash
  gcloud run services update kiw1 --region=us-central1 --min-instances=0 --max-instances=1
  ```
- **Gemini Free Tier Quotas:**
  Google Cloud enforces default free tier quotas (`GenerateContent free tier input token count limit per model per day`).
  When usage reaches 100% of the free tier limit, Google throttles/blocks requests rather than charging the card.
- **Budget Alerts:**
  Set a strict $1.00 budget in GCP Billing with alerts at 50%, 90%, and 100% emailed to the billing admin.

## 2. Detaching & Deleting Debit Card from Google Cloud / Google Pay
Google Cloud does not permit deleting the primary payment method while a Cloud Billing Account is active.

### Execution Protocol:
1. **Close the Cloud Billing Account:**
   - Navigate to [Google Cloud Billing Console](https://console.cloud.google.com/billing).
   - Go to **Account Management** (or **Settings**) in the left sidebar.
   - Click **Close Billing Account** and confirm.
   - *Effect:* Immediately terminates all active billing and disables paid services.
2. **Remove Card on Google Pay:**
   - Navigate to [pay.google.com](https://pay.google.com).
   - Go to **Payment methods**.
   - Click **Remove** on the linked debit card.
   - Google Pay allows removal with no replacement required once the billing account is closed.

## 3. Post-Hackathon Teardown Command
To permanently delete the Cloud Run container after the judging period:
```bash
gcloud run services delete kiw1 --region=us-central1 --quiet
```
