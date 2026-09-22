#!/usr/bin/env python3
"""
Anthropic Model Context Protocol (MCP) Client & Gateway Dispatcher
=================================================================
Provides a universal bridge for Anthropic MCP stdio servers:
- Compliant with MCP JSON-RPC 2.0 stdio transport specification.
- Connects to any local MCP server (Python, Node/npx, Go, Rust).
- Features a built-in zero-dependency MCP server providing SQLite, FileTree, and Math tools.
- Enables autonomous agents to dynamically discover schemas and invoke external toolsets.
"""

import os
import sys
import json
import sqlite3
import argparse
import subprocess
import threading
import queue

# ------------------------------------------------------------------------------
# 1. MCP JSON-RPC 2.0 Stdio Client
# ------------------------------------------------------------------------------
class MCPStdioClient:
    def __init__(self, command_str):
        self.command_str = command_str
        self.proc = None
        self.msg_id = 1
        self.response_queue = queue.Queue()
        self.reader_thread = None
        self.is_running = False

    def start(self):
        self.proc = subprocess.Popen(
            self.command_str,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        self.is_running = True
        self.reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.reader_thread.start()
        
        # Initialize MCP handshake
        init_payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"roots": {"listChanged": True}},
                "clientInfo": {"name": "Antigravity-MCP-Bridge", "version": "1.0.0"}
            }
        }
        res = self.send_request(init_payload)
        
        # Send initialized notification
        notif = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        self.send_notification(notif)
        return res

    def _next_id(self):
        cur = self.msg_id
        self.msg_id += 1
        return cur

    def _read_loop(self):
        while self.is_running and self.proc and self.proc.poll() is None:
            line = self.proc.stdout.readline()
            if not line:
                break
            line_str = line.strip()
            if not line_str:
                continue
            try:
                data = json.loads(line_str)
                self.response_queue.put(data)
            except json.JSONDecodeError:
                pass

    def send_notification(self, payload):
        if not self.proc or self.proc.poll() is not None:
            return
        line = json.dumps(payload) + "\n"
        self.proc.stdin.write(line)
        self.proc.stdin.flush()

    def send_request(self, payload, timeout=12):
        if not self.proc or self.proc.poll() is not None:
            return {"error": "Server process is not running"}
        req_id = payload.get("id")
        line = json.dumps(payload) + "\n"
        self.proc.stdin.write(line)
        self.proc.stdin.flush()

        # Wait for matching response
        end_time = threading.Event()
        while True:
            try:
                resp = self.response_queue.get(timeout=timeout)
                if resp.get("id") == req_id:
                    return resp
            except queue.Empty:
                return {"error": f"Request timeout after {timeout}s"}

    def list_tools(self):
        req = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/list",
            "params": {}
        }
        return self.send_request(req)

    def call_tool(self, tool_name, arguments):
        req = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        return self.send_request(req)

    def stop(self):
        self.is_running = False
        if self.proc:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=2)
            except Exception:
                if self.proc:
                    self.proc.kill()

# ------------------------------------------------------------------------------
# 2. Built-in Lightweight MCP Server (Zero-Dependency Stdio Server)
# ------------------------------------------------------------------------------
def run_builtin_server():
    """Lightweight stdio MCP server for immediate local experimentation"""
    tools_spec = [
        {
            "name": "sqlite_query",
            "description": "Execute a safe SQL query on a local SQLite database and return results",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "db_path": {"type": "string", "description": "Path to SQLite file (or :memory:)"},
                    "query": {"type": "string", "description": "SQL SELECT query to execute"}
                },
                "required": ["db_path", "query"]
            }
        },
        {
            "name": "fs_tree",
            "description": "Scan a directory and return a compact file tree structure",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Root path to scan"},
                    "max_depth": {"type": "integer", "default": 2}
                },
                "required": ["path"]
            }
        },
        {
            "name": "safe_eval",
            "description": "Safely compute mathematical or scientific numerical expressions",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Math expression like 'math.sqrt(256) + math.log(10)'"}
                },
                "required": ["expression"]
            }
        }
    ]

    for line in sys.stdin:
        line_str = line.strip()
        if not line_str:
            continue
        try:
            req = json.loads(line_str)
        except Exception:
            continue

        method = req.get("method")
        msg_id = req.get("id")

        if method == "initialize":
            res = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "Builtin-MCP-Armory", "version": "1.0.0"}
                }
            }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        elif method == "tools/list":
            res = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": tools_spec}
            }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        elif method == "tools/call":
            params = req.get("params", {})
            name = params.get("name")
            args = params.get("arguments", {})
            content = []

            try:
                if name == "sqlite_query":
                    db_p = args.get("db_path", ":memory:")
                    query = args.get("query", "")
                    with sqlite3.connect(db_p) as conn:
                        cursor = conn.cursor()
                        cursor.execute(query)
                        rows = cursor.fetchall()
                        cols = [d[0] for d in cursor.description] if cursor.description else []
                    content.append({"type": "text", "text": json.dumps({"columns": cols, "rows": rows[:100]}, ensure_ascii=False)})

                elif name == "fs_tree":
                    root_p = args.get("path", ".")
                    max_d = args.get("max_depth", 2)
                    tree_list = []
                    for root, dirs, files in os.walk(root_p):
                        depth = root[len(root_p):].count(os.sep)
                        if depth > max_d:
                            dirs.clear()
                            continue
                        indent = "  " * depth
                        tree_list.append(f"{indent}{os.path.basename(root)}/")
                        for f in files[:20]:
                            tree_list.append(f"{indent}  {f}")
                    content.append({"type": "text", "text": "\n".join(tree_list[:150])})

                elif name == "safe_eval":
                    import math
                    expr = args.get("expression", "0")
                    allowed_names = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
                    allowed_names["math"] = math
                    val = eval(expr, {"__builtins__": {}}, allowed_names)
                    content.append({"type": "text", "text": str(val)})

                else:
                    content.append({"type": "text", "text": f"Unknown tool: {name}"})

                res = {"jsonrpc": "2.0", "id": msg_id, "result": {"content": content}}
            except Exception as e:
                res = {"jsonrpc": "2.0", "id": msg_id, "result": {"content": [{"type": "text", "text": f"Execution Error: {str(e)}"}], "isError": True}}

            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

# ------------------------------------------------------------------------------
# 3. CLI Main Entrypoint
# ------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Anthropic Model Context Protocol (MCP) Client & Gateway Dispatcher"
    )
    parser.add_argument("--server", "-s", default=None, help="Command to start MCP server (e.g. 'npx -y @modelcontextprotocol/server-filesystem /tmp')")
    parser.add_argument("--builtin-server", action="store_true", help="Internal flag: run the built-in MCP server daemon")
    parser.add_argument("--list-tools", action="store_true", help="Discover and list all registered tools from the MCP server")
    parser.add_argument("--call-tool", default=None, help="Name of tool to execute")
    parser.add_argument("--params", default="{}", help="JSON string of arguments to pass to the tool")
    parser.add_argument("--output", "-o", default=None, help="File path to save JSON results")

    args = parser.parse_args()

    if args.builtin_server:
        run_builtin_server()
        sys.exit(0)

    # If no server specified, default to self-contained built-in server
    server_cmd = args.server or f"python3 {os.path.abspath(__file__)} --builtin-server"

    print(f"🔌 [MCP-Bridge] Connecting to MCP Server: '{server_cmd}'...")
    client = MCPStdioClient(server_cmd)
    
    try:
        init_res = client.start()
        if "error" in init_res:
            print(f"❌ Connection failed: {init_res['error']}", file=sys.stderr)
            sys.exit(1)
            
        server_info = init_res.get("result", {}).get("serverInfo", {})
        print(f"✅ Handshake successful! Connected to: {server_info.get('name', 'MCP Server')} (v{server_info.get('version', 'unknown')})")

        output_data = {}

        if args.list_tools or not args.call_tool:
            tools_res = client.list_tools()
            tools_list = tools_res.get("result", {}).get("tools", [])
            output_data["tools"] = tools_list
            print("\n" + "=" * 65)
            print(f"🛠️ Available MCP Tools ({len(tools_list)} tools discovered):")
            print("=" * 65)
            for t in tools_list:
                desc = t.get("description", "No description")
                params = list(t.get("inputSchema", {}).get("properties", {}).keys())
                print(f"• \033[1;32m{t.get('name')}\033[0m: {desc}")
                print(f"  Parameters: {', '.join(params) if params else 'None'}")
            print("=" * 65)

        if args.call_tool:
            try:
                parsed_args = json.loads(args.params)
            except Exception as e:
                print(f"❌ Invalid JSON in --params: {e}", file=sys.stderr)
                sys.exit(1)

            print(f"\n⚡ Invoking MCP Tool: '{args.call_tool}' with params: {parsed_args}...")
            call_res = client.call_tool(args.call_tool, parsed_args)
            output_data["tool_result"] = call_res
            print("\n" + "=" * 65)
            print(f"📥 Tool Execution Output:")
            print("=" * 65)
            print(json.dumps(call_res.get("result", call_res), indent=2, ensure_ascii=False))
            print("=" * 65)

        if args.output:
            os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Results exported to: {args.output}")

    finally:
        client.stop()

if __name__ == "__main__":
    main()
