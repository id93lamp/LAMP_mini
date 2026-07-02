"""
MCP Tool Interfaces
===================
Defines the tool schemas and dispatcher used by the Builder Agent.

LAMP uses the Model Context Protocol (MCP) to give the Builder structured
access to three external services:

1. get_cow_definition   — looks up a CoW definition/lemma by name from the
                          local ontology (metadata.json).  Fast and precise.

2. search_lean_explore  — performs BM25 keyword search over Mathlib via the
                          LeanExplore MCP server.  Use only for Mathlib lemmas.

3. get_theorem_family   — uses the CoW ontology to find related theorems in
                          the same conceptual family (for alternative strategies).

4. get_prerequisites    — uses the ontology to find prerequisite theorems.

5. get_lean_goal_state  — queries the Lean LSP to retrieve the exact tactic
                          goal state at the 'sorry' position.  Expensive (~15s).

External services / credentials
---------------------------------
All external endpoints are read from environment variables in .env:
  LEAN_EXPLORE_API_KEY  — API key for the LeanExplore cloud backend.
                          Leave empty to use the local backend.
  (LSP and ontology are purely local — no credentials needed.)
"""

import json
import asyncio
import os
import tempfile
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
load_dotenv()

# ── LeanExplore MCP client ────────────────────────────────────────────────────

class LeanExploreClient:
    """
    Wraps the LeanExplore MCP server for synchronous usage.
    Uses the 'api' backend if LEAN_EXPLORE_API_KEY is set,
    otherwise falls back to the 'local' backend.
    """
    _TIMEOUT_SECS = 60

    def __init__(self):
        self.api_key = os.getenv("LEAN_EXPLORE_API_KEY", "")
        if self.api_key:
            self.backend = "api"
            self.args = ["mcp", "serve", "--backend", "api", "--api-key", self.api_key]
        else:
            self.backend = "local"
            self.args = ["mcp", "serve", "--backend", "local"]
        self.command = "lean-explore"

    async def _call_tool_async(self, tool_name: str, arguments: dict) -> Any:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        server_params = StdioServerParameters(command=self.command, args=self.args)
        try:
            async with asyncio.timeout(self._TIMEOUT_SECS):
                async with stdio_client(server_params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        result = await session.call_tool(tool_name, arguments)
                        return result.content
        except asyncio.TimeoutError:
            print(f"[LeanExploreClient] Timeout ({self._TIMEOUT_SECS}s) calling {tool_name}.")
            return []
        except Exception as e:
            print(f"[LeanExploreClient] Error: {e}")
            return []

    def search_summary(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        content = asyncio.run(self._call_tool_async("search_summary", {"query": query, "limit": limit}))
        if not content:
            return []
        try:
            return json.loads(content[0].text).get("results", [])
        except Exception:
            return []


# ── Lean LSP MCP client ───────────────────────────────────────────────────────

class LeanLSPClient:
    """
    Wraps the lean-lsp-mcp server to query the tactic goal state at 'sorry'.
    The Lean project path must point to a built CoW project (lake build).
    """
    _TIMEOUT_SECS = 20

    def __init__(self, lean_project_path: str = "CoW"):
        self.lean_project_path = os.path.abspath(lean_project_path)
        self.command = "lean-lsp-mcp"
        self.args = ["--lean-project-path", self.lean_project_path, "--transport", "stdio"]

    async def _call_tool_async(self, tool_name: str, arguments: dict) -> Any:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        server_params = StdioServerParameters(command=self.command, args=self.args)
        try:
            async with asyncio.timeout(self._TIMEOUT_SECS):
                async with stdio_client(server_params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        result = await session.call_tool(tool_name, arguments)
                        return result.content
        except asyncio.TimeoutError:
            print(f"[LeanLSPClient] Timeout ({self._TIMEOUT_SECS}s).")
            return []
        except Exception as e:
            print(f"[LeanLSPClient] Error: {e}")
            return []

    def get_goal_at_sorry(self, lean_code: str) -> Optional[str]:
        """Write lean_code to a temp file in the project and query the LSP."""
        lines = lean_code.split("\n")
        sorry_line = next((i for i, l in enumerate(lines) if "sorry" in l), None)
        if sorry_line is None:
            return None
        tmp_path = os.path.join(self.lean_project_path, "_lsp_query_tmp.lean")
        try:
            with open(tmp_path, "w") as f:
                f.write(lean_code)
            file_uri = f"file://{tmp_path}"
            content = asyncio.run(self._call_tool_async("lean_goal", {
                "textDocument": {"uri": file_uri},
                "position": {"line": sorry_line, "character": 2},
            }))
            if not content:
                return None
            raw = content[0].text if content else ""
            try:
                data = json.loads(raw)
                goal = data.get("goals", data.get("goal", raw))
                return str(goal) if goal else None
            except Exception:
                return raw or None
        except Exception as e:
            print(f"[LeanLSPClient] Failed: {e}")
            return None
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


# ── CoW Ontology client ───────────────────────────────────────────────────────

class OntologyClient:
    """
    Local ontology client.  Reads metadata.json (shipped with LAMP_mini)
    to provide definition lookup, theorem family queries, and prerequisites.

    metadata.json was produced as part of the LAMP research and is not
    independently authored.  See README.md for attribution.
    """

    def __init__(self, metadata_path: str = "metadata.json"):
        self._corpus = []
        if os.path.exists(metadata_path):
            with open(metadata_path, encoding="utf-8") as fh:
                self._corpus = json.load(fh)
        else:
            print(f"[OntologyClient] Warning: {metadata_path} not found.")

    def get_item(self, name: str) -> Optional[Dict[str, Any]]:
        for item in self._corpus:
            if item.get("name") == name:
                return item
        return None

    def get_theorem_family(self, theorem_name: str) -> List[str]:
        item = self.get_item(theorem_name)
        if not item:
            return []
        family_tag = item.get("family") or item.get("module")
        if not family_tag:
            return []
        return [
            it["name"] for it in self._corpus
            if (it.get("family") == family_tag or it.get("module") == family_tag)
            and it["name"] != theorem_name
        ]

    def get_prerequisites(self, theorem_name: str) -> List[str]:
        item = self.get_item(theorem_name)
        if not item:
            return []
        return item.get("dependencies", [])


# ── Semantic ToolBox ──────────────────────────────────────────────────────────

class SemanticToolBox:
    """
    Aggregates all MCP tool schemas and dispatches tool calls from the Builder.
    """

    def __init__(self):
        self.explore_client = LeanExploreClient()
        self.ontology_client = OntologyClient()
        self.lsp_client = LeanLSPClient(lean_project_path="CoW")
        self._current_proof: str = ""

    def set_current_proof(self, proof: str):
        """Called by the Orchestrator so the LSP tool has the proof context."""
        self._current_proof = proof

    # ── Tool schemas (passed to the LLM) ─────────────────────────────────────

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "get_cow_definition",
                "description": (
                    "Retrieves the exact Lean 4 definition or lemma statement from the CoW "
                    "(Combinatorics on Words) ontology by name. "
                    "Use this FIRST to look up how CoW-specific types and lemmas are defined "
                    "(e.g., IsBorder, IsProperPrefix, Word, IsFactor). "
                    "This is faster and more accurate than general search for CoW-specific names."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The exact CoW definition or lemma name (e.g., 'IsBorder', 'IsProperPrefix', 'IsBorder.length_lt').",
                        }
                    },
                    "required": ["name"],
                },
            },
            {
                "name": "search_lean_explore",
                "description": (
                    "WARNING: Use this tool ONLY as a last resort when you need a Mathlib lemma name you have forgotten. "
                    "Do NOT use this for CoW definitions — use `get_cow_definition` instead. "
                    "Performs BM25 keyword search over Mathlib. May return noisy or irrelevant results."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The specific Mathlib concept or lemma name to search for. Keep queries short.",
                        }
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "get_theorem_family",
                "description": (
                    "Uses the CoW Ontology to find related theorems in the same conceptual family. "
                    "Use this ONLY if your initial plan hits a dead-end and you need inspiration for alternative approaches."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "theorem_name": {
                            "type": "string",
                            "description": "The name of the theorem to find related family members for.",
                        }
                    },
                    "required": ["theorem_name"],
                },
            },
            {
                "name": "get_prerequisites",
                "description": "Uses the CoW Ontology to find prerequisite theorems for a given theorem.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "theorem_name": {
                            "type": "string",
                            "description": "The name of the theorem to find prerequisites for.",
                        }
                    },
                    "required": ["theorem_name"],
                },
            },
            {
                "name": "get_lean_goal_state",
                "description": (
                    "Calls the Lean LSP to retrieve the exact tactic goal state at the current 'sorry' position. "
                    "Use this when you know the proof structure but need to see the exact hypotheses and target goal "
                    "that Lean sees at the sorry placeholder. Expensive (~15s) — call at most once per attempt."
                ),
                "input_schema": {"type": "object", "properties": {}, "required": []},
            },
        ]

    # ── Tool executor ─────────────────────────────────────────────────────────

    def execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> str:
        try:
            if tool_name == "get_cow_definition":
                name = tool_args.get("name", "")
                item = self.ontology_client.get_item(name)
                if not item:
                    return f"No CoW definition found for '{name}'. Check the spelling or try `search_lean_explore`."
                result = (
                    f"**{item['name']}** ({item.get('type', 'unknown')})\n"
                    f"Statement: `{item.get('statement', 'N/A')}`\n"
                    f"Description: {item.get('description', '')}\n"
                    f"File: {item.get('file', '')}\n"
                    f"Dependencies: {', '.join(item.get('dependencies', []))}"
                )
                if item.get("related_concepts"):
                    result += f"\nRelated: {', '.join(item['related_concepts'])}"
                return result

            elif tool_name == "search_lean_explore":
                query = tool_args.get("query", "")
                results = self.explore_client.search_summary(query, limit=5)
                if not results:
                    return "No results found in LeanExplore."
                return "\n\n".join(
                    f"Theorem: {r.get('name', 'Unknown')}\nDescription/Type: {r.get('description', '')}"
                    for r in results
                )

            elif tool_name == "get_theorem_family":
                name = tool_args.get("theorem_name", "")
                members = self.ontology_client.get_theorem_family(name)
                if not members:
                    return f"No family members found for {name}."
                return f"Family members of {name}: {', '.join(members)}"

            elif tool_name == "get_prerequisites":
                name = tool_args.get("theorem_name", "")
                prereqs = self.ontology_client.get_prerequisites(name)
                if not prereqs:
                    return f"No prerequisites found for {name}."
                return f"Prerequisites for {name}: {', '.join(prereqs)}"

            elif tool_name == "get_lean_goal_state":
                if not self._current_proof:
                    return "No proof context available."
                goal = self.lsp_client.get_goal_at_sorry(self._current_proof)
                if goal:
                    return f"Lean tactic goal state at 'sorry':\n{goal}"
                return "Lean LSP could not retrieve the goal state. Fall back to reasoning from the source context."

            else:
                return f"Error: Unknown tool '{tool_name}'"

        except Exception as e:
            return f"Error executing tool {tool_name}: {e}"
