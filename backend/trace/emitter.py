import asyncio
import json
import datetime
from typing import Dict, List, Any, Optional

class TraceEmitter:
    def __init__(self):
        # session_id -> list of events
        self._history: Dict[str, List[Dict[str, Any]]] = {}
        # session_id -> list of asyncio.Queue for SSE listeners
        self._listeners: Dict[str, List[asyncio.Queue]] = {}

    def emit(
        self,
        session_id: str,
        event_type: str,
        title: str,
        data: Dict[str, Any],
        status: str = "PASSED", # RUNNING, PASSED, BLOCKED, ESCALATED, WARNING
        rule_ids: Optional[str] = None,
        confidence: Optional[float] = None
    ) -> Dict[str, Any]:
        if session_id not in self._history:
            self._history[session_id] = []

        seq = len(self._history[session_id]) + 1
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        event = {
            "seq": seq,
            "session_id": session_id,
            "timestamp": timestamp,
            "type": event_type,
            "title": title,
            "status": status,
            "rule_ids": rule_ids,
            "confidence": confidence,
            "data": data
        }

        self._history[session_id].append(event)

        # Notify active SSE subscribers
        if session_id in self._listeners:
            for q in list(self._listeners[session_id]):
                try:
                    q.put_nowait(event)
                except asyncio.QueueFull:
                    pass

        return event

    def get_history(self, session_id: str, since_seq: int = 0) -> List[Dict[str, Any]]:
        history = self._history.get(session_id, [])
        if since_seq > 0:
            return [e for e in history if e["seq"] > since_seq]
        return list(history)

    async def subscribe(self, session_id: str, since_seq: int = 0):
        queue = asyncio.Queue(maxsize=100)
        if session_id not in self._listeners:
            self._listeners[session_id] = []
        self._listeners[session_id].append(queue)

        try:
            # Yield any historical events if reconnecting with sequence number
            historical = self.get_history(session_id, since_seq)
            for evt in historical:
                yield f"data: {json.dumps(evt)}\n\n"

            # Yield new incoming live events
            while True:
                evt = await queue.get()
                yield f"data: {json.dumps(evt)}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            if session_id in self._listeners and queue in self._listeners[session_id]:
                self._listeners[session_id].remove(queue)

trace_emitter = TraceEmitter()
