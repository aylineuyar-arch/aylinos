"""
AylinOS — Application History Importer
----------------------------------------
One-time import of existing application history into SQLite.

Status mapping (from spreadsheet color coding):
  no_reply             = white rows (no response received)
  interviewing         = yellow rows (active interview in progress)
  rejected_interview   = gray rows (eliminated after interview rounds)
  rejected_early       = red rows (eliminated via email, no recruiter engagement)

Run once from repo root:
  cd aylinos && python scripts/import_applications.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.schema import get_conn, init_db
from datetime import datetime

# ---------------------------------------------------------------------------
# Full application history
# Format: (company, role, date_string, status)
#
# status key:
#   "no_reply"           — white (no response)
#   "interviewing"       — yellow (active interview)
#   "rejected_interview" — gray (eliminated after rounds)
#   "rejected_early"     — red (eliminated via email, no recruiter engagement)
#
# Gray and yellow statuses to be confirmed — marked below based on spreadsheet.
# Feedback notes added separately via: python scripts/add_feedback.py
# ---------------------------------------------------------------------------

APPLICATIONS = [
    # ── Dec 2025 ──────────────────────────────────────────────────────────
    ("Matta.AI",          "Chief of Staff",                                          "2025-12-15", "no_reply"),
    ("BT Group",          "Senior Manager, Portfolio Strategic Initiatives",         "2026-01-08", "no_reply"),
    ("Skild AI",          "TBD (Summer Intern)",                                     "2026-01-01", "no_reply"),

    # ── Jan 2026 ──────────────────────────────────────────────────────────
    ("Mastercard",        "Product Innovation Manager (R-259893)",                  "2026-01-14", "no_reply"),
    ("Luminance",         "Product Manager",                                         "2026-01-14", "no_reply"),
    ("Burns Sheehan",     "Senior Product Manager",                                  "2026-01-14", "no_reply"),
    ("La Fosse",          "Senior Product Manager",                                  "2026-01-14", "no_reply"),
    ("Salt",              "RevOps & Strategy Manager",                               "2026-01-14", "no_reply"),
    ("Pump.co",           "Technical Product Manager",                               "2026-01-14", "no_reply"),
    ("Governr",           "Chief of Staff",                                          "2026-01-14", "no_reply"),
    ("Dartmouth Partners","Senior Strategy Manager",                                  "2026-01-14", "no_reply"),
    ("Flamapp.ai",        "Chief of Staff",                                          "2026-01-14", "no_reply"),
    ("AUI",               "Product Manager",                                         "2026-01-14", "no_reply"),
    ("Squad",             "Strategic Initiatives & Ops Manager",                     "2026-01-16", "no_reply"),
    ("Swap",              "Revenue Strategy & Operations Manager",                   "2026-01-16", "no_reply"),
    ("Google",            "Associate Manager, Product Strategy and Ops",             "2026-01-16", "no_reply"),
    ("Microsoft",         "Business Program Management - MBA",                       "2026-01-18", "no_reply"),
    ("Galaxy Ventures",   "General Talent Pool",                                     "2026-01-21", "no_reply"),
    ("Galaxy Ventures",   "Associate, Strategy & Corporate Development",             "2026-01-21", "no_reply"),
    ("Revolut",           "Product Strategy Manager",                                "2026-01-22", "no_reply"),

    # ── Apr 2026 ──────────────────────────────────────────────────────────
    ("Scale AI",          "Business Operations, GPS",                                "2026-04-05", "no_reply"),
    ("32Co",              "Operations and Strategy Associate",                       "2026-04-05", "no_reply"),
    ("Mercor",            "Strategic Project Lead",                                  "2026-04-05", "no_reply"),
    ("Orbital",           "Strategy",                                                "2026-04-05", "no_reply"),
    ("Dealops",           "Forward Deploy Specialist",                               "2026-04-05", "no_reply"),
    ("HappyRobot",        "Strategy and Operations",                                 "2026-04-05", "no_reply"),
    ("Valence",           "Associate, Strategy and Operations",                      "2026-04-05", "no_reply"),
    ("Mercor",            "Strategic Project Lead",                                  "2026-04-05", "no_reply"),
    ("Entain",            "Strategy Manager",                                        "2026-04-05", "no_reply"),
    ("eBay",              "Strategy & Ops Manager",                                  "2026-04-05", "no_reply"),
    ("Adobe",             "Business Ops Lead",                                       "2026-04-05", "no_reply"),
    ("PER",               "Venture Associate",                                       "2026-04-05", "no_reply"),
    ("Uber",              "Strategic Ops Lead",                                      "2026-04-05", "no_reply"),
    ("TikTok",            "Strategy and Ops",                                        "2026-04-05", "no_reply"),
    ("Greylock Partners", "Strategy and Ops Lead",                                   "2026-04-05", "no_reply"),
    ("Handshake",         "Strategic Project Lead",                                  "2026-04-05", "no_reply"),
    ("Valon",             "Strategy and Ops Senior Associate",                       "2026-04-05", "no_reply"),
    ("DataDog",           "Manager, GTM/Strategy/Ops",                              "2026-04-05", "no_reply"),
    ("Notion",            "Partner Strategy and Ops Manager",                        "2026-04-05", "no_reply"),
    ("Zip",               "GTM Strategy and Ops",                                    "2026-04-05", "no_reply"),
    ("Parloa",            "Business Generalist",                                     "2026-04-05", "no_reply"),
    ("GlossGenius",       "Strategy & Ops Manager",                                  "2026-04-05", "no_reply"),
    ("Cohere",            "Business Ops Lead",                                       "2026-04-05", "no_reply"),
    ("Figma",             "Business Ops Lead",                                       "2026-04-05", "no_reply"),
    ("Twitch",            "Senior Manager, Strategy and Ops",                        "2026-04-05", "no_reply"),
    ("Navan",             "GTM Strategy and Ops",                                    "2026-04-05", "no_reply"),
    ("Verve",             "Strategy and Ops Lead",                                   "2026-04-05", "no_reply"),
    ("Deeptune",          "Strategic Project Lead",                                  "2026-04-05", "no_reply"),
    ("Poseidon",          "Strategic Initiatives & Ops Manager",                     "2026-04-06", "no_reply"),
    ("Harvey",            "GTM Strategy and Ops",                                    "2026-04-07", "no_reply"),
    ("Scribe",            "",                                                        "2026-04-07", "no_reply"),
    ("Notion",            "GTM AI and Innovation Manager",                           "2026-04-07", "no_reply"),
    ("Hebbia",            "Solution Engineer",                                       "2026-04-07", "no_reply"),
    ("Checkout.com",      "Chief of Staff to CMO",                                   "2026-04-07", "no_reply"),
    ("TransformWorks",    "Chief of Staff",                                          "2026-04-07", "no_reply"),
    ("Textio",            "",                                                        "2026-04-09", "no_reply"),
    ("MongoDB",           "",                                                        "2026-04-09", "no_reply"),
    ("Snowflake",         "Strategic Initiatives Associate",                         "2026-04-09", "no_reply"),
    ("Oura",              "Senior Business Ops Program Manager",                     "2026-04-09", "no_reply"),
    ("Stripe",            "Product Strategy and Ops",                                "2026-04-09", "no_reply"),
    ("Plaid",             "Business Ops Lead",                                       "2026-04-09", "no_reply"),
    ("Uber",              "Senior Strategic Ops Manager",                            "2026-04-09", "no_reply"),
    ("Planlabs",          "Chief of Staff",                                          "2026-04-09", "no_reply"),
    ("Adobe",             "Associate, Corp Strategy",                                "2026-04-12", "no_reply"),
    ("Forter",            "Strategy and Ops Associate",                              "2026-04-12", "no_reply"),
    ("Flex",              "CoS/VP of Ops",                                           "2026-04-12", "no_reply"),
    ("Arch",              "Chief of Staff",                                          "2026-04-12", "no_reply"),
    ("Check",             "",                                                        "2026-04-12", "no_reply"),
    ("Crucibl",           "Chief of Staff",                                          "2026-04-12", "no_reply"),
    ("WorkBoard AI",      "",                                                        "2026-04-12", "no_reply"),
    ("Google",            "",                                                        "2026-04-12", "no_reply"),
    ("Ocean Infinity",    "Chief of Staff",                                          "2026-04-12", "no_reply"),
    ("Zen Educate",       "Product Ops Manager",                                     "2026-04-12", "no_reply"),
    ("Anterior",          "Director of Ops",                                         "2026-04-12", "no_reply"),
    ("Clay",              "Strategy and Ops Manager",                                "2026-04-12", "no_reply"),
    ("Cleo AI",           "Strategy and Ops Manager",                                "2026-04-12", "no_reply"),
    ("Actively AI",       "CoS to CEO",                                              "2026-04-13", "no_reply"),
    ("Northslope",        "Business Ops and Strategy",                               "2026-04-13", "no_reply"),
    ("HockeyStack",       "Strategy and Operations Principal / Manager",             "2026-04-13", "no_reply"),
    ("Cognition",         "Business Ops",                                            "2026-04-13", "no_reply"),
    ("Thread AI",         "Business Ops Strategist",                                 "2026-04-14", "no_reply"),
    ("Voy",               "Strategy and Ops Manager",                                "2026-04-14", "no_reply"),
    ("Wheely",            "Founder's Associate",                                     "2026-04-14", "no_reply"),
    ("Spotify",           "Markets Strategy and Ops Manager",                        "2026-04-14", "no_reply"),
    ("Pallett",           "GTM Chief of Staff",                                      "2026-04-14", "no_reply"),
    ("SuperAnnotate",     "Strategy and Ops Manager",                                "2026-04-14", "no_reply"),
    ("Edra",              "Strategy and Ops",                                        "2026-04-14", "no_reply"),
    ("Vertice",           "GTM Strategy and Ops",                                    "2026-04-15", "no_reply"),
    ("Loop AI",           "Product Strategy and Ops",                                "2026-04-15", "no_reply"),
    ("Via",               "Strategy and Ops",                                        "2026-04-15", "no_reply"),
    ("RWS",               "Group Chief of Staff",                                    "2026-04-15", "no_reply"),
    ("Airwallex",         "Operations Strategy Senior Manager",                      "2026-04-15", "no_reply"),
    ("Vector8",           "AI Strategist",                                           "2026-04-15", "no_reply"),
    ("Wayve",             "Commercial Strategy Manager",                             "2026-04-15", "no_reply"),
    ("Rivian",            "Chief of Staff",                                          "2026-04-15", "no_reply"),
    ("Seamflow",          "Chief of Staff",                                          "2026-04-15", "no_reply"),
    ("Multiverse",        "Chief of Staff",                                          "2026-04-15", "no_reply"),
    ("Verto",             "Expansion Lead",                                          "2026-04-16", "no_reply"),
    ("Faculty",           "Senior Manager",                                          "2026-04-16", "no_reply"),
    ("Thought Machine",   "Engineering Program Manager",                             "2026-04-16", "no_reply"),
    ("Monzo",             "Senior Product Ops",                                      "2026-04-16", "no_reply"),
    ("SumUp",             "Strategy and Ops Manager",                                "2026-04-16", "no_reply"),
    ("Deblock",           "Strategy and Ops Manager",                                "2026-04-16", "no_reply"),
    ("Vendelux",          "Strategic Business Operations Partner",                   "2026-04-16", "no_reply"),
    ("Deliveroo",         "Promotions Strategy Manager",                             "2026-04-16", "no_reply"),
    ("Forter",            "Strategy Ops Associate",                                  "2026-04-16", "no_reply"),
    ("Parloa",            "Business Generalist",                                     "2026-04-16", "no_reply"),
    ("Workstream",        "Strategic Project Lead",                                  "2026-04-16", "no_reply"),
    ("Fay",               "BizOps",                                                  "2026-04-16", "no_reply"),
    ("Permit Flow",       "BizOps",                                                  "2026-04-17", "no_reply"),
    ("Cobalt ID",         "Chief of Staff",                                          "2026-04-23", "no_reply"),
    ("Snorkel AI",        "Contributor Experience",                                  "2026-04-23", "no_reply"),
    ("Tilt",              "Strategy & Ops Manager",                                  "2026-04-23", "no_reply"),
    ("Deutsche Bank",     "Strategic Dev Lead",                                      "2026-04-23", "no_reply"),
    ("Ambience",          "Chief of Staff",                                          "2026-04-23", "no_reply"),
    ("Pebl",              "",                                                        "2026-04-23", "no_reply"),
    ("Relay",             "Strategy & Ops Manager",                                  "2026-04-23", "no_reply"),
    ("Arrive",            "BizOps",                                                  "2026-04-23", "no_reply"),
    ("Voi",               "Strategic Ops Lead",                                      "2026-04-23", "no_reply"),
    ("Numan",             "Strategy and Commercial Manager",                         "2026-04-23", "no_reply"),
    ("TikTok",            "Strategy & Ops Manager",                                  "2026-04-23", "no_reply"),
    ("Tricentis",         "GTM Strategy and Ops",                                    "2026-04-23", "no_reply"),
    ("Cordis",            "Strategic Initiatives Associate",                         "2026-04-23", "no_reply"),
    ("d.local",           "Strategy Manager",                                        "2026-04-23", "no_reply"),
    ("Revin",             "Strategy & Ops Manager",                                  "2026-04-23", "no_reply"),
    ("Serval",            "GTM Strategy and Ops",                                    "2026-04-23", "no_reply"),
    ("Chime",             "Strategic Ops Lead",                                      "2026-04-26", "no_reply"),
    ("Zoox",              "GTM",                                                     "2026-04-26", "no_reply"),
    ("Tabs",              "Strategy & Operations",                                   "2026-04-26", "no_reply"),
    ("Verve",             "Chief of Staff",                                          "2026-04-26", "no_reply"),
    ("JPMorgan",          "Digital Strategy",                                        "2026-04-26", "no_reply"),
    ("Salesforce",        "GTM Strategy Manager",                                    "2026-04-26", "no_reply"),
    ("Locate",            "Chief of Staff",                                          "2026-04-26", "no_reply"),
    ("Rowspace",          "Strategy and Ops",                                        "2026-04-26", "no_reply"),
    ("Scrunch",           "AI Strategist",                                           "2026-04-26", "no_reply"),
    ("Gamma",             "GTM",                                                     "2026-04-26", "no_reply"),
    ("Serval",            "GTM",                                                     "2026-04-26", "no_reply"),
    ("Salient",           "GTM Founders Office",                                     "2026-04-26", "no_reply"),
    ("Palo Alto Networks","GTM",                                                     "2026-04-26", "no_reply"),
    ("Multiverse",        "Data Portfolio Lead",                                     "2026-04-26", "no_reply"),
    ("Multiverse",        "AI Portfolio Lead",                                       "2026-04-26", "no_reply"),
    ("Mistral AI",        "AI Deployment Strategist",                                "2026-04-27", "no_reply"),
    ("Relay",             "Associate Chief of Staff",                                "2026-04-28", "no_reply"),
    ("Scale AI",          "Strategic Project Lead",                                  "2026-04-28", "no_reply"),
    ("Lindus",            "AI Tools Builder",                                        "2026-04-28", "no_reply"),
    ("Kore.ai",           "GTM Strategy and Intelligence Manager",                   "2026-04-28", "no_reply"),
    ("Valence",           "Strategy and Ops",                                        "2026-04-28", "no_reply"),
    ("Confirmo",          "Product Ops Manager",                                     "2026-04-29", "no_reply"),
    ("Allwyn",            "Business Manager to CTO",                                 "2026-04-29", "no_reply"),
    ("Faculty",           "Senior Manager, Strategy and Ops",                        "2026-04-29", "no_reply"),
    ("Deducta",           "AI Deployment Strategist",                                "2026-04-29", "no_reply"),
    ("Raylo",             "Strategy and Analytics Manager",                          "2026-04-29", "no_reply"),
    ("Swift",             "Digital Assets Strategic Execution Lead",                 "2026-04-29", "no_reply"),
    ("Zinier",            "Founder's Associate",                                     "2026-04-29", "no_reply"),
    ("Locate",            "Chief of Staff",                                          "2026-04-30", "no_reply"),
    ("Entain",            "Senior Strategy Manager",                                 "2026-04-30", "no_reply"),
    ("Finastra",          "Lead - Portfolio Strategy",                               "2026-04-30", "no_reply"),
    ("Cloudflare",        "Strategy / GTM",                                          "2026-04-30", "no_reply"),
    ("Legora",            "GTM Strategy and Ops",                                    "2026-04-30", "no_reply"),
    ("Peregrine",         "Deployment Strategist, UK",                               "2026-04-30", "no_reply"),
    ("Moloco",            "Strategic Growth Manager",                                "2026-04-30", "no_reply"),
    ("Celonis",           "VP GTM Operations",                                       "2026-04-30", "no_reply"),
    ("Attest",            "Workflow Ops",                                            "2026-04-30", "no_reply"),
    ("Terra",             "Partner Strategist",                                      "2026-04-30", "no_reply"),
    ("Orbital",           "Strategy",                                                "2026-04-30", "no_reply"),
    ("Flatpay",           "Chief of Staff",                                          "2026-04-30", "no_reply"),

    # ── May 2026 ──────────────────────────────────────────────────────────
    ("Veed",              "Strategy and Ops",                                        "2026-05-02", "no_reply"),
    ("Fyxer",             "Product Team",                                            "2026-05-02", "no_reply"),
    ("Omnea",             "Founding Engineer or similar",                            "2026-05-02", "no_reply"),
    ("Verto",             "Strategy Operations Analyst (Founder's Associate Scheme)","2026-05-02", "no_reply"),
    ("Pivotal Partners",  "Founder's Associate",                                     "2026-05-02", "no_reply"),
    ("Vertice",           "Business Development Representative",                     "2026-05-02", "no_reply"),
    ("Normal",            "Deployment Strategist, UK",                               "2026-05-02", "no_reply"),
    ("Coreweave",         "Deployment Strategist, UK",                               "2026-05-02", "no_reply"),
    ("Actively AI",       "GTM Ops Lead",                                            "2026-05-03", "no_reply"),
    ("Nscale",            "Droid",                                                   "2026-05-03", "no_reply"),
    ("Standard Bots",     "Strategy & Ops Manager",                                  "2026-05-05", "no_reply"),
    ("Decagon",           "Product Ops Manager",                                     "2026-05-05", "no_reply"),
    ("August",            "Strategy & Operations",                                   "2026-05-05", "no_reply"),
    ("Whatnot",           "Business Ops",                                            "2026-05-05", "no_reply"),
    ("Glean",             "Field Operations Manager, Strategic",                     "2026-05-05", "no_reply"),
    ("Hived",             "Strategic Initiatives",                                   "2026-05-06", "no_reply"),
    ("Aventum",           "Innovation Manager",                                      "2026-05-06", "no_reply"),
    ("Abound",            "Growth and Partnership Manager",                          "2026-05-06", "no_reply"),
    ("ASOS",              "Special Projects",                                        "2026-05-06", "no_reply"),
    ("Waymo",             "Project Management",                                      "2026-05-06", "no_reply"),
    ("Pleo",              "Strategic Program Manager",                               "2026-05-06", "no_reply"),
    ("Moloco",            "Implementation Manager",                                  "2026-05-06", "no_reply"),
    ("Cleo AI",           "Tech Partner Manager",                                    "2026-05-06", "no_reply"),
    ("JPMorgan",          "AI Manager",                                              "2026-05-06", "no_reply"),
    ("Decagon",           "Business Value Consultant",                               "2026-05-06", "no_reply"),
    ("Vercel",            "Startup Accelerator Manager",                             "2026-05-06", "no_reply"),
    ("Ramp",              "Manager, Partner Success Strategy & Operations",          "2026-05-06", "no_reply"),
    ("Distyl",            "AI Strategist (All Levels)",                              "2026-05-06", "no_reply"),
    ("Scope",             "Forward Deploy Engineer",                                 "2026-05-06", "no_reply"),
    ("Strella",           "Strategy & Operations Manager",                           "2026-05-06", "no_reply"),
    ("Normal",            "Deployment Strategist Lead",                              "2026-05-06", "no_reply"),
    ("Lawhive",           "Founder's Office",                                        "2026-05-06", "no_reply"),
    ("Pallett",           "Deployment Strategist (AI Team)",                         "2026-05-06", "no_reply"),
    ("Hebbia",            "AI Strategist",                                           "2026-05-06", "no_reply"),
    ("Logic Monitor",     "Chief of Staff",                                          "2026-05-06", "no_reply"),
    ("Adaptive",          "AI Product Operations Associate",                         "2026-05-06", "no_reply"),
    ("Towerbrook",        "AI Ops",                                                  "2026-05-06", "no_reply"),
    ("Overview",          "GTM Builder",                                             "2026-05-06", "no_reply"),
    ("Nscale",            "Strategic Operations Lead, Office of the CEO",            "2026-05-07", "no_reply"),
    ("Dobs.ai",           "Chief of Staff",                                          "2026-05-07", "no_reply"),
    ("Raycon",            "Chief of Staff",                                          "2026-05-07", "no_reply"),
    ("BOI",               "AI Transformation Lead",                                  "2026-05-07", "no_reply"),
    ("Opencall",          "Chief of Staff",                                          "2026-05-11", "no_reply"),
    ("Gen",               "",                                                        "2026-05-11", "no_reply"),
    ("Adaptive",          "Product Ops Manager",                                     "2026-05-11", "no_reply"),
    ("Pleo",              "Strategic Program Manager",                               "2026-05-11", "no_reply"),
    ("Mytos",             "Chief of Staff",                                          "2026-05-11", "no_reply"),
    ("Heron Data",        "Product Manager",                                         "2026-05-11", "no_reply"),
    ("Clay",              "GTM",                                                     "2026-05-11", "no_reply"),
    ("Wayve",             "Strategic Partnership Manager",                           "2026-05-11", "no_reply"),
    ("Wayve",             "Release Manager",                                         "2026-05-11", "no_reply"),
    ("Wayve",             "Technical Operations Manager",                            "2026-05-11", "no_reply"),
    ("Wayve",             "Robotaxi Technical Operations",                           "2026-05-11", "no_reply"),
    ("Ramp",              "AI Ops Specialist",                                       "2026-05-11", "no_reply"),
    ("Dentsu",            "Corp Strategy",                                           "2026-05-12", "no_reply"),
    ("Eucalyptus",        "Strategy & Ops Manager (Expansion) UK",                  "2026-05-12", "no_reply"),
    ("Wolt",              "Strategy & Ops",                                          "2026-05-12", "no_reply"),
    ("Ankar",             "GTM Delivery",                                            "2026-05-12", "no_reply"),
    ("Wise",              "Regional Strategy Lead",                                  "2026-05-12", "no_reply"),
    ("Multiplex",         "Product Owner (Data & AI)",                               "2026-05-12", "no_reply"),
    ("Nooks",             "AI Deployment Strategist",                                "2026-05-12", "no_reply"),
    ("Writer",            "AI Deployment Engineer",                                  "2026-05-12", "no_reply"),
    ("Bolt",              "Ops Manager",                                             "2026-05-12", "no_reply"),
    ("Coreweave",         "Product Growth Strategist",                               "2026-05-12", "no_reply"),
    ("Lovable",           "Deployment Strategist",                                   "2026-05-12", "no_reply"),
    ("Fever",             "Strategy and Ops",                                        "2026-05-12", "no_reply"),
    ("Revolut",           "Ops Manager",                                             "2026-05-12", "no_reply"),
    ("Alloy",             "Strategy Ops",                                            "2026-05-13", "no_reply"),
    ("Walker Hamill",     "Chief of Staff",                                          "2026-05-13", "no_reply"),
    ("Meticulous",        "Head of Ops",                                             "2026-05-13", "no_reply"),
    ("Trading Hub",       "Business Manager",                                        "2026-05-13", "no_reply"),
    ("Endava",            "Strategy",                                                "2026-05-13", "no_reply"),
    ("Romi",              "Ops Lead (Founder's Associate)",                          "2026-05-13", "no_reply"),
    ("Carwow",            "Strategy and Corp Dev Associate",                         "2026-05-13", "no_reply"),
    ("Liberty Global",    "Business Ops CEO Office",                                 "2026-05-13", "no_reply"),
    ("Initi8",            "Chief of Staff",                                          "2026-05-13", "no_reply"),
    ("Plum",              "Founder Associate",                                       "2026-05-13", "no_reply"),
    ("Turnkey",           "BizOps",                                                  "2026-05-13", "no_reply"),
    ("VTS",               "Chief of Staff",                                          "2026-05-13", "no_reply"),
    ("Lendable",          "CoS to CTO",                                              "2026-05-14", "no_reply"),
    ("Cartesia",          "GTM Strategist",                                          "2026-05-16", "no_reply"),
    ("Depthfirst",        "Biz Ops",                                                 "2026-05-16", "no_reply"),
    ("Ctrl Alt",          "Product Ops Manager",                                     "2026-05-16", "no_reply"),
    ("Zenos",             "Ops",                                                     "2026-05-17", "no_reply"),
    ("WD",                "Chief of Staff",                                          "2026-05-17", "no_reply"),
    ("Ghost",             "Chief of Staff",                                          "2026-05-17", "no_reply"),
    ("Formic",            "Chief of Staff",                                          "2026-05-17", "no_reply"),
    ("eBay",              "Strategy & Operations Manager",                           "2026-05-17", "no_reply"),
    ("Axon",              "Chief of Staff",                                          "2026-05-17", "no_reply"),
    ("Core",              "Chief of Staff",                                          "2026-05-17", "no_reply"),
    ("CFGI",              "CoS to COO",                                              "2026-05-17", "no_reply"),
    ("Writer",            "AI Deployment Engineer",                                  "2026-05-17", "no_reply"),
    ("Actively AI",       "Agent Ops Lead",                                          "2026-05-17", "no_reply"),
    ("Togather",          "AI Ops",                                                  "2026-05-17", "no_reply"),
    ("Nooks",             "AI Deployment Strategist",                                "2026-05-17", "no_reply"),
    ("9fin",              "AI Fluency Lead",                                         "2026-05-18", "no_reply"),
    ("SolveAI",           "Forward Deployed Engineer",                               "2026-05-18", "no_reply"),
    ("YobiAI",            "BizOps and Strategy",                                     "2026-05-18", "no_reply"),
    ("GlossGenius",       "Strategy & Ops",                                          "2026-05-18", "no_reply"),
    ("Personio",          "Sr. Customer Business Manager",                           "2026-05-18", "no_reply"),
    ("Causaly",           "Strategic Solutions & Market Expansions Lead - EMEA",     "2026-05-18", "no_reply"),
    ("Equals",            "Product Manager",                                         "2026-05-18", "no_reply"),
    ("Orbital",           "Product Manager",                                         "2026-05-18", "no_reply"),
    ("Flex",              "Strategy & Ops",                                          "2026-05-18", "no_reply"),
    ("Physical Intelligence", "Strategy & Ops",                                     "2026-05-18", "no_reply"),
    ("TalentPluto",       "Strategy & Ops",                                          "2026-05-18", "no_reply"),
    ("Cerberus Capital",  "AI Deployment Strategist",                                "2026-05-18", "no_reply"),
    ("Stripe",            "Product Manager, GTM",                                    "2026-05-18", "no_reply"),
    ("Beacon Software",   "Portfolio PM",                                            "2026-05-18", "no_reply"),
    ("Databricks",        "Deployment Strategist",                                   "2026-05-18", "no_reply"),
    ("Condukt",           "Agent Deployment Strategist",                             "2026-05-18", "no_reply"),
    ("Magnitude Consulting", "Deployment Strategist",                               "2026-05-18", "no_reply"),
    ("Kana",              "AI Solutions Lead",                                       "2026-05-20", "no_reply"),
    ("Tabs",              "Product Launch Manager",                                  "2026-05-20", "no_reply"),
    ("Lendable",          "Product Manager",                                         "2026-05-20", "no_reply"),
    ("Plaid",             "Integration Operations Program Manager",                  "2026-05-20", "no_reply"),
    ("SolveAI",           "Deployment Strategist",                                   "2026-05-20", "no_reply"),
    ("HappyRobot",        "Deployment Strategist",                                   "2026-05-20", "no_reply"),
    ("OpenAI",            "Deployment Strategist",                                   "2026-05-20", "no_reply"),
    ("Normal",            "Deployment Strategist",                                   "2026-05-20", "no_reply"),
    ("Nsave",             "Founder's Associate",                                     "2026-05-20", "no_reply"),
    ("Cursor",            "AI Deployment Manager",                                   "2026-05-20", "no_reply"),
    ("Morgan Stanley",    "Product Manager - AI and Transformation Strategy",        "2026-05-20", "no_reply"),
    ("Condukt",           "Agentic Product Owner",                                   "2026-05-20", "no_reply"),
    ("Beazley",           "Product Owner",                                           "2026-05-20", "no_reply"),
    ("Ethos",             "Strategic Project Lead",                                  "2026-05-20", "no_reply"),
    ("Tracelight",        "AI Deployment Team",                                      "2026-05-23", "no_reply"),
    ("Wise",              "AI Implementation Senior Manager, TGS",                  "2026-05-23", "no_reply"),
    ("Glean",             "AI Outcomes Manager, London",                             "2026-05-23", "no_reply"),
    ("Glean",             "AI Outcomes Manager, West",                               "2026-05-23", "no_reply"),
    ("Pallett",           "Chief of Staff",                                          "2026-05-24", "no_reply"),
    ("Sphinx",            "Chief of Staff",                                          "2026-05-24", "no_reply"),
    ("TTS",               "Founder's Associate",                                     "2026-05-24", "no_reply"),
    ("RSM",               "AI Transformation Leader",                                "2026-05-24", "no_reply"),
    ("Centellic",         "Senior Strategy Manager",                                 "2026-05-24", "no_reply"),
    ("JPMorgan",          "AI Strategist",                                           "2026-05-24", "no_reply"),
    ("Encord",            "Deployment Strategist",                                   "2026-05-24", "no_reply"),
    ("Serval",            "GTM Strategy & Ops Manager (Customer)",                   "2026-05-24", "no_reply"),
    ("Actively AI",       "Agent Engagement Manager",                                "2026-05-24", "no_reply"),
    ("Attio",             "Product",                                                 "2026-05-25", "no_reply"),
    ("Lloyds Bank",       "AI Strategy Lead",                                        "2026-05-25", "no_reply"),
    ("Anthropic",         "Applied AI Architect, Startups",                          "2026-05-25", "no_reply"),
    ("Anthropic",         "Forward Deployed Engineer, Applied AI",                   "2026-05-25", "no_reply"),
    ("Anthropic",         "Applied AI Architect, Commercial",                        "2026-05-25", "no_reply"),
    ("Anthropic",         "Applied AI Architect, Enterprise Tech",                   "2026-05-25", "no_reply"),
    ("OpenAI",            "AI Deployment Engineer - ChatGPT Ecosystem",              "2026-05-25", "no_reply"),
    ("Scale AI",          "AI Deployment Strategist, Enterprise",                    "2026-05-26", "no_reply"),
    ("Moment",            "Strategy & Ops Leader",                                   "2026-05-27", "no_reply"),
    ("Seamflow",          "Product Engineer",                                        "2026-05-27", "no_reply"),
    ("GlossGenius",       "Strategy & Operations Manager",                           "2026-05-27", "no_reply"),
    ("Morgan Stanley",    "AI Product Manager",                                      "2026-05-28", "no_reply"),
    ("Meticulous",        "GTM Operator",                                            "2026-05-28", "no_reply"),
    ("Ankar",             "Founder Associate",                                       "2026-05-28", "no_reply"),
    ("Apron",             "GTM Engineer",                                            "2026-05-28", "no_reply"),
    ("Mistral AI",        "AI Deployment Strategist, AI4Engineering - EMEA",        "2026-05-28", "no_reply"),
    ("Liberis",           "Product Ops Manager",                                     "2026-05-28", "no_reply"),
    ("Meticulous",        "Founder Associate",                                       "2026-05-28", "no_reply"),
    ("Revolut",           "AI Deployment Engineer",                                  "2026-05-28", "no_reply"),
    ("Bending Spoons",    "Office of the CEO",                                       "2026-05-28", "no_reply"),
    ("Scale AI",          "Strategic Project Lead, Gen AI",                          "2026-05-28", "no_reply"),
    ("Abound",            "Chief of Staff to CTO",                                   "2026-05-30", "no_reply"),
    ("ModelML",           "Strategy and Ops",                                        "2026-05-31", "no_reply"),
    ("Tenex",             "AI Strategist",                                           "2026-05-31", "rejected_interview"),
    ("Cognition",         "Applied AI Transformation Manager",                       "2026-05-31", "no_reply"),

    # ── Jun 2026 ──────────────────────────────────────────────────────────
    ("Tabs",              "AI Strategist (All Levels)",                              "2026-06-01", "no_reply"),
    ("Airbnb",            "Senior Growth & Operations Manager, EMEA",               "2026-06-02", "no_reply"),
    ("H",                 "Catalyst - Special Projects, CEO's Office - US",         "2026-06-03", "no_reply"),
    ("Pigment",           "AI Deployment Strategist",                               "2026-06-03", "no_reply"),
    ("Plaid",             "Scaled Account Manager",                                  "2026-06-03", "no_reply"),
    ("TikTok",            "Strategy and Operations Manager, Creative Product, EUI", "2026-06-03", "no_reply"),
    ("Monzo",             "Chief of Staff",                                          "2026-06-03", "no_reply"),
    ("OpenAI",            "AI Deployment Engineer, Large Enterprise",               "2026-06-03", "no_reply"),
    ("Lendable",          "Strategy and Operations Manager",                         "2026-06-08", "no_reply"),
    ("Monzo",             "Strategic Project Lead",                                  "2026-06-08", "no_reply"),
    ("Notion",            "Central GTM Strategy & Operations Manager",               "2026-06-08", "no_reply"),
    ("Graphcore",         "Business Transformation Lead",                            "2026-06-08", "no_reply"),
    ("Tyea",              "Strategy Manager",                                        "2026-06-09", "no_reply"),
    ("Magentic",          "Deployment Strategist",                                   "2026-06-09", "no_reply"),
    ("Revolut",           "Product Owner (Technical)",                               "2026-06-16", "no_reply"),
    ("Revolut",           "Product Strategy Manager",                                "2026-06-16", "no_reply"),
    ("Revolut",           "Product Owner Sprint",                                    "2026-06-16", "no_reply"),
    ("PlanLab",           "Delivery Lead",                                           "2026-06-16", "no_reply"),
    ("Emerge Capital",    "Head of Platform",                                        "2026-06-16", "no_reply"),
    ("JuniorAI",          "AI Deployment Lead",                                      "2026-06-16", "no_reply"),
    ("Cursor",            "AI Deployment Manager",                                   "2026-06-16", "no_reply"),
    ("Conduct",           "AI Operations Engineer",                                  "2026-06-18", "no_reply"),
    ("Condukt",           "Agent Deployment Strategist",                             "2026-06-18", "no_reply"),
    ("Relay",             "Chief of Staff Associate",                                "2026-06-18", "no_reply"),
    ("Seamflow",          "Deployment Strategist",                                   "2026-06-18", "no_reply"),
    ("Marsh",             "Product Strategy Analyst - London",                       "2026-06-18", "no_reply"),
    ("Softserve",         "Product Strategist",                                      "2026-06-18", "no_reply"),
    ("Cogna",             "Solution Strategist",                                     "2026-06-18", "no_reply"),
    ("Buro Happold",      "Manager - Digital Strategy & Transformation",             "2026-06-18", "no_reply"),
]

# ---------------------------------------------------------------------------
# Companies confirmed as yellow (active interview) from spreadsheet
# Update this list when you share feedback
# ---------------------------------------------------------------------------
ACTIVE_INTERVIEWS = {
    # Add companies here as you confirm them, e.g.:
    # "Tenex",
}

# Companies confirmed as gray (eliminated after interview rounds)
ELIMINATED_AFTER_INTERVIEW = {
    "Tenex",  # confirmed — "close call, tough decision"
}

# Companies confirmed as red (eliminated via email, no recruiter engagement)
ELIMINATED_EARLY = set()


def _make_id(company: str, role: str, date: str) -> str:
    base = f"{company}_{role}_{date}".lower()
    return "".join(c if c.isalnum() or c == "_" else "_" for c in base)[:80]


def run():
    init_db()
    now = datetime.utcnow().isoformat()

    with get_conn() as conn:
        inserted = 0
        skipped = 0

        for company, role, date_str, default_status in APPLICATIONS:
            job_id = _make_id(company, role, date_str)

            # Determine status from color override sets
            if company in ACTIVE_INTERVIEWS:
                status = "interviewing"
            elif company in ELIMINATED_AFTER_INTERVIEW:
                status = "rejected_interview"
            elif company in ELIMINATED_EARLY:
                status = "rejected_early"
            else:
                status = default_status

            # Check if already exists
            exists = conn.execute(
                "SELECT id FROM jobs WHERE id=?", (job_id,)
            ).fetchone()

            if exists:
                skipped += 1
                continue

            # Insert job record
            conn.execute("""
                INSERT INTO jobs (id, title, company, location, url, source,
                                  company_type, fit_score, conversion_score,
                                  reasons, apply_flag, posted_date, fetched_at, raw_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_id, role or "(not recorded)", company,
                "", "", "manual_import",
                "", None, None,
                "", 0, date_str, now, "{}"
            ))

            # Insert application status
            conn.execute("""
                INSERT INTO applications (job_id, status, applied_at, notes, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (job_id, status, date_str, "", now))

            # Insert outcome event
            conn.execute("""
                INSERT INTO outcomes (job_id, event_type, event_date, notes)
                VALUES (?, ?, ?, ?)
            """, (job_id, "applied", date_str, ""))

            inserted += 1

    print(f"\n[Import] Done.")
    print(f"  Inserted : {inserted}")
    print(f"  Skipped  : {skipped} (already in DB)")
    print(f"  Total    : {len(APPLICATIONS)}")

    # Print summary by status
    with get_conn() as conn:
        for row in conn.execute("""
            SELECT a.status, COUNT(*) as n
            FROM applications a
            WHERE a.id IN (SELECT MAX(id) FROM applications GROUP BY job_id)
            GROUP BY a.status ORDER BY n DESC
        """).fetchall():
            print(f"  {row['status']:<25} {row['n']}")


if __name__ == "__main__":
    run()
