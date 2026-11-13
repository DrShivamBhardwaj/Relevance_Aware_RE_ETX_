"""Scenario-specific energy ledger with explicit, UNCALIBRATED power values.

Not a source of hardware measurements. Adds energy to node state before source
transmissions and after each report for approximated ACK handling.
"""
import os
import numpy as np

class ExtendedEnergyProfile:
    def __init__(self, cfg, radio, topology):
        self.radio = radio
        self.topology = topology
        self.sense_j = float(os.environ.get("REVIEW_SENSING_UJ", "0"))*1e-6
        self.cpu_j = float(os.environ.get("REVIEW_CPU_UJ", "0"))*1e-6
        self.idle_j = float(os.environ.get("REVIEW_IDLE_UJ", "0"))*1e-6
        self.context_bits = int(os.environ.get("REVIEW_CONTEXT_BITS", "0"))
        self.routing_bits = int(os.environ.get("REVIEW_ROUTING_BITS", "0"))
        self.ack_bits = int(os.environ.get("REVIEW_ACK_BITS", "0"))
        self.radius = float(os.environ.get("REVIEW_GOSSIP_RADIUS_M", "20"))
        assert min(self.sense_j,self.cpu_j,self.idle_j,self.context_bits,self.routing_bits,self.ack_bits)>=0
        assert self.radius > 0
        self.e_sense=0.
        self.e_cpu=0.
        self.e_idle=0.
        self.e_control=0.
        self.e_ack=0.

    def round_cost(self, network, round_id):
        ids=np.flatnonzero(network.alive)
        if not len(ids):return
        for component,amount,counter in [
            ("sense",self.sense_j,"e_sense"),
            ("cpu",self.cpu_j,"e_cpu"),
            ("idle",self.idle_j,"e_idle")]:
            if amount:
                before=network.total_residual_energy
                network.consume_energy(ids,amount,round_id)
                setattr(self,counter,getattr(self,counter)+before-network.total_residual_energy)
        # Node disseminates a control message to ALL physical neighbours;
        # per-round pairwise reception is charged separately.
        for bits in (self.context_bits,self.routing_bits):
            if not bits:continue
            for i in ids:
                i=int(i)
                if not network.alive[i]:continue
                neighbours=np.flatnonzero(
                    (self.topology.distance_matrix[i] <= self.radius)
                    & network.alive
                )
                neighbours=neighbours[neighbours!=i]
                if not len(neighbours):continue
                d=float(np.max(self.topology.distance_matrix[i,neighbours]))
                before=network.total_residual_energy
                network.consume_energy([i],float(self.radio.tx_energy(bits,d)),round_id)
                for j in neighbours:
                    if network.alive[j]:
                        network.consume_energy([int(j)],float(self.radio.rx_energy(bits)),round_id)
                self.e_control+=before-network.total_residual_energy

    def ack_cost(self,network,path,frame_attempts,round_id):
        if not self.ack_bits or not frame_attempts or not path:return
        hops=max(len(path)-1,1)
        # Total frame attempts allocated evenly among the route hops.
        # This is a conservative aggregate proxy; no ACK MAC timing/retry.
        attempts=float(frame_attempts)/hops
        for a,b in zip(path[:-1],path[1:]):
            a,b=int(a),int(b)
            if a>=network.num_nodes or not network.alive[a]:continue
            before=network.total_residual_energy
            # Sensor sends its own ACK? Actual ACK comes from receiver, and
            # is RX at sender; charge receiver TX only if battery powered.
            network.consume_energy([a],attempts*float(self.radio.rx_energy(self.ack_bits)),round_id)
            if b<network.num_nodes and network.alive[b]:
                distance=float(self.topology.distance_matrix[a,b])
                network.consume_energy([b],attempts*float(self.radio.tx_energy(self.ack_bits,distance)),round_id)
            self.e_ack+=before-network.total_residual_energy
