from dataclasses import dataclass
from enum import Enum, auto


class Phase(Enum):
    WORK = auto()
    BREAK = auto()


class PhaseAction(Enum):
    CONTINUE = auto()
    NEXT = auto()
    RESET_SESSION = auto()


@dataclass
class SessionStats:
    completed_cycles: int
    total_cycles: int

    @property
    def total_cycles_label(self) -> str:
        return "∞" if self.total_cycles == 0 else str(self.total_cycles)

    @property
    def remaining_cycles_label(self) -> str:
        if self.total_cycles == 0:
            return "∞"
        remaining = max(0, self.total_cycles - self.completed_cycles)
        return str(remaining)

    @property
    def progress_percent(self) -> str:
        if self.total_cycles == 0:
            return "∞"
        progress = (self.completed_cycles / self.total_cycles) * 100
        return f"{progress:.0f}%"

    @property
    def current_cycle_label(self) -> str:
        current_cycle = self.completed_cycles + 1
        if self.total_cycles == 0:
            return f"{current_cycle}/∞"
        return f"{min(current_cycle, self.total_cycles)}/{self.total_cycles}"
