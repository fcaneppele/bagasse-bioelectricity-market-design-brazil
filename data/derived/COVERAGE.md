# Coverage report: BIOMASSA_ACL derived monthly series

- Raw files downloaded on: 2026-11-17
- Source: CCEE Dados Abertos, https://dadosabertos.ccee.org.br/dataset/biomassa_acl (CC BY 4.0)
- Raw records read: 35
- Months covered: 2023-10 to 2026-09 (35 months)
- Calendar months missing inside the range: ['2026-03']
- Columns used: {'month': 'MES_REFERENCIA', 'capacity': 'CAPACIDADE_INSTALADA_BIOMASSA', 'guarantee': 'GARANTIA_FISICA_BIOMASSA', 'generation': 'GERACAO_BIOMASSA'}
- Missing (unparseable or empty) values per field before aggregation: {'month': 0, 'installed_capacity_MW': 0, 'physical_guarantee_MW': 0, 'generation_MWmed': 0}
- Treatment: records with empty month are dropped; numeric fields are summed by month with
  min_count=1 (a month with all values missing stays empty, it is not set to zero). No imputation.
- Units: capacity and guarantee in MW; generation in MWmed (average MW over the period), not MWh.
- The guarantee-to-capacity ratio is descriptive; it is not a capacity factor.

## Raw files (SHA-256)

- `biomassa_acl_2023.csv`: 0de04066cdbd97a36298f57be3427012f03b3d6390779875a3a88271245262bb
- `biomassa_acl_2024.csv`: ae258e4e76c1dee63cd0cfa211acad5dd49533d70b5c0ecf3988570edfbe7356
- `biomassa_acl_2025.csv`: c2e975f4fa0bdee13ea633e15cad6fea4fa596f0e0215b61698bc084859be71c
- `biomassa_acl_2026.csv`: a9419b32a7bdd133b14c5d174d2ae5e836e974f2ebddecc55b3480d75753228e

## Comparison with Table 1 as published

Max absolute difference: capacity 0.0 MW; guarantee 0.0 MW.
Table 1 months absent from the recomputed series: none.
Any non-zero difference or absent month must be resolved before the manuscript is finalised.
