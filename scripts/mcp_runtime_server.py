#!/usr/bin/env python3
"""Executable entrypoint for VeriScholar Runtime Diagnostics MCP Server.

Used by Antigravity / Gemini CLI to spawn the MCP server over stdio.
"""

import sys
import os

# Ensure repo packages are in sys.path
workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
core_src = os.path.join(workspace_dir, "packages", "core", "src")
if core_src not in sys.path:
    sys.path.insert(0, core_src)

from core.mcp.runtime_server import main

if __name__ == "__main__":
    main()
