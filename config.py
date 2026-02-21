"""Configuration for the agent-based testing POC."""
import os
from dataclasses import dataclass, field

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass
class Config:
    """Runtime config: persona, API, and scenario selection."""
    persona: str = "doctor"  # "doctor" | "senior_customer"
    api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    use_mock: bool = field(default_factory=lambda: not bool(os.getenv("OPENAI_API_KEY")))
    max_turns_per_scenario: int = 5
    report_dir: str = "reports"
    scenarios: list[str] = field(default_factory=lambda: [
        "persona",
        "hallucination",
        "emotional",
        "safety",
        "long_conversation",
    ])

    def avatar_context(self) -> str:
        if self.persona == "doctor":
            return (
                "You are a doctor in a medical sales training scenario. "
                "You interact with Medical Representatives (MRs) discussing Glenmark medicines. "
                "Stay professional, medically accurate, and ethically compliant."
            )
        return (
            "You are a 70-year-old male customer in a Tata Motors sales scenario. "
            "You show safety concerns, pricing sensitivity, and some hesitation. "
            "Behave like a realistic senior customer."
        )
