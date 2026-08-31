import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

@dataclass
class OTelSpan:
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    name: str
    kind: str  # "SERVER", "CLIENT", "INTERNAL", "PRODUCER"
    start_time_unix_nano: int
    end_time_unix_nano: Optional[int] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)
    status_code: str = "OK"  # "OK", "ERROR", "UNSET"
    status_message: Optional[str] = None

class OpenTelemetryService:
    """OpenTelemetry-Compliant Observability Collector:
    Emits W3C TraceContext spans (traceparent, span_id, attributes)
    capturing end-to-end reasoning chains, tool invocations, Model Armor checks,
    and Gateway policy decisions.
    """

    def __init__(self):
        self._spans: Dict[str, List[OTelSpan]] = {}  # trace_id -> List[OTelSpan]
        self._trace_metadata: Dict[str, Dict[str, Any]] = {}

    def start_trace(self, task_name: str, user_id: str = "default_user") -> str:
        """Starts a new W3C-compliant trace context."""
        trace_id = uuid.uuid4().hex  # 32-char hex string (W3C standard)
        self._spans[trace_id] = []
        self._trace_metadata[trace_id] = {
            "trace_id": trace_id,
            "task_name": task_name,
            "user_id": user_id,
            "start_time": datetime.now(timezone.utc).isoformat(),
        }
        # Create Root Span
        self.start_span(
            trace_id=trace_id,
            name=f"turn:{task_name[:32]}",
            parent_span_id=None,
            kind="SERVER",
            attributes={
                "service.name": "kiw1-agent",
                "service.version": "3.5.0",
                "user.id": user_id,
                "task.prompt": task_name,
            },
        )
        return trace_id

    def start_span(
        self,
        trace_id: str,
        name: str,
        parent_span_id: Optional[str] = None,
        kind: str = "INTERNAL",
        attributes: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Creates and starts a new OpenTelemetry child span."""
        span_id = uuid.uuid4().hex[:16]  # 16-char hex string (W3C standard)
        now_ns = int(time.time() * 1_000_000_000)

        span = OTelSpan(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            name=name,
            kind=kind,
            start_time_unix_nano=now_ns,
            attributes=attributes or {},
        )

        if trace_id not in self._spans:
            self._spans[trace_id] = []
        self._spans[trace_id].append(span)
        return span_id

    def end_span(
        self,
        trace_id: str,
        span_id: str,
        status: str = "OK",
        error_message: Optional[str] = None,
        attributes_update: Optional[Dict[str, Any]] = None,
    ):
        """Closes a span with duration, status, and custom attributes."""
        now_ns = int(time.time() * 1_000_000_000)
        spans = self._spans.get(trace_id, [])
        for s in spans:
            if s.span_id == span_id:
                s.end_time_unix_nano = now_ns
                s.status_code = status
                s.status_message = error_message
                if attributes_update:
                    s.attributes.update(attributes_update)
                break

    def export_trace_waterfall(self, trace_id: str) -> Dict[str, Any]:
        """Exports W3C compliant trace format with timeline waterfall and parent-child hierarchy."""
        spans = self._spans.get(trace_id, [])
        if not spans:
            return {"trace_id": trace_id, "spans": [], "total_duration_ms": 0}

        min_start = min(s.start_time_unix_nano for s in spans)
        max_end = max((s.end_time_unix_nano or s.start_time_unix_nano) for s in spans)
        total_duration_ms = round((max_end - min_start) / 1_000_000.0, 2)

        span_records = []
        for s in spans:
            end_ns = s.end_time_unix_nano or s.start_time_unix_nano
            offset_ms = round((s.start_time_unix_nano - min_start) / 1_000_000.0, 2)
            duration_ms = round((end_ns - s.start_time_unix_nano) / 1_000_000.0, 2)

            span_records.append({
                "span_id": s.span_id,
                "parent_span_id": s.parent_span_id,
                "name": s.name,
                "kind": s.kind,
                "offset_ms": offset_ms,
                "duration_ms": max(duration_ms, 0.1),
                "status": s.status_code,
                "error": s.status_message,
                "attributes": s.attributes,
                "w3c_traceparent": f"00-{trace_id}-{s.span_id}-01",
            })

        return {
            "trace_id": trace_id,
            "metadata": self._trace_metadata.get(trace_id, {}),
            "total_duration_ms": total_duration_ms,
            "span_count": len(spans),
            "spans": span_records,
        }

    def list_recent_traces(self, limit: int = 15) -> List[Dict[str, Any]]:
        recent_ids = list(self._spans.keys())[-limit:]
        return [self.export_trace_waterfall(tid) for tid in reversed(recent_ids)]

otel_service = OpenTelemetryService()
