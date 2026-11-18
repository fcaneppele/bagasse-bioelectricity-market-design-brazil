"""Build the monthly BIOMASSA_ACL series used in Table 1 of the manuscript.

Input : the CSV files downloaded manually from https://dadosabertos.ccee.org.br/dataset/biomassa_acl
        and placed, unmodified, in data/raw/ (one or more files; ';' or ',' separated).
Output: data/derived/biomassa_acl_monthly.csv   (one row per month, aggregated)
        data/derived/COVERAGE.md                 (coverage, missing values, extraction metadata)
        data/derived/table1_check.csv            (comparison with the values printed in the manuscript)

Column names are detected by keyword; if detection fails, pass them explicitly, e.g.
    python scripts/build_monthly_series.py --month MES_REFERENCIA --capacity POTENCIA_INSTALADA \
        --guarantee GARANTIA_FISICA --generation GERACAO
Run from the repository root:  python scripts/build_monthly_series.py --extracted 2026-11-18
"""
import argparse
import hashlib
import pathlib
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
DER = ROOT / "data" / "derived"

KEYS = {
    "month": ["MES_REFERENCIA", "MES", "DATA", "PERIODO", "REFERENCIA"],
    "capacity": ["POTENCIA", "CAPACIDADE"],
    "guarantee": ["GARANTIA"],
    "generation": ["GERACAO"],
}


def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_raw():
    files = sorted(p for p in RAW.iterdir() if p.suffix.lower() == ".csv")
    if not files:
        sys.exit(f"No CSV files in {RAW}. Download them from the CCEE portal first (see data/raw/README.md).")
    frames = []
    for p in files:
        for enc in ("utf-8-sig", "latin-1"):
            try:
                df = pd.read_csv(p, sep=None, engine="python", encoding=enc, dtype=str)
                break
            except UnicodeDecodeError:
                continue
        df["__source_file"] = p.name
        frames.append(df)
    return files, pd.concat(frames, ignore_index=True)


def detect(cols, role, override):
    if override:
        if override not in cols:
            sys.exit(f"Column '{override}' not found. Available: {list(cols)}")
        return override
    up = {c: c.upper() for c in cols}
    for k in KEYS[role]:
        hits = [c for c, u in up.items() if k in u]
        if hits:
            return hits[0]
    return None


def to_num(s):
    s = s.astype(str).str.strip().replace({"": None, "nan": None, "None": None})
    # Brazilian format "1.234,5" -> 1234.5 ; plain "1234.5" kept
    br = s.str.contains(",", na=False)
    s = s.where(~br, s.str.replace(".", "", regex=False).str.replace(",", ".", regex=False))
    return pd.to_numeric(s, errors="coerce")


def to_month(s):
    s = s.astype(str).str.strip()
    d = pd.to_datetime(s, errors="coerce", format="mixed", dayfirst=False)
    alt = pd.to_datetime(s, errors="coerce", format="%Y%m")
    d = d.fillna(alt)
    return d.dt.to_period("M").astype(str)


def main():
    ap = argparse.ArgumentParser()
    for r in KEYS:
        ap.add_argument(f"--{r}")
    ap.add_argument("--extracted", required=True, help="date the raw files were downloaded (YYYY-MM-DD)")
    a = ap.parse_args()

    files, df = load_raw()
    cols = [c for c in df.columns if c != "__source_file"]
    col = {r: detect(cols, r, getattr(a, r)) for r in KEYS}
    print("Detected columns:", col)
    if not (col["month"] and col["capacity"] and col["guarantee"]):
        sys.exit(f"Could not detect required columns. Available: {cols}. Pass them explicitly.")

    d = pd.DataFrame({"month": to_month(df[col["month"]])})
    d["installed_capacity_MW"] = to_num(df[col["capacity"]])
    d["physical_guarantee_MW"] = to_num(df[col["guarantee"]])
    if col["generation"]:
        d["generation_MWmed"] = to_num(df[col["generation"]])
    n_rows = len(d)
    missing = d.isna().sum().to_dict()

    g = d.dropna(subset=["month"]).groupby("month", as_index=False)
    agg = g.sum(min_count=1)
    agg["n_records"] = g.size()["size"].values
    agg["guarantee_to_capacity_ratio_pct"] = (100 * agg["physical_guarantee_MW"] / agg["installed_capacity_MW"]).round(1)
    for c in ("installed_capacity_MW", "physical_guarantee_MW"):
        agg[f"{c}_mom_change_pct"] = (100 * agg[c].pct_change()).round(1)
    agg = agg.sort_values("month")
    DER.mkdir(parents=True, exist_ok=True)
    agg.to_csv(DER / "biomassa_acl_monthly.csv", index=False)

    pub = pd.read_csv(DER / "table1_abridged_as_published.csv", dtype={"month": str})
    chk = pub.merge(agg[["month", "installed_capacity_MW", "physical_guarantee_MW"]], on="month",
                    how="left", suffixes=("_published", "_recomputed"))
    for c in ("installed_capacity_MW", "physical_guarantee_MW"):
        chk[f"{c}_diff"] = (chk[f"{c}_recomputed"] - chk[f"{c}_published"]).round(1)
    chk.to_csv(DER / "table1_check.csv", index=False)

    months = pd.period_range(agg["month"].min(), agg["month"].max(), freq="M").astype(str)
    gaps = sorted(set(months) - set(agg["month"]))
    lines = [
        "# Coverage report: BIOMASSA_ACL derived monthly series", "",
        f"- Raw files downloaded on: {a.extracted}",
        f"- Source: CCEE Dados Abertos, https://dadosabertos.ccee.org.br/dataset/biomassa_acl (CC BY 4.0)",
        f"- Raw records read: {n_rows}",
        f"- Months covered: {agg['month'].min()} to {agg['month'].max()} ({len(agg)} months)",
        f"- Calendar months missing inside the range: {gaps if gaps else 'none'}",
        f"- Columns used: {col}",
        f"- Missing (unparseable or empty) values per field before aggregation: {missing}",
        "- Treatment: records with empty month are dropped; numeric fields are summed by month with",
        "  min_count=1 (a month with all values missing stays empty, it is not set to zero). No imputation.",
        "- Units: capacity and guarantee in MW; generation in MWmed (average MW over the period), not MWh.",
        "- The guarantee-to-capacity ratio is descriptive; it is not a capacity factor.", "",
        "## Raw files (SHA-256)", "",
    ] + [f"- `{p.name}`: {sha256(p)}" for p in files] + [
        "", "## Comparison with Table 1 as published", "",
        "Max absolute difference: capacity "
        f"{chk['installed_capacity_MW_diff'].abs().max()} MW; guarantee {chk['physical_guarantee_MW_diff'].abs().max()} MW.",
        f"Table 1 months absent from the recomputed series: "
        f"{chk.loc[chk['installed_capacity_MW_recomputed'].isna(), 'month'].tolist() or 'none'}.",
        "Any non-zero difference or absent month must be resolved before the manuscript is finalised.",
    ]
    (DER / "COVERAGE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
