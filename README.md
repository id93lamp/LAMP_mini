# LAMP_mini

> ⚠️ **The LAMP framework code in this repository is a stripped-down version.**
> The orchestration pipeline (Planner → Builder → Verifier) is simplified for portability.
> However, **the CoW Lean library, the 90-theorem evaluation suite, and the raw evaluation logs
> are released in full** (see the sections below for details).

---

## What is LAMP?

**LAMP** (Lean-based Agentic Framework with MCP and Proof Repair) is an automated theorem proving
system for Lean 4 operating on the **Combinatorics on Words (CoW)** domain. It uses a three-agent pipeline:

```
Theorem + sorry
      │
      ▼
 ┌─────────────┐
 │  Planner    │  ← generates proof strategy using CoW library source
 └──────┬──────┘
        │ plan
        ▼
 ┌─────────────┐        ┌────────────────────┐
 │  Builder    │ ──────▶│  MCP Tools         │
 └──────┬──────┘ ◀───── │  (CoW lookup, LSP, │
        │ patch          │   Mathlib search)  │
        ▼               └────────────────────┘
 ┌─────────────┐
 │  Verifier   │  ← Lean REPL via subprocess
 └──────┬──────┘
        │
   ✅ Proved  /  ❌ Re-plan (up to max_replans)
```

The key innovation is **CoW library grounding**: the Planner and Builder are given the full source
of the CoW Lean library as context, allowing them to reference existing lemmas by name rather than
re-deriving them.

---

## What is included in this release

| Component | Status | Notes |
|---|---|---|
| Orchestrator (Planner→Builder→Verifier loop) | ✅ Mini | Simplified single-threaded version (`orchestrator.py`) |
| Planner Agent | ✅ Mini | `planner.py` |
| Builder Agent | ✅ Mini | `builder.py` |
| Lean REPL Verifier | ✅ Mini | `verifier.py` (attributed below) |
| MCP Tool interfaces | ✅ Mini | `mcp_tools.py` |
| LLM backends: Claude, Kimi, DeepSeek | ✅ Mini | `llm/` |
| CoW Lean Library (8 modules, 93 declarations) | ✅ **Full Release** | See [CoW Library](#cow-library) section |
| CoW Semantic Ontology (`metadata.json`) | ✅ **Full Release** | Definitions covering all modules |
| 90-Theorem Evaluation Suite (`evaluation_suite.json`) | ✅ **Full Release** | See [Evaluation Suite](#evaluation-suite) section |
| Raw Evaluation Logs (CoW & MiniF2F) | ✅ **Full Release** | Part of the full LAMP system; contains logs of the numbers reported in the paper (all 3 models under `logs/`) |
| 5-theorem mini benchmark | ✅ Included | `benchmark.py` |
| Ablation studies (full) | ❌ Omitted | See paper for results |
| Parallel Lean worker scheduler | ❌ Omitted | Single-threaded only |

---

## Requirements

### System

| Dependency | Version | Notes |
|---|---|---|
| Python | ≥ 3.10 | |
| Lean 4 | v4.17.0 | Via `elan` |
| `elan` | any | Lean toolchain manager |

### Python Packages

Installed packages (defined in `requirements.txt`):
- `anthropic` - Claude API
- `openai` - Kimi / DeepSeek (OpenAI-compatible)
- `mcp` - Model Context Protocol client (LeanExplore & LSP tools)
- `lean-explore` - LeanExplore Mathlib search tool
- `lean-lsp-mcp` - Lean LSP interaction tool
- `python-dotenv` - `.env` loading
- `requests` - HTTP for Claude direct API
- `numpy` - used by verifier utilities

---

## Setup Instructions

Follow these step-by-step instructions to set up the environment and build the necessary components.

### 1. Install Lean 4 via elan

`elan` is the Lean toolchain manager. It will automatically download and manage the correct Lean
version (v4.17.0) specified in the project's `lean-toolchain` files.

```bash
# Install elan (Lean toolchain manager)
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh

# Configure your current shell session
source ~/.elan/env
```

Verify that `elan` and `lake` are correctly installed:
```bash
lake --version
```

### 2. Set Up Python Virtual Environment

Since the MCP tools (`lean-explore` and `lean-lsp-mcp`) are run from the command-line, setting up
and activating a virtual environment is required so they are placed in your `PATH`.

```bash
# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Build the Lean REPL

The verifier calls the Lean REPL via a subprocess. It must be cloned and built locally:

```bash
cd repl
lake build
cd ..
```

### 4. Build the CoW Library

The `CoW` library provides the Combinatorics on Words domain context:

```bash
cd CoW
lake build
cd ..
```

> ⏱️ **Note**: First-time build downloads Mathlib (~1 GB) and may take 10–30 minutes depending on
> your internet connection and CPU. Subsequent builds are incremental.

### 5. Configure API Keys

```bash
cp .env.example .env
```

Edit `.env` and fill in **one** of the API keys for the backend you wish to use:

```ini
# Choose your backend (CLAUDE, KIMI, or DEEPSEEK)
PROVER_BACKEND=CLAUDE

# Fill in the matching key
CLAUDE_API_KEY=sk-ant-...      # https://console.anthropic.com
KIMI_API_KEY=sk-...            # https://platform.moonshot.cn
DEEPSEEK_API_KEY=sk-...        # https://platform.deepseek.com

# Mode: 'cow' = paper's main contribution (recommended)
PROVER_MODE=cow
```

---

## How to Run

Ensure your Python virtual environment is activated (`source .venv/bin/activate`) and the Lean
environment is loaded (`source ~/.elan/env`) before running.

### 1. Quick Start (3 Theorems)

Run the quick-start demo which executes 3 theorems (Easy, Medium, and Hard) through the full
proving pipeline:

```bash
python run_example.py
```

Expected output:
```
════════════════════════════════════════════════════════════════
  LAMP_mini - Quick-Start Example
════════════════════════════════════════════════════════════════

[1/3] word_length_eq_zero_iff  [EASY]
      A word has length 0 iff it is the empty list.
─────────────────────────────────────────────────────────────────
[Planner] Reasoning: ...
[Builder] ...
[Orchestrator] ✅ Proof verified after patch!

✅  Proved in 18.3s
   := by
     simp [List.length_eq_zero]
...
```

### 2. Full Mini Benchmark (5 Theorems)

Run the benchmark suite covering 5 representative theorems:

```bash
python benchmark.py
```

The benchmark covers **2 Easy · 2 Medium · 1 Hard** theorems across 4 CoW modules:

| # | Theorem | Module | Difficulty |
|---|---|---|---|
| 1 | `word_length_eq_zero_iff` | Word | Easy |
| 2 | `prefix_of_concat` | Factor | Easy |
| 3 | `prefix_antisymm` | Factor | Medium |
| 4 | `proper_prefix_trans` | ProperPrefix | Medium |
| 5 | `border_of_border_is_border` | Border | **Hard** |

Results are saved to `eval_results/lamp_mini_benchmark_<timestamp>.json`.
Proved theorems are saved as `.lean` files in `verified_proofs_mini/`.

> ⚠️ This mini benchmark (5 theorems) is **not** comparable to the full evaluation (90 theorems).
> See `logs/` for the raw logs of the full evaluation runs reported in the paper.

---

## CoW Library

The `CoW/` directory contains the **full Lean 4 Combinatorics on Words library** developed as part of this research. It is a **complete release** (not a subset). The library is organized as a Lean 4 package with Mathlib as a dependency.

For detailed architecture, custom notations, and the module-by-module declaration summary, please see **[CoW.md](CoW.md)**.

---

## Evaluation Suite

### `evaluation_suite.json`

The **full 90-theorem evaluation suite** used in the paper is released as `evaluation_suite.json`. Each entry encodes the theorem name, difficulty, module, formal Lean 4 statement, and a `sorry`-filled skeleton ready for the prover.

For a detailed distribution table and an annotated, human-readable overview of all 90 theorems, please see **[Cow_Evaluation_suite_theorem_reference.md](Cow_Evaluation_suite_theorem_reference.md)**.

### `metadata.json`

`metadata.json` encodes the **full CoW semantic ontology** (the definitions spanning all modules) with structured fields for each declaration (statement, description, tags, dependencies, related concepts, category, and difficulty). This is the ontology queried by the `get_cow_definition` and related MCP tools at runtime.

---

## Raw Evaluation Logs

The `logs/` directory contains the **complete raw logs** from all evaluation runs reported in the
paper, organized by model:

```
logs/
├── Claude/
│   ├── log_cow_batch1_claude.txt    # CoW suite: theorems 1-45 (Claude)
│   ├── log_cow_batch2_claude.txt    # CoW suite: theorems 46-90 (Claude)
│   └── log_minif2f_claude.txt       # MiniF2F benchmark (Claude)
├── Kimi/
│   ├── log_cow_batch1_kimi.txt      # CoW suite: theorems 1-45 (Kimi)
│   ├── log_cow_batch2_kimi.txt      # CoW suite: theorems 46-90 (Kimi)
│   └── log_minif2f_kimi.txt         # MiniF2F benchmark (Kimi)
└── Deepseek/
    ├── log_cow_batch1_deepseek.txt  # CoW suite: theorems 1-45 (DeepSeek)
    ├── log_cow_batch2_deepseek.txt  # CoW suite: theorems 46-90 (DeepSeek)
    └── log_minif2f_deepseek.txt     # MiniF2F benchmark (DeepSeek)
```

> **Note**: The CoW evaluation suite run was split into two batches of 45 theorems each (Batch 1:
> theorems 1–45, Batch 2: theorems 46–90) for practical scheduling reasons. The logs for each
> batch are kept separate per model. The MiniF2F logs were run in a single pass per model.

---

## MCP Tools

The Builder has access to 5 tools via the Model Context Protocol:

| Tool | Description |
|---|---|
| `get_cow_definition` | Looks up a CoW lemma/definition by name from the local ontology (`metadata.json`) |
| `search_lean_explore` | BM25 search over Mathlib (last resort for Mathlib lemmas) |
| `get_theorem_family` | Finds related theorems in the same conceptual family |
| `get_prerequisites` | Finds prerequisite theorems from the ontology |
| `get_lean_goal_state` | Queries the Lean LSP for the exact tactic goal state at `sorry` |

Tool credentials are read from `.env` only (no hardcoded endpoints).
The LSP and ontology tools are purely local.

---

## Project Structure

```
LAMP_mini/
├── README.md                               # This file
├── CoW.md                                  # Full CoW library documentation
├── Cow_Evaluation_suite_theorem_reference.md  # Annotated list of all 90 theorems
├── .env.example                            # API key template (copy to .env)
├── .gitignore
├── requirements.txt
│
├── orchestrator.py        # Planner → Builder → Verifier loop (mini)
├── planner.py             # Strategic reasoning agent (mini)
├── builder.py             # Lean 4 code generation agent (mini)
├── verifier.py            # Lean REPL verifier (adopted from DeepSeek)
├── mcp_tools.py           # Tool schemas and MCP client wrappers (mini)
│
├── llm/
│   ├── claude.py          # Anthropic Claude backend
│   ├── kimi.py            # Moonshot Kimi K2 backend
│   └── deepseek.py        # DeepSeek backend
│
├── CoW/                   # ★ Full Lean 4 CoW library (complete release)
│   ├── lakefile.toml
│   ├── lean-toolchain     # Pins Lean 4 v4.17.0
│   ├── CoW.lean           # Root import
│   └── CoW/
│       ├── Word.lean
│       ├── Factor.lean
│       ├── ProperPrefix.lean
│       ├── ProperSuffix.lean
│       ├── Border.lean
│       ├── Period.lean
│       ├── Conjugacy.lean
│       └── Morphism.lean
│
├── repl/                  # Lean REPL (submodule)
│
├── logs/                  # ★ Full raw evaluation logs (complete release)
│   ├── Claude/
│   │   ├── log_cow_batch1_claude.txt
│   │   ├── log_cow_batch2_claude.txt
│   │   └── log_minif2f_claude.txt
│   ├── Kimi/
│   │   ├── log_cow_batch1_kimi.txt
│   │   ├── log_cow_batch2_kimi.txt
│   │   └── log_minif2f_kimi.txt
│   └── Deepseek/
│       ├── log_cow_batch1_deepseek.txt
│       ├── log_cow_batch2_deepseek.txt
│       └── log_minif2f_deepseek.txt
│
├── evaluation_suite.json  # ★ Full 90-theorem evaluation suite (complete release)
├── metadata.json          # ★ Full CoW semantic ontology (complete release)
│
├── run_example.py         # Quick-start: 3 theorems end-to-end
└── benchmark.py           # Mini benchmark: 5 theorems
```

---

## Attribution

### Lean REPL Verifier

`verifier.py` contains code adopted from the **DeepSeek-Prover-V1.5** project:
> https://github.com/deepseek-ai/DeepSeek-Prover-V1.5
> MIT License - Copyright 2024 DeepSeek

The `verify_lean4_file()` function (subprocess-based REPL interface) is derived from
that codebase with minor modifications for single-threaded use.

### CoW Library & Ontology

The `CoW/` Lean library and `metadata.json` ontology were developed as original research
contributions of the LAMP project. They encode the foundational formalization of
Combinatorics on Words in Lean 4, a domain currently without Mathlib coverage.

---

## Troubleshooting

**`lake: command not found`**
→ Run `source ~/.elan/env` or restart your shell after installing elan.

**`lean-explore: command not found`**
→ The LeanExplore tool is optional. If not installed, `search_lean_explore` will timeout
  and fall back gracefully. Install with `pip install lean-explore` or set `LEAN_EXPLORE_API_KEY`
  to use the cloud backend.

**`lean-lsp-mcp: command not found`**
→ The LSP tool is optional. Install with `pip install lean-lsp-mcp`. Without it,
  `get_lean_goal_state` returns a graceful error and the Builder falls back to context-based
  reasoning.

**Lean REPL times out**
→ First-time import compilation can take several minutes. Increase the `timeout` parameter
  in `verify_lean4_file()` calls if needed (default: 30s per theorem attempt).

**API rate limits**
→ All LLM clients implement exponential backoff. For Claude: 5 retries with base delay 10s.
  For Kimi/DeepSeek: 5 retries with base delay 5s.

---

*The LAMP framework code in this repository is a stripped-down, portable version of the full system.
The full CoW formalization library, evaluation suite, semantic ontology, and raw evaluation logs
are released in their entirety. Full experimental details and ablation study results are described
in the accompanying paper.*
