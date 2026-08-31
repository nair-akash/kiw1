import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class ClarifyingQuestion:
    id: str
    question: str
    options: List[str]

@dataclass
class RefinedBrief:
    original_prompt: str
    is_ambiguous: bool
    reasons: List[str] = field(default_factory=list)
    questions: List[ClarifyingQuestion] = field(default_factory=list)
    goal: str = ""
    constraints: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    out_of_scope: List[str] = field(default_factory=list)

class PromptRefinery:
    """Pre-execution interrogation and ambiguity classifier.
    Deterministic heuristic classification executes in code with zero token overhead.
    """

    AMBIGUOUS_PRONOUNS = {"it", "them", "that", "this", "those", "these", "him", "her"}
    VAGUE_VERBS = {"fix", "do", "make", "clean", "look", "check", "handle", "manage", "improve", "update"}
    VAGUE_TARGETS = {"stuff", "things", "everything", "something", "problem", "issue", "bug", "files"}
    CONVERSATIONAL_GREETINGS = {
        "hi", "hello", "hey", "howdy", "greetings", "good morning", "good afternoon", "good evening",
        "yo", "sup", "help", "who are you", "what can you do", "what are you", "how are you", "test",
        "ping", "status", "who are you?", "what can you do?", "how are you?", "hey there", "hello there",
        "hi there", "start", "welcome"
    }

    def classify_ambiguity(self, prompt: str) -> tuple[bool, List[str]]:
        """Determines if a prompt is ambiguous using pure Python heuristics."""
        reasons = []
        cleaned = prompt.strip().lower()
        words = re.findall(r"\b[a-z0-9_-]+\b", cleaned)

        # Check conversational bypass for greetings / self-introduction questions
        is_greeting = (
            cleaned in self.CONVERSATIONAL_GREETINGS
            or any(cleaned.startswith(g) and len(words) <= 4 for g in ["hi", "hello", "hey", "howdy", "good morning", "good afternoon", "good evening", "who are you", "how are you", "what can you do"])
        )

        # 1. Very short prompts (< 3 words) that are not recognized greetings
        if len(words) < 3 and not is_greeting:
            reasons.append("Prompt is very short and lacks context.")

        # 2. Unresolved pronouns at key positions
        found_pronouns = [w for w in words if w in self.AMBIGUOUS_PRONOUNS]
        if found_pronouns and len(words) <= 6 and not is_greeting:
            reasons.append(f"Contains unresolved pronouns: {', '.join(set(found_pronouns))}.")

        # 3. Vague verbs with no specified concrete entity
        if words and words[0] in self.VAGUE_VERBS and not is_greeting:
            if len(words) <= 4:
                reasons.append(f"Starts with vague action '{words[0]}' without specific target or scope.")

        # 4. Vague targets
        found_targets = [w for w in words if w in self.VAGUE_TARGETS]
        if found_targets and not is_greeting:
            reasons.append(f"Refers to non-specific target: {', '.join(set(found_targets))}.")

        # 5. Missing success criteria / scope in open-ended statements
        if cleaned in ["make it better", "fix it", "do research", "summarize", "clean up", "run"]:
            reasons.append("Lacks measurable success criteria and defined scope.")

        is_ambiguous = len(reasons) > 0
        return is_ambiguous, reasons

    def generate_clarifications(self, prompt: str, reasons: List[str]) -> List[ClarifyingQuestion]:
        """Generates at most 3 batched clarifying questions with options."""
        questions: List[ClarifyingQuestion] = []
        prompt_lower = prompt.lower()

        # Question 1: Target / Scope clarification
        if any("pronoun" in r or "target" in r or "short" in r for r in reasons):
            questions.append(ClarifyingQuestion(
                id="target_scope",
                question="Which specific target or document should this action apply to?",
                options=[
                    "The most recently modified file in the workspace",
                    "The current project documentation and seed data",
                    "All files matching the active workspace",
                ]
            ))

        # Question 2: Action / Outcome clarification
        if any("vague" in r or "action" in r for r in reasons):
            questions.append(ClarifyingQuestion(
                id="desired_action",
                question="What exact outcome would you like to achieve?",
                options=[
                    "Generate a concise plain-text summary",
                    "Execute the end-to-end task and save the results",
                    "Propose a step-by-step plan before making any changes",
                ]
            ))

        # Question 3: Constraints / Mode clarification
        questions.append(ClarifyingQuestion(
            id="execution_mode",
            question="What constraint or effort level should be applied?",
            options=[
                "Standard speed and automatic error recovery",
                "Thorough deep-reasoning mode with verification",
                "Quick dry-run without persistent modifications",
            ]
        ))

        return questions[:3]

    def refine(self, prompt: str) -> RefinedBrief:
        """Processes a prompt through the refinery."""
        is_ambiguous, reasons = self.classify_ambiguity(prompt)

        if not is_ambiguous:
            # Clear prompt: produce structured brief and execute immediately
            return RefinedBrief(
                original_prompt=prompt,
                is_ambiguous=False,
                goal=prompt.strip(),
                constraints=["Adhere to local data boundary", "Deterministic budget limits"],
                success_criteria=["Task completed with verified output"],
                out_of_scope=["Modifications outside workspace context"],
            )

        questions = self.generate_clarifications(prompt, reasons)
        return RefinedBrief(
            original_prompt=prompt,
            is_ambiguous=True,
            reasons=reasons,
            questions=questions,
            goal=f"Clarify and execute: '{prompt}'",
            constraints=["Requires user clarification before irreversible action"],
            success_criteria=["User resolves ambiguity", "Brief agreed upon"],
            out_of_scope=["Unbounded execution on vague inputs"],
        )

    def apply_clarifications(self, original_prompt: str, answers: Dict[str, str]) -> RefinedBrief:
        """Constructs an explicit actionable brief once clarifications are answered."""
        goal_parts = [original_prompt.strip()]
        for q_id, ans in answers.items():
            goal_parts.append(f"[{q_id}: {ans}]")

        refined_goal = " | ".join(goal_parts)

        return RefinedBrief(
            original_prompt=original_prompt,
            is_ambiguous=False,
            goal=refined_goal,
            constraints=["Adhere to user clarified answers", "Observe local data boundary"],
            success_criteria=["All specified goals in the clarified brief are met"],
            out_of_scope=["Actions contradictory to provided answers"],
        )

refinery = PromptRefinery()
