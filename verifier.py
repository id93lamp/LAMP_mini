"""
Verifier
========
Lean 4 proof verifier via the REPL subprocess interface.

Adopted from the DeepSeek-Prover-V1.5 project:
  https://github.com/deepseek-ai/DeepSeek-Prover-V1.5
  (MIT License, Copyright 2024 DeepSeek)

This file provides two functions used throughout LAMP_mini:
  - verify_lean4_file(code, ...)  → raw result dict
  - parse_lean_result(raw)       → structured VerificationResult

The verifier works by writing the Lean 4 code as a JSON command to the
REPL's stdin and reading the JSON response from stdout.  The REPL must
be built in advance:
    cd repl && lake build

Only the single-threaded path is exposed here. The parallel scheduler
from the full LAMP system is omitted for simplicity.
"""

import os
import json
import time
import tempfile
import traceback
import subprocess
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

# ── Result dataclasses ────────────────────────────────────────────────────────

@dataclass
class SourcePosition:
    line: int
    column: int
    end_line: Optional[int] = None
    end_column: Optional[int] = None


@dataclass
class LeanGoal:
    hypotheses: List[str]
    target: str
    full_state: str
    source_position: SourcePosition


@dataclass
class LeanError:
    message: str
    raw_message: str
    source_position: SourcePosition


@dataclass
class LeanWarning:
    message: str
    raw_message: str
    source_position: SourcePosition


@dataclass
class VerificationResult:
    passed: bool
    complete: bool
    verify_time: float
    goals: List[LeanGoal] = field(default_factory=list)
    errors: List[LeanError] = field(default_factory=list)
    warnings: List[LeanWarning] = field(default_factory=list)
    verified_code: str = ""


# ── Lean REPL verifier ────────────────────────────────────────────────────────

HOME_DIR = os.path.expanduser("~")
DEFAULT_LAKE_PATH = os.path.join(HOME_DIR, ".elan", "bin", "lake")
DEFAULT_LEAN_WORKSPACE = "repl/"


def verify_lean4_file(
    code: str,
    lake_path: str = DEFAULT_LAKE_PATH,
    lean_workspace: str = DEFAULT_LEAN_WORKSPACE,
    timeout: int = 300,
) -> Dict[str, Any]:
    """
    Verify a Lean 4 code string using the REPL subprocess.

    Parameters
    ----------
    code          : Full Lean 4 source (imports + theorem).
    lake_path     : Path to the `lake` binary (default: ~/.elan/bin/lake).
    lean_workspace: Path to the Lean project with a built REPL (default: repl/).
    timeout       : Subprocess timeout in seconds.

    Returns
    -------
    dict with keys: pass, complete, errors, warnings, sorries, verify_time.
    """
    command = json.dumps({"cmd": code}, ensure_ascii=False)
    start = time.time()
    try:
        with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as tmp:
            tmp.write(command + "\r\n\r\n")
            tmp.seek(0)
            proc = subprocess.run(
                [lake_path, "exe", "repl"],
                stdin=tmp,
                capture_output=True,
                text=True,
                cwd=lean_workspace,
                timeout=timeout,
            )
        result = json.loads(proc.stdout)
        out = {
            "sorries":  result.get("sorries", []),
            "errors":   [m for m in result.get("messages", []) if m["severity"] == "error"],
            "warnings": [m for m in result.get("messages", []) if m["severity"] == "warning"],
            "infos":    [m for m in result.get("messages", []) if m["severity"] == "info"],
            "system_errors": None,
            "verified_code": code,
        }
        out["pass"] = not out["errors"]
        out["complete"] = (
            out["pass"]
            and not out["sorries"]
            and not any(
                "declaration uses 'sorry'" in w["data"] or "failed" in w["data"]
                for w in out["warnings"]
            )
        )
    except Exception:
        out = {
            "pass": False,
            "complete": False,
            "system_errors": traceback.format_exc(),
            "sorries": [],
            "errors": [],
            "warnings": [],
            "verified_code": code,
        }
    out["verify_time"] = time.time() - start
    return out


# ── Parser ────────────────────────────────────────────────────────────────────

def _parse_position(pos: Dict[str, Any]) -> SourcePosition:
    if not pos:
        return SourcePosition(line=0, column=0)
    return SourcePosition(
        line=pos.get("line", 0),
        column=pos.get("column", 0),
        end_line=pos.get("endLine"),
        end_column=pos.get("endColumn"),
    )


def parse_lean_result(raw: Dict[str, Any]) -> VerificationResult:
    """Convert a raw REPL result dict into a structured VerificationResult."""
    goals = []
    for sorry in raw.get("sorries", []):
        pos = _parse_position(sorry.get("pos", {}))
        full_state = sorry.get("goal", "")
        lines = full_state.strip().split("\n")
        hypotheses = []
        target = ""
        in_target = False
        for line in lines:
            if line.startswith("⊢"):
                in_target = True
                target = line[1:].strip()
            elif in_target:
                target += " " + line.strip()
            else:
                hypotheses.append(line.strip())
        goals.append(LeanGoal(hypotheses=hypotheses, target=target,
                               full_state=full_state, source_position=pos))

    errors = [
        LeanError(message=e.get("data", ""), raw_message=e.get("data", ""),
                  source_position=_parse_position(e.get("pos", {})))
        for e in raw.get("errors", [])
    ]
    warnings = [
        LeanWarning(message=w.get("data", ""), raw_message=w.get("data", ""),
                    source_position=_parse_position(w.get("pos", {})))
        for w in raw.get("warnings", [])
    ]

    passed = raw.get("pass", len(errors) == 0)
    has_sorry_warns = any("uses 'sorry'" in w.message for w in warnings)
    complete = passed and not goals and not has_sorry_warns

    return VerificationResult(
        passed=passed,
        complete=complete,
        verify_time=raw.get("verify_time", 0.0),
        goals=goals,
        errors=errors,
        warnings=warnings,
        verified_code=raw.get("verified_code", ""),
    )
