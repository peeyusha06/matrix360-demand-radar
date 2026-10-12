from datetime import date

from push_to_shared_db import idempotency_key, to_lead

TODAY = date(2026, 10, 12)


def test_lead_matches_mayur_contract():
    sig = {"kind": "lead", "id": "x", "client": "Lakhotia", "property_type": "industrial",
           "company": "Acme Ltd", "contact_name": "Contact to identify", "email": "a@acme.test",
           "sources": ["https://a", "https://b"], "what_happened": "W.", "why_it_matters": "Y."}
    p = to_lead(sig, TODAY)
    assert p["source"] == "radar" and p["consent"] is False and p["opted_out"] is False
    assert p["evidence"] == "https://a | https://b"
    assert p["next_action_date"] == "2026-10-14T09:00:00"
    assert "phone" not in p  # None fields are dropped, not sent as null
    assert idempotency_key(p) == idempotency_key(dict(p))


def test_skips_competitors_unnamed_and_contactless():
    assert to_lead({"kind": "competitor", "company": "X"}) is None
    assert to_lead({"kind": "needs_research", "company": None}) is None
    assert to_lead({"kind": "lead", "company": "X", "sources": []}) is None
