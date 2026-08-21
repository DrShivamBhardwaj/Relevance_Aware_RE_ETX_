class PerformanceMetrics:
    def __init__(self):
        self.generated_packets = 0
        self.attempted_packets = 0
        self.delivered_packets = 0

        self.energy_dropped_packets = 0
        self.channel_dropped_packets = 0
        self.route_dropped_packets = 0

        self.delivered_bits = 0
        self.total_delay = 0.0

        self.total_frame_attempts = 0
        self.total_retransmissions = 0
        self.failed_frame_attempts = 0

    def register_generated(
        self,
        count
    ):
        self.generated_packets += int(
            count
        )

    def register_attempted(
        self,
        count
    ):
        self.attempted_packets += int(
            count
        )

    def register_delivered(
        self,
        count,
        packet_size,
        delays
    ):
        count = int(count)

        self.delivered_packets += count

        self.delivered_bits += (
            count
            * int(packet_size)
        )

        if count > 0:
            self.total_delay += float(
                sum(delays)
            )

    def register_energy_drop(
        self,
        count
    ):
        self.energy_dropped_packets += int(
            count
        )

    def register_channel_drop(
        self,
        count
    ):
        self.channel_dropped_packets += int(
            count
        )

    def register_route_drop(
        self,
        count
    ):
        self.route_dropped_packets += int(
            count
        )

    def register_frame_stats(
        self,
        attempts,
        retransmissions,
        failed_attempts
    ):
        self.total_frame_attempts += int(
            attempts
        )

        self.total_retransmissions += int(
            retransmissions
        )

        self.failed_frame_attempts += int(
            failed_attempts
        )

    @property
    def pdr(self):
        if self.generated_packets == 0:
            return 0.0

        return (
            self.delivered_packets
            / self.generated_packets
        )

    @property
    def average_delay(self):
        if self.delivered_packets == 0:
            return 0.0

        return (
            self.total_delay
            / self.delivered_packets
        )

    def throughput(
        self,
        elapsed_time
    ):
        if elapsed_time <= 0:
            return 0.0

        return (
            self.delivered_bits
            / elapsed_time
        )
