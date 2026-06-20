"""
AylinOS — Prompt Eval Test Cases
----------------------------------
25 labeled examples derived from real application outcomes.

Ground truth labels:
  HIGH   → should score apply=True (fit>=65, conversion>=45)
  MEDIUM → borderline, apply=False expected but fit should be 55-70
  LOW    → clearly wrong fit, apply=False expected

HIGH cases = companies that granted interviews (from update_outcomes.py ground truth).
MEDIUM/LOW = constructed from real patterns in 358-application corpus.
"""

TEST_CASES = [
    # ── HIGH FIT — real interview outcomes ──────────────────────────────────────
    {
        "id": "tenex_ai_strategist",
        "job": {
            "title": "AI Strategist",
            "company": "Tenex",
            "company_type": "competitive-tech",
            "location": "New York, NY",
            "description": "Define and drive AI deployment strategy for enterprise clients. Work cross-functionally with product and engineering to translate AI capabilities into business value. MBA preferred."
        },
        "expected_apply": True,
        "label": "HIGH",
        "source": "real_outcome",
        "notes": "Got interview — exact role match"
    },
    {
        "id": "hebbia_ai_strategist",
        "job": {
            "title": "AI Strategist",
            "company": "Hebbia",
            "company_type": "competitive-tech",
            "location": "New York, NY",
            "description": "Own go-to-market strategy for AI search platform. Partner with enterprise customers to deploy AI solutions. Requires strong analytical and communication skills."
        },
        "expected_apply": True,
        "label": "HIGH",
        "source": "real_outcome",
        "notes": "Got interview — AI strategist title, NYC, competitive-tech"
    },
    {
        "id": "hebbia_solution_engineer",
        "job": {
            "title": "Solution Engineer",
            "company": "Hebbia",
            "company_type": "competitive-tech",
            "location": "New York, NY",
            "description": "Act as technical advisor to enterprise customers deploying Hebbia's AI platform. Bridge product and customer needs. Technical background preferred but not required."
        },
        "expected_apply": True,
        "label": "HIGH",
        "source": "real_outcome",
        "notes": "Got interview — deployment-adjacent, customer-facing"
    },
    {
        "id": "scale_ai_strategic_project_lead",
        "job": {
            "title": "Strategic Project Lead, Gen AI",
            "company": "Scale AI",
            "company_type": "competitive-tech",
            "location": "New York, NY",
            "description": "Lead strategic initiatives for Scale's Gen AI business unit. Own cross-functional projects from scoping to delivery. MBA or equivalent experience strongly preferred."
        },
        "expected_apply": True,
        "label": "HIGH",
        "source": "real_outcome",
        "notes": "Got interview — lost on live SQL case study"
    },
    {
        "id": "hockeystack_strategy_ops",
        "job": {
            "title": "Strategy and Operations",
            "company": "HockeyStack",
            "company_type": "high-growth-startup",
            "location": "New York, NY",
            "description": "Build the operational backbone for a fast-growing B2B SaaS company. Own planning cycles, reporting, and cross-functional coordination. Early hire with direct CEO access."
        },
        "expected_apply": True,
        "label": "HIGH",
        "source": "real_outcome",
        "notes": "Got interview"
    },
    {
        "id": "vendelux_strategic_business",
        "job": {
            "title": "Strategic Business Associate",
            "company": "Vendelux",
            "company_type": "high-growth-startup",
            "location": "New York, NY",
            "description": "Drive revenue strategy and GTM execution for AI-powered event intelligence platform. Work directly with the founding team."
        },
        "expected_apply": True,
        "label": "HIGH",
        "source": "real_outcome",
        "notes": "Got interview"
    },
    {
        "id": "august_strategy_ops",
        "job": {
            "title": "Strategy & Operations",
            "company": "August",
            "company_type": "high-growth-startup",
            "location": "New York, NY",
            "description": "Own strategic operations for AI-driven HR platform. Drive OKR planning, company reporting, and special projects."
        },
        "expected_apply": True,
        "label": "HIGH",
        "source": "real_outcome",
        "notes": "Got interview"
    },
    {
        "id": "relay_strategy_ops_manager",
        "job": {
            "title": "Strategy & Operations Manager",
            "company": "Relay",
            "company_type": "high-growth-startup",
            "location": "New York, NY",
            "description": "Lead cross-functional initiatives at fintech startup. Manage business operations, analytics, and strategic planning. Reports to COO."
        },
        "expected_apply": True,
        "label": "HIGH",
        "source": "real_outcome",
        "notes": "Got interview"
    },
    {
        "id": "transformworks_chief_of_staff",
        "job": {
            "title": "Chief of Staff",
            "company": "TransformWorks",
            "company_type": "high-growth-startup",
            "location": "New York, NY",
            "description": "Serve as force multiplier to CEO. Drive company-wide initiatives, OKRs, board preparation, and special projects at AI transformation consultancy."
        },
        "expected_apply": True,
        "label": "HIGH",
        "source": "real_outcome",
        "notes": "Got interview"
    },
    {
        "id": "handshake_strategic_project_lead",
        "job": {
            "title": "Strategic Project Lead",
            "company": "Handshake",
            "company_type": "high-growth-startup",
            "location": "New York, NY",
            "description": "Lead high-impact strategic initiatives at Handshake. Own cross-functional projects end-to-end. MBA preferred."
        },
        "expected_apply": True,
        "label": "HIGH",
        "source": "real_outcome",
        "notes": "Got interview"
    },
    {
        "id": "bending_spoons_office_ceo",
        "job": {
            "title": "Office of CEO",
            "company": "Bending Spoons",
            "company_type": "high-growth-startup",
            "location": "London, UK",
            "description": "Work directly with CEO on company strategy, M&A, product direction, and operational excellence. Highly selective program for top MBA graduates."
        },
        "expected_apply": True,
        "label": "HIGH",
        "source": "real_outcome",
        "notes": "Got interview — London, selective CEO program"
    },
    {
        "id": "forter_strategy_ops",
        "job": {
            "title": "Strategy & Operations Associate",
            "company": "Forter",
            "company_type": "high-growth-startup",
            "location": "New York, NY",
            "description": "Drive operational strategy and execution at fraud prevention AI company. Own cross-functional projects and company-wide analytics."
        },
        "expected_apply": True,
        "label": "HIGH",
        "source": "real_outcome",
        "notes": "Got interview"
    },
    {
        "id": "vertice_gtm_strategy",
        "job": {
            "title": "GTM Strategy",
            "company": "Vertice",
            "company_type": "high-growth-startup",
            "location": "London, UK",
            "description": "Build and execute go-to-market strategy for SaaS spend management platform. Define ICP, pricing, and expansion playbooks."
        },
        "expected_apply": True,
        "label": "HIGH",
        "source": "real_outcome",
        "notes": "Got interview — London, GTM role"
    },
    {
        "id": "poseidon_strategic_initiatives",
        "job": {
            "title": "Strategic Initiatives",
            "company": "Poseidon",
            "company_type": "high-growth-startup",
            "location": "New York, NY",
            "description": "Lead strategic projects for climate tech startup. Interface with investors, partners, and cross-functional teams."
        },
        "expected_apply": True,
        "label": "HIGH",
        "source": "real_outcome",
        "notes": "Got interview"
    },
    {
        "id": "cartesia_gtm_strategist",
        "job": {
            "title": "GTM Strategist",
            "company": "Cartesia",
            "company_type": "competitive-tech",
            "location": "San Francisco, CA",
            "description": "Define and execute GTM strategy for AI voice and speech platform. Own sales motion, pricing, and partnership development."
        },
        "expected_apply": True,
        "label": "HIGH",
        "source": "real_outcome",
        "notes": "Got interview — SF but strong AI fit"
    },

    # ── MEDIUM FIT — borderline / mixed signals ─────────────────────────────────
    {
        "id": "jpmorgan_digital_strategy",
        "job": {
            "title": "Digital Strategy Associate",
            "company": "JPMorgan",
            "company_type": "enterprise",
            "location": "New York, NY",
            "description": "Drive digital transformation initiatives across the corporate and investment bank. MBA required. Rotational program across tech, ops, and strategy functions."
        },
        "expected_apply": False,
        "label": "MEDIUM",
        "source": "real_outcome",
        "notes": "Got interview but enterprise company — lower conversion. Should have fit 60-70, conversion 25-40"
    },
    {
        "id": "openai_solutions_engineer",
        "job": {
            "title": "Solutions Engineer",
            "company": "OpenAI",
            "company_type": "top-ai-lab",
            "location": "New York, NY",
            "description": "Help enterprise customers deploy OpenAI APIs. Technical background in AI/ML strongly preferred. Work with Fortune 500 clients on integration and adoption."
        },
        "expected_apply": False,
        "label": "MEDIUM",
        "source": "constructed",
        "notes": "Top lab = low conversion despite high fit. Fit ~75, conversion ~20"
    },
    {
        "id": "databricks_strategy_ops",
        "job": {
            "title": "Strategy & Ops Manager",
            "company": "Databricks",
            "company_type": "high-growth-startup",
            "location": "San Francisco, CA",
            "description": "Drive business operations for data intelligence platform. Work with GTM and product teams on planning, forecasting, and execution."
        },
        "expected_apply": False,
        "label": "MEDIUM",
        "source": "constructed",
        "notes": "SF location penalty, good role type. Should be borderline"
    },
    {
        "id": "google_strategy_analyst",
        "job": {
            "title": "Strategy Analyst",
            "company": "Google",
            "company_type": "big-tech",
            "location": "New York, NY",
            "description": "Support strategic planning and business operations for Google's core ads business. Analytical background required."
        },
        "expected_apply": False,
        "label": "MEDIUM",
        "source": "constructed",
        "notes": "Big-tech conversion headwinds. Not AI-focused. Fit 55-65, conversion 25-35"
    },
    {
        "id": "a16z_chief_of_staff",
        "job": {
            "title": "Chief of Staff",
            "company": "a16z",
            "company_type": "vc-firm",
            "location": "New York, NY",
            "description": "Chief of Staff to General Partner. Manage portfolio operations, partner scheduling, and fund strategy projects. Requires investment or strategy background."
        },
        "expected_apply": False,
        "label": "MEDIUM",
        "source": "constructed",
        "notes": "VC CoS — good title, but VC domain mismatch. Borderline"
    },

    # ── LOW FIT — clear mismatches ───────────────────────────────────────────────
    {
        "id": "stripe_software_engineer",
        "job": {
            "title": "Software Engineer, Payments",
            "company": "Stripe",
            "company_type": "high-growth-startup",
            "location": "New York, NY",
            "description": "Build distributed payment infrastructure in Go and Java. 5+ years backend engineering experience required."
        },
        "expected_apply": False,
        "label": "LOW",
        "source": "constructed",
        "notes": "Engineering role — excluded by title filter but testing scoring"
    },
    {
        "id": "deloitte_senior_consultant",
        "job": {
            "title": "Senior Consultant, Technology",
            "company": "Deloitte",
            "company_type": "enterprise",
            "location": "New York, NY",
            "description": "Join Deloitte's Technology Strategy practice. Advise Fortune 500 clients on digital transformation. MBA preferred."
        },
        "expected_apply": False,
        "label": "LOW",
        "source": "constructed",
        "notes": "Returning to Deloitte = explicit anti-target. Enterprise + consulting = low conversion"
    },
    {
        "id": "jpmorgan_vp_finance",
        "job": {
            "title": "Vice President, Corporate Finance",
            "company": "JPMorgan",
            "company_type": "enterprise",
            "location": "New York, NY",
            "description": "Lead corporate finance advisory for large cap M&A transactions. 7+ years investment banking required."
        },
        "expected_apply": False,
        "label": "LOW",
        "source": "constructed",
        "notes": "VP seniority + traditional finance = double exclusion"
    },
    {
        "id": "salesforce_account_executive",
        "job": {
            "title": "Account Executive, Enterprise",
            "company": "Salesforce",
            "company_type": "big-tech",
            "location": "New York, NY",
            "description": "Drive new logo acquisition and enterprise sales for Salesforce CRM. Quota-carrying role. 3+ years enterprise SaaS sales required."
        },
        "expected_apply": False,
        "label": "LOW",
        "source": "constructed",
        "notes": "Pure sales / quota-carrying — wrong role type entirely"
    },
    {
        "id": "mckinsey_associate",
        "job": {
            "title": "Associate",
            "company": "McKinsey & Company",
            "company_type": "enterprise",
            "location": "New York, NY",
            "description": "Join McKinsey as an Associate post-MBA. Work on strategy projects across industries. MBA from top program required."
        },
        "expected_apply": False,
        "label": "LOW",
        "source": "constructed",
        "notes": "Classic consulting = explicitly excluded. Low conversion, low fit"
    },
]
