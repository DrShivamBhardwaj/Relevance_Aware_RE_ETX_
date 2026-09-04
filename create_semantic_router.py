from pathlib import Path

src = Path("simulator/routing_re_etx.py")
dst = Path("simulator/routing_semantic_re_etx.py")

text = src.read_text()

text = text.replace(
    "class ResidualEnergyETXRouter:",
    "class SemanticResidualEnergyETXRouter:"
)

text = text.replace(
    "energy_weight=1.0,\n        epsilon=1e-12",
    "energy_weight=1.0,\n        semantic_weight=1.0,\n        semantic_age=None,\n        epsilon=1e-12"
)

text = text.replace(
    """self.energy_weight = float(
            energy_weight
        )""",
    """self.energy_weight = float(
            energy_weight
        )

        self.semantic_weight = float(
            semantic_weight
        )"""
)

text = text.replace(
    """self.initial_energy = float(
            initial_energy
        )""",
    """self.initial_energy = float(
            initial_energy
        )

        if semantic_age is None:
            self.semantic_age = np.zeros(
                self.num_nodes,
                dtype=np.float64
            )
        else:
            self.semantic_age = np.asarray(
                semantic_age,
                dtype=np.float64
            ).copy()

        if self.semantic_age.shape != (self.num_nodes,):
            raise ValueError(
                "semantic_age vector has invalid shape."
            )"""
)

old = """scarcity = (
            self.energy_scarcity[i]
            +
            self.energy_scarcity[j]
        ) / 2.0"""

new = """scarcity = (
            self.energy_scarcity[i]
            +
            self.energy_scarcity[j]
        ) / 2.0

        semantic = (
            self.semantic_age[i]
            +
            self.semantic_age[j]
        ) / 2.0"""

text = text.replace(old, new)

text = text.replace(
    """self.energy_weight
                *
                scarcity""",
    """self.energy_weight
                *
                scarcity
                +
                self.semantic_weight
                *
                semantic"""
)

dst.write_text(text)

print("Semantic RE-ETX router created")
