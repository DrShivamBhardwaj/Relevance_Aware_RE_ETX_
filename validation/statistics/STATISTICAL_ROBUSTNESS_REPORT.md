# Statistical robustness report

All tests use paired seed-level comparisons at correlation 0.9. Exact sign-flip p-values are paired permutation tests over 10 seeds; Holm correction is applied within each dataset-baseline family. Bootstrap intervals are percentile 95% intervals for the paired mean difference.

## intel_lab

### Proposed vs resource

| Metric | Proposed | Baseline | Diff | % change | p | Holm p | 95% bootstrap CI |
|---|---:|---:|---:|---:|---:|---:|---:|
| rmse_c | 1.742 | 1.745 | -0.003336 | -0.19% | 0.2246 | 0.2246 | [-0.007752, 0.001691] |
| mae_c | 0.7968 | 0.8297 | -0.03282 | -3.96% | 0.0020 | 0.0117 | [-0.04477, -0.02128] |
| effective_bits | 9.826e+05 | 2.217e+06 | -1.234e+06 | -55.67% | 0.0020 | 0.0117 | [-1.254e+06, -1.214e+06] |
| energy_j | 3.46 | 6.298 | -2.838 | -45.06% | 0.0020 | 0.0117 | [-2.883, -2.793] |
| max_relay_energy_j | 0.09757 | 0.1393 | -0.0417 | -29.94% | 0.0020 | 0.0117 | [-0.04726, -0.03597] |
| representation_js | 0.02314 | 0.1231 | -0.09999 | -81.21% | 0.0020 | 0.0117 | [-0.1075, -0.09332] |

## uci_har

### Proposed vs resource

| Metric | Proposed | Baseline | Diff | % change | p | Holm p | 95% bootstrap CI |
|---|---:|---:|---:|---:|---:|---:|---:|
| accuracy | 0.9061 | 0.8754 | 0.03076 | 3.51% | 0.0020 | 0.0156 | [0.01524, 0.05087] |
| macro_f1 | 0.906 | 0.8724 | 0.03355 | 3.85% | 0.0020 | 0.0156 | [0.01556, 0.05657] |
| worst_client_accuracy | 0.7169 | 0.6814 | 0.03555 | 5.22% | 0.0156 | 0.0156 | [0.0157, 0.05883] |
| p10_client_accuracy | 0.8537 | 0.7963 | 0.05748 | 7.22% | 0.0020 | 0.0156 | [0.02881, 0.09021] |
| effective_bits | 1.164e+07 | 2.965e+07 | -1.801e+07 | -60.75% | 0.0020 | 0.0156 | [-1.904e+07, -1.705e+07] |
| energy_j | 20.03 | 45.92 | -25.89 | -56.38% | 0.0020 | 0.0156 | [-27.53, -24.29] |
| max_relay_energy_j | 1.415 | 0.4576 | 0.9576 | 209.28% | 0.0020 | 0.0156 | [0.647, 1.226] |
| representation_js | 0.03273 | 0.1634 | -0.1307 | -79.97% | 0.0020 | 0.0156 | [-0.1576, -0.1055] |
