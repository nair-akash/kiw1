import os
from dataclasses import dataclass
from typing import Literal
from dotenv import load_dotenv

load_dotenv()

EffortLevel = Literal["quick", "standard", "thorough"]
VaultMode = Literal["sealed", "answers-only", "excerpt"]

@dataclass(frozen=True)
class Settings:
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    project_id: str = os.getenv("GOOGLE_CLOUD_PROJECT", "kiw1-local")
    region: str = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
    uid: str = os.getenv("KIW1_UID", "demo-user")
    default_effort: EffortLevel = os.getenv("KIW1_DEFAULT_EFFORT", "standard")  # type: ignore
    vault_mode: VaultMode = os.getenv("KIW1_VAULT_MODE", "answers-only")  # type: ignore
    local_vault_path: str = os.getenv("KIW1_LOCAL_VAULT_PATH", "./seed/synthetic_vault")
    port: int = int(os.getenv("PORT", "8080"))

    # Models (Strictly Gemini 3.5, 3.6, and 3.7)
    flash_model: str = os.getenv("KIW1_FLASH_MODEL", "gemini-3.7-flash")
    pro_model: str = os.getenv("KIW1_PRO_MODEL", "gemini-3.7-pro")
    local_fallback_model: str = "gemma-2-9b-it"

    # Thinking Budget Configuration for Effort Control (PRD §6.9)
    thinking_budgets = {
        "quick": 0,          # Minimal/no reasoning tokens for fastest response
        "standard": 2048,    # Standard reasoning budget
        "thorough": 8192,    # Deep reasoning budget for complex tasks
    }

    # Skill Forge Thresholds (PRD §6.2)
    skill_forge_threshold: int = 3
    skill_forge_window_days: int = 7
    skill_retirement_min_invocations: int = 5
    skill_retirement_min_success_rate: float = 0.60

    # Pricing per 1M tokens for cost accounting (Gemini 3.7 Flash & Pro)
    # Flash: $0.075 / 1M prompt, $0.30 / 1M completion
    # Pro: $1.25 / 1M prompt, $5.00 / 1M completion
    flash_prompt_cost_per_m: float = 0.075
    flash_completion_cost_per_m: float = 0.30
    pro_prompt_cost_per_m: float = 1.25
    pro_completion_cost_per_m: float = 5.00

    # Overnight Research Budget Limits
    nightly_research_token_cap: int = 250000
    nightly_research_cost_cap: float = 0.50  # $0.50 max per overnight run

settings = Settings()
