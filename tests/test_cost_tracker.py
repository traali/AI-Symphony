"""
Tests for the cost tracking module.
"""

import pytest

from src.cost_tracker import (
    BudgetExceededError,
    CostTracker,
    get_cost_tracker,
    reset_cost_tracker,
    set_budget_limit,
)


class TestCostTracker:
    """Tests for CostTracker class."""

    def test_add_cost_accumulates(self):
        """Test that costs are accumulated correctly."""
        tracker = CostTracker()
        tracker.add_cost(0.001)
        tracker.add_cost(0.002)
        tracker.add_cost(0.003)

        assert tracker.total_cost == pytest.approx(0.006)
        assert tracker.request_count == 3

    def test_get_summary_returns_correct_data(self):
        """Test that summary contains correct information."""
        tracker = CostTracker(budget_limit=1.0)
        tracker.add_cost(0.25)

        summary = tracker.get_summary()

        assert summary["total_cost_usd"] == 0.25
        assert summary["request_count"] == 1
        assert summary["budget_limit"] == 1.0
        assert summary["budget_remaining"] == 0.75

    def test_budget_exceeded_raises_error(self):
        """Test that exceeding budget raises BudgetExceededError."""
        tracker = CostTracker(budget_limit=0.10)
        tracker.add_cost(0.05)

        with pytest.raises(BudgetExceededError):
            tracker.add_cost(0.06)  # This exceeds the $0.10 budget

    def test_reset_clears_tracker(self):
        """Test that reset clears all accumulated data."""
        tracker = CostTracker()
        tracker.add_cost(0.50)
        tracker.reset()

        assert tracker.total_cost == 0.0
        assert tracker.request_count == 0

    def test_format_summary_returns_string(self):
        """Test that format_summary returns a formatted string."""
        tracker = CostTracker()
        tracker.add_cost(0.123)

        summary = tracker.format_summary()

        assert "Cost Summary" in summary
        assert "$0.123" in summary
        assert "1" in summary


class TestGlobalTrackerFunctions:
    """Tests for global tracker functions."""

    def test_get_cost_tracker_returns_singleton(self):
        """Test that get_cost_tracker returns the same instance."""
        tracker1 = get_cost_tracker()
        tracker2 = get_cost_tracker()

        assert tracker1 is tracker2

    def test_set_budget_limit_updates_tracker(self):
        """Test that set_budget_limit updates the global tracker."""
        reset_cost_tracker()
        set_budget_limit(5.0)

        tracker = get_cost_tracker()
        assert tracker.budget_limit == 5.0

    def test_reset_cost_tracker_clears_data(self):
        """Test that reset_cost_tracker clears accumulated data."""
        tracker = get_cost_tracker()
        tracker.add_cost(1.0)

        reset_cost_tracker()

        assert tracker.total_cost == 0.0
