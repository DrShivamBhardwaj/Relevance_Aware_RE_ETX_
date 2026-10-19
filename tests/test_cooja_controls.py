from pathlib import Path
import sys
import unittest
import tempfile
import xml.etree.ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'validation/cooja'))
from run_suite import schedule_for,parse_log,make_config

class AllocationControlTests(unittest.TestCase):
    def records(self):
        return [dict(node=i,round=r,bits=16 if r<10 else [4,8,12,16][i-2],zt=(5-i)*10)
                for r in range(12) for i in range(2,6)]
    def test_permutation_preserves_each_round_and_warmup(self):
        original=self.records()
        for policy in ['shuffled','temporal_matched']:
            schedule=schedule_for(original,4,12,1001,policy)
            for r in range(12):
                self.assertEqual(sorted(schedule[r][2:]),sorted(x['bits'] for x in original if x['round']==r))
    def test_balanced_control_preserves_total_offered_bits(self):
        schedule=schedule_for(self.records(),4,12,1001,'balanced')
        for r in range(12):self.assertEqual(sum(schedule[r]),sum(x['bits'] for x in self.records() if x['round']==r))
    def test_incomplete_replay_cannot_be_silently_matched(self):
        with self.assertRaises(ValueError):schedule_for(self.records()[:-1],4,12,1001,'shuffled')
    def test_missing_reports_enter_error_denominator(self):
        # Synthetic unit-test fixture, not experiment output.
        text='META,1001,1,10,128\n'
        for r in range(12):text+=f'TX,2,{r},{16 if r<10 else 4},{516 if r<10 else 141},0,0,0,0,250\n'
        text+='RX,2,10,4,141,0,1,1\nACT,1,12,0,0,0,0,1000,1000\nACT,2,12,1,1,1000,2000,1000,999\n'
        _,s=parse_log(text,1,12,10)
        self.assertEqual(s['offered_reports'],2)
        self.assertEqual(s['on_time_pdr'],.5)
        self.assertGreater(s['receiver_rmse'],0)
    def test_total_network_failure_is_retained(self):
        text='META,1001,1,10,128\n'
        for r in range(12):text+=f'TX,2,{r},16,516,0,0,0,0,250\n'
        text+='ACT,1,12,0,0,0,0,1000,1000\nACT,2,12,1,1,1000,2000,1000,999\n'
        _,s=parse_log(text,1,12,10)
        self.assertEqual(s['on_time_pdr'],0)
        self.assertAlmostEqual(s['receiver_rmse'],1/4096)
        self.assertIsNone(s['mean_delivered_delay_s'])
    def test_incomplete_simulation_cannot_pass_analysis(self):
        with self.assertRaises(ValueError):parse_log('META,1001,1,10,128\n',1,12,10)
    def test_routing_ablation_reaches_compile_command_and_motes_have_type(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);contiki=root/'contiki'
            template=contiki/'tests/07-simulation-base/08-ipv6-unicast.csc'
            template.parent.mkdir(parents=True)
            template.write_text('<simconf><simulation><motetype><moteinterface>org.contikios.cooja.interfaces.Position</moteinterface></motetype></simulation></simconf>')
            case=dict(nodes=4,rounds=12,seed=1001,period=10,scenario=0,amplitude=4096)
            for policy,flag in [('adaptive',1),('adaptive_etx_replay',0),('shuffled_etx_replay',0)]:
                folder=root/policy;values=make_config(folder,contiki,case,policy)
                xml=ET.parse(folder/'simulation.csc')
                self.assertEqual(len(xml.findall('.//motetype/mote')),5)
                self.assertFalse(xml.findall('./simulation/mote'))
                self.assertIn(f'STUDY_ROUTING={flag}',xml.find('.//commands').text)
                self.assertEqual(values['ENERGY_AWARE'],flag)
