"""
AylinOS — Company Classifier
------------------------------
Backfills company_type for all manually imported jobs.
Run once: python3 scripts/classify_companies.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.schema import get_conn, init_db

def classify(name: str) -> str:
    n = name.lower()

    # Top AI Labs
    if any(x in n for x in ["anthropic", "openai", "deepmind", "google deepmind"]):
        return "top-ai-lab"

    # Big Tech
    if any(x in n for x in ["google", "microsoft", "meta ", "apple", "amazon", "salesforce", "oracle", "ibm", "adobe", "tiktok", "spotify", "airbnb", "uber", "waymo", "zoox"]):
        return "big-tech"

    # Big Finance / Enterprise
    if any(x in n for x in ["jpmorgan", "jpm", "morgan stanley", "goldman", "deutsche bank", "mastercard", "visa", "swift", "lloyds", "barclays", "bt group", "salesforce", "cerberus", "finastra", "entain", "allwyn", "trading hub", "dentsu", "endava", "rsm", "cfgi", "beazley", "marsh"]):
        return "big-finance"

    # VC / PE firms
    if any(x in n for x in ["ventures", "capital", "partners", "a16z", "sequoia", "lightspeed", "general catalyst", "index", "accel", "balderton", "towerbrook", "pivotal", "emerge", "per ", "walker hamill", "depthfirst", "greylock"]):
        return "vc-firm"

    # AI Startups / competitive tech
    if any(x in n for x in [
        "mistral", "cohere", "scale ai", "scale", "hugging", "perplexity", "glean",
        "elevenlabs", "harvey", "cognition", "condukt", "cogna", "tenex", "hebbia",
        "writer", "cursor", "nooks", "lovable", "cartesia", "decagon", "meticulous",
        "actively ai", "thread ai", "happyrobot", "deeptune", "normal ", "pallett",
        "pigment", "distyl", "kore.ai", "tracelight", "magnitude", "solveai", "yobiai",
        "magentic", "juniorai", "seamflow", "dobs.ai", "peregrine", "encord",
        "databricks", "snowflake", "datadog", "confluent", "linear", "attio",
        "clay ", "retool", "replit", "vercel", "cursor", "bolt", "lovable",
        "synthesia", "wayve", "physical intelligence", "skild", "standard bots",
        "formic", "nscale", "coreweave", "serval", "kana", "tracelight", "ankar",
        "ambience", "hockeystack", "thread", "poseidon", "dealops", "valence",
        "scope", "strella", "overview", "modelml", "tabs", "salient", "scrunch",
        "vector8", "gamma", "apron", "opencall", "mytos", "raycon", "dobs",
        "august ", "moment", "romi", "initi8", "lawhive", "ctrl alt", "zenos",
        "ghost ", "axon", "core ", "togather", "9fin", "causaly", "equals",
        "orbital", "talentpluto", "beacon", "tracelight", "matta", "flamapp",
        "governr", "aui", "loop ai", "deeptune", "edra", "northslope",
        "superannotate", "voy ", "wheely", "pallett", "deducta", "lindus",
        "confirmo", "zinier", "legora", "moloco", "attest", "terra ", "flatpay",
        "fyxer", "omnea", "verto", "normal", "adaptive", "heron", "mytos",
        "cartesia", "depthfirst", "wol", "multiplex", "alloy", "carwow",
        "plum ", "turnkey", "vts ", "lendable", "liberis", "nsave", "ethos",
        "wise ", "glean", "sphinx", "tts ", "centellic", "encord", "serval",
        "h ", " h,", "pigment", "graphcore", "tyea", "planlab", "conduct",
        "relay ", "softserve", "buro", "cobalt", "snorkel", "tilt ", "tricentis",
        "cordis", "d.local", "revin", "chime", "locate", "rowspace", "gamma",
        "palo alto", "multiverse", "workstream", "permit", "fay ", "voi ",
        "numan", "arrive ", "pebl", "via ", "rws", "airwallex", "rivian",
        "vendelux", "monzo", "sumup", "deblock", "deliveroo", "forter",
        "faculty", "thought machine", "mercor", "32co", "zip ", "parloa",
        "cohere", "twitch", "navan", "verve", "handshake", "valon",
        "notion", "figma", "airtable", "intercom", "lattice", "discord",
        "transformworks", "planlabs", "thread ai", "hived", "aventum",
        "abound", "asos", "pleo", "cleo ai", "vercel", "ramp",
        "strella", "lawhive", "logic monitor", "overview", "raycon",
        "opencall", "gen ", "wayve", "eucalyptus", "wolt", "bolt ",
        "fever ", "walker hamill", "trading hub", "liberty global",
        "plum", "vts", "lendable", "moment", "glossgenius", "gloss",
        "relay", "scribe", "textio", "mongodb", "oura", "plaid",
        "stripe", "databricks", "snowflake", "datadog"
    ]):
        return "ai-startup"

    # Fintech
    if any(x in n for x in ["ramp", "brex", "chime", "carta", "mercury", "deel", "gusto", "klarna", "affirm", "plaid", "stripe", "checkout", "revolut", "wise", "monzo", "starling", "raylo", "lendable", "liberis", "abound", "alloy", "flex ", "tabs ", "flatpay", "airwallex", "d.local", "chime", "zip", "paypal", "numan", "verto", "deblock", "sumup"]):
        return "fintech"

    # Health Tech
    if any(x in n for x in ["hinge health", "lyra", "spring health", "modern health", "hims", "eucalyptus", "anterior", "ambience", "fay "]):
        return "health-tech"

    # Recruiting / Staffing
    if any(x in n for x in ["burns sheehan", "la fosse", "salt ", "dartmouth partners", "walker hamill", "per ", "galaxy ventures", "pivotal"]):
        return "recruiter"

    return "startup"


def run():
    init_db()
    with get_conn() as conn:
        jobs = conn.execute("SELECT id, company FROM jobs WHERE company_type = '' OR company_type IS NULL").fetchall()
        updated = 0
        for job in jobs:
            ct = classify(job["company"])
            conn.execute("UPDATE jobs SET company_type=? WHERE id=?", (ct, job["id"]))
            updated += 1

    print(f"[Classify] Updated {updated} jobs.")

    # Show breakdown
    with get_conn() as conn:
        for row in conn.execute("SELECT company_type, COUNT(*) as n FROM jobs GROUP BY company_type ORDER BY n DESC").fetchall():
            print(f"  {row['company_type']:<20} {row['n']}")

if __name__ == "__main__":
    run()
