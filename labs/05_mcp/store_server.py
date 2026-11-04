"""An MCP server for the lab's support desk: two tools and one resource, over stdio.

Written for the MCP Python SDK 2.x (pip install "mcp>=2"), where v1's FastMCP was renamed MCPServer:
https://py.sdk.modelcontextprotocol.io/v2/migration/#fastmcp-renamed-to-mcpserver
(On mcp 1.x the same code works with:  from mcp.server.fastmcp import FastMCP as MCPServer)

You never run this file yourself: the client launches it as a subprocess and talks JSON-RPC over stdin/stdout.
"""
import json
from pathlib import Path

from mcp.server.mcpserver import MCPServer

KB = json.loads((Path(__file__).resolve().parent.parent / "data" / "kb.json").read_text(encoding="utf-8"))
ORDERS = {
    "ORD-55120": {"status": "Shipped", "item": "MX-750 mixer grinder", "total_rs": 1899},
    "ORD-90011": {"status": "Returned", "item": "cotton kurta", "total_rs": 649},
}

server = MCPServer("store-support")


@server.tool()
def lookup_order(order_id: str) -> dict:
    """Get status, item and total (in rupees) for an order id like ORD-12345."""
    if order_id not in ORDERS:
        return {"error": f"order {order_id} not found"}
    return {"order_id": order_id, **ORDERS[order_id]}


@server.tool()
def search_policies(query: str, k: int = 2) -> list[dict]:
    """Keyword search over the store's policy pages. Returns the best k pages with their ids."""
    words = {w for w in query.lower().split() if len(w) > 2}
    scored = sorted(KB, key=lambda d: -sum(w in d["text"].lower() or w in d["title"].lower() for w in words))
    return [{"id": d["id"], "title": d["title"], "text": d["text"]} for d in scored[:k]]


@server.resource("policies://index")
def policy_index() -> str:
    """The list of policy page ids and titles (data the host can show or the model can read)."""
    return "\n".join(f"{d['id']}: {d['title']}" for d in KB)


if __name__ == "__main__":
    server.run()  # stdio transport by default
