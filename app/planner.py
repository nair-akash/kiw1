from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class CandidatePath:
    id: str
    name: str
    description: str
    estimated_time_s: float
    estimated_cost_usd: float
    effort_level: str
    risk_level: str
    steps: List[str]
    can_parallelize: bool
    score: float = 0.0
    reasoning: str = ""

@dataclass
class SubtaskNode:
    id: str
    title: str
    tool_or_action: str
    dependencies: List[str]
    is_independent: bool = True

@dataclass
class StrategicPlan:
    task: str
    candidates: List[CandidatePath]
    selected_path: CandidatePath
    selection_reason: str
    subtasks: List[SubtaskNode]
    use_parallel_agents: bool

class StrategicPlanner:
    """Strategic Planner generating and scoring 3 candidate execution paths in pure Python."""

    def generate_candidate_paths(self, task: str) -> List[CandidatePath]:
        """Generates 3 distinct candidate paths: Fastest, Cheapest, Most Thorough."""
        # 1. Fastest Path
        fastest = CandidatePath(
            id="path_fastest",
            name="Fastest Direct Route",
            description="Executes essential tools sequentially with quick effort and minimal round-trips.",
            estimated_time_s=1.2,
            estimated_cost_usd=0.0003,
            effort_level="quick",
            risk_level="low",
            steps=["Retrieve relevant context", "Execute single primary action", "Format summary"],
            can_parallelize=False,
            reasoning="Optimized for lowest latency and direct execution.",
        )

        # 2. Cheapest Path
        cheapest = CandidatePath(
            id="path_cheapest",
            name="Cheapest Cached Route",
            description="Leverages local cache and Memory Palace first, minimizing model generation tokens.",
            estimated_time_s=1.8,
            estimated_cost_usd=0.0001,
            effort_level="quick",
            risk_level="none",
            steps=["Query Memory Palace structure", "Reuse cached tool results", "Output synthesized result"],
            can_parallelize=False,
            reasoning="Optimized for minimal API token expenditure.",
        )

        # 3. Most Thorough Path
        thorough = CandidatePath(
            id="path_thorough",
            name="Most Thorough & Verified Route",
            description="Decomposes into multi-step validation, parallel research sub-agents, and self-consistency verification.",
            estimated_time_s=4.5,
            estimated_cost_usd=0.0015,
            effort_level="thorough",
            risk_level="none",
            steps=[
                "Parse all constraints & query Memory Palace",
                "Execute parallel sub-queries",
                "Run cross-validation check",
                "Synthesize verified report",
            ],
            can_parallelize=True,
            reasoning="Optimized for highest accuracy, full verification, and risk elimination.",
        )

        return [fastest, cheapest, thorough]

    def score_paths(
        self,
        paths: List[CandidatePath],
        user_weights: Optional[Dict[str, float]] = None,
    ) -> tuple[CandidatePath, str]:
        """Scores candidate paths using deterministic weighted utility in pure code.
        Weights default to balanced: time (0.3), cost (0.2), accuracy/thoroughness (0.4), risk (0.1).
        """
        weights = user_weights or {
            "time": 0.3,
            "cost": 0.2,
            "thoroughness": 0.4,
            "risk_safety": 0.1,
        }

        best_path = None
        best_score = -1.0
        details = []

        for p in paths:
            # Normalize components to 0.0 - 1.0 utility
            time_score = max(0.0, 1.0 - (p.estimated_time_s / 6.0))
            cost_score = max(0.0, 1.0 - (p.estimated_cost_usd / 0.005))
            thorough_score = 1.0 if p.effort_level == "thorough" else (0.6 if p.effort_level == "standard" else 0.4)
            safety_score = 1.0 if p.risk_level == "none" else (0.8 if p.risk_level == "low" else 0.4)

            total = (
                weights["time"] * time_score
                + weights["cost"] * cost_score
                + weights["thoroughness"] * thorough_score
                + weights["risk_safety"] * safety_score
            )
            p.score = round(total, 4)
            details.append(f"{p.name} (score: {p.score:.3f})")

            if total > best_score:
                best_score = total
                best_path = p

        assert best_path is not None
        reason = (
            f"Selected '{best_path.name}' with composite score {best_score:.3f} "
            f"outperforming alternatives: {', '.join(details)}."
        )
        return best_path, reason

    def build_plan(self, task: str, user_weights: Optional[Dict[str, float]] = None) -> StrategicPlan:
        """Constructs full strategic plan with candidate comparison and subtask graph."""
        candidates = self.generate_candidate_paths(task)
        selected_path, reason = self.score_paths(candidates, user_weights)

        # Decompose into subtasks
        subtasks = []
        for idx, step_desc in enumerate(selected_path.steps):
            deps = [f"subtask_{idx}"] if idx > 0 and not selected_path.can_parallelize else []
            subtasks.append(SubtaskNode(
                id=f"subtask_{idx + 1}",
                title=step_desc,
                tool_or_action=step_desc.lower().replace(" ", "_"),
                dependencies=deps,
                is_independent=len(deps) == 0,
            ))

        # Check parallel condition in code (PRD §6.4: >= 2 independent branches)
        independent_count = sum(1 for s in subtasks if s.is_independent)
        use_parallel = selected_path.can_parallelize and independent_count >= 2

        return StrategicPlan(
            task=task,
            candidates=candidates,
            selected_path=selected_path,
            selection_reason=reason,
            subtasks=subtasks,
            use_parallel_agents=use_parallel,
        )

planner = StrategicPlanner()
