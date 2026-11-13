"""Explicit reference DCT codec + application-level receiver reconstruction.

An NEW, controlled diagnostic extension; the submitted simulator does NOT
implement any corresponding source codec or waveform sampler. It CANNOT be
used to assert original semantic-fidelity performance or hardware validation.

One sensor report: 256 deterministic within-report samples. Progressive first
floor(budget/16) orthonormal DCT coefficients, 16-bit signed, step=1/512, no
headers and no coding overhead (optimistic). Missing packets use last decoded
report held at sink; no earlier report = all zero. Raw samples are deliberately
independent of the channel RNG, and ground truth only scores event F1.
"""
import numpy as np
from scipy.fft import dct,idct
class ReceiverReferenceCodec:
    def __init__(self, num_nodes,seed,n_samples=256,event_threshold=.5):
        self.n_nodes=int(num_nodes)
        self.seed=int(seed)
        self.n_samples=int(n_samples)
        self.event_threshold=float(event_threshold)
        self.last=np.zeros((self.n_nodes,n_samples),dtype=np.float64)
        self.sse=0.
        self.zero_sse=0.
        self.n=0
        self.tp=self.fp=self.fn=0
        self.packets=0
        self.received=0
    def record(self,source,round_id,measurement,event_true,bits,delivered):
        source=int(source)
        # A different per-node, per-round RNG stream does not perturb PHY
        # random draws; identical source sequences across control modes.
        seed=(self.seed*1000003+int(round_id)*65537+source*97) % (2**32)
        rng=np.random.default_rng(seed)
        raw=float(measurement)+rng.normal(0,0.08,self.n_samples)
        if delivered:
            coeff=dct(raw,norm="ortho")
            retained=max(1,min(self.n_samples,int(bits)//16))
            discrete=np.clip(np.rint(coeff[:retained]*512),-32768,32767).astype(np.int16)
            rec=np.zeros(self.n_samples,dtype=np.float64)
            rec[:retained]=discrete.astype(np.float64)/512
            self.last[source]=idct(rec,norm="ortho")
            self.received+=1
        reconstructed=self.last[source]
        self.sse+=float(np.sum((raw-reconstructed)**2))
        self.zero_sse+=float(np.sum(raw**2))
        self.n+=self.n_samples
        predicted=bool(float(reconstructed.mean()) >= self.event_threshold)
        target=bool(event_true)
        self.tp+=int(predicted and target)
        self.fp+=int(predicted and not target)
        self.fn+=int(not predicted and target)
        self.packets+=1
    def results(self):
        p=self.tp/(self.tp+self.fp) if self.tp+self.fp else 0.
        r=self.tp/(self.tp+self.fn) if self.tp+self.fn else 0.
        f1=2*p*r/(p+r) if p+r else 0.
        return dict(rmse=float(np.sqrt(self.sse/self.n)),zero_rmse=float(np.sqrt(self.zero_sse/self.n)),
                    precision=p,recall=r,event_f1=f1,
                    tp=self.tp,fp=self.fp,fn=self.fn,reports=self.packets,received=self.received)
