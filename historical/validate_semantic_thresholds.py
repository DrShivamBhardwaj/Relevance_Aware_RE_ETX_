import numpy as np

from config import SimulationConfig
from simulator.topology import Topology
from simulator.sensing import CorrelatedSensingField
from simulator.semantic_relevance import SemanticRelevanceEstimator


def metrics_at_threshold(
    scores,
    labels,
    threshold
):
    prediction = (
        scores >= threshold
    )

    positive = (
        labels == 1
    )

    negative = (
        labels == 0
    )

    tp = int(
        np.sum(
            prediction
            & positive
        )
    )

    fp = int(
        np.sum(
            prediction
            & negative
        )
    )

    fn = int(
        np.sum(
            (~prediction)
            & positive
        )
    )

    tn = int(
        np.sum(
            (~prediction)
            & negative
        )
    )

    precision = (
        tp / (tp + fp)
        if (tp + fp) > 0
        else 0.0
    )

    recall = (
        tp / (tp + fn)
        if (tp + fn) > 0
        else 0.0
    )

    specificity = (
        tn / (tn + fp)
        if (tn + fp) > 0
        else 0.0
    )

    if (
        precision + recall
        > 0
    ):
        f1 = (
            2.0
            * precision
            * recall
            / (
                precision
                + recall
            )
        )
    else:
        f1 = 0.0

    return {
        "threshold": threshold,
        "precision": precision,
        "recall": recall,
        "specificity": specificity,
        "f1": f1,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn
    }


def main():
    config = SimulationConfig()

    topology = Topology(
        config
    )

    field = CorrelatedSensingField(
        config,
        topology
    )

    estimator = SemanticRelevanceEstimator(
        topology,
        warmup_rounds=50
    )

    scores = []
    labels = []

    for _ in range(3000):
        current = field.step()

        result = estimator.compute(
            current,
            field.previous_observation
        )

        if not result[
            "baseline_ready"
        ]:
            continue

        relevance = (
            result["relevance"]
        )

        truth = field.event_truth(
            threshold=0.5
        )

        scores.extend(
            relevance.tolist()
        )

        labels.extend(
            truth.astype(
                np.int64
            ).tolist()
        )

    scores = np.asarray(
        scores,
        dtype=np.float64
    )

    labels = np.asarray(
        labels,
        dtype=np.int64
    )

    positives = int(
        np.sum(
            labels == 1
        )
    )

    negatives = int(
        np.sum(
            labels == 0
        )
    )

    prevalence = (
        positives
        / (
            positives
            + negatives
        )
    )

    thresholds = np.arange(
        0.10,
        0.91,
        0.05
    )

    results = [
        metrics_at_threshold(
            scores,
            labels,
            float(t)
        )
        for t in thresholds
    ]

    best_f1 = max(
        results,
        key=lambda x: x["f1"]
    )

    # Best precision while maintaining
    # at least 80% recall.
    high_recall = [
        r
        for r in results
        if r["recall"] >= 0.80
    ]

    if high_recall:
        best_recall80 = max(
            high_recall,
            key=lambda x: x["precision"]
        )
    else:
        best_recall80 = None

    print("=" * 90)
    print("SEMANTIC OPERATING-THRESHOLD CALIBRATION")
    print("=" * 90)

    print(
        f"Positive samples     : "
        f"{positives}"
    )

    print(
        f"Negative samples     : "
        f"{negatives}"
    )

    print(
        f"Event-node prevalence: "
        f"{prevalence * 100:.3f}%"
    )

    print()

    print(
        f"{'Threshold':>10} "
        f"{'Precision':>11} "
        f"{'Recall':>10} "
        f"{'Specificity':>12} "
        f"{'F1':>10}"
    )

    print("-" * 60)

    for r in results:
        print(
            f"{r['threshold']:10.2f} "
            f"{r['precision']:11.4f} "
            f"{r['recall']:10.4f} "
            f"{r['specificity']:12.4f} "
            f"{r['f1']:10.4f}"
        )

    print()
    print("Best F1 operating point")
    print("-" * 60)

    print(
        f"Threshold : "
        f"{best_f1['threshold']:.2f}"
    )

    print(
        f"Precision : "
        f"{best_f1['precision']:.4f}"
    )

    print(
        f"Recall    : "
        f"{best_f1['recall']:.4f}"
    )

    print(
        f"F1        : "
        f"{best_f1['f1']:.4f}"
    )

    if best_recall80 is not None:
        print()
        print(
            "Best precision subject to recall >= 0.80"
        )

        print("-" * 60)

        print(
            f"Threshold : "
            f"{best_recall80['threshold']:.2f}"
        )

        print(
            f"Precision : "
            f"{best_recall80['precision']:.4f}"
        )

        print(
            f"Recall    : "
            f"{best_recall80['recall']:.4f}"
        )

        print(
            f"F1        : "
            f"{best_recall80['f1']:.4f}"
        )

    print()
    print(
        "Semantic threshold calibration PASSED."
    )


if __name__ == "__main__":
    main()
