from pathlib import Path
import re

p = Path("simulator/routing_semantic_re_etx.py")
text = p.read_text()

sensor_pattern = r"""    def _sensor_link_cost\(.*?\n    def _sink_link_cost"""

sensor_replacement = """    def _sensor_link_cost(
        self,
        i,
        j
    ):
        base_etx = float(
            self.graph.sensor_etx[
                i,
                j
            ]
        )

        scarcity = (
            self.energy_scarcity[i]
            +
            self.energy_scarcity[j]
        ) / 2.0

        semantic = (
            self.semantic_age[i]
            +
            self.semantic_age[j]
        ) / 2.0

        return (
            base_etx
            *
            (
                1.0
                +
                self.energy_weight
                *
                scarcity
                +
                self.semantic_weight
                *
                semantic
            )
        )

    def _sink_link_cost"""

text_new, count = re.subn(
    sensor_pattern,
    sensor_replacement,
    text,
    flags=re.S
)

if count != 1:
    raise RuntimeError(
        f"Sensor function replacement failed: {count}"
    )

text = text_new


sink_pattern = r"""    def _sink_link_cost\(.*?\n    def _build_adjacency"""

sink_replacement = """    def _sink_link_cost(
        self,
        i
    ):
        base_etx = float(
            self.graph.bs_etx[i]
        )

        scarcity = (
            self.energy_scarcity[i]
            /
            2.0
        )

        semantic = self.semantic_age[i]

        return (
            base_etx
            *
            (
                1.0
                +
                self.energy_weight
                *
                scarcity
                +
                self.semantic_weight
                *
                semantic
            )
        )

    def _build_adjacency"""

text_new, count = re.subn(
    sink_pattern,
    sink_replacement,
    text,
    flags=re.S
)

if count != 1:
    raise RuntimeError(
        f"Sink function replacement failed: {count}"
    )

text = text_new

p.write_text(text)

print("Semantic cost functions replaced successfully")
