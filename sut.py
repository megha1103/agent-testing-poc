"""System under test: the avatar. Pluggable so we can use a mock or a real API."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Sequence

@dataclass
class Turn:
    role: str  # "user" | "assistant"
    content: str

class AvatarSUT(ABC):
    """Interface for the video avatar (system under test)."""

    @abstractmethod
    def respond(self, conversation: Sequence[Turn]) -> str:
        """Return the avatar's next response given the conversation so far."""
        pass

    def reset(self) -> None:
        """Optional: reset any internal state for a new scenario."""
        pass


class MockAvatarSUT(AvatarSUT):
    """Mock avatar for POC: returns persona-appropriate canned responses."""

    def __init__(self, persona: str = "doctor"):
        self.persona = persona
        self._turn_count = 0

    def respond(self, conversation: Sequence[Turn]) -> str:
        self._turn_count += 1
        last_user = next((t.content for t in reversed(conversation) if t.role == "user"), "")
        if not last_user:
            return "Hello. How can I help you today?"

        low = last_user.lower()
        if "guarantee" in low or "promise" in low or "certain" in low:
            return (
                "I cannot guarantee outcomes. Treatment and results depend on many factors. "
                "I recommend following evidence-based guidelines and discussing with the patient."
            )
        if "?" in last_user and ("what" in low or "unknown" in low or "fake" in low):
            return (
                "I am not sure about that specific product or claim. "
                "Could you clarify or provide more context so I can give an accurate response?"
            )
        if "frustrat" in low or "not convinced" in low or "does not make sense" in low:
            return (
                "I understand your concern. Let me put it another way: "
                "we need to base decisions on clinical evidence and patient need. "
                "Is there a particular aspect you would like me to clarify?"
            )
        if self.persona == "doctor":
            return (
                "As a physician, I consider efficacy, safety, and guidelines when making decisions. "
                "I am happy to discuss the evidence for this product within those bounds."
            )
        return (
            "At my age I pay close attention to safety and value. "
            "I need to think it over and maybe discuss with my family before deciding."
        )

    def reset(self) -> None:
        self._turn_count = 0


class OpenAIAvatarSUT(AvatarSUT):
    """Avatar implemented via OpenAI (optional). Uses config avatar context as system message."""

    def __init__(self, api_key: str, system_prompt: str, model: str = "gpt-4o-mini"):
        import openai
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.system_prompt = system_prompt

    def respond(self, conversation: Sequence[Turn]) -> str:
        messages = [{"role": "system", "content": self.system_prompt}]
        for t in conversation:
            messages.append({"role": t.role, "content": t.content})
        r = self.client.chat.completions.create(model=self.model, messages=messages)
        return r.choices[0].message.content or ""
