"""Cliente mínimo del demonio REA (session_daemon.py): rq.call(sock, tool, **args) -> objeto JSON del resultado."""
import json
import socket


def calls(sock: str, items: list[tuple[str, dict]]) -> list:
    s = socket.socket(socket.AF_UNIX)
    s.connect(sock)
    s.sendall((json.dumps({"calls": [{"tool": t, "args": a} for t, a in items]}) + "\n").encode())
    out = []
    for line in s.makefile("rb"):
        rec = json.loads(line)
        res = rec.get("result", rec)
        text = None
        for c in (res.get("content") or []):
            if c.get("type") == "text":
                text = c["text"]
                break
        try:
            out.append(json.loads(text) if text else res)
        except (TypeError, ValueError):
            out.append(text if text is not None else res)
    return out


def call(sock: str, tool: str, **args):
    return calls(sock, [(tool, args)])[0]


def norm(sock: str, items: list[tuple[str, dict]]) -> list:
    """Como calls(), pero devuelve solo el `normalized_result` (sin el sobre de evidencia)."""
    out = []
    for r in calls(sock, items):
        out.append(r.get("normalized_result", r) if isinstance(r, dict) else r)
    return out
