# Home Assistant GenAI BRI Demo – Design Document

## 1. Context & Purpose

This demo is part of the **DBUS 901 Doctoral Capstone Research** on **GenAI-driven Build, Release, and Integration (BRI) Engineering**.

The goal is to build a small but realistic pipeline around a Home Assistant configuration / custom component repository and then layer a GenAI-ready “agent” on top of that pipeline. This demo is the first reference implementation; the same pattern will later be reused for other projects such as PX4 and additional Home Assistant plugins.

Core objectives:

- Establish a **baseline BRI CI pipeline** (integration, build, test, release, policy).
- Instrument the pipeline with simple **metrics** (time, test counts, warnings).
- Add an **agent_analysis** step that consumes these metrics and emits recommendations.

## 2. Repository & Technology Stack

**Repository**

- GitHub: `anne500/home-assistant-bri-demo`  
- Based on an example Home Assistant configuration / custom component layout.

**Stack**

- Language: **Python**
- CI: **GitHub Actions**
- Tests: **pytest** + `pytest-homeassistant-custom-component`
- Target runtime: Home Assistant ecosystem (no physical devices required)

This makes the demo:

- Fast to build and test.
- Easy to run in GitHub-hosted runners.
- A good contrast to heavier C/C++ projects like PX4.

## 3. BRI Pipeline Overview

The CI pipeline is structured into five primary BRI stages, each implemented as a GitHub Actions job:

1. **Integration Agent (Repo & Config Checks)**  
   - Verifies expected structure (e.g., `custom_components/`, optionally `tests/`).  
   - Fails fast if the repository layout is obviously broken.

2. **Build Agent (Compile & Dependencies)**  
   - Sets up Python and installs test dependencies.  
   - Runs a lightweight “build” step: `python -m compileall custom_components`.  
   - Records total build time as `build_seconds`.

3. **Test Agent (Pytest)**  
   - Ensures a `tests/` directory exists (creates a minimal test if needed).  
   - Runs `pytest` and records test duration (`test_seconds`) and a simple test count (`tests_total`).  
   - Publishes a JUnit XML report as an artifact.

4. **Release Agent (Simulated Packaging)**  
   - Simulates packaging by zipping the `custom_components/` directory into `dist/custom_components.zip`.  
   - Records a boolean flag `release_simulated`.

5. **Policy Agent (Branch & Result Checks)**  
   - Applies simple policy checks (e.g., branch naming conventions for PRs).  
   - Records `policy_warnings` as a summary metric.

These five jobs form the **traditional BRI pipeline** for this repo.

## 4. Metrics & Instrumentation

Each job writes time-stamped logs and **METRIC** lines in a simple key–value format, for example:
```text
METRIC job=build_agent key=build_seconds value=1
METRIC job=test_agent key=test_seconds value=2
METRIC job=test_agent key=tests_total value=tests/test_sanity.py:1
METRIC job=release_agent key=release_simulated value=1
METRIC job=policy_agent key=policy_warnings value=0
```
## 5. GenAI-Ready Design (High-Level)

Before introducing any actual GenAI model, the pipeline is deliberately prepared for an “agent layer”:

- All jobs emit structured metrics (`METRIC ...`) that are easy to parse programmatically.
- Logs and artifacts are stored in a consistent layout across runs (`build.log`, `test.log`, `release.log`, `policy.log`, `pytest-report.xml`, `dist/`, etc.).
- A dedicated `agent_analysis` job runs at the end of the workflow and depends on all previous BRI jobs.
- The `agent_analysis` job executes a Python script (`agents/analyze_bri_run.py`) that:
  - Reads the logs and `METRIC` lines.
  - Aggregates simple metrics (build time, test time, number of tests, warnings).
  - Writes a human-readable summary and recommendation to `last_run_summary.txt`.

Sections 6–8 then document:
- The **numerical baseline metrics** from the first full BRI run.
- The **GenAI overlay plan** for BRI engineering.
- The **actual output** produced by the initial `agent_analysis` job.

## 6. Baseline BRI Metrics (Run #1)

This section records the metrics from the first successful run of the **Home Assistant BRI multi-agent baseline workflow** on GitHub Actions.

### 6.1 Cleaned Baseline Metrics Table

| Job           | Metric            | Value (Run #1)         | Notes                                  |
|---------------|-------------------|------------------------|----------------------------------------|
| Build Agent   | `build_seconds`   | **0 s**                | Build is effectively instant for this small repo. |
| Test Agent    | `test_seconds`    | **2 s**                | End-to-end pytest runtime.             |
| Test Agent    | `tests_total`     | **1 test**             | Only `tests/test_sanity.py` is present. |
| Release Agent | `release_simulated` | **1 (true)**         | Packaging step ran and produced `dist/custom_components.zip`. |
| Policy Agent  | `policy_warnings` | **0**                  | No policy violations detected.         |

### 6.2 Baseline Run Narrative

In the baseline Home Assistant BRI pipeline, the build step completed in effectively zero seconds, the test suite (one sanity test) ran in approximately two seconds, the simulated release step successfully packaged the custom components, and the policy checks reported zero warnings.

## 7. GenAI Overlay Plan for BRI Engineering

This section describes how a GenAI "agent layer" will sit on top of the baseline BRI pipeline for the Home Assistant demo. The same pattern will later be reused for additional demo projects (e.g., PX4, other plugins).

### 7.1 Conceptual Agent Roles

We keep five main roles under the Build, Release, and Integration (BRI) umbrella:

- **Integration Agent**  
  Reviews repository structure and configuration changes (e.g., `custom_components/`, `tests/`, YAML/JSON config). Suggests structural fixes or missing checks.

- **Build Agent**  
  Watches build times and dependency installation. Proposes optimizations (caching, dependency pruning, Python version selection).

- **Test Agent**  
  Monitors test suite size and failures. Suggests new test cases and areas of low coverage (e.g., "only 1 test present – add more scenario-based tests").

- **Release Agent**  
  Observes release artifacts and tagging patterns. Proposes versioning schemes, changelog entries, and criteria for promoting a build.

- **Policy Agent**  
  Enforces and explains rules: branch naming, required checks, and minimum test criteria (e.g., "block merge if tests_total < N" or if certain jobs fail).

In the current implementation these agents are represented as **CI jobs and scripts** that read logs and metrics and emit recommendations. In later phases, GenAI models can generate or edit these scripts directly.

### 7.2 Data Flow for GenAI-Assisted Analysis

1. **CI Run → Metrics & Logs**  
   The BRI workflow runs and produces:
   - `build.log`, `test.log`, `release.log`, `policy.log`
   - `pytest-report.xml`
   - `dist/custom_components.zip`

2. **Agent Context Packaging (Future Enhancement)**  
   A post-processing step will:
   - Parse all `METRIC` lines (e.g., `build_seconds`, `test_seconds`, `tests_total`).
   - Optionally normalize metrics into a small JSON file (e.g., `bri_metrics.json`).
   - Prepare a short textual summary (e.g., `agents/last_run_summary.md`).

3. **GenAI Agent Invocation (Outside this Repo)**  
   An external GenAI system (e.g., a separate “BRI Agent Orchestrator” service) will:
   - Read the metrics + summary.
   - Propose changes to:
     - CI workflow (YAML),
     - Test files,
     - Configuration and policies.

4. **Human-in-the-Loop Application**  
   Proposed changes are reviewed by a human engineer and merged via normal Git processes (PRs, code review). This keeps the pipeline safe, auditable, and aligned with engineering practice.

### 7.3 Planned Repo-Level Enhancements

To make this demo “GenAI-ready”, the following lightweight changes are planned:

1. **Agents Folder**

   Add an `agents/` directory to hold analysis scripts and summaries:

   - `agents/README.md` – describes the BRI agent roles.
   - `agents/analyze_bri_run.py` – parses logs and prints structured recommendations.
   - `agents/last_run_summary.md` – optional textual summary generated by the script.

2. **Agent Analysis Job in CI**

   Extend the GitHub Actions workflow with an additional job, for example:

   - `agent_analysis` job that:
     - Runs after the existing BRI jobs.
     - Downloads the artifacts (logs, reports).
     - Calls `python agents/analyze_bri_run.py`.
     - Emits “Agent Recommendations” into workflow logs and writes a markdown summary artifact.

3. **Cross-Demo Reuse**

   The same `agents/analyze_bri_run.py` and overall BRI structure can be reused in:
   - The PX4 demo repository.
   - Additional Home Assistant or plugin-based demos.
   - Future embedded or cloud-based BRI projects.

In this way the Home Assistant demo becomes the **first, simple reference implementation** of a GenAI-ready BRI pipeline, with metrics, logs, and a clear hook where GenAI agents can be integrated.

## 8. Agent Analysis Output (Run #1)

After enabling the `agent_analysis` job in the BRI workflow, the pipeline now runs a sixth job that downloads the build/test/release/policy logs, parses all `METRIC` lines, and emits a human-readable recommendation. The corresponding summary is stored in `last_run_summary.txt` as a CI artifact.

### 8.1 Metrics Observed by the Agent

For the first fully green run, the agent parsed the following metrics:

- `build_agent.build_seconds = 1`
- `test_agent.test_seconds = 2`
- `test_agent.tests_total = tests/test_sanity.py:1`  (interpreted as **1 trivial test**)
- `release_agent.release_simulated = 1`
- `policy_agent.policy_warnings = 0`

These values match the baseline metrics recorded earlier in Section 6.

### 8.2 Initial Agent Recommendation

Based on these metrics and the minimal test layout, the placeholder BRI agent produced the following recommendation (from `last_run_summary.txt` and the CI logs):

> **Agent Suggestion:** Only 1 trivial test detected. Consider adding more scenario-based tests for the custom components.

This closes the loop between:
1. A traditional BRI pipeline (integration, build, test, release, policy), and  
2. A GenAI-ready “agent layer” that consumes logs and metrics, then proposes concrete next steps for improving test depth and pipeline quality.

