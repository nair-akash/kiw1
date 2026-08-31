import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.gateway import agent_gateway

@dataclass
class EnterpriseAgentRecord:
    agent_id: str
    name: str
    version: str
    department: str
    description: str
    capabilities: List[str]
    allowed_tools: List[str]
    status: str  # "certified", "experimental", "deprecated", "published"
    author: str
    created_at: str
    last_updated: str
    invocations: int = 0
    rating: float = 5.0
    sla_ms: int = 2500
    metadata: Dict[str, Any] = field(default_factory=dict)

class EnterpriseAgentRegistry:
    """Enterprise Agent Registry:
    Central repository for publishing, versioning, cataloging, and discovering
    enterprise-approved institutional agents across departments.
    """

    def __init__(self):
        self._registry: Dict[str, EnterpriseAgentRecord] = {}
        self._init_certified_fleet()

    def _init_certified_fleet(self):
        """Pre-populates the enterprise registry with certified institutional fleet agents."""
        fleet = [
            EnterpriseAgentRecord(
                agent_id="secops-sentinel",
                name="SecOps Sentinel",
                version="2.1.0",
                department="SecOps",
                description="Autonomous institutional vulnerability auditor, penetration testing validator, and security telemetry inspector.",
                capabilities=["network:web", "security:audit", "vulnerability:scan"],
                allowed_tools=["web_search", "fetch_page", "calculate", "execute_skill"],
                status="certified",
                author="Chief Information Security Office (CISO)",
                created_at="2026-08-01T00:00:00Z",
                last_updated="2026-08-30T12:00:00Z",
                invocations=1420,
                rating=4.95,
                sla_ms=1800,
                metadata={"compliance": ["SOC2", "ISO27001", "HIPAA"], "zero_trust_level": "Tier-1"},
            ),
            EnterpriseAgentRecord(
                agent_id="finops-analyzer",
                name="FinOps Analyzer",
                version="1.8.4",
                department="Finance",
                description="Enterprise invoice validation, cloud cost allocation, GST calculation, and real-time forex arbitrage auditing.",
                capabilities=["financial:calculation", "currency:forex", "tax:gst"],
                allowed_tools=["calculate", "web_search", "draft_email", "remember", "recall"],
                status="certified",
                author="Finance Systems Engineering",
                created_at="2026-08-05T00:00:00Z",
                last_updated="2026-08-31T09:00:00Z",
                invocations=3280,
                rating=4.98,
                sla_ms=1200,
                metadata={"currency_support": ["OMR", "INR", "USD", "EUR", "AED"], "audit_standards": ["GAAP", "IFRS"]},
            ),
            EnterpriseAgentRecord(
                agent_id="devops-orchestrator",
                name="DevOps Orchestrator",
                version="3.0.1",
                department="DevOps",
                description="Automated CI/CD pipeline verification, container sandbox execution, and cloud deployment health validation.",
                capabilities=["sandbox:python", "infra:cloud", "runtime:async"],
                allowed_tools=["execute_python_code", "web_search", "execute_skill"],
                status="certified",
                author="Platform Engineering Team",
                created_at="2026-08-10T00:00:00Z",
                last_updated="2026-08-31T15:00:00Z",
                invocations=2150,
                rating=4.91,
                sla_ms=2100,
                metadata={"supported_clouds": ["GCP", "AWS", "Azure"], "sandbox_isolation": "gVisor-compatible"},
            ),
            EnterpriseAgentRecord(
                agent_id="compliance-guardian",
                name="Compliance Guardian",
                version="2.0.0",
                department="Compliance",
                description="Data sovereignty enforcer, GDPR consent ledger validator, and Model Armor zero-leak verification agent.",
                capabilities=["governance:sovereignty", "privacy:gdpr", "armor:inline"],
                allowed_tools=["query_vault", "web_search", "remember", "recall"],
                status="certified",
                author="Legal & Regulatory Affairs",
                created_at="2026-08-12T00:00:00Z",
                last_updated="2026-08-31T18:00:00Z",
                invocations=980,
                rating=5.0,
                sla_ms=1500,
                metadata={"sovereignty_zones": ["US-Central", "EU-Frankfurt", "AP-Sydney"], "retention_policy": "7-years"},
            ),
            EnterpriseAgentRecord(
                agent_id="taskmaster-executive",
                name="Taskmaster Executive",
                version="2.5.0",
                department="Executive",
                description="Multi-step heavy-lifting chore automation engine that orchestrates research, calculations, and structured deliverables.",
                capabilities=["workflow:chore-automation", "multi-step:dag", "state:persistent"],
                allowed_tools=["*"],
                status="certified",
                author="Autonomous Operations Core",
                created_at="2026-08-15T00:00:00Z",
                last_updated="2026-09-01T00:00:00Z",
                invocations=4500,
                rating=4.99,
                sla_ms=3000,
                metadata={"heavy_lifting": True, "human_in_the_loop_support": True},
            ),
        ]

        for agent in fleet:
            self._registry[agent.agent_id] = agent

    def list_agents(self, department: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns list of enterprise agents matching optional filters."""
        results = []
        for a in self._registry.values():
            if department and a.department.lower() != department.lower():
                continue
            if status and a.status.lower() != status.lower():
                continue
            results.append({
                "agent_id": a.agent_id,
                "name": a.name,
                "version": a.version,
                "department": a.department,
                "description": a.description,
                "capabilities": a.capabilities,
                "allowed_tools": a.allowed_tools,
                "status": a.status,
                "author": a.author,
                "invocations": a.invocations,
                "rating": a.rating,
                "sla_ms": a.sla_ms,
                "last_updated": a.last_updated,
                "metadata": a.metadata,
            })
        return sorted(results, key=lambda x: x["invocations"], reverse=True)

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        a = self._registry.get(agent_id)
        if not a:
            return None
        return {
            "agent_id": a.agent_id,
            "name": a.name,
            "version": a.version,
            "department": a.department,
            "description": a.description,
            "capabilities": a.capabilities,
            "allowed_tools": a.allowed_tools,
            "status": a.status,
            "author": a.author,
            "invocations": a.invocations,
            "rating": a.rating,
            "sla_ms": a.sla_ms,
            "created_at": a.created_at,
            "last_updated": a.last_updated,
            "metadata": a.metadata,
        }

    def publish_agent(
        self,
        name: str,
        department: str,
        description: str,
        capabilities: List[str],
        allowed_tools: List[str],
        author: str = "Enterprise Developer",
        version: str = "1.0.0",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Publishes a new enterprise-approved agent into the central registry."""
        agent_id = f"agent-{name.lower().replace(' ', '-')}-{uuid.uuid4().hex[:6]}"
        now = datetime.now(timezone.utc).isoformat()
        record = EnterpriseAgentRecord(
            agent_id=agent_id,
            name=name,
            version=version,
            department=department,
            description=description,
            capabilities=capabilities,
            allowed_tools=allowed_tools,
            status="published",
            author=author,
            created_at=now,
            last_updated=now,
            invocations=0,
            rating=5.0,
            sla_ms=2500,
            metadata=metadata or {},
        )
        self._registry[agent_id] = record

        # Register cryptographic identity in Zero-Trust Gateway
        agent_gateway.issue_identity(
            agent_id=agent_id,
            name=name,
            department=department,
            roles=["institutional-agent"],
            allowed_tools=set(allowed_tools),
        )

        return self.get_agent(agent_id)

    def record_invocation(self, agent_id: str):
        if agent_id in self._registry:
            self._registry[agent_id].invocations += 1

agent_registry = EnterpriseAgentRegistry()
