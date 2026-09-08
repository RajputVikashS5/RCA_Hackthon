"""Offline, reproducible evaluation utilities for retrieval and RCA quality."""

from .runner import EvaluationCase, EvaluationReport, evaluate_cases

__all__ = ["EvaluationCase", "EvaluationReport", "evaluate_cases"]
