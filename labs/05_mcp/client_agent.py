"""Lab 05 - An MCP client that gives a local LLM the tools of any MCP server.

Lessons: 4.6 MCP (servers and clients), 4.2 tool calling.
Run:   python labs/05_mcp/client_agent.py

What happens:
  1. The client launches store_server.py as a subprocess (stdio transport).
  2. It lists the server's tools and reads a resource - no hand-written integration code.
  3. It converts each MCP tool's JSON Schema into an Ollama tool schema.
  4. qwen2.5:7b decides which tool to call; the client forwards the call to the MCP server.
Swap store_server.py for any other MCP server and the agent gains its tools with zero new glue.
"""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import chat, check_ollama, header  # noqa: E402

from mcp import Client, StdioServerParameters  # noqa: E402

SERVER = StdioServerParameters(command=sys.executable, args=[str(Path(__file__).with_name("store_server.py"))])


def to_ollama_schema(tool) -> dict:
    return {"type": "function", "function": {"name": tool.name, "description": tool.description or "",
                                             "parameters": tool.input_schema}}


async def run_agent(client, ollama_tools, question: str, max_steps: int = 5):
    msgs = [{"role": "system", "content": "You are a store support agent. Use the tools; never guess. "
                                          "Answer in 1-3 sentences and cite policy ids like [ship-03]."},
            {"role": "user", "content": question}]
    for step in range(1, max_steps + 1):
        m = chat(msgs, tools=ollama_tools, num_predict=200).message
        if not m.tool_calls:
            print(f"    step {step}: FINAL -> {m.content.strip()}")
            return
        msgs.append({"role": "assistant", "content": m.content or "", "tool_calls": [c.model_dump() for c in m.tool_calls]})
        for c in m.tool_calls:
            args = dict(c.function.arguments)
            result = await client.call_tool(c.function.name, args)  # JSON-RPC tools/call to the server
            text = "\n".join(getattr(b, "text", "") for b in result.content)
            print(f"    step {step}: MCP tools/call {c.function.name}({args}) -> {text[:110].replace(chr(10), ' ')}...")
            msgs.append({"role": "tool", "content": text, "tool_name": c.function.name})
    print(f"    STOPPED after {max_steps} steps")


async def main():
    check_ollama()
    async with Client(SERVER) as client:
        header("1) Connect and discover (no integration code written for this server)")
        print(f"  server={client.server_info.name!r}  negotiated protocol version={client.protocol_version}")
        tools = (await client.list_tools()).tools
        for t in tools:
            print(f"  tool {t.name}: {t.description}")
            print(f"       input schema: {json.dumps(t.input_schema)}")
        res = await client.read_resource("policies://index")
        first = res.contents[0].text.splitlines()
        print(f"  resource policies://index -> {len(first)} lines, e.g. {first[:3]}")

        header("2) Hand the MCP tools to the local LLM and let it work")
        ollama_tools = [to_ollama_schema(t) for t in tools]
        for q in ("Has my order ORD-55120 shipped, and can I still change its delivery address?",
                  "What is the warranty on the MX-750 mixer?"):
            print(f"  user: {q}")
            await run_agent(client, ollama_tools, q)

        header("3) Trust boundary")
        print("  Look: the model only ever saw tool NAMES, DESCRIPTIONS and RESULTS that the server chose to send.")
        print("  A malicious server can put instructions in any of those (tool poisoning / indirect injection),")
        print("  so treat third-party servers like third-party code: pin versions, least privilege, and keep")
        print("  approval gates for actions in YOUR client code (lab 04, lab 07).")


if __name__ == "__main__":
    asyncio.run(main())
