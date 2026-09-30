# Design Documentation

Diagrams use Mermaid (renders on GitHub; or paste into https://mermaid.live to export PNG for your PDF report).

## 1. Functional Requirements
- **FR1** Collect name, age, sex, height, weight, activity level with validation.
- **FR2** Calculate BMI, BMR, TDEE, calorie target, water intake, healthy weight range.
- **FR3** Classify BMI (WHO) and show colour-coded result + suggestions.
- **FR4** Save each assessment; view history (Read).
- **FR5** Add/edit a note (Update); delete a record (Delete, with confirmation).
- **FR6** Progress report: weight change, trend, average BMI.

## 2. Non-Functional Requirements
| # | Type | Requirement | How it is met |
|---|---|---|---|
| NFR1 | Usability | Clear prompts, re-prompt on error, `cancel` anywhere, colour output | `cli.ask()`, `formatter.py` |
| NFR2 | Reliability | No data loss on crash; recover from corrupt file | Atomic write (temp + rename), `.corrupt` backup |
| NFR3 | Error handling | Invalid input never crashes app | `validators.py` + `ValidationError`, last-resort handler in `main.py` |
| NFR4 | Maintainability | Modular, single-responsibility, documented, tested | 11 modules, 62 unit tests |
| NFR5 | Logging | Events/errors recorded to file | `logger.py` rotating log |
| NFR6 | Performance / Efficiency | Instant response, no external dependencies | Pure functions, stdlib only |
| NFR7 | Security / Privacy | Data stays local; no network access | JSON file on local disk |

## 3. System Architecture
```mermaid
flowchart TB
    U([User]) --> CLI[cli.py - menu & workflow]
    CLI --> V[validators.py]
    CLI --> S[services.py]
    S --> C[calculators.py]
    S --> CL[classifier.py]
    CLI --> A[advice.py]
    CLI --> AN[analytics.py]
    CLI --> F[formatter.py]
    CLI --> ST[storage.py]
    ST --> DB[(data/history.json)]
    CLI -.-> L[logger.py] -.-> LOG[(logs/app.log)]
    C & CL & V --> CFG[config.py]
    S --> M[models.py]
```

## 4. Workflow Diagram
```mermaid
flowchart TD
    A([Start]) --> B[Show menu]
    B --> C{Choice}
    C -->|1| D[Prompt inputs] --> E{Valid?}
    E -->|No| D
    E -->|Yes| F[Calculate metrics] --> G[Classify BMI] --> H[Show results + advice] --> I[Save to history] --> B
    C -->|2| J[Show history] --> B
    C -->|3| K[Compute & show progress] --> B
    C -->|4| L[Update note] --> B
    C -->|5| M{Confirm delete?} -->|Yes| N[Delete record] --> B
    M -->|No| B
    C -->|6| Z([Exit])
```

## 5. Use Case Diagram
```mermaid
flowchart LR
    User((User))
    subgraph System [BMI & Fitness Tracker]
        UC1[Create assessment]
        UC2[View results & advice]
        UC3[View history]
        UC4[Edit note]
        UC5[Delete record]
        UC6[View progress report]
    end
    User --- UC1 & UC3 & UC4 & UC5 & UC6
    UC1 -.include.-> UC2
```

## 6. Sequence Diagram (New Assessment)
```mermaid
sequenceDiagram
    actor User
    participant CLI
    participant Validators
    participant Services
    participant Calc as Calculators/Classifier
    participant Store as HistoryStore
    User->>CLI: choose "New assessment"
    loop each field
        CLI->>User: prompt
        User->>CLI: raw input
        CLI->>Validators: validate
        Validators-->>CLI: value / ValidationError
    end
    CLI->>Services: build_assessment(profile)
    Services->>Calc: BMI, category, BMR, TDEE, water
    Calc-->>Services: results
    Services-->>CLI: Assessment
    CLI->>User: display results + advice
    CLI->>Store: add(assessment)
    Store-->>CLI: saved with id
    CLI->>User: "Saved as record #id"
```

## 7. Class Diagram
```mermaid
classDiagram
    class UserProfile {
        +str name
        +int age
        +str sex
        +float height_cm
        +float weight_kg
        +str activity
    }
    class Assessment {
        +UserProfile profile
        +float bmi
        +str category
        +float bmr
        +float tdee
        +float target_calories
        +float water_liters
        +str timestamp
        +int id
        +str note
        +to_dict()
        +from_dict()
    }
    class HistoryStore {
        +add()
        +list_all()
        +get()
        +update_note()
        +delete()
        +clear()
    }
    class FitnessTrackerCLI {
        +run()
        +new_assessment()
        +view_history()
        +progress_report()
        +edit_note()
        +delete_record()
    }
    Assessment *-- UserProfile
    HistoryStore ..> Assessment
    FitnessTrackerCLI --> HistoryStore
    FitnessTrackerCLI ..> Assessment
```

## 8. Storage Design (ER / Schema)
```mermaid
erDiagram
    ASSESSMENT ||--|| PROFILE_SNAPSHOT : contains
    ASSESSMENT {
        int id PK
        string timestamp
        float bmi
        string category
        float bmr
        float tdee
        float target_calories
        float water_liters
        float healthy_min_kg
        float healthy_max_kg
        string note
    }
    PROFILE_SNAPSHOT {
        string name
        int age
        string sex
        float height_cm
        float weight_kg
        string activity
    }
```
Stored as a JSON array in `data/history.json`; each element is one assessment with its embedded profile snapshot.

## 9. Design Decisions & Rationale
- **JSON over SQLite:** small, human-readable data; zero setup. SQLite is listed as a future upgrade.
- **Pure calculation functions:** easy to unit test, no I/O side effects.
- **Dependency-injected I/O in CLI** (`input_fn`, `output_fn`): allows automated testing of interactive flows.
- **Mifflin-St Jeor** BMR: considered more accurate for modern populations than Harris-Benedict.
- **Snapshot profile per record:** each record is self-contained, so history stays correct even if a user's details change.
- **Atomic writes:** prevents half-written files.

## 10. Testing Approach
Unit tests (pytest) per module + CLI integration tests with simulated input; boundary-value tests for BMI categories and validation ranges; failure-path tests for corrupt storage.

## 11. Report Outline Mapping (PDF Section 6)
Cover Page -> Introduction (README overview) -> Problem Statement (statement.md) -> FR/NFR (section 1-2 above) -> Architecture (3) -> Diagrams (4-8) -> Decisions (9) -> Implementation (module list in README) -> Screenshots (run app & capture) -> Testing (10) -> Challenges (e.g. float rounding in tests, corrupt-file handling, testable CLI) -> Learnings -> Future Enhancements -> References (WHO BMI classification; Mifflin et al., 1990, Am J Clin Nutr).
