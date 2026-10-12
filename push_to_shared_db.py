"""Send Demand Radar leads into Mayur's shared lead database.

Dry run by default (prints what would be sent). Add --send to post.

    python push_to_shared_db.py                      # dry run
    python push_to_shared_db.py --send               # post to http://127.0.0.1:8000
    SHARED_DB_URL=https://... python push_to_shared_db.py --send

Only signals with kind "lead" are sent. Competitors and unnamed companies stay
on the radar page. Radar leads never claim consent, so Tanmayi's policy gate
blocks WhatsApp for them; first contact is a manual, human-approved LinkedIn
message.
"""
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).parent
DB_URL = os.environ.get("SHARED_DB_URL", "http://127.0.0.1:8000").rstrip("/")


def to_lead(signal, today=None):
    """Map one radar signal to Mayur's canonical LeadCreate payload, or None."""
    if signal.get("kind") != "lead" or not signal.get("company"):
        return None
    if not (signal.get("phone") or signal.get("email") or signal.get("linkedin_url")):
        return None  # Mayur's API needs at least one contact identifier
    today = today or date.today()
    lead = {
        "client": signal["client"],
        "property_type": signal["property_type"],
        "lead_type": signal.get("lead_type", "company"),
        "source": "radar",
        "evidence": " | ".join(signal["sources"])[:2000],
        "name": signal["contact_name"],
        "company": signal["company"],
        "phone": signal.get("phone"),
        "email": signal.get("email"),
        "linkedin_url": signal.get("linkedin_url"),
        "consent": False,
        "opted_out": False,
        "owner": "Peeyusha",
        "next_action": "Verify contact person, then send approved first message manually on LinkedIn",
        "next_action_date": (today + timedelta(days=2)).isoformat() + "T09:00:00",
        "industry": signal.get("industry"),
        "business_requirements": f"{signal['what_happened']} Why: {signal['why_it_matters']}"[:1000],
    }
    return {k: v for k, v in lead.items() if v is not None}


def idempotency_key(payload):
    # Same payload -> same key, so re-running the radar never creates a second lead.
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:32]
    return f"radar-{digest}"


def post(payload):
    req = urllib.request.Request(
        f"{DB_URL}/api/v1/leads",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Idempotency-Key": idempotency_key(payload)},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]


def main():
    send = "--send" in sys.argv
    signals = json.loads((HERE / "signals.json").read_text())["signals"]
    for s in signals:
        payload = to_lead(s)
        if payload is None:
            print(f"skip  {s['id']} ({s.get('kind')})")
            continue
        if not send:
            print(f"would send {s['id']}:\n{json.dumps(payload, indent=2)}\n")
            continue
        code, body = post(payload)
        if code == 201 and isinstance(body, dict):
            tag = ("already in" if body.get("idempotent_replay")
                   else "duplicate" if body.get("is_duplicate") else "saved")
            lead = body["lead"]
            print(f"{tag:9} {s['id']} -> {body['lead_id']} fit={lead.get('fit_score')} intent={lead.get('intent')}")
        else:
            print(f"error {code} {s['id']}: {body}")
    if not send:
        print(f"Dry run. Add --send to post to {DB_URL}")


if __name__ == "__main__":
    main()
