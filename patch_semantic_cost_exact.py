from pathlib import Path

p = Path("simulator/routing_semantic_re_etx.py")
text = p.read_text()

old_sensor = """        scarcity = (
            self.energy_scarcity[i]
            + self.energy_scarcity[j]
        ) / 2.0
        return (
            base_etx
            * (
                1.0
                + self.energy_weight
                * scarcity
            )
        )"""

new_sensor = """        scarcity = (
            self.energy_scarcity[i]
            + self.energy_scarcity[j]
        ) / 2.0

        semantic = (
            self.semantic_age[i]
            + self.semantic_age[j]
        ) / 2.0

        return (
            base_etx
            * (
                1.0
                + self.energy_weight
                * scarcity
                + self.semantic_weight
                * semantic
            )
        )"""

if old_sensor not in text:
    raise RuntimeError("Sensor cost block not found")

text = text.replace(old_sensor, new_sensor)


old_sink = """        scarcity = (
            self.energy_scarcity[i]
            / 2.0
        )
        return (
            base_etx
            * (
                1.0
                + self.energy_weight
                * scarcity
            )
        )"""

new_sink = """        scarcity = (
            self.energy_scarcity[i]
            / 2.0
        )

        semantic = self.semantic_age[i]

        return (
            base_etx
            * (
                1.0
                + self.energy_weight
                * scarcity
                + self.semantic_weight
                * semantic
            )
        )"""

if old_sink not in text:
    raise RuntimeError("Sink cost block not found")

text = text.replace(old_sink, new_sink)

p.write_text(text)

print("Semantic routing cost inserted")
