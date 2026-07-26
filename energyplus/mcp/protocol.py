from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class ToolCall:

    tool: str

    arguments: Dict[str, Any]


@dataclass
class ToolResult:

    success: bool

    data: Any

    message: str = ""


@dataclass
class AgentResponse:

    reasoning: str

    confidence: float

    tool_call: ToolCall | None = None

    final_action: float | None = None