import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent

st.set_page_config(
    page_title="PDE Solver AI | Seat 126",
    page_icon="🧠",
    layout="wide",
)

st.markdown("""
<style>
.stApp {background: #0b1220; color: #e5e7eb;}
.block-container {padding-top: 2rem; max-width: 1250px;}
h1, h2, h3 {color: #f8fafc !important;}
div[data-testid="stMetric"] {
    background: #172338;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #334155;
}
</style>
""", unsafe_allow_html=True)

st.title("🧠 Verifier-Guided PDE Solver")
st.caption("Seat 126 · Annapurna Labs Hackathon · Qwen3-8B on AWS Trainium2")

st.markdown(
    "An AI agent that proposes mathematical solutions, checks them using "
    "symbolic verification, and uses feedback to improve incorrect answers."
)

with st.sidebar:
    st.header("⚙️ Experiment Settings")
    level = st.selectbox(
        "Problem difficulty", [0, 1],
        format_func=lambda x: "Level 0 · Warm-up" if x == 0 else "Level 1 · Heat Equation"
    )
    sub = st.number_input("Subproblem", min_value=1, max_value=3, value=1)
    samples = st.slider("Candidates per round", 1, 4, 2)
    rounds = st.slider("Maximum rounds", 1, 4, 2)
    mode = st.radio("Execution mode", ["Saved results", "Live Trainium inference"])
    base_url = st.text_input(
        "Model API URL",
        value=os.environ.get("HEATROD_BASE_URL", "http://localhost:8000/v1"),
        disabled=mode == "Saved results",
    )
    st.caption("Live mode requires a reachable Qwen3-8B API.")

tab1, tab2, tab3 = st.tabs([
    "🚀 Solve & Verify",
    "📊 Results",
    "🏗️ Architecture"
])

with tab1:
    st.subheader("Solve a Heat Equation")
    st.latex(r"\frac{\partial u}{\partial t}=\alpha\frac{\partial^2 u}{\partial x^2}")
    st.write("The agent predicts how heat changes along a rod and verifies its mathematical solution.")

    if st.button("▶ Solve & Verify", type="primary", width="stretch"):
        if mode == "Saved results":
            st.info("Displaying previously recorded evidence. No live AI inference is performed.")
            result_dir = ROOT / "experiment-results"
            files = sorted(f for f in result_dir.rglob("*") if f.is_file()) if result_dir.exists() else []
            if files:
                st.success(f"Found {len(files)} saved experiment files.")
                for f in files[:20]:
                    st.write(f"📄 {f.relative_to(ROOT)}")
            else:
                st.warning("No saved experiment files were found.")
        else:
            with tempfile.TemporaryDirectory() as temp_dir:
                log_file = Path(temp_dir) / "attempts.jsonl"
                command = [
                    sys.executable, str(ROOT / "agent_verified_success.py"),
                    "--level", str(level),
                    "--sub", str(sub),
                    "--samples", str(samples),
                    "--rounds", str(rounds),
                    "--base", base_url,
                    "--log", str(log_file),
                ]

                with st.spinner("Qwen3-8B is solving and verifying the PDE..."):
                    try:
                        result = subprocess.run(
                            command, cwd=str(ROOT),
                            capture_output=True, text=True, timeout=300,
                        )
                    except subprocess.TimeoutExpired:
                        st.error("The run exceeded five minutes.")
                        result = None
                    except Exception as exc:
                        st.error(f"Unable to start agent: {exc}")
                        result = None

                if result is not None:
                    if result.returncode == 0:
                        st.success("Agent run completed. See verification details below.")
                    else:
                        st.error("Agent exited with an error.")

                    st.code(result.stdout or "(No standard output)", language="text")

                    if result.stderr:
                        with st.expander("Diagnostic output"):
                            st.code(result.stderr, language="text")

                    if log_file.exists():
                        attempts = []
                        for line in log_file.read_text().splitlines():
                            try:
                                attempts.append(json.loads(line))
                            except json.JSONDecodeError:
                                pass

                        if attempts:
                            df = pd.DataFrame(attempts)
                            if "reward" in df:
                                st.metric("Best verification score", f"{df['reward'].max():.2f} / 1.00")
                                st.line_chart(df["reward"])
                            st.dataframe(df, width="stretch")

    st.divider()
    st.subheader("🌡️ How heat diffuses through a rod")
    st.caption("Illustrative physics graph, not a prediction from the AI.")

    x = np.linspace(0, 1, 101)
    times = [0, 0.03, 0.08, 0.15]
    chart = pd.DataFrame({
        f"t = {t:.2f}": np.exp(-(np.pi ** 2) * t) * np.sin(np.pi * x)
        for t in times
    }, index=x)
    chart.index.name = "Position along rod"
    st.line_chart(chart)

with tab2:
    st.subheader("Recorded Experiment Results")
    st.caption("Small test sets. Independent selection is a separate experiment.")

    results = pd.DataFrame({
        "Method": ["Baseline", "Verifier-guided", "Independent selection"],
        "Successful": [4, 5, 2],
        "Total": [5, 5, 2],
    })
    results["Success rate (%)"] = 100 * results["Successful"] / results["Total"]

    st.dataframe(results, hide_index=True, width="stretch")
    st.bar_chart(results.set_index("Method")["Success rate (%)"])
    st.info("These recorded results are not generated by the dashboard.")

with tab3:
    st.subheader("How Our Agent Works")
    st.markdown("""
**1. User selects a PDE problem**

↓

**2. Qwen3-8B generates candidate solutions on Trainium2**

↓

**3. Python/SymPy verifier checks the equation and its conditions**

↓

**4. Incorrect answers receive feedback and another attempt**

↓

**5. Verified solutions are accepted and logged**
""")
    st.markdown(
        "[Seat 126 GitHub Submission]"
        "(https://github.com/yahavb/trainium-agent-labs/pull/11)"
    )

st.divider()
st.caption("Built by Team 126 · NYU · Annapurna Labs Hackathon")
