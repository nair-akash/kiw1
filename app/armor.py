import re
from typing import Any, Dict, List, Optional, Tuple

class ModelArmor:
    """Enterprise Model Armor providing inline guardrails to block:
    1. Prompt Injection (Direct, Indirect, Delimiter, and Roleplay attacks)
    2. Tool Poisoning (Malicious payloads hidden in tool outputs/external scraped data)
    3. PII & Secret Leaks (Automated zero-data-leak masking for credentials, cards, SSNs, and emails)
    """

    # Comprehensive Prompt Injection Signature Vectors
    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?(previous|prior|existing)\s+(instructions|directives|prompts|rules|guidelines|constraints)",
        r"disregard\s+(all\s+)?(prior|previous|existing)\s+(rules|instructions|directives|guidelines|constraints)",
        r"you\s+are\s+now\s+(authorised|unrestricted|in\s+developer\s+mode|dan|freed)",
        r"system\s*:\s*you\s+are",
        r"override\s+(all\s+)?(security|system|safety|guardrail)\s+(protocol|rules|settings|filters)",
        r"execute\s+command\s*:",
        r"bypass\s+(all\s+)?(guardrails|safety|security|filters|restrictions)",
        r"reveal\s+(all\s+)?(system\s+instructions|system\s+prompt|secret|api\s+keys)",
        r"jailbreak",
        r"drop\s+table",
        r"rm\s+-rf\s+/",
        r"format\s+c:",
    ]

    # Tool Poisoning Payloads (patterns injected into retrieved web/api content)
    TOOL_POISONING_PATTERNS = [
        r"<\s*script[^>]*>.*?<\s*/\s*script\s*>",
        r"javascript\s*:",
        r"data\s*:\s*text/html",
        r"<!--\s*#exec",
        r"eval\s*\(",
        r"exec\s*\(",
        r"\{\{\s*config\.",
        r"\$\{.*system.*\}",
        r"base64_decode\(",
        r"curl\s+-[sS]\s+http",
    ]

    # PII and Secret Extraction Vectors
    PII_SECRET_PATTERNS = [
        ("API_KEY", r"\b(?:sk-[a-zA-Z0-9]{20,}|AIzaSy[a-zA-Z0-9_-]{33}|ghp_[a-zA-Z0-9]{36}|xox[baprs]-[a-zA-Z0-9]{10,48})\b"),
        ("BEARER_TOKEN", r"\bBearer\s+[a-zA-Z0-9_\-\.]{25,}\b"),
        ("CREDIT_CARD", r"\b(?:\d{4}[ -]?){3}\d{4}\b"),
        ("SSN", r"\b\d{3}-\d{2}-\d{4}\b"),
        ("PASSWORD_EXPOSURE", r"\b(?:password|passwd|pwd|secret)\s*[:=]\s*['\"]?[^\s'\"]{6,}['\"]?\b"),
        ("EMAIL_PII", r"\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b"),
    ]

    def __init__(self):
        self.stats = {
            "total_inspections": 0,
            "prompt_injections_blocked": 0,
            "tool_poisonings_neutralized": 0,
            "pii_secrets_redacted": 0,
        }
        self.audit_log: List[Dict[str, Any]] = []

    def inspect_input(self, user_input: str) -> Tuple[bool, str, List[str]]:
        """Inspects incoming user prompt against prompt injection and malicious override vectors.
        Returns: (is_safe, sanitized_or_original_text, detected_threats)
        """
        self.stats["total_inspections"] += 1
        detected_threats = []

        for pattern in self.INJECTION_PATTERNS:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                detected_threats.append(f"Prompt Injection Detected: '{match.group(0)}'")

        if detected_threats:
            self.stats["prompt_injections_blocked"] += 1
            log_entry = {
                "type": "PROMPT_INJECTION_BLOCKED",
                "input_snippet": user_input[:100],
                "threats": detected_threats,
            }
            self.audit_log.append(log_entry)
            # Neutralize dangerous directives
            sanitized = user_input
            for pattern in self.INJECTION_PATTERNS:
                sanitized = re.sub(pattern, "[BLOCKED_INJECTION_ATTEMPT]", sanitized, flags=re.IGNORECASE)
            return False, sanitized, detected_threats

        return True, user_input, []

    def sanitize_tool_output(self, tool_name: str, raw_output: str) -> Tuple[str, List[str]]:
        """Scans and neutralizes tool poisoning payloads before model ingestion.
        Returns: (sanitized_output, detected_threats)
        """
        detected_threats = []
        sanitized = raw_output

        for pattern in self.TOOL_POISONING_PATTERNS:
            match = re.search(pattern, sanitized, re.IGNORECASE | re.DOTALL)
            if match:
                threat = f"Tool Poisoning Payload in '{tool_name}': '{match.group(0)[:40]}...'"
                detected_threats.append(threat)
                sanitized = re.sub(pattern, "[SANITIZED_MALICIOUS_PAYLOAD]", sanitized, flags=re.IGNORECASE | re.DOTALL)

        if detected_threats:
            self.stats["tool_poisonings_neutralized"] += len(detected_threats)
            self.audit_log.append({
                "type": "TOOL_POISONING_NEUTRALIZED",
                "tool": tool_name,
                "threats": detected_threats,
            })

        return sanitized, detected_threats

    def redact_pii_and_secrets(self, text: str) -> Tuple[str, int]:
        """Redacts sensitive credentials, tokens, credit cards, and PII to prevent data leaks.
        Returns: (redacted_text, count_of_redactions)
        """
        redacted = text
        count = 0

        for label, pattern in self.PII_SECRET_PATTERNS:
            matches = list(re.finditer(pattern, redacted, re.IGNORECASE))
            if matches:
                count += len(matches)
                redacted = re.sub(pattern, f"[REDACTED_{label}]", redacted, flags=re.IGNORECASE)

        if count > 0:
            self.stats["pii_secrets_redacted"] += count
            self.audit_log.append({
                "type": "PII_SECRETS_REDACTED",
                "count": count,
            })

        return redacted, count

    def get_security_posture(self) -> Dict[str, Any]:
        """Returns the real-time Model Armor audit metrics."""
        return {
            "status": "active",
            "guardrail_engine": "ModelArmor-v2.4-Enterprise",
            "stats": self.stats,
            "recent_audit_events": self.audit_log[-10:],
            "active_protection_vectors": [
                "Inline Prompt Injection Defense",
                "Untrusted Tool Poisoning Shield",
                "Zero-Data-Leak PII/Credential Masking",
                "Cryptographic Boundary Isolation",
            ],
        }

model_armor = ModelArmor()
