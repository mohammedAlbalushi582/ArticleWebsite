from abc import ABC, abstractmethod
from typing import TypedDict


class AnalysisResult(TypedDict):
    title: str
    summary: str
    key_points: list[str]
    tags: list[str]


class Analyzer(ABC):
    @abstractmethod
    def analyze(self, text: str) -> AnalysisResult:
        """Analyze article text and return structured results."""
        ...

    @abstractmethod
    def chat(self, system_prompt: str, messages: list[dict]) -> str:
        """Send a chat message with article context and return the assistant reply."""
        ...
