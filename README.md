# Bagasse bioelectricity market design in Brazil: data and document log

Supporting material for the manuscript *"Firm-energy guarantee rules and biomass bioelectricity in Brazil's
electricity market: an exploratory market-design analysis"* (Guido, Fontana, Gimenes, Frigo and Caneppele),
submitted to *Utilities Policy*.

The primary source is the **CCEE open-data portal**. This repository holds the material **derived** by the study:
the monthly series behind Table 1, the scripts that build it, and the log of regulatory and judicial documents
reviewed. It does not replace the primary sources.

## Contents

| Path | Content |
|---|---|
| `data/raw/` | CCEE BIOMASSA_ACL CSV files, unmodified (CC BY 4.0, CCEE) |
| `data/derived/biomassa_acl_monthly.csv` | Monthly installed capacity (MW), physical guarantee (MW), generation (MWmed), guarantee-to-capacity ratio and month-on-month changes |
| `data/derived/COVERAGE.md` | Coverage, extraction date, missing values, SHA-256 of raw files, check against Table 1 |
| `data/derived/table1_abridged_as_published.csv` | The nine months printed in Table 1 of the manuscript |
| `data/derived/table1_check.csv` | Published vs. recomputed values |
| `docs/document_log.csv` | Regulatory instruments, CCEE bulletins and STJ decisions reviewed, with verification status |
| `scripts/build_monthly_series.py` | Builds the derived files from `data/raw/` |
| `scripts/make_figure1.py` | Draws Fig. 1 of the paper from the derived series |
| `figures/Figure_1.pdf`, `figures/Figure_1.png` | Fig. 1 (vector and 340-dpi raster) |

## Primary sources

- **CCEE Dados Abertos**, dataset BIOMASSA_ACL: https://dadosabertos.ccee.org.br/dataset/biomassa_acl
- **Ministério de Minas e Energia**, Portaria MME nº 564/2014 (firm-energy guarantee of zero-CVU biomass plants)
- **EPE**, report EPE-DEE-RE-056/2023-r0
- **CCEE**, Comunicado 952/23 and the bulletin "Ajustes relativos às ações judiciais do relatório SUM001"
- **STJ**, REsp 1.950.332/RJ (and its Embargos de Declaração) and REsp 1.945.210/RS
- **ANEEL**, Resolução Normativa nº 1.080/2023

Full locations are in `docs/document_log.csv` and in the manuscript's reference list.

## Reproducing the numbers in the paper

```bash
pip install -r requirements.txt
# 1. download the BIOMASSA_ACL CSV files from the CCEE portal into data/raw/
# 2. build the series (give the download date)
python scripts/build_monthly_series.py --extracted YYYY-MM-DD
# 3. draw Fig. 1
python scripts/make_figure1.py
```

The files in `data/raw/` were downloaded on 17 November 2026 and cover October 2023 to September 2026
(35 monthly records; March 2026 is absent from the CCEE files and is not imputed). CCEE publishes the
series as one aggregate record per month, so no plant-level analysis is possible from this dataset.

The script prints the detected columns. If detection fails, pass them explicitly
(`--month`, `--capacity`, `--guarantee`, `--generation`). It then writes the derived files and reports any
difference between the recomputed values and Table 1.

## Units and caveats

- Installed capacity and physical guarantee are in **MW**; the generation field is in **MWmed** (average MW
  over the reference period), not MWh.
- The dataset covers biomass as classified by CCEE; it has not been confirmed to be restricted to sugarcane bagasse.
- It has not been confirmed whether the guarantee field reports plant totals or the portion allocated to the ACL.
  The guarantee-to-capacity ratio is therefore descriptive only, and is not a capacity factor.
- No interrupted-time-series or causal analysis is performed.
- The systematic coding of the ~139 CCEE judicial-actions bulletins has **not** been executed; the document log
  covers only the bounded corpus described in Section 3.2 of the paper.

## Licence

Code: MIT (see `LICENSE`). Derived data and documentation: CC BY 4.0. Raw CCEE data: CC BY 4.0, © CCEE.

## Citation

See `CITATION.cff`. Archived on Zenodo: version 1.0.0, [10.5281/zenodo.24327807](https://doi.org/10.5281/zenodo.24327807)
(all versions: [10.5281/zenodo.24327806](https://doi.org/10.5281/zenodo.24327806)).

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24327807.svg)](https://doi.org/10.5281/zenodo.24327807)
