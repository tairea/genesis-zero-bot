#!/usr/bin/env python3
"""
live_server.py — Real-time knowledge graph visualization server.

Streams live graph updates to connected browsers via WebSocket.
New concepts and relations appear in real-time as documents are ingested.

Production: nginx reverse-proxies wss://graph.regentribe.org/ws -> ws://127.0.0.1:8788
Frontend:   static live.html on GitHub Pages connects to wss://graph.regentribe.org/ws

Usage:
    python live_server.py                        # WebSocket on 127.0.0.1:8788
    python live_server.py --port 8788            # custom port
    python live_server.py --with-http            # also serve live.html on :8787 (local dev)
"""

import asyncio
import json
import os
import sys
from functools import partial
from pathlib import Path

import websockets
from surrealdb import AsyncSurreal

# ── Config ────────────────────────────────────────────────────────────────────

DB_URL = os.environ.get("SURREALDB_URL", "ws://127.0.0.1:8000")
DB_PASS = os.environ.get("SURREAL_PASS", "root")
POLL_INTERVAL = 2  # seconds

VIZ_DIR = Path(__file__).parent / "viz"

TYPE_COLORS = {
    "entity": "#00d4ff", "system": "#ff6b35", "process": "#7b2cbf",
    "idea": "#2ec4b6", "event": "#ffbe0b", "person": "#e71d36",
    "place": "#06d6a0", "attribute": "#9b5de5", "quantity": "#f15bb5",
    "quality": "#00bbf9", "project": "#80ed99", "organization": "#ff9f1c",
    "skill": "#fdcb6e", "resource": "#74b9ff", "practice": "#a29bfe",
}


# ── SurrealDB helpers ─────────────────────────────────────────────────────────

async def get_db():
    db = AsyncSurreal(url=DB_URL)
    await db.connect()
    await db.signin({"username": "root", "password": DB_PASS})
    await db.use("semantic_graph", "main")
    return db


def _id_str(val):
    s = str(val) if hasattr(val, "table_name") else str(val)
    return s.split(":")[-1] if ":" in s else s


def _full_id(val):
    return str(val) if hasattr(val, "table_name") else str(val)


def transform_node(c: dict) -> dict:
    ctype = c.get("type", "concept")
    return {
        "id": _id_str(c.get("id", "")),
        "fullId": _full_id(c.get("id", "")),
        "name": c.get("name", "Unknown"),
        "type": ctype,
        "description": c.get("description", "") or "",
        "rung": c.get("rung", 0),
        "nars_confidence": c.get("nars_confidence", 0.5),
        "nars_frequency": c.get("nars_frequency", 0.5),
        "evidence_count": c.get("evidence_count", 1),
        "color": TYPE_COLORS.get(ctype, "#ffffff"),
    }


def transform_link(r: dict) -> dict | None:
    source = _id_str(r.get("in", ""))
    target = _id_str(r.get("out", ""))
    if not source or not target or source == target:
        return None
    return {
        "source": source,
        "target": target,
        "verb": r.get("verb", "RELATES_TO"),
        "verb_category": r.get("verb_category", ""),
        "evidence": r.get("evidence", "") or "",
        "nars_confidence": r.get("nars_confidence", 0.5),
    }


async def fetch_full_graph(db) -> dict:
    concepts = await db.query(
        "SELECT id, name, type, description, rung, "
        "nars_frequency, nars_confidence, evidence_count FROM concept"
    )
    relations = await db.query(
        "SELECT id, in, out, verb, verb_category, evidence, nars_confidence FROM relates"
    )
    nodes = [transform_node(c) for c in (concepts or []) if isinstance(c, dict)]
    links = [l for r in (relations or []) if isinstance(r, dict) for l in [transform_link(r)] if l]
    return {"nodes": nodes, "links": links}


async def fetch_counts(db) -> tuple[int, int]:
    cr = await db.query("SELECT count() as cnt FROM concept GROUP ALL")
    rr = await db.query("SELECT count() as cnt FROM relates GROUP ALL")
    cc = cr[0].get("cnt", 0) if cr and isinstance(cr, list) and cr else 0
    rc = rr[0].get("cnt", 0) if rr and isinstance(rr, list) and rr else 0
    return cc, rc


# ── WebSocket server ──────────────────────────────────────────────────────────

clients: set = set()


async def ws_handler(websocket):
    clients.add(websocket)
    print(f"Client connected ({len(clients)} total)")
    try:
        db = await get_db()
        try:
            data = await fetch_full_graph(db)
            init_msg = {"type": "init", **data, "openRouterApiKey": os.environ.get("OPENROUTER_API_KEY", "")}
            await websocket.send(json.dumps(init_msg, default=str))
        finally:
            await db.close()

        async for _ in websocket:
            pass  # keep alive
    finally:
        clients.discard(websocket)
        print(f"Client disconnected ({len(clients)} total)")


async def broadcast(msg: dict):
    if not clients:
        return
    payload = json.dumps(msg, default=str)
    dead = set()
    for ws in clients:
        try:
            await ws.send(payload)
        except websockets.exceptions.ConnectionClosed:
            dead.add(ws)
    clients -= dead


async def poll_loop():
    db = await get_db()
    last_cc, last_rc = await fetch_counts(db)
    print(f"Initial graph: {last_cc} concepts, {last_rc} relations")

    while True:
        await asyncio.sleep(POLL_INTERVAL)
        if not clients:
            continue

        try:
            cc, rc = await fetch_counts(db)

            if cc > last_cc:
                diff = cc - last_cc
                new = await db.query(
                    "SELECT id, name, type, description, rung, "
                    "nars_frequency, nars_confidence, evidence_count "
                    "FROM concept ORDER BY created_at DESC LIMIT $n",
                    {"n": diff},
                )
                for c in reversed(new or []):
                    if isinstance(c, dict):
                        node = transform_node(c)
                        await broadcast({"type": "node", "node": node})
                        print(f"  + node: {node['name']} ({node['type']})")
                last_cc = cc

            if rc > last_rc:
                diff = rc - last_rc
                new = await db.query(
                    "SELECT id, in, out, verb, verb_category, evidence, nars_confidence "
                    "FROM relates ORDER BY created_at DESC LIMIT $n",
                    {"n": diff},
                )
                for r in reversed(new or []):
                    if isinstance(r, dict):
                        link = transform_link(r)
                        if link:
                            await broadcast({"type": "link", "link": link})
                            print(f"  + link: {link['source']} --{link['verb']}--> {link['target']}")
                last_rc = rc

        except Exception as e:
            print(f"Poll error: {e}")
            try:
                await db.close()
            except Exception:
                pass
            db = await get_db()
            last_cc, last_rc = await fetch_counts(db)


# ── Optional HTTP server (local dev only) ─────────────────────────────────────

async def run_http_server(host: str, port: int, ws_port: int):
    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(VIZ_DIR), **kwargs)

        def do_GET(self):
            if self.path in ("/", "/live", "/live.html"):
                html = (VIZ_DIR / "live.html").read_text()
                ws_host = self.headers.get("Host", "localhost").split(":")[0]
                html = html.replace("__WS_URL__", f"ws://{ws_host}:{ws_port}/ws")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", len(html.encode()))
                self.end_headers()
                self.wfile.write(html.encode())
            else:
                super().do_GET()

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer((host, port), Handler)
    print(f"HTTP server: http://{host}:{port}/")
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, server.serve_forever)


# ── Main ──────────────────────────────────────────────────────────────────────

async def main(host: str, ws_port: int, http_port: int | None = None):
    print(f"\n  Knowledge Graph — Live Server")
    print(f"  ─────────────────────────────")
    print(f"  WebSocket: ws://{host}:{ws_port}/ws")
    print(f"  SurrealDB: {DB_URL}")
    if http_port:
        print(f"  HTTP (dev): http://{host}:{http_port}/")
    print()

    async with websockets.serve(ws_handler, host, ws_port):
        print(f"WebSocket listening on ws://{host}:{ws_port}/")
        poll_task = asyncio.create_task(poll_loop())
        try:
            if http_port:
                await run_http_server(host, http_port, ws_port)
            else:
                await asyncio.Future()  # run forever
        finally:
            poll_task.cancel()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Live knowledge graph WebSocket server")
    parser.add_argument("--host", default="127.0.0.1",
                        help="Bind address (default: 127.0.0.1, nginx proxies externally)")
    parser.add_argument("--port", type=int, default=8788, help="WebSocket port (default: 8788)")
    parser.add_argument("--with-http", action="store_true",
                        help="Also serve live.html on port 8787 (for local dev without nginx)")
    parser.add_argument("--http-port", type=int, default=8787, help="HTTP port when using --with-http")
    args = parser.parse_args()

    try:
        asyncio.run(main(args.host, args.port, args.http_port if args.with_http else None))
    except KeyboardInterrupt:
        print("\nShutdown.")
