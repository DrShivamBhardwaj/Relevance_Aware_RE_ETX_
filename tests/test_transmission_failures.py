import unittest
from types import SimpleNamespace
from simulator.multihop_transmission import MultiHopTransmitter

class TransmissionFailureTests(unittest.TestCase):
    def test_absent_route_has_zero_physical_work(self):
        tx = MultiHopTransmitter.__new__(MultiHopTransmitter)
        result = tx.transmit(None, None, round_id=1, app_bits=4000)
        self.assertFalse(result.success)
        self.assertEqual(result.drop_reason, 'route')
        self.assertEqual((result.radio_bits, result.frame_attempts, result.airtime), (0, 0, 0))
    def test_dead_sender_does_not_transmit(self):
        tx = MultiHopTransmitter.__new__(MultiHopTransmitter)
        tx.sink_id = 1
        net = SimpleNamespace(alive=[False])
        result = tx.transmit(net, [0, 1], round_id=1, app_bits=1000)
        self.assertFalse(result.success)
        self.assertEqual(result.drop_reason, 'energy')
        self.assertEqual(result.radio_bits, 0)


class FakeNetwork:
    def __init__(self, energy):
        self.energy=list(energy);self.alive=[True]*len(energy);self.energy_epsilon=1e-12
    def consume_energy(self,nodes,costs,round_id):
        for i,cost in zip(nodes,costs):
            if cost<0 or cost>self.energy[i]+1e-12:raise AssertionError('Energy ledger overflow')
            self.energy[i]=max(0,self.energy[i]-cost)
            self.alive[i]=self.energy[i]>1e-12

class DepletionAndRetryTests(unittest.TestCase):
    def make_transmitter(self, success):
        from simulator.frame import FrameModel
        cfg=SimpleNamespace(packet_size=16,mac_payload_bits=8,mac_overhead_bits=0,
                            max_retries=1,bit_rate=8000.,propagation_speed=3e8,processing_delay=.001)
        radio=SimpleNamespace(tx_energy=lambda n,d:n*.001,rx_energy=lambda n:n*.0005)
        channel=SimpleNamespace(attempt_frame=lambda n,snr:success)
        tx=MultiHopTransmitter(cfg,radio,channel,FrameModel(cfg),SimpleNamespace(sink_id=2))
        tx._link_state=lambda a,b:(1.,30.)
        return tx
    def test_partial_sender_exhaustion_preserves_energy(self):
        net=FakeNetwork([.003,1.]);r=self.make_transmitter(True).transmit(net,[0,2],1,16)
        self.assertEqual(r.drop_reason,'energy');self.assertAlmostEqual(r.tx_energy,.003)
        self.assertAlmostEqual(net.energy[0],0);self.assertLess(r.airtime,.001)
    def test_receiver_exhaustion_is_not_a_success(self):
        net=FakeNetwork([1.,.001]);r=self.make_transmitter(True).transmit(net,[0,1,2],1,16)
        self.assertFalse(r.success);self.assertEqual(r.drop_reason,'energy')
        self.assertAlmostEqual(r.rx_energy,.001);self.assertAlmostEqual(r.tx_energy,.008)
    def test_frame_retry_cap_stops_failed_report(self):
        net=FakeNetwork([1.,1.]);r=self.make_transmitter(False).transmit(net,[0,2],1,16)
        self.assertEqual(r.drop_reason,'channel');self.assertEqual(r.frame_attempts,2)
        self.assertEqual(r.retransmissions,1);self.assertAlmostEqual(r.tx_energy,.016)

if __name__ == '__main__': unittest.main()
