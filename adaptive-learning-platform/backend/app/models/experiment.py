"""
A/B testing experiment models.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Optional


class ExperimentVariant(BaseModel):
    """Variant in an A/B test."""
    variant_id: str
    name: str
    description: str
    weight: float = 0.5  # Traffic split


class Experiment(BaseModel):
    """A/B test experiment."""
    name: str
    description: str
    variants: List[ExperimentVariant]
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None


class ExperimentAssignment(BaseModel):
    """User assignment to experiment variant."""
    experiment_id: str
    user_id: str
    variant_id: str
    assigned_at: datetime = Field(default_factory=datetime.utcnow)


class ExperimentMetric(BaseModel):
    """Metric tracked for an experiment."""
    experiment_id: str
    variant_id: str
    user_id: str
    metric_name: str
    metric_value: float
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
