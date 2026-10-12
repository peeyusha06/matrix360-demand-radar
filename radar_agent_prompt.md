# Demand Radar: research instructions

Give this to an AI agent with web search (Claude with Firecrawl, or any agent that can read web pages). Run it once a week to start, daily later.

---

Find public events from the last 4 months that show a company or group of people in West Bengal is likely to need property soon. Match each to one client:

- **Lakhotia Industrial Complex** (industrial land, Ranihati–Amta Road, Howrah, plots 1–6+ acres): factory expansions, new plants, IPOs whose stated use of funds includes a new facility, warehouse or logistics growth in Howrah, Hooghly or Kolkata. Best fit: plastics and packaging, light engineering, FMCG, pharma, 3PL, agro-processing, electricals, textiles.
- **Shree Heights** (2 and 3 BHK flats, Chandannagar, Hooghly district): new plants or offices in Hooghly that bring in salaried staff.
- **Vrindavan Greens** (plots near Kalyani, Nadia): hiring drives at AIIMS Kalyani, JNM Hospital, University of Kalyani, IISER Kolkata, IIIT Kalyani, or industry in the Kalyani belt.

Good sources: Financial Express, Economic Times, Business Standard, The Telegraph, IPO prospectuses (the "Objects of the Issue" section), official notices on government and institute websites, WBIDC.

Rules:
1. Every fact must come from a page you opened. Put that page's URL in `sources`.
2. Never guess a number, date or company name. If the name is hidden, set `kind` to `needs_research`.
3. Contacts: only official public company contacts (company website contact page, company LinkedIn page). Never personal phone numbers or personal emails.
4. Competing industrial parks or housing projects go in as `kind: "competitor"`.
5. Skip anything already in `signals.json` (same company and same event).

Output: new entries for the `signals` list in `signals.json`, same fields as the existing entries. For each `lead`, write `first_message` using the rules in `first_message_prompt.md`: under 280 characters, open with the real event, one project fact, one easy ask, no AI-sounding words, no em dashes.

Then a person checks the new entries and runs:

```
python push_to_shared_db.py          # check what will be sent
python push_to_shared_db.py --send   # send to the shared database
```
