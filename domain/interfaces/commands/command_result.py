from dataclasses import dataclass, field
from domain.enums.command_status import CommandStatus
from typing import Any, Dict


@dataclass
class CommandResult:
    """Command return value after execution."""
    success: bool
    status: CommandStatus
    message: str
    duration_ms: float = 0.0
    extra: Dict[str, Any] = field(default_factory=dict)
