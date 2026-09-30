# Personal BMI & Fitness Tracker CLI

## Overview
An interactive, offline terminal application that calculates your Body Mass Index (BMI), daily calorie needs and ideal water intake, classifies your result, gives personalised wellness tips, and tracks your progress over time.

Built with **Python (standard library only)** to demonstrate control flow (`if/elif/else`), functions, modular design, string formatting, file I/O, exception handling, logging and unit testing.

## Features
| Module | Capabilities |
|---|---|
| **1. Health Metrics** | BMI, BMR (Mifflin-St Jeor), TDEE, water intake, healthy weight range |
| **2. Classification & Advice** | WHO category (Underweight / Normal / Overweight / Obese) with colour highlights, calorie target, personalised suggestions |
| **3. History & Progress** | Save assessments, view history, add notes, delete records, progress report (weight change, trend, average BMI) |

Also: strict input validation with re-prompts, `cancel` at any prompt, atomic JSON saves, corrupt-file recovery, rotating log file.

## Technologies
- Python 3.9+ (standard library: `dataclasses`, `json`, `logging`, `pathlib`)
- ANSI escape codes for colours (auto-disabled if unsupported or `NO_COLOR` is set)
- `pytest` for testing
- Git / GitHub for version control

> The original idea mentioned `colorama` / `Rich`. This version uses plain ANSI codes so it has **zero runtime dependencies**. You can swap `formatter.py` to use Rich if you prefer.

## Project Structure
```
fitness-tracker-cli/
├── main.py                    # entry point
├── fitness_tracker/
│   ├── config.py              # constants & limits
│   ├── models.py              # UserProfile, Assessment dataclasses
│   ├── validators.py          # input validation
│   ├── calculators.py         # BMI / BMR / TDEE / water
│   ├── classifier.py          # WHO category + calorie target
│   ├── advice.py              # personalised suggestions
│   ├── services.py            # builds full Assessment
│   ├── storage.py             # JSON CRUD
│   ├── analytics.py           # progress summary
│   ├── formatter.py           # coloured terminal output
│   ├── logger.py              # rotating file logger
│   └── cli.py                 # menu / workflow
├── tests/                     # pytest unit tests
├── docs/                      # design diagrams & report outline
├── data/  logs/               # runtime files (git-ignored)
├── statement.md
└── requirements.txt
```

## Install & Run
```bash
git clone <your-repo-url>
cd fitness-tracker-cli
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt    # only needed for running tests
python main.py
```

## Testing
```bash
pip install pytest
python -m pytest -v
```
Covers formulas, category boundaries (18.5 / 25 / 30), validation edge cases, storage CRUD, corrupt-file recovery, progress analytics, and full CLI flows using simulated input.

## Sample Session
```
Name: Asha
Age (years): 25
Sex (m/f): f
Height (cm): 165
Weight (kg): 60
Choose 1-5: 3

--- Results for Asha ---
BMI:                 22.0  (NORMAL)
Healthy weight:      50.4-67.8 kg
BMR:                 1345 kcal/day
Maintenance (TDEE):  2085 kcal/day
Target calories:     2085 kcal/day
Water intake:        2.6 L/day
```
*(Add your own screenshots to a `screenshots/` folder.)*

## Git Workflow Suggestion
```bash
git init
git add .gitignore requirements.txt && git commit -m "chore: project setup"
git add fitness_tracker/config.py fitness_tracker/models.py fitness_tracker/validators.py && git commit -m "feat: config, models, validation"
git add fitness_tracker/calculators.py fitness_tracker/classifier.py fitness_tracker/advice.py fitness_tracker/services.py && git commit -m "feat: health metrics and classification"
git add fitness_tracker/storage.py fitness_tracker/analytics.py && git commit -m "feat: history storage and analytics"
git add fitness_tracker/formatter.py fitness_tracker/cli.py fitness_tracker/logger.py main.py && git commit -m "feat: CLI"
git add tests && git commit -m "test: unit tests"
git add README.md statement.md docs && git commit -m "docs: README, statement, design"
git branch -M main && git remote add origin <url> && git push -u origin main
```

## Disclaimer
This tool gives general wellness guidance only and is not medical advice. BMI does not account for muscle mass, age-related changes or body composition.

## Future Enhancements
Imperial units, goal setting, CSV export, charts (matplotlib), multiple user profiles, Rich-based UI, password-protected profiles.
