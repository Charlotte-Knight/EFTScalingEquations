## Preliminary CMS equations produced by Matthew Knight (matthew.knight@cern.ch)

### Model details

|                        |                     |
|------------------------|---------------------|
| Model                  | SMEFT               |
| Flavour Symmetry       | topU3l: $U(2)^2$    |
| Input Parameter Scheme | $\{m_W, m_Z, G_F\}$ |

### Wilson Coefficients

We consider the all CP-even and CP-odd operators except in GGH where we neglect contributions from four-fermion operators

### Derivation details

| Process           | Equation derivation method                     |
|-------------------|------------------------------------------------|
| ggH               | SMEFTatNLO                                     |
| qqH               | SMEFTsim                                       |
| WH_lep            | SMEFTsim                                       |
| ZH_lep            | SMEFTsim                                       |
| ggZH              | SMEFTatNLO                                     |
| ttH               | SMEFTsim                                       |
| tH                | SMEFTsim                                       |
|                   |                                                |
| H->gamgam         | [Analytic loop-level](https://arxiv.org/abs/1807.11504)   |
| H->Zgam           | [Analytic loop-level](https://arxiv.org/abs/1801.01136)   |
| H->gluglu         | Use ggH 0j pT 0->10 scaling eqn (SMEFTatNLO)   |
| All other decay modes   | SMEFTsim


### Notes on acceptance
No acceptance corrections

### Additional notes
Changes with respect to the last [iteration](../CMS-prelim-SMEFT-topU3l_22_05_05) include:
- Replace H->gluglu equation (consequence for total width) with the ggH 0j pT 0->10 equation which is derived with SMEFTatNLO