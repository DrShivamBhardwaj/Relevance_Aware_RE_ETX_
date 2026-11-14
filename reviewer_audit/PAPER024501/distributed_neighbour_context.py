"""Optional 100-node *received-observation* scenario for reviewer M1.

The original implementation centrally reads all current neighbours without
messages. In this separate scenario each alive sender disseminates one
observation to alive neighbours within 20 m. Each receiving node stores only
successfully received observations, and uses its last received sample after a
miss. Packet TX and listening RX energy (including failed receptions) are
charged to actual node batteries. Synchronous packet scheduling, independent
per-neighbour erasures and an assumed packet energy model remain idealised.

This is not the original algorithm and is not paper-equivalent M3 firmware.
"""
import numpy as np

class ReceivedNeighbourContext:
    def __init__(self, config, topology, *, context_bytes=25,
                 success_probability=1.0, radius=20.0):
        self.n=int(config.num_nodes)
        self.matrix=np.full((self.n,self.n), np.nan, dtype=np.float64)
        self.last_round=np.full((self.n,self.n),-1,dtype=np.int64)
        self.dist=np.asarray(topology.distance_matrix)
        self.neighbours=(self.dist<=radius)
        np.fill_diagonal(self.neighbours,False)
        self.rng=np.random.default_rng(int(config.seed)+834001)
        self.context_bytes=int(context_bytes)
        self.frame_bits=int(context_bytes)*8+int(config.mac_overhead_bits)
        self.success_probability=float(success_probability)
        if not (2<=self.context_bytes<=80):
            raise ValueError("context_bytes must be 2..80")
        if not (0<=self.success_probability<=1):
            raise ValueError("success_probability must be 0..1")
        self.sent=0
        self.rx_attempts=0
        self.received=0
        self.e_control=0.0
        self.stale_age_sum=0.0
        self.stale_age_count=0

    def advance(self, observations, network, radio, round_id):
        observations=np.asarray(observations,dtype=float)
        if len(observations)!=self.n:
            raise ValueError("wrong number of observations")
        for i in range(self.n):
            if not network.alive[i]:
                self.matrix[:,i]=np.nan
                self.last_round[:,i]=-1
        ids=np.flatnonzero(network.alive)
        # Broadcast-based access: each sender spends a single TX energy cost
        # at the furthest current neighbour, regardless of who decodes.
        for src in ids:
            src=int(src)
            if not network.alive[src]:continue
            receivers=np.flatnonzero(self.neighbours[src]&network.alive)
            if not len(receivers):continue
            d=float(np.max(self.dist[src,receivers]))
            before=network.total_residual_energy
            network.consume_energy([src],float(radio.tx_energy(self.frame_bits,d)),round_id)
            self.e_control += before-network.total_residual_energy
            self.sent+=1
            # Those receivers listen whether or not frame CRC passes.
            for rec in receivers:
                rec=int(rec)
                if not network.alive[rec]:continue
                before=network.total_residual_energy
                network.consume_energy([rec],float(radio.rx_energy(self.frame_bits)),round_id)
                self.e_control += before-network.total_residual_energy
                self.rx_attempts+=1
                if self.rng.random()<self.success_probability:
                    self.matrix[rec,src]=observations[src]
                    self.last_round[rec,src]=round_id
                    self.received+=1
        valid=(self.last_round>=0)&self.neighbours
        if valid.any():
            ages=np.maximum(0,round_id-self.last_round[valid])
            self.stale_age_sum+=float(np.sum(ages))
            self.stale_age_count+=len(ages)
        return self.matrix.copy()

    def results(self):
        return {"context_packets_sent":self.sent,
                "context_receive_attempts":self.rx_attempts,
                "context_updates_received":self.received,
                "context_rx_fraction":self.received/self.rx_attempts if self.rx_attempts else 0,
                "mean_cached_context_age_rounds":
                    self.stale_age_sum/self.stale_age_count if self.stale_age_count else 0,
                "total_context_battery_energy_J":self.e_control}
