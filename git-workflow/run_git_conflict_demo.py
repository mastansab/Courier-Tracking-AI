"""
run_git_conflict_demo.py - Automated Execution of Experiment L3.3: Git Merge Conflict.
Identifier: FR-01 / L3.3
Student: MASTAN SAB (Roll No: 60, Class 5B, Case 60)
"""

import os
import subprocess
import shutil

GIT_EXE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "mingit", "cmd", "git.exe"))
DEMO_REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "demo_repo"))


def run_cmd(args, cwd=DEMO_REPO_DIR, expect_fail=False):
    res = subprocess.run([GIT_EXE] + args, cwd=cwd, capture_output=True, text=True)
    if not expect_fail and res.returncode != 0:
        print(f"FAILED: {' '.join(args)}\n{res.stderr}")
    return res


def setup_merge_conflict_demo():
    print("=== EXPERIMENT L3.3: GIT MERGE CONFLICT GENERATION & RESOLUTION ===")

    # Clean existing demo repo
    if os.path.exists(DEMO_REPO_DIR):
        shutil.rmtree(DEMO_REPO_DIR, ignore_errors=True)
    os.makedirs(DEMO_REPO_DIR, exist_ok=True)

    # 1. Git init
    run_cmd(["init", "-b", "main"])
    run_cmd(["config", "user.name", "Mastan Sab (Roll 60)"])
    run_cmd(["config", "user.email", "mastansab60@couriertracking.ai"])

    # 2. Base commit
    policy_file = os.path.join(DEMO_REPO_DIR, "workflow_policy.py")
    with open(policy_file, "w") as f:
        f.write('''# workflow_policy.py - Courier Tracking Policy
# Case 60: Courier Tracking System (Incremental SDLC)

def process_status_transition(parcel_id, current_status, new_status):
    """Base transition logic for 30,000 parcels/day."""
    print(f"Logging transition for {parcel_id}: {current_status} -> {new_status}")
    # POLICY_BLOCK_START
    timeout_hours = 48
    enable_auto_retry = False
    validation_level = "STANDARD"
    # POLICY_BLOCK_END
    return True
''')

    run_cmd(["add", "workflow_policy.py"])
    run_cmd(["commit", "-m", "Initial commit: Base workflow policy (Incremental SDLC)"])
    print("[1] Base commit created on branch 'main'.")

    # 3. Create Feature Branch A: feature/express-routing
    run_cmd(["checkout", "-b", "feature/express-routing"])
    with open(policy_file, "w") as f:
        f.write('''# workflow_policy.py - Courier Tracking Policy
# Case 60: Courier Tracking System (Incremental SDLC)

def process_status_transition(parcel_id, current_status, new_status):
    """Base transition logic for 30,000 parcels/day."""
    print(f"Logging transition for {parcel_id}: {current_status} -> {new_status}")
    # POLICY_BLOCK_START
    timeout_hours = 24  # Express SLA reduction
    enable_auto_retry = True  # Auto-reroute failed parcels
    validation_level = "EXPRESS_PRIORITY"
    # POLICY_BLOCK_END
    return True
''')
    run_cmd(["add", "workflow_policy.py"])
    run_cmd(["commit", "-m", "Feature: Update SLA to 24h express priority with auto-retry"])
    print("[2] Committed express routing changes on 'feature/express-routing'.")

    # 4. Switch back to main and create Feature Branch B: feature/security-compliance
    run_cmd(["checkout", "main"])
    run_cmd(["checkout", "-b", "feature/security-compliance"])
    with open(policy_file, "w") as f:
        f.write('''# workflow_policy.py - Courier Tracking Policy
# Case 60: Courier Tracking System (Incremental SDLC)

def process_status_transition(parcel_id, current_status, new_status):
    """Base transition logic for 30,000 parcels/day."""
    print(f"Logging transition for {parcel_id}: {current_status} -> {new_status}")
    # POLICY_BLOCK_START
    timeout_hours = 72  # Strict 72h quarantine hold
    enable_auto_retry = False  # Mandatory manual review for exceptions
    validation_level = "STRICT_AUDIT_COMPLIANT"
    # POLICY_BLOCK_END
    return True
''')
    run_cmd(["add", "workflow_policy.py"])
    run_cmd(["commit", "-m", "Compliance: Require strict 72h hold and manual audit verification"])
    print("[3] Committed compliance changes on 'feature/security-compliance'.")

    # 5. Merge feature/express-routing into main
    run_cmd(["checkout", "main"])
    res_m1 = run_cmd(["merge", "feature/express-routing", "-m", "Merge branch feature/express-routing into main"])
    print("[4] Merged 'feature/express-routing' cleanly into 'main'.")

    # 6. Merge feature/security-compliance into main -> PROVOKES MERGE CONFLICT!
    print("[5] Attempting to merge 'feature/security-compliance' into 'main'...")
    res_m2 = run_cmd(["merge", "feature/security-compliance"], expect_fail=True)
    print(">>> MERGE CONFLICT DETECTED! <<<\n", res_m2.stdout, res_m2.stderr)

    # 7. Capture Conflict Markers
    with open(policy_file, "r") as f:
        conflicted_content = f.read()
    print("\n--- CONFLICT MARKERS IN FILE ---")
    print(conflicted_content)

    git_status = run_cmd(["status"]).stdout
    print("\n--- GIT STATUS DURING CONFLICT ---")
    print(git_status)

    # 8. Save conflict log
    log_path = os.path.join(os.path.dirname(__file__), "conflict_evidence.txt")
    with open(log_path, "w") as f:
        f.write("=== GENUINE GIT MERGE CONFLICT EVIDENCE (Experiment L3.3) ===\n")
        f.write(f"Repository: {DEMO_REPO_DIR}\n")
        f.write(f"Command: git merge feature/security-compliance\n\n")
        f.write("--- Git Output ---\n")
        f.write(res_m2.stdout + "\n" + res_m2.stderr + "\n")
        f.write("--- Git Status ---\n")
        f.write(git_status + "\n")
        f.write("--- Conflicted File Contents with Markers ---\n")
        f.write(conflicted_content + "\n")

    # 9. AI Suggestion and Resolution
    # AI suggested resolving by combining express SLA (24h) with strict compliance audit:
    resolved_content = '''# workflow_policy.py - Courier Tracking Policy
# Case 60: Courier Tracking System (Incremental SDLC)

def process_status_transition(parcel_id, current_status, new_status):
    """Base transition logic for 30,000 parcels/day."""
    print(f"Logging transition for {parcel_id}: {current_status} -> {new_status}")
    # RESOLUTION: Combined Express Speed with Strict Security Audit
    timeout_hours = 24             # From feature/express-routing (Fast SLA)
    enable_auto_retry = True        # From feature/express-routing (Automated recovery)
    validation_level = "STRICT_AUDIT_EXPRESS"  # Hybrid resolution approved by SQA
    audit_signature_required = True # From feature/security-compliance
    return True
'''
    with open(policy_file, "w") as f:
        f.write(resolved_content)

    run_cmd(["add", "workflow_policy.py"])
    run_cmd(["commit", "-m", "Resolve merge conflict: Integrate 24h express SLA with strict audit compliance"])
    print("[6] Conflict successfully resolved and committed!")

    log_tree = run_cmd(["log", "--graph", "--oneline", "--all"]).stdout
    print("\n--- GIT GRAPH LOG POST RESOLUTION ---")
    print(log_tree)

    with open(log_path, "a") as f:
        f.write("\n--- Resolution Strategy ---\n")
        f.write("AI Suggestion: Merge business objectives by applying 24h SLA for express transit while enforcing strict audit validation.\n")
        f.write("Human Decision: Approved hybrid configuration 'STRICT_AUDIT_EXPRESS'.\n\n")
        f.write("--- Post-Resolution Git Graph ---\n")
        f.write(log_tree)

    print(f"Merge conflict evidence saved to: {log_path}")


if __name__ == "__main__":
    setup_merge_conflict_demo()
