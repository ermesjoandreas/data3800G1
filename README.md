# Alcohol consumption and use of healthcare services (ESS round 11)

DATA3800 Introduction to Data Science with Scripting, OsloMet, autumn 2026. Group 1.

## Research question

How does alcohol consumption relate to the use of healthcare services, when controlling for gender and age?

## Data

European Social Survey, round 11 (file `ESS11e04_2`).

The data is **not** included in this repository. ESS conditions of use do not allow redistribution, and the file is too large for git.

1. Download ESS round 11 (CSV) from the [ESS Data Portal](https://ess.sikt.no/).
2. Unzip it and put `ESS11e04_2.csv` in `data/raw/`.
3. The codebook (`ESS11e04_2 codebook.html`) comes in the same zip. Keep it next to the CSV.

## Project structure

```
data/raw/          original ESS file, never edited (not in git)
data/processed/    cleaned data produced by the code (not in git)
src/               pipeline code (loading, cleaning, analysis)
notebooks/         exploration
figures/           figures produced by the code
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Running the pipeline

_To be filled in._

## Workflow

- Work on your own branch and merge into `main` with a pull request.
- Shared code goes in `src/`. Notebooks are personal, so name them after yourself or the task to avoid merge conflicts.
- Never commit anything in `data/`.

## Group

- Andreas Morgan Ermesjø
- Øyvind Runde
- Jonas Haugedal
- Jesper Østervold
