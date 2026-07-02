# LAMP_mini - A stripped down version of LAMP

> ⚠️ **This is a simplified, stripped-down version of LAMP.**
> It is **not representative of the system's full capability**, does not include the complete
> evaluation suite, and omits several production components.
---

## What is LAMP?

**LAMP** (Lean-based Agentic Framework with MCP and Proof Repair) is an automated theorem proving system for Lean 4
that operates on the **Combinatorics on Words (CoW)** domain. It uses a three-agent pipeline:

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

The key innovation is **CoW library grounding**: the Planner and Builder are given the full
source of the CoW Lean library as context, allowing them to reference existing lemmas by name
rather than re-deriving them.

---

## What is included / excluded in this package

| Component | Status | Notes |
|---|---|---|
| Orchestrator (Planner→Builder→Verifier loop) | ✅ Full | `orchestrator.py` |
| Planner Agent | ✅ Full | `planner.py` |
| Builder Agent | ✅ Full | `builder.py` |
| Lean REPL Verifier | ✅ Full | `verifier.py` - attributed below |
| MCP Tool interfaces | ✅ Full | `mcp_tools.py` |
| LLM backends: Claude, Kimi, DeepSeek | ✅ Full | `llm/` |
| CoW Lean Library (9 modules) | ✅ Subset | 29 declarations total (see CoW Library section) |
| 5-theorem benchmark | ✅ Included | `benchmark.py` |
| Full 90-theorem evaluation suite | ❌ Omitted | See paper for results |
| Ablation studies | ❌ Omitted | See paper for results |
| Parallel Lean worker scheduler | ❌ Omitted | Single-threaded only |
| CoW semantic ontology (`metadata.json`) | ✅ Subset | 29 declarations (matching the library subset) |

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

`elan` is the Lean toolchain manager. It will automatically download and manage the correct Lean version (v4.17.0) specified in the project's `lean-toolchain` files.

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

Since the MCP tools (`lean-explore` and `lean-lsp-mcp`) are run from the command-line, setting up and activating a virtual environment is required so they are placed in your `PATH`.

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
# Build the REPL executable
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

> ⏱️ **Note**: First-time build downloads Mathlib (~1 GB) and may take 10–30 minutes depending on your internet connection and CPU. Subsequent builds are incremental.

### 5. Configure API Keys

```bash
cp .env.example .env
```

Edit `.env` and fill in **one** of the API keys for the backend you wish to use, and set `PROVER_BACKEND` accordingly:

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

Ensure your Python virtual environment is activated (`source .venv/bin/activate`) and Lean environment is loaded (`source ~/.elan/env`) before running the scripts.

### 1. Quick Start (3 Theorems)

Run the quick-start demo which executes 3 theorems (Easy, Medium, and Hard) through the full proving pipeline:

```bash
python run_example.py
```

Expected output:
```
════════════════════════════════════════════════════════════════
  LAMP_mini - Quick-Start Example
  (This is a reduced demo. See paper for full system results.)
════════════════════════════════════════════════════════════════

[1/3] word_length_eq_zero_iff  [EASY]
      A word has length 0 iff it is the empty list.
─────────────────────────────────────────────────────────────────
[Planner] Reasoning: ...
[Planner] Plan: ...
[Builder] ...
[Orchestrator] ✅ Proof verified after patch!

✅  Proved in 18.3s
   := by
     simp [List.length_eq_zero]
...
```

### 2. Full Mini Benchmark (5 Theorems)

Run the benchmark suite covering all 5 selected representative theorems:

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

> ⚠️ This mini benchmark (5 theorems) is **not** comparable to the full evaluation (90 theorems) reported in the paper. Pass rates here will differ from paper results due to the smaller and different distribution of theorems, and reduced retry budgets.

---

## CoW Library

The `CoW/` directory contains a **Lean 4 Combinatorics on Words library** developed as part of
this research. It is organized as a Lean 4 package with Mathlib as a dependency.

### Modules and Declarations

| Module | Status | Key Declarations / Concepts |
|---|---|---|
| `Word` | ✅ Subset | `Word α`, `Word.concat` (`⬝`), `Word.length`, `Word.pow_succ`, `Monoid` |
| `Factor` | ✅ Subset | `IsPrefix` (`≤ₚ`), `IsSuffix` (`≤ₛ`), `IsFactor` (`≤f`) |
| `ProperPrefix` | ✅ Subset | `IsProperPrefix` (`<ₚ`), `IsProperPrefix.def` |
| `ProperSuffix` | ✅ Subset | `IsProperSuffix` (`<ₛ`), `IsProperSuffix.iff` |
| `Border` | ✅ Subset | `IsBorder` |
| `Period` | ✅ Subset | `IsPrimitive` |
| `Conjugacy` | ✅ Subset | `IsConjugate` definition |
| `Morphism` | ✅ Subset | `applyMorphism` (`•w`) |
| `Squares` | ✅ Subset | `IsSquare` definition |

The full modules (including `IsCoding`, `IsUniform`, `compMorphism`, `conjugate_trans`, etc.) are in the complete LAMP repository.

**Declaration count**: **29 total** across all 9 modules  - well within the
foundational subset the 5 benchmark theorems need to compile and run.

---

## MCP Tools

The Builder has access to 5 tools via the Model Context Protocol:

| Tool | Description |
|---|---|
| `get_cow_definition` | Looks up a CoW lemma/definition by name from the local ontology |
| `search_lean_explore` | BM25 search over Mathlib (last resort for Mathlib lemmas) |
| `get_theorem_family` | Finds related theorems in the same conceptual family |
| `get_prerequisites` | Finds prerequisite theorems from the ontology |
| `get_lean_goal_state` | Queries the Lean LSP for the exact tactic goal state at `sorry` |

Tool credentials are read from `.env` only (no hardcoded endpoints).
The LSP and ontology tools are purely local.

---

## Attribution

### Lean REPL Verifier

`verifier.py` contains code adopted from the **DeepSeek-Prover-V1.5** project:
> https://github.com/deepseek-ai/DeepSeek-Prover-V1.5
> MIT License - Copyright 2024 DeepSeek

The `verify_lean4_file()` function (subprocess-based REPL interface) is derived from
that codebase with minor modifications for single-threaded use.

### CoW Ontology (`metadata.json`)

`metadata.json` was produced as part of the LAMP research and encodes the semantic
relationships between CoW definitions and theorems. It is not independently authored -
it was constructed semi-automatically from the CoW Lean library during the LAMP study.

---

## Project Structure

```
LAMP_mini/
├── README.md              # This file
├── .env.example           # API key template (copy to .env)
├── .gitignore
├── requirements.txt
│
├── orchestrator.py        # Planner → Builder → Verifier loop
├── planner.py             # Strategic reasoning agent
├── builder.py             # Lean 4 code generation agent
├── verifier.py            # Lean REPL verifier (adopted from DeepSeek)
├── mcp_tools.py           # Tool schemas and MCP client wrappers
│
├── llm/
│   ├── claude.py          # Anthropic Claude backend
│   ├── kimi.py            # Moonshot Kimi K2 backend
│   └── deepseek.py        # DeepSeek backend
│
├── CoW/                   # Lean 4 CoW library (mini subset)
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
│       ├── Morphism.lean   
│       └── Squares.lean    
│
├── repl/                  # Lean REPL 
│
├── run_example.py         # Quick-start: 3 theorems end-to-end
├── benchmark.py           # Full mini benchmark: 5 theorems
└── metadata.json          # CoW ontology (see Attribution)
```

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
  `get_lean_goal_state` returns a graceful error and the Builder falls back to context-based reasoning.

**Lean REPL times out**  
→ First-time import compilation can take several minutes. Increase the `timeout` parameter
  in `verify_lean4_file()` calls if needed (default: 30s per theorem attempt).

**API rate limits**  
→ All LLM clients implement exponential backoff. For Claude: 5 retries with base delay 10s.
  For Kimi/DeepSeek: 5 retries with base delay 5s.

---

*LAMP_mini is a stripped version of the original LAMP system. The full system, evaluation suite, and
experimental results are described in the accompanying paper.*
