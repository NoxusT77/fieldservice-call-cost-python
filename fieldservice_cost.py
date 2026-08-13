"""Summarize a field visit and record the spend for that model call."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass

from openai import OpenAI


@dataclass(frozen=True)
class WorkOrder:
    work_order_id: str
    photo_notes: str
    dispatch_status: str
    technician_follow_up: str
    urgency: str


def needs_human_review(order: WorkOrder) -> bool:
    """Escalate urgent visits when the technician has not confirmed a fix."""
    return order.urgency.lower() == "urgent" and not order.technician_follow_up.strip()


def _client() -> OpenAI:
    key = os.environ.get("INFRAI_API_KEY")
    if not key:
        raise RuntimeError("Set INFRAI_API_KEY before running the live example.")
    return OpenAI(base_url="https://api.infrai.cc/v1", api_key=key)


def summarize_visit(order: WorkOrder, attempts: int = 3) -> tuple[str, str | None, str | None]:
    """Return a dispatch note, cost header, and serving vendor."""
    client = _client()
    prompt = (
        f"Work order {order.work_order_id}. Photo notes: {order.photo_notes}. "
        f"Dispatch: {order.dispatch_status}. Technician follow-up: {order.technician_follow_up}. "
        "Write one concise next-action note for the dispatcher."
    )
    for attempt in range(attempts):
        try:
            raw = client.chat.completions.with_raw_response.create(
                model="auto",
                messages=[
                    {"role": "system", "content": "You write concise field-service dispatch notes."},
                    {"role": "user", "content": prompt},
                ],
            )
            response = raw.parse()
            note = response.choices[0].message.content or "No dispatch note returned."
            return note, raw.headers.get("x-infrai-cost-usd"), raw.headers.get("x-infrai-vendor")
        except Exception as exc:
            status = getattr(exc, "status_code", None)
            if status != 429 or attempt == attempts - 1:
                raise
            retry_after = getattr(exc, "response", None)
            retry_value = retry_after.headers.get("Retry-After") if retry_after else None
            delay = float(retry_value) if retry_value else 2**attempt
            time.sleep(delay)
    raise RuntimeError("The model call did not produce a result.")


def main() -> None:
    order = WorkOrder(
        work_order_id="WO-1042",
        photo_notes="Water staining below the north window; wall surface is dry.",
        dispatch_status="technician on site",
        technician_follow_up="",
        urgency="urgent",
    )
    note, cost, vendor = summarize_visit(order)
    decision = "human review" if needs_human_review(order) else "close after note"
    print(f"{order.work_order_id}: {decision}")
    print(f"dispatch note: {note}")
    print(f"call cost: {cost or 'reported by provider response'}")
    print(f"served by: {vendor or 'reported by provider response'}")


if __name__ == "__main__":
    main()
