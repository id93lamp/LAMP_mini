"""
Planner Agent
=============
The Planner is the strategic reasoning component of the LAMP pipeline.

Given a Lean 4 theorem (with `sorry` as placeholder) and the CoW library
source as context, the Planner produces:
  - A <reasoning> block: step-by-step mathematical analysis.
  - A <plan> block: concrete proof strategy referencing specific CoW lemmas.

The Planner maintains conversation history so it can revise its strategy
when the Builder feeds back that the previous plan was unworkable.

Environment variables (set in .env):
  PROVER_BACKEND — CLAUDE | KIMI | DEEPSEEK  (default: CLAUDE)
  PROVER_MODE    — cow | normal              (default: cow)
"""

import re
import os
from typing import Optional, Tuple


class PlannerAgent:
    """
    Strategic reasoning agent.

    Maintains persistent conversation history across re-planning iterations
    so that the LLM remembers the theorem, prior plans, and Builder feedback.
    """

    def __init__(self):
        self.history = []
        mode = os.getenv("PROVER_MODE", "cow").lower().strip()

        if mode == "normal":
            # Generic Mathlib mode — no CoW library injection
            self.system_prompt = (
                "You are an expert Lean 4 mathematical strategist and theorem prover. "
                "Your task is to analyze a Lean 4 theorem goal and provide a concrete, step-by-step mathematical plan to prove it. "
                "Use your general knowledge of Lean 4 and Mathlib to formulate a proof strategy. "
                "You must first provide a <reasoning> block where you think step-by-step about the mathematical structure of the problem. "
                "Then, provide a <plan> block containing your step-by-step strategy. "
                "Do NOT write the final Lean 4 code. Only provide the conceptual mathematical plan. "
                "Another agent will attempt to implement your plan. If that agent fails, you will be given its failure reasoning and asked to revise your plan."
            )
        else:
            # CoW mode (paper's main contribution) — library-grounded planning
            self.system_prompt = (
                "You are an expert Lean 4 mathematical strategist and theorem prover. "
                "Your task is to analyze a Lean 4 theorem goal and provide a concrete, step-by-step mathematical plan to prove it. "
                "You will be given the full CoW library source in a <lean_context> block. "
                "Use this context to identify already-proven lemmas you can directly apply — do NOT re-prove what already exists. "
                "You must first provide a <reasoning> block where you think step-by-step about the mathematical structure of the problem. "
                "Then, provide a <plan> block containing your step-by-step strategy, referencing specific lemma names from the <lean_context>. "
                "Do NOT write the final Lean 4 code. Only provide the conceptual mathematical plan. "
                "Another agent will attempt to implement your plan. If that agent fails, you will be given its failure reasoning and asked to revise your plan."
            )

    # ── Public API ────────────────────────────────────────────────────────────

    def generate_plan(
        self,
        theorem_goal: str,
        builder_feedback: Optional[str] = None,
        lean_context: str = "",
    ) -> Tuple[str, str]:
        """
        Generate (or revise) a proof plan.

        Parameters
        ----------
        theorem_goal : str
            The full Lean 4 file (imports + theorem statement with sorry).
        builder_feedback : str, optional
            Failure reasoning from the Builder on the previous plan.
        lean_context : str
            Concatenated CoW library source (injected on first call only).

        Returns
        -------
        (reasoning, plan) : Tuple[str, str]
        """
        mode = os.getenv("PROVER_MODE", "cow").lower().strip()

        # On first call in cow mode, prepend the library source as a user message
        if not self.history and lean_context and mode == "cow":
            self.history.append({
                "role": "user",
                "content": (
                    f"Here is the full source of the CoW Lean library you are working with:\n"
                    f"<lean_context>\n{lean_context}\n</lean_context>\n\n"
                    "Please study the available definitions and proven lemmas before generating your plan."
                ),
            })
            self.history.append({
                "role": "assistant",
                "content": (
                    "Understood. I have reviewed the CoW library source and will reference "
                    "its definitions and lemmas in my plan."
                ),
            })

        prompt = f"Theorem Goal:\n```lean4\n{theorem_goal}\n```\n\n"
        if builder_feedback:
            prompt += (
                f"The Builder Agent failed to implement your previous plan. "
                f"Here is its feedback:\n{builder_feedback}\n\n"
            )
            if mode == "cow":
                prompt += "Please revise your mathematical strategy. Reference specific lemma names from the <lean_context> you were given."
            else:
                prompt += "Please revise your mathematical strategy."
        else:
            if mode == "cow":
                prompt += "Please generate your initial mathematical plan, referencing specific lemma names from the <lean_context> where applicable."
            else:
                prompt += "Please generate your initial mathematical plan."

        self.history.append({"role": "user", "content": prompt})
        response = self._call_llm(tools=None)

        response_text = ""
        if "content" in response and response["content"]:
            response_text = response["content"][0].get("text", "")
        self.history.append({"role": "assistant", "content": response_text})

        return self._parse_response(response_text)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _call_llm(self, tools):
        backend = os.getenv("PROVER_BACKEND", "CLAUDE").upper().strip()
        if backend == "DEEPSEEK":
            from llm.deepseek import generate_with_tools
        elif backend == "KIMI":
            from llm.kimi import generate_with_tools
        else:
            from llm.claude import generate_with_tools
        return generate_with_tools(self.history, self.system_prompt, tools=tools)

    def _parse_response(self, text: str) -> Tuple[str, str]:
        reasoning_match = re.search(
            r"<reasoning>(.*?)</reasoning>", text, re.DOTALL | re.IGNORECASE
        )
        plan_match = re.search(
            r"<plan>(.*?)</plan>", text, re.DOTALL | re.IGNORECASE
        )

        reasoning = reasoning_match.group(1).strip() if reasoning_match else None
        plan = plan_match.group(1).strip() if plan_match else None

        # Fallback: parse markdown headers
        if not plan:
            for header in [r"(?:###|##|#)\s*Plan\b", r"\*\*Plan:?\*\*", r"\bPlan\s*:"]:
                m = re.search(header, text, re.IGNORECASE)
                if m:
                    plan = text[m.end():].strip()
                    pre = text[: m.start()].strip()
                    for rh in [r"(?:###|##|#)\s*Reasoning\b", r"\*\*Reasoning:?\*\*", r"\bReasoning\s*:"]:
                        rm = re.search(rh, pre, re.IGNORECASE)
                        if rm:
                            reasoning = pre[rm.end():].strip()
                            break
                    else:
                        reasoning = pre
                    break

        if not reasoning:
            reasoning = text.strip()
        if not plan:
            plan = "No specific plan block detected."
        return reasoning, plan
