# Demand Radar

Finds companies and groups of people in West Bengal who are likely to need property soon, using public news, IPO filings and official notices. Each signal has its source, the client it fits, and a first message a person can send.

Part of the Matrix360 lead platform. Step 1 (Find) in the team plan.

## What's here

| File | What it is |
|---|---|
| `index.html` | The radar page. Open it in a browser. |
| `signals.json` | The signals. Every fact links to its source. |
| `push_to_shared_db.py` | Sends the leads in `signals.json` to Mayur's shared lead database. |
| `test_push.py` | Checks the mapping to Mayur's lead format. |
| `radar_agent_prompt.md` | Instructions for the AI agent that finds new signals. |
| `first_message_prompt.md` | Rules for writing the first message (Lakhotia version). |

## Send leads to the shared database

Needs Python 3.10+. No packages to install.

```
python push_to_shared_db.py                    # dry run: shows what would be sent
python push_to_shared_db.py --send             # sends to http://127.0.0.1:8000
SHARED_DB_URL=https://<mayur-url> python push_to_shared_db.py --send
```

Running it again is safe. The same lead is never saved twice.

## How it fits with everyone else

- **Mayur (shared database):** leads go to `POST /api/v1/leads` in the agreed format, with `source: "radar"` and the source links in `evidence`. No change to Mayur's code.
- **Pratha (scoring):** radar leads arrive with a low fit score (20 to 30) because plot size, budget and timeline are unknown. That is expected. The score goes up once someone confirms those details.
- **Tanmayi (consent gate):** radar leads are saved with `consent: false`, so her gate blocks WhatsApp for them. First contact is a LinkedIn message that a person approves and sends.
- **Avinash (ads):** the company list in `signals.json` can become an ad audience later.

## Rules

- Only facts from a page that was opened and checked. No guessed numbers or names.
- Only official public company contacts. No personal phone numbers or emails.
- Competitors and unnamed companies stay on the page and are never sent to the database.
- A person approves every message before it goes out.

## Tested

On 12 Oct 2026, against Mayur's `referralops_demo` running locally:
- Mayur's own test suite: 29 passed.
- First send: 4 leads saved. Beverage (no name) and 2 competitors skipped.
- Second send: the same 4 lead IDs came back. No duplicates were created.
- Read back with `GET /api/v1/leads?source=radar`: 4 leads, all `consent: false`, stage `new`.
