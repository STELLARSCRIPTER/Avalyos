import time
import json
from avalyos_python_qsharp import init_quantum_environment, sample_branches_multiple

# Initialize Q# environment
print("Initializing Q# environment...")
ok = init_quantum_environment()
if not ok:
    print("Failed to initialize Q# environment. Exiting.")
    raise SystemExit(1)

# Trial run to estimate per-sample time
trial_n = 100
print(f"Running trial of {trial_n} samples to estimate per-sample time...")
start = time.perf_counter()
_trial = sample_branches_multiple(num_samples=trial_n)
end = time.perf_counter()
trial_elapsed = end - start
per_sample = trial_elapsed / max(1, trial_n)
print(f"Trial elapsed: {trial_elapsed:.2f}s, per-sample: {per_sample:.6f}s")

# Estimate for 10k
target_n = 10_000
est_seconds = per_sample * target_n
est_minutes = est_seconds / 60.0
print(f"Estimated runtime for {target_n:,} samples: {est_minutes:.2f} minutes ({est_seconds:.1f}s)")

# Run the 10k simulation
print(f"Starting full run of {target_n:,} samples...")
start_full = time.perf_counter()
results = sample_branches_multiple(num_samples=target_n)
end_full = time.perf_counter()
full_elapsed = end_full - start_full
full_minutes = full_elapsed / 60.0
print(f"Full run completed. Elapsed: {full_elapsed:.2f}s ({full_minutes:.2f} minutes)")

# Summarize
summary = {
    "trial_n": trial_n,
    "trial_elapsed_seconds": trial_elapsed,
    "per_sample_seconds": per_sample,
    "target_n": target_n,
    "estimated_seconds": est_seconds,
    "estimated_minutes": est_minutes,
    "actual_elapsed_seconds": full_elapsed,
    "actual_elapsed_minutes": full_minutes,
    "samples_returned": len(results),
}

with open("qsharp_10k_summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)

print("Summary written to qsharp_10k_summary.json")

# Best-effort log to database
try:
    from database_models import log_simulation_result
    log_simulation_result(
        simulation_type="monte_carlo_qsharp",
        company="",
        branch="",
        n_samples=target_n,
        results={
            "estimated_minutes": est_minutes,
            "actual_minutes": full_minutes,
            "samples_returned": len(results),
        },
    )
    print("Logged simulation result to database (best-effort).")
except Exception as e:
    print(f"Could not log to database: {e}")

print("Done.")
