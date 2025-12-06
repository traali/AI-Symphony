"""
Cost Tracking Module for AI Symphony

Tracks OpenRouter API costs and provides budget enforcement.
"""

import logging
import threading
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class CostTracker:
    """Tracks accumulated costs from LLM API calls.

    OpenRouter returns cost information in response headers:
    - x-openrouter-cost: Cost in USD for the request

    This tracker accumulates costs across all requests and can
    enforce budget limits.
    """

    budget_limit: float | None = None
    total_cost: float = 0.0
    request_count: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def add_cost(self, cost: float):
        """Add cost from a single request."""
        with self._lock:
            self.total_cost += cost
            self.request_count += 1

            logger.debug(f"Request cost: ${cost:.4f}, Total: ${self.total_cost:.4f}")

            if self.budget_limit and self.total_cost >= self.budget_limit:
                raise BudgetExceededError(
                    f"Budget limit of ${self.budget_limit:.2f} exceeded. "
                    f"Current total: ${self.total_cost:.4f}"
                )

    def get_summary(self) -> dict:
        """Get a summary of accumulated costs."""
        with self._lock:
            avg_cost = self.total_cost / self.request_count if self.request_count > 0 else 0
            return {
                "total_cost_usd": round(self.total_cost, 4),
                "request_count": self.request_count,
                "average_cost_per_request": round(avg_cost, 4),
                "budget_limit": self.budget_limit,
                "budget_remaining": (
                    round(self.budget_limit - self.total_cost, 4) if self.budget_limit else None
                ),
            }

    def format_summary(self) -> str:
        """Format cost summary as a human-readable string."""
        summary = self.get_summary()
        lines = [
            "💰 Cost Summary",
            f"   Total Cost: ${summary['total_cost_usd']:.4f}",
            f"   Requests: {summary['request_count']}",
            f"   Avg/Request: ${summary['average_cost_per_request']:.4f}",
        ]
        if summary["budget_limit"]:
            lines.append(f"   Budget Limit: ${summary['budget_limit']:.2f}")
            lines.append(f"   Budget Remaining: ${summary['budget_remaining']:.4f}")
        return "\n".join(lines)

    def reset(self):
        """Reset the cost tracker."""
        with self._lock:
            self.total_cost = 0.0
            self.request_count = 0


class BudgetExceededError(Exception):
    """Raised when the budget limit is exceeded."""

    pass


# Global cost tracker instance
_global_tracker: CostTracker | None = None


def get_cost_tracker() -> CostTracker:
    """Get or create the global cost tracker."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = CostTracker()
    return _global_tracker


def set_budget_limit(limit: float):
    """Set the budget limit for the global cost tracker."""
    tracker = get_cost_tracker()
    tracker.budget_limit = limit
    logger.info(f"Budget limit set to ${limit:.2f}")


def reset_cost_tracker():
    """Reset the global cost tracker."""
    global _global_tracker
    if _global_tracker:
        _global_tracker.reset()
