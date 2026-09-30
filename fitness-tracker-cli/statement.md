# Problem Statement

## Problem
Many people want a quick way to understand their body metrics (BMI, daily calorie needs, water intake) and to see whether they are improving over time. Existing apps are heavy, need accounts, and hide how numbers are calculated. Manual calculation is error-prone, and there is no simple record of progress.

## Scope
A lightweight, offline, interactive **command-line** application that:
- Calculates BMI, BMR, TDEE, calorie target and daily water intake from user input.
- Classifies BMI using WHO categories and gives personalised wellness suggestions.
- Stores every assessment locally and reports weight/BMI progress over time.

**Out of scope:** medical diagnosis, imperial units, multi-user accounts, cloud sync, GUI/web interface (see Future Enhancements in README).

## Target Users
- Students and individuals starting a fitness journey.
- Users who want a private, offline tool with no sign-up.
- Learners who want to see clear, testable health-formula code.

## High-Level Features
1. **Health Metrics Module** - BMI, BMR (Mifflin-St Jeor), TDEE, water intake, healthy weight range.
2. **Classification & Advice Module** - WHO category, colour-coded output, calorie target, personalised suggestions.
3. **History & Progress Module** - CRUD on saved assessments (JSON storage), progress report with trend analysis.
4. Robust input validation, logging, and graceful error recovery.
