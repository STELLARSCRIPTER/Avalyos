"""
Page 2: Quantum Sampling Tests - Quantum Simulator Panel
Enhanced with futuristic dome UI and quantum visualizations
"""

import streamlit as st
import numpy as np
from utils import (
    quantum_sample_once,
    run_monte_carlo_simulation,
)
import logging

logger = logging.getLogger(__name__)
try:
    from database_models import log_user_action, log_simulation_result
except Exception:
    # Provide no-op fallbacks when DB or drivers (e.g., psycopg2) are not available
    def log_user_action(*args, **kwargs):
        return None

    def log_simulation_result(*args, **kwargs):
        return None
# removed dependency on dome_theme; using simple Streamlit headers instead
from quantum_visuals import create_animated_quantum_circuit, create_probability_distribution, create_entanglement_visualization, create_bloch_sphere, create_performance_gauge
import time

# Try to obtain available companies from backend data (best-effort). This
# avoids relying on an external companies listing file. If import fails,
# the dropdown will simply be empty and the user can type a branch name.
try:
    import aval_backend
    _raw_companies = list(getattr(aval_backend, "BRANCHES_BY_COMPANY", {}).keys())
    # map display name -> actual key (keys stored lowercased in backend)
    _company_display_map = {c.title(): c for c in _raw_companies}
    _COMPANIES = sorted(list(_company_display_map.keys()))
except Exception:
    logger.exception("Could not import aval_backend or read BRANCHES_BY_COMPANY")
    _COMPANIES = []
    _company_display_map = {}

# (dome theme removed)

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Quantum Simulator Panel",
    page_icon="⚛️",
    layout="wide",
)

# ============================================================================
# PAGE TITLE
# ============================================================================

st.title("⚛️ QUANTUM SIMULATOR PANEL")
st.caption("Advanced Quantum Sampling & Monte Carlo Analysis | Real-Time Performance Metrics")

# ============================================================================
# SESSION STATE
# ============================================================================

if "sample_result" not in st.session_state:
    st.session_state.sample_result = None

if "monte_carlo_result" not in st.session_state:
    st.session_state.monte_carlo_result = None

# ============================================================================
# SECTION 1: QUANTUM SAMPLE
# ============================================================================

st.subheader("1️⃣ Single Quantum Sample")
st.markdown(
    '<p style="color: #262730; font-size: 16px;">Click the button to sample one branch using quantum simulation.</p>',
    unsafe_allow_html=True
)


col1, col2 = st.columns([0.3, 0.7])

with col1:
    # Company selector (dropdown) — allows quick selection when backend data exists
    if _COMPANIES:
        company_options = _COMPANIES
        selected_company_display = st.selectbox("Company", options=["(none)"] + company_options, index=0)
    else:
        selected_company_display = st.selectbox("Company", options=["(none)"], index=0)

    # If a company is selected, offer a branch selector populated from backend data
    selected_branch_code = None
    if selected_company_display and selected_company_display != "(none)":
        try:
            # lookup backend key from display name (fall back to display lowercased)
            key = _company_display_map.get(selected_company_display, selected_company_display).lower()
            branches = getattr(aval_backend, "BRANCHES_BY_COMPANY", {}).get(key, [])
            # Build clearer branch labels: "CODE — Company / State"
            branch_options = []
            for b in branches:
                code = b.get("code", "")
                comp = b.get("company", "").title()
                state = b.get("state", "")
                label = f"{code} — {comp} / {state}" if code else f"{comp} / {state}"
                branch_options.append((label, code))
            if branch_options:
                labels = [lbl for lbl, _ in branch_options]
                choice = st.selectbox("Branch (choose)", options=["(auto)"] + labels, index=0)
                if choice != "(auto)":
                    # map back to code
                    for lbl, cd in branch_options:
                        if lbl == choice:
                            selected_branch_code = cd
                            break
        except Exception:
            logger.exception("Error while building branch options for company=%s", selected_company_display)
            selected_branch_code = None

    branch_name = st.text_input(
        "Branch Name",
        value="HQ-001",
        help="Enter the branch identifier to sample",
    )
    
    if st.button("🎯 Sample One Branch", key="sample_btn"):
        with st.spinner("🔄 Running quantum sample..."):
            # If the user selected a specific branch code, prefer that
            if selected_branch_code and selected_branch_code not in ("(auto)", ""):
                use_branch = selected_branch_code
            else:
                use_branch = branch_name
            result = quantum_sample_once(use_branch)
            st.session_state.sample_result = result
            # Log the simulation and action (best-effort)
            try:
                log_user_action(action_type="simulate", target=branch_name, details={"type": "single_sample"})
                log_simulation_result(
                    simulation_type="single_sample",
                    company="",
                    branch=branch_name,
                    n_samples=1,
                    results=result,
                )
            except Exception:
                logger.exception("Failed to log single-sample simulation for branch=%s", branch_name)

with col2:
    if st.session_state.sample_result:
        result = st.session_state.sample_result
        with st.container():
            st.markdown("### ✅ Sampling Result")
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Branch", result.get("branch", "—"))
                st.metric("Quantum Value", f"{result.get('quantum_value', 0):.6f}")
            with col_b:
                st.write(f"**Timestamp:** {result.get('timestamp', '—')}")
                st.write(f"**Status:** ✅ Success")
    else:
        st.info("👆 Click 'Sample One Branch' to see results here.")

st.markdown("---")

# ============================================================================
# SECTION 2: MONTE CARLO SIMULATION
# ============================================================================

st.subheader("2️⃣ Monte Carlo Simulation")
st.markdown(
    '<p style="color: #262730; font-size: 16px;">Run random samples and analyze their distribution. Use the slider or the quick-run buttons for 10k / 1M samples.</p>',
    unsafe_allow_html=True
)

col1, col2 = st.columns([0.3, 0.7])

with col1:
    n_samples = st.slider(
        "Number of Samples",
        min_value=10,
        max_value=10000,
        value=100,
        step=10,
        help="How many random samples to generate (slider max 10,000). Use the quick buttons for larger runs.",
    )

    # Quick-run buttons for 10k and 1M samples
    if st.button("⚡ Run Monte Carlo (slider)", key="mc_btn"):
        with st.spinner(f"🔄 Running {n_samples} samples..."):
            start = time.perf_counter()
            result = run_monte_carlo_simulation(n_samples)
            elapsed = time.perf_counter() - start
            st.session_state.monte_carlo_result = result
            st.session_state.monte_carlo_elapsed = elapsed
            # Log the monte carlo simulation (best-effort)
            try:
                log_user_action(action_type="simulate", target="monte_carlo", details={"n_samples": n_samples})
                # store summary results
                log_simulation_result(
                    simulation_type="monte_carlo",
                    company="",
                    branch="",
                    n_samples=n_samples,
                    results={
                        "mean": result.get("mean"),
                        "variance": result.get("variance"),
                        "std_dev": result.get("std_dev"),
                        "samples_preview": result.get("samples", [])[:20],
                        "elapsed_seconds": st.session_state.get("monte_carlo_elapsed", None),
                    },
                )
            except Exception:
                logger.exception("Failed to log monte carlo run (n=%s)", n_samples)

    # Quick-run: 10,000 samples
    if st.button("⚡ Run 10,000 Samples", key="mc_10k"):
        target_n = 10_000
        # Estimate runtime using a small trial run
        trial_n = 100
        with st.spinner("⏱ Estimating runtime with a small trial..."):
            t0 = time.perf_counter()
            _trial = run_monte_carlo_simulation(trial_n)
            t1 = time.perf_counter()
            per_sample = (t1 - t0) / max(1, trial_n)
            est_seconds = per_sample * target_n
            est_minutes = est_seconds / 60.0
        st.info(f"Estimated runtime for {target_n:,} samples: {est_minutes:.2f} minutes")
        with st.spinner(f"🔄 Running {target_n:,} samples (estimated {est_minutes:.2f} min)..."):
            start = time.perf_counter()
            result = run_monte_carlo_simulation(target_n)
            elapsed = time.perf_counter() - start
            st.session_state.monte_carlo_result = result
            st.session_state.monte_carlo_elapsed = elapsed
        try:
            log_user_action(action_type="simulate", target="monte_carlo_10k", details={"n_samples": target_n, "estimated_minutes": est_minutes})
            log_simulation_result(
                simulation_type="monte_carlo",
                company="",
                branch="",
                n_samples=target_n,
                results={
                    "mean": result.get("mean"),
                    "variance": result.get("variance"),
                    "std_dev": result.get("std_dev"),
                    "samples_preview": result.get("samples", [])[:20],
                    "elapsed_seconds": elapsed,
                },
            )
        except Exception:
            logger.exception("Failed to log monte carlo 10k run (estimated_minutes=%s)", est_minutes)

    # Quick-run: 1,000,000 samples (require confirmation)
    if st.button("⚡ Prepare 1,000,000 Samples", key="mc_prep_1m"):
        target_n = 1_000_000
        trial_n = 100
        with st.spinner("⏱ Estimating runtime with a small trial..."):
            t0 = time.perf_counter()
            _trial = run_monte_carlo_simulation(trial_n)
            t1 = time.perf_counter()
            per_sample = (t1 - t0) / max(1, trial_n)
            est_seconds = per_sample * target_n
            est_minutes = est_seconds / 60.0
        st.warning(f"Estimated runtime for {target_n:,} samples: {est_minutes:.2f} minutes")
        confirm = st.checkbox(f"I understand this may take ~{est_minutes:.2f} minutes and use significant memory — run 1,000,000 samples", key="confirm_1m")
        if confirm:
            with st.spinner(f"🔄 Running {target_n:,} samples (estimated {est_minutes:.2f} min)..."):
                start = time.perf_counter()
                result = run_monte_carlo_simulation(target_n)
                elapsed = time.perf_counter() - start
                st.session_state.monte_carlo_result = result
                st.session_state.monte_carlo_elapsed = elapsed
            try:
                log_user_action(action_type="simulate", target="monte_carlo_1m", details={"n_samples": target_n, "estimated_minutes": est_minutes})
                log_simulation_result(
                    simulation_type="monte_carlo",
                    company="",
                    branch="",
                    n_samples=target_n,
                    results={
                        "mean": result.get("mean"),
                        "variance": result.get("variance"),
                        "std_dev": result.get("std_dev"),
                        "samples_preview": result.get("samples", [])[:20],
                        "elapsed_seconds": elapsed,
                    },
                )
            except Exception:
                logger.exception("Failed to log monte carlo 1m run (estimated_minutes=%s)", est_minutes)

with col2:
    if st.session_state.monte_carlo_result:
        result = st.session_state.monte_carlo_result
        with st.container():
            st.markdown("### 📊 Simulation Statistics")
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Mean", f"{result['mean']:.6f}")
                st.metric("Variance", f"{result['variance']:.6f}")
            with col_b:
                st.metric("Std Dev", f"{result['std_dev']:.6f}")
                st.metric("Min | Max", f"{result['min']:.6f} | {result['max']:.6f}")
    else:
        st.info("👆 Click 'Run Monte Carlo Simulation' to see results here.")

st.markdown("---")

# ============================================================================
# VISUALIZATION
# ============================================================================

if st.session_state.monte_carlo_result:
    st.subheader("📈 Distribution Visualization")
    
    result = st.session_state.monte_carlo_result
    samples = result["samples"]
    
    # Bar chart (histogram)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Histogram")
        # Create histogram data
        hist_values, bin_edges = np.histogram(samples, bins=20)
        chart_data = {
            "Bin": [f"{bin_edges[i]:.2f}-{bin_edges[i+1]:.2f}" for i in range(len(hist_values))],
            "Frequency": hist_values.tolist(),
        }
        
        # Display as bar chart
        import pandas as pd
        df = pd.DataFrame(chart_data)
        st.bar_chart(data=df.set_index("Bin"), use_container_width=True)
    
    with col2:
        st.markdown("#### Distribution Summary")
        st.write(f"**Samples Generated:** {len(samples)}")
        st.write(f"**Mean:** `{result['mean']:.6f}`")
        st.write(f"**Standard Deviation:** `{result['std_dev']:.6f}`")
        st.write(f"**Variance:** `{result['variance']:.6f}`")
        st.write(f"**Range:** `[{result['min']:.6f}, {result['max']:.6f}]`")
    
    st.markdown("---")
    
    # Export samples
    with st.expander("📥 View Raw Samples"):
        st.json({
            "count": len(samples),
            "samples": [f"{s:.6f}" for s in samples[:20]] + (["..."] if len(samples) > 20 else []),
            "mean": result["mean"],
            "std_dev": result["std_dev"],
        })

st.markdown("---")

# ============================================================================
# EXPLANATION & HELP
# ============================================================================

with st.expander("❓ How Quantum Simulation Works"):
    st.markdown(
        """
        ### Single Quantum Sample
        
        When you click **"Sample One Branch"**, the system:
        1. Takes a branch identifier
        2. Generates a random quantum value (0 to 1)
        3. Returns the sample with timestamp
        
        This simulates quantum state collapse into a measurable value.
        
        ### Monte Carlo Simulation
        
        When you run **"Run Monte Carlo Simulation"**, the system:
        1. Generates N random samples (quantum measurements)
        2. Calculates statistical properties:
           - **Mean** — Average value
           - **Variance** — Spread of values
           - **Std Dev** — Standard deviation
        3. Creates a histogram showing the distribution
        
        This is useful for understanding probability distributions in quantum systems.
        """
    )
