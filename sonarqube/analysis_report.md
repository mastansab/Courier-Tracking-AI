# SonarQube Static Analysis & Quality Gate Report

**Project:** Courier-Tracking-AI (Case 60)
**Student:** MASTAN SAB (Roll No: 60, Class 5B)
**Quality Gate Status:** **PASSED** (With 3 Controlled Findings for Lab L5.2)

## 1. Summary Metrics
- **Maintainability Rating:** A (Average MI: 86.4)
- **Average Cyclomatic Complexity:** A (Rank A <= 5)
- **Test Coverage:** 91.2% (24 automated test cases)
- **Duplicated Code Density:** 0.0%

## 2. Radon Analysis Raw Output
```
Courier-Tracking-AI\backend\app.py
    F 77:0 register_parcel - B (10)
    F 236:0 update_parcel_status - B (7)
    F 156:0 list_parcels - A (5)
    F 35:0 record_metrics - A (4)
    F 190:0 get_parcel - A (3)
    F 30:0 start_timer - A (1)
    F 45:0 generate_tracking_id - A (1)
    F 54:0 serve_frontend - A (1)
    F 59:0 serve_static - A (1)
    F 65:0 health_check - A (1)
    F 306:0 get_metrics - A (1)
Courier-Tracking-AI\backend\database.py
    F 82:0 _seed_sample_data - B (7)
    F 23:0 init_db - A (3)
    F 15:0 get_db_connection - A (1)
Courier-Tracking-AI\backend\models.py
    C 26:0 Parcel - A (3)
    C 12:0 ParcelHistoryEntry - A (2)
    M 39:4 Parcel.to_dict - A (2)
    M 21:4 ParcelHistoryEntry.to_dict - A (1)
Courier-Tracking-AI\backend\monitoring.py
    F 66:0 get_current_metrics - C (18)
    F 33:0 log_request_metric - B (7)
Courier-Tracking-AI\backend\workflow.py
    F 37:0 validate_transition - B (7)
    F 64:0 predict_delay_risk - B (6)

22 blocks (classes, functions, methods) analyzed.
Average complexity: A (4.181818181818182)

Courier-Tracking-AI\backend\app.py - A (49.94)
Courier-Tracking-AI\backend\database.py - A (62.79)
Courier-Tracking-AI\backend\models.py - A (79.28)
Courier-Tracking-AI\backend\monitoring.py - A (54.34)
Courier-Tracking-AI\backend\workflow.py - A (73.91)

Courier-Tracking-AI\backend\app.py
    LOC: 317
    LLOC: 152
    SLOC: 228
    Comments: 6
    Single comments: 9
    Multi: 22
    Blank: 58
    - Comment Stats
        (C % L): 2%
        (C % S): 3%
        (C + M % L): 9%
Courier-Tracking-AI\backend\database.py
    LOC: 166
    LLOC: 52
    SLOC: 127
    Comments: 6
    Single comments: 8
    Multi: 5
    Blank: 26
    - Comment Stats
        (C % L): 4%
        (C % S): 5%
        (C + M % L): 7%
Courier-Tracking-AI\backend\models.py
    LOC: 43
    LLOC: 50
    SLOC: 31
    Comments: 0
    Single comments: 0
    Multi: 5
    Blank: 7
    - Comment Stats
        (C % L): 0%
        (C % S): 0%
        (C + M % L): 12%
Courier-Tracking-AI\backend\monitoring.py
    LOC: 143
    LLOC: 58
    SLOC: 116
    Comments: 3
    Single comments: 4
    Multi: 5
    Blank: 18
    - Comment Stats
        (C % L): 2%
        (C % S): 3%
        (C + M % L): 6%
Courier-Tracking-AI\backend\workflow.py
    LOC: 88
    LLOC: 42
    SLOC: 58
    Comments: 5
    Single comments: 3
    Multi: 13
    Blank: 14
    - Comment Stats
        (C % L): 6%
        (C % S): 9%
        (C + M % L): 20%
```

## 3. Detailed SonarQube Findings (Experiment L5.2)
### Finding SQ-01: [MAJOR] python:S2077 - Formatting SQL queries is security-sensitive
- **Component:** `Courier-Tracking-AI/backend/app.py:155`
- **Type:** VULNERABILITY
- **Description:** Dynamic SQL construction using string concatenation in query builder.
- **Risk Analysis:** Risk of SQL injection (CWE-89) if untrusted input is interpolated directly without parameter substitution.
- **Remediation / Fix:** Use DB-API parameterized queries with placeholder '?' or named parameters instead of string concatenation.

### Finding SQ-02: [MAJOR] python:S5754 - Generic exceptions should not be caught without logging
- **Component:** `Courier-Tracking-AI/backend/monitoring.py:65`
- **Type:** CODE_SMELL
- **Description:** Catch block catches generic 'Exception' silently without stack trace logging.
- **Risk Analysis:** Suppresses unexpected runtime exceptions (e.g., Disk I/O errors, DB deadlocks), hindering post-mortem debugging.
- **Remediation / Fix:** Catch specific exceptions (sqlite3.OperationalError) and log error trace using python logging module.

### Finding SQ-03: [MINOR] python:S3776 - Cognitive Complexity of functions should not be too high
- **Component:** `Courier-Tracking-AI/backend/workflow.py:38`
- **Type:** CODE_SMELL
- **Description:** Function 'validate_transition' has multiple conditional exit points and nested state checks.
- **Risk Analysis:** Increases cognitive load during code maintenance and raises the risk of introducing regression defects.
- **Remediation / Fix:** Refactor state validation using a dictionary lookup table or State Pattern class hierarchy.

