import numpy as np


class SemanticPayloadController:
    """
    Relevance-aware application payload adaptation.

    Base rule:
        rho = rho_min + (1-rho_min)*v

    Safeguards:
        v >= high-recall threshold
            -> at least high_recall_min_ratio

        v >= high-confidence threshold
            -> full payload

    The controller operates on semantic relevance only.
    It does not use oracle event labels.
    """

    def __init__(
        self,
        config
    ):
        self.full_payload_bits = int(
            config.packet_size
        )

        self.min_ratio = float(
            config.semantic_min_payload_ratio
        )

        self.high_recall_threshold = float(
            config.semantic_high_recall_threshold
        )

        self.high_confidence_threshold = float(
            config.semantic_high_confidence_threshold
        )

        self.high_recall_min_ratio = float(
            config.semantic_high_recall_min_ratio
        )

        if not (
            0.0
            < self.min_ratio
            <= 1.0
        ):
            raise ValueError(
                "Invalid minimum payload ratio."
            )

    def payload_ratio(
        self,
        relevance
    ):
        relevance = np.asarray(
            relevance,
            dtype=np.float64
        )

        relevance = np.clip(
            relevance,
            0.0,
            1.0
        )

        ratio = (
            self.min_ratio
            + (
                1.0
                - self.min_ratio
            )
            * relevance
        )

        high_recall = (
            relevance
            >= self.high_recall_threshold
        )

        ratio = np.where(
            high_recall,
            np.maximum(
                ratio,
                self.high_recall_min_ratio
            ),
            ratio
        )

        high_confidence = (
            relevance
            >= self.high_confidence_threshold
        )

        ratio = np.where(
            high_confidence,
            1.0,
            ratio
        )

        return np.clip(
            ratio,
            self.min_ratio,
            1.0
        )

    def payload_bits(
        self,
        relevance
    ):
        ratio = self.payload_ratio(
            relevance
        )

        bits = np.ceil(
            ratio
            * self.full_payload_bits
        ).astype(
            np.int64
        )

        # Byte-align application payload.
        bits = (
            (
                bits + 7
            )
            // 8
        ) * 8

        bits = np.clip(
            bits,
            8,
            self.full_payload_bits
        )

        return bits
