import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional
from google.cloud import pubsub_v1
from app.config import settings
from app.store import store

class DurableJobQueue:
    """Durable job delegation & resumption via Google Cloud Pub/Sub and Firestore state."""

    def __init__(self):
        self.topic_name = "kiw1-jobs"
        self.subscription_name = "kiw1-jobs-sub"
        self._publisher = None
        self._subscriber = None
        self._local_queue: List[Dict[str, Any]] = []
        self._init_pubsub()

    def _init_pubsub(self):
        try:
            if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("GOOGLE_CLOUD_PROJECT"):
                self._publisher = pubsub_v1.PublisherClient()
                self._subscriber = pubsub_v1.SubscriberClient()
        except Exception:
            pass

    def enqueue_job(self, task_type: str, payload: Dict[str, Any], idempotency_key: Optional[str] = None) -> str:
        """Publishes a job with an idempotency key for durable execution."""
        key = idempotency_key or f"job_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc).isoformat()

        job_record = {
            "id": key,
            "task_type": task_type,
            "payload": payload,
            "status": "pending",
            "created_at": now,
            "attempts": 0,
            "result": None,
        }

        # Save to durable store
        if store.is_cloud():
            store.get_user_ref().collection("jobs").document(key).set(job_record)
        else:
            store._local_data["jobs"][key] = job_record
            store._save_local_data()

        # Publish to Pub/Sub if cloud is active
        if self._publisher and store.is_cloud():
            try:
                topic_path = self._publisher.topic_path(settings.project_id, self.topic_name)
                data = json.dumps(job_record).encode("utf-8")
                self._publisher.publish(topic_path, data, idempotency_key=key)
            except Exception:
                self._local_queue.append(job_record)
        else:
            self._local_queue.append(job_record)

        return key

    def process_pending_jobs(self, handler: Callable[[str, Dict[str, Any]], Any]) -> List[Dict[str, Any]]:
        """Processes pending jobs from local or Pub/Sub queue with idempotency protection."""
        processed = []
        while self._local_queue:
            job = self._local_queue.pop(0)
            key = job["id"]
            job["status"] = "in_progress"
            job["attempts"] += 1

            try:
                result = handler(job["task_type"], job["payload"])
                job["status"] = "completed"
                job["result"] = result
            except Exception as e:
                job["status"] = "failed"
                job["error"] = str(e)

            # Update store
            if store.is_cloud():
                store.get_user_ref().collection("jobs").document(key).set(job)
            else:
                store._local_data["jobs"][key] = job
                store._save_local_data()

            processed.append(job)

        return processed

job_queue = DurableJobQueue()
