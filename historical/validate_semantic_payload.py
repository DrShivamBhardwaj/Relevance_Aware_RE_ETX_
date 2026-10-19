import numpy as np

from config import SimulationConfig
from simulator.topology import Topology
from simulator.frame import FrameModel
from simulator.sensing import CorrelatedSensingField
from simulator.semantic_relevance import (
    SemanticRelevanceEstimator
)
from simulator.semantic_payload import (
    SemanticPayloadController
)


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

    payload = SemanticPayloadController(
        config
    )

    frame = FrameModel(
        config
    )

    event_payloads = []
    non_event_payloads = []

    event_ratios = []
    non_event_ratios = []

    total_application_bits = 0
    total_radio_bits = 0

    full_application_bits = 0
    full_radio_bits = 0

    high_confidence_count = 0
    high_confidence_full_count = 0

    previous_relevance = -1.0
    previous_ratio = -1.0

    monotonic_pairs = []

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

        ratios = (
            payload.payload_ratio(
                relevance
            )
        )

        bits = (
            payload.payload_bits(
                relevance
            )
        )

        truth = field.event_truth(
            threshold=0.5
        )

        if np.any(truth):
            event_payloads.extend(
                bits[
                    truth
                ].tolist()
            )

            event_ratios.extend(
                ratios[
                    truth
                ].tolist()
            )

        if np.any(~truth):
            non_event_payloads.extend(
                bits[
                    ~truth
                ].tolist()
            )

            non_event_ratios.extend(
                ratios[
                    ~truth
                ].tolist()
            )

        for node_bits in bits:
            total_application_bits += int(
                node_bits
            )

            total_radio_bits += (
                frame.radio_bits(
                    int(node_bits)
                )
            )

            full_application_bits += (
                config.packet_size
            )

            full_radio_bits += (
                frame.radio_bits(
                    config.packet_size
                )
            )

        high_confidence = (
            relevance
            >= config.semantic_high_confidence_threshold
        )

        high_confidence_count += int(
            np.sum(
                high_confidence
            )
        )

        high_confidence_full_count += int(
            np.sum(
                bits[
                    high_confidence
                ]
                == config.packet_size
            )
        )

        # --------------------------------------
        # Direct monotonicity validation
        # --------------------------------------

        order = np.argsort(
            relevance
        )

        sorted_relevance = relevance[
            order
        ]

        sorted_ratio = ratios[
            order
        ]

        monotonic_pairs.append(
            np.all(
                np.diff(
                    sorted_ratio
                )
                >= -1e-12
            )
        )

    application_saving = (
        1.0
        - total_application_bits
        / full_application_bits
    )

    radio_saving = (
        1.0
        - total_radio_bits
        / full_radio_bits
    )

    print("=" * 82)
    print("SEMANTIC PAYLOAD ADAPTATION VALIDATION")
    print("=" * 82)

    print(
        f"Event-node mean payload      : "
        f"{np.mean(event_payloads):.2f} bits"
    )

    print(
        f"Non-event mean payload       : "
        f"{np.mean(non_event_payloads):.2f} bits"
    )

    print(
        f"Event-node mean ratio        : "
        f"{np.mean(event_ratios):.4f}"
    )

    print(
        f"Non-event mean ratio         : "
        f"{np.mean(non_event_ratios):.4f}"
    )

    print(
        f"Full-data application bits   : "
        f"{full_application_bits}"
    )

    print(
        f"Semantic application bits    : "
        f"{total_application_bits}"
    )

    print(
        f"Application-bit reduction    : "
        f"{application_saving * 100:.3f}%"
    )

    print(
        f"Full-data radio bits         : "
        f"{full_radio_bits}"
    )

    print(
        f"Semantic radio bits          : "
        f"{total_radio_bits}"
    )

    print(
        f"Radio-bit reduction          : "
        f"{radio_saving * 100:.3f}%"
    )

    print(
        f"High-confidence samples      : "
        f"{high_confidence_count}"
    )

    print(
        f"High-confidence full payload : "
        f"{high_confidence_full_count}"
    )

    print(
        f"Monotonic rounds             : "
        f"{sum(monotonic_pairs)}/"
        f"{len(monotonic_pairs)}"
    )

    assert (
        np.mean(
            event_payloads
        )
        >
        np.mean(
            non_event_payloads
        )
    )

    assert (
        total_application_bits
        < full_application_bits
    )

    assert (
        total_radio_bits
        < full_radio_bits
    )

    assert (
        high_confidence_count
        == high_confidence_full_count
    )

    assert all(
        monotonic_pairs
    )

    print()
    print(
        "Semantic payload adaptation PASSED."
    )


if __name__ == "__main__":
    main()
