import numpy as np


class SemanticAgeTracker:
    """
    Slotted information-age tracker.

    Age=1 means the sink successfully received the
    previous round's source update.

    Semantic age:
        SA_i(t) = relevance_i(t) * age_i(t)
    """

    def __init__(
        self,
        num_nodes
    ):
        self.num_nodes = int(
            num_nodes
        )

        self.age = np.ones(
            self.num_nodes,
            dtype=np.int64
        )

    def semantic_age(
        self,
        relevance
    ):
        relevance = np.asarray(
            relevance,
            dtype=np.float64
        )

        if (
            relevance.shape
            != (self.num_nodes,)
        ):
            raise ValueError(
                "Invalid relevance vector shape."
            )

        return (
            relevance
            * self.age
        )

    def update(
        self,
        delivered_mask
    ):
        delivered_mask = np.asarray(
            delivered_mask,
            dtype=bool
        )

        if (
            delivered_mask.shape
            != (self.num_nodes,)
        ):
            raise ValueError(
                "Invalid delivery mask shape."
            )

        self.age += 1

        self.age[
            delivered_mask
        ] = 1

    def reset(self):
        self.age.fill(
            1
        )
