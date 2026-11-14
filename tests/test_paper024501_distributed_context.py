import numpy as np
import pytest
from config import SimulationConfig
from simulator.topology import Topology
from simulator.network import SensorNetwork
from simulator.energy import RadioEnergyModel
from simulator.semantic_relevance import SemanticRelevanceEstimator
from reviewer_audit.PAPER024501.distributed_neighbour_context import ReceivedNeighbourContext

def setup_case(seed=42):
    c=SimulationConfig(seed=seed,num_nodes=12)
    t=Topology(c)
    return c,t,SensorNetwork(c,t),RadioEnergyModel(c)

def test_successful_context_is_receiver_specific_not_central():
    c,t,n,r=setup_case()
    a=ReceivedNeighbourContext(c,t,context_bytes=25,success_probability=1)
    obs=np.arange(c.num_nodes,dtype=float)
    old=n.total_residual_energy
    matrix=a.advance(obs,n,r,1)
    for i in range(c.num_nodes):
        for j in range(c.num_nodes):
            if i!=j and t.distance_matrix[i,j]<=20 and n.alive[j]:
                assert matrix[i,j]==obs[j]
            else:
                assert np.isnan(matrix[i,j])
    assert old-n.total_residual_energy>=0
    assert a.results()["context_packets_sent"]>0

def test_missed_context_holds_prior_observation_without_oracle():
    c,t,n,r=setup_case()
    a=ReceivedNeighbourContext(c,t,context_bytes=25,success_probability=1)
    first=np.arange(c.num_nodes,dtype=float)
    snap=a.advance(first,n,r,1)
    a.success_probability=0
    latest=first+99
    stale=a.advance(latest,n,r,2)
    assert np.array_equal(np.isnan(stale),np.isnan(snap))
    np.testing.assert_array_equal(stale[np.isfinite(stale)],snap[np.isfinite(snap)])
    assert a.results()["mean_cached_context_age_rounds"]>0

def test_default_spatial_path_is_unchanged_when_none():
    c,t,n,r=setup_case()
    e=SemanticRelevanceEstimator(t)
    obs=np.linspace(0,1,c.num_nodes)
    np.testing.assert_allclose(e._spatial_feature(obs),e._spatial_feature(obs,neighbour_values=None))

def test_no_context_packet_when_success_probability_zero():
    c,t,n,r=setup_case()
    a=ReceivedNeighbourContext(c,t,success_probability=0)
    x=a.advance(np.ones(c.num_nodes),n,r,1)
    assert np.isnan(x).all()
    assert a.results()["context_updates_received"]==0
    assert a.results()["context_receive_attempts"]>0

def test_invalid_context_size_or_success_rejected():
    c,t,n,r=setup_case()
    with pytest.raises(ValueError):ReceivedNeighbourContext(c,t,context_bytes=0)
    with pytest.raises(ValueError):ReceivedNeighbourContext(c,t,success_probability=1.1)
