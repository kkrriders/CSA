"""
A/B testing experiment routes.
"""
from fastapi import APIRouter, Depends
from bson import ObjectId
import hashlib

from app.core.database import get_database
from app.core.security import get_current_user_id
from app.models.experiment import Experiment, ExperimentMetric

router = APIRouter()


@router.post("/")
async def create_experiment(
    experiment: Experiment,
    db=Depends(get_database)
):
    """Create a new A/B test experiment."""
    result = await db.experiments.insert_one(experiment.dict())

    return {
        "experiment_id": str(result.inserted_id),
        "message": "Experiment created successfully"
    }


@router.get("/{experiment_id}/variant")
async def get_user_variant(
    experiment_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get the variant assigned to a user (consistent hashing)."""
    # Check if already assigned
    assignment = await db.experiment_assignments.find_one({
        "experiment_id": experiment_id,
        "user_id": user_id
    })

    if assignment:
        return {"variant_id": assignment["variant_id"]}

    # Get experiment
    experiment = await db.experiments.find_one({"_id": ObjectId(experiment_id)})
    if not experiment or not experiment.get("active"):
        return {"variant_id": None, "message": "Experiment not active"}

    # Assign variant using consistent hashing
    hash_input = f"{experiment_id}:{user_id}"
    hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
    variant_index = hash_value % len(experiment["variants"])
    variant = experiment["variants"][variant_index]

    # Store assignment
    await db.experiment_assignments.insert_one({
        "experiment_id": experiment_id,
        "user_id": user_id,
        "variant_id": variant["variant_id"]
    })

    return {"variant_id": variant["variant_id"]}


@router.post("/{experiment_id}/track")
async def track_metric(
    experiment_id: str,
    metric: ExperimentMetric,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Track a metric for an experiment."""
    metric.user_id = user_id
    metric.experiment_id = experiment_id

    await db.experiment_metrics.insert_one(metric.dict())

    return {"message": "Metric tracked"}


@router.get("/{experiment_id}/results")
async def get_experiment_results(
    experiment_id: str,
    db=Depends(get_database)
):
    """Get experiment results and analysis."""
    # Get all metrics
    cursor = db.experiment_metrics.find({"experiment_id": experiment_id})
    metrics = await cursor.to_list(length=100000)

    # Group by variant
    variant_stats = {}

    for metric in metrics:
        variant_id = metric["variant_id"]

        if variant_id not in variant_stats:
            variant_stats[variant_id] = {"values": [], "count": 0}

        variant_stats[variant_id]["values"].append(metric["metric_value"])
        variant_stats[variant_id]["count"] += 1

    # Calculate statistics
    results = {}
    for variant_id, stats in variant_stats.items():
        values = stats["values"]
        results[variant_id] = {
            "count": len(values),
            "mean": sum(values) / len(values) if values else 0,
            "min": min(values) if values else 0,
            "max": max(values) if values else 0
        }

    return {"experiment_id": experiment_id, "results": results}
