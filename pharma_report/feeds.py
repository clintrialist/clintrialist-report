"""Feed registry: FDA sources + journals grouped by therapeutic area."""

CATEGORIES = {
    "general": "General Medical",
    "stats":   "Statistics & Trial Methods",
    "gi":      "Gastroenterology",
    "immuno":  "Immunology",
    "onc":     "Oncology",
    "neuro":   "Neuroscience",
}

# Regulatory Watch -- guidance documents, drug approvals, and workshop announcements
# from FDA (US), EMA (EU), Health Canada, and PMDA (Japan).
# Recalls / warning letters are filtered out via both Google News negative search
# and post-fetch title filtering (see REGULATORY_EXCLUDE_TITLES below).
REGULATORY_AGENCIES = ["FDA", "EMA", "Health Canada", "PMDA"]
REGULATORY_AGENCY_HOMES = {
    "FDA":          "https://www.fda.gov/",
    "EMA":          "https://www.ema.europa.eu/",
    "Health Canada": "https://www.canada.ca/en/health-canada.html",
    "PMDA":         "https://www.pmda.go.jp/english/",
}
PER_AGENCY_LIMIT = 8   # items per agency shown in the Regulatory Watch panel

REGULATORY_FEEDS = [
    # FDA (US)
    {"agency": "FDA", "name": "FDA Approvals",
     "rss": "https://news.google.com/rss/search?q=site:fda.gov+(%22drug+approval%22+OR+%22approved%22+OR+%22novel+drug%22)+-recall+-%22warning+letter%22&hl=en-US&gl=US&ceid=US:en"},
    {"agency": "FDA", "name": "FDA Guidance",
     "rss": "https://news.google.com/rss/search?q=site:fda.gov+(%22guidance+for+industry%22+OR+%22draft+guidance%22+OR+%22final+guidance%22)+-recall+-%22warning+letter%22&hl=en-US&gl=US&ceid=US:en"},
    {"agency": "FDA", "name": "FDA Workshops",
     "rss": "https://news.google.com/rss/search?q=site:fda.gov+(workshop+OR+%22public+meeting%22+OR+%22advisory+committee%22)+-recall+-%22warning+letter%22&hl=en-US&gl=US&ceid=US:en"},

    # EMA (European Medicines Agency)
    {"agency": "EMA", "name": "EMA Approvals",
     "rss": "https://news.google.com/rss/search?q=site:ema.europa.eu+(CHMP+OR+%22marketing+authorisation%22+OR+%22positive+opinion%22+OR+approval)+-recall+-%22safety+signal%22&hl=en-US&gl=US&ceid=US:en"},
    {"agency": "EMA", "name": "EMA Guidance",
     "rss": "https://news.google.com/rss/search?q=site:ema.europa.eu+(guideline+OR+guidance+OR+%22reflection+paper%22+OR+%22scientific+guideline%22)+-recall&hl=en-US&gl=US&ceid=US:en"},
    {"agency": "EMA", "name": "EMA Workshops",
     "rss": "https://news.google.com/rss/search?q=site:ema.europa.eu+(workshop+OR+%22stakeholder+meeting%22+OR+webinar)+-recall&hl=en-US&gl=US&ceid=US:en"},

    # Health Canada
    {"agency": "Health Canada", "name": "Health Canada Approvals",
     "rss": "https://news.google.com/rss/search?q=site:canada.ca/en/health-canada+(authorization+OR+approval+OR+%22Notice+of+Compliance%22)+-recall+-warning&hl=en-US&gl=US&ceid=US:en"},
    {"agency": "Health Canada", "name": "Health Canada Guidance",
     "rss": "https://news.google.com/rss/search?q=site:canada.ca/en/health-canada+(guidance+OR+guideline+OR+%22policy+document%22)+-recall+-warning&hl=en-US&gl=US&ceid=US:en"},
    {"agency": "Health Canada", "name": "Health Canada Workshops",
     "rss": "https://news.google.com/rss/search?q=site:canada.ca/en/health-canada+(workshop+OR+consultation+OR+forum)+-recall&hl=en-US&gl=US&ceid=US:en"},

    # PMDA (Japan -- English site)
    {"agency": "PMDA", "name": "PMDA Approvals",
     "rss": "https://news.google.com/rss/search?q=site:pmda.go.jp+(approval+OR+%22review+report%22+OR+review)+-recall&hl=en-US&gl=US&ceid=US:en"},
    {"agency": "PMDA", "name": "PMDA Guidance",
     "rss": "https://news.google.com/rss/search?q=site:pmda.go.jp+(guideline+OR+notification+OR+%22Q%26A%22)+-recall&hl=en-US&gl=US&ceid=US:en"},
    {"agency": "PMDA", "name": "PMDA Workshops",
     "rss": "https://news.google.com/rss/search?q=site:pmda.go.jp+(workshop+OR+symposium+OR+briefing)+-recall&hl=en-US&gl=US&ceid=US:en"},
]

# Post-fetch exclusion: dropped if a substring appears anywhere in the title
# (case-insensitive). Catches whatever Google News's negative-search misses.
REGULATORY_EXCLUDE_TITLES = [
    "recall",
    "warning letter",
    "import alert",
    "safety alert",
    "market withdrawal",
    "consumer update",
    "shortage",
]

# Industry trade press -- left column, under FDA.
INDUSTRY_FEEDS = [
    {"name": "Fierce Pharma",   "rss": "https://www.fiercepharma.com/rss/xml"},
    {"name": "Fierce Biotech",  "rss": "https://www.fiercebiotech.com/rss/xml"},
]
INDUSTRY_LIMIT = 10

PER_JOURNAL_LIMIT = 5
GENERAL_LIMIT = 4   # latest N titles per general-medical journal


def _gnews(query: str) -> str:
    """Google News RSS search URL builder for journals without a working publisher RSS."""
    return f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"


# Each entry: name, category, rss URL, journal home / latest-issue URL.
JOURNALS = [
    # --- General Medical (left column, under FDA) ---
    {
        "name": "NEJM",
        "category": "general",
        "rss":  "https://www.nejm.org/action/showFeed?type=etoc&feed=rss&jc=nejm",
        "home": "https://www.nejm.org/",
    },
    {
        "name": "The Lancet",
        "category": "general",
        "rss":  "https://www.thelancet.com/rssfeed/lancet_current.xml",
        "home": "https://www.thelancet.com/journals/lancet/issue/current",
    },
    {
        "name": "JAMA",
        "category": "general",
        "rss":  _gnews("site:jamanetwork.com/journals/jama"),
        "home": "https://jamanetwork.com/journals/jama",
    },
    {
        "name": "BMJ",
        "category": "general",
        "rss":  _gnews("site:bmj.com/content"),
        "home": "https://www.bmj.com/",
    },

    # --- Statistics & Trial Methods (alphabetical) ---
    {
        "name": "Clinical Trials",
        "category": "stats",
        "rss":  "https://journals.sagepub.com/action/showFeed?type=etoc&feed=rss&jc=ctja",
        "home": "https://journals.sagepub.com/home/ctj",
    },
    {
        "name": "Contemporary Clinical Trials",
        "category": "stats",
        "rss":  "https://rss.sciencedirect.com/publication/science/15517144",
        "home": "https://www.sciencedirect.com/journal/contemporary-clinical-trials",
    },
    {
        "name": "Journal of Biopharmaceutical Statistics",
        "category": "stats",
        "rss":  "https://www.tandfonline.com/feed/rss/lbps20",
        "home": "https://www.tandfonline.com/journals/lbps20",
    },
    {
        "name": "Pharmaceutical Statistics",
        "category": "stats",
        "rss":  "https://onlinelibrary.wiley.com/feed/15391612/most-recent",
        "home": "https://onlinelibrary.wiley.com/journal/15391612",
    },
    {
        "name": "Pharmacoepidemiology and Drug Safety",
        "category": "stats",
        "rss":  "https://onlinelibrary.wiley.com/feed/10991557/most-recent",
        "home": "https://onlinelibrary.wiley.com/journal/10991557",
    },
    {
        "name": "Statistics in Biopharmaceutical Research",
        "category": "stats",
        "rss":  "https://www.tandfonline.com/feed/rss/usbr20",
        "home": "https://www.tandfonline.com/journals/usbr20",
    },
    {
        "name": "Statistics in Medicine",
        "category": "stats",
        "rss":  "https://onlinelibrary.wiley.com/feed/10970258/most-recent",
        "home": "https://onlinelibrary.wiley.com/journal/10970258",
    },
    {
        "name": "Therapeutic Innovation & Regulatory Science",
        "category": "stats",
        "rss":  _gnews("Therapeutic+Innovation+Regulatory+Science+journal"),
        "home": "https://link.springer.com/journal/43441",
    },
    {
        "name": "Trials",
        "category": "stats",
        "rss":  _gnews("site:trialsjournal.biomedcentral.com"),
        "home": "https://trialsjournal.biomedcentral.com/",
    },

    # --- Gastroenterology ---
    {
        "name": "Alimentary Pharmacology & Therapeutics",
        "category": "gi",
        "rss":  "https://onlinelibrary.wiley.com/feed/13652036/most-recent",
        "home": "https://onlinelibrary.wiley.com/journal/13652036",
    },
    {
        "name": "BMJ Open Gastroenterology",
        "category": "gi",
        "rss":  "https://bmjopengastro.bmj.com/rss/current.xml",
        "home": "https://bmjopengastro.bmj.com/",
    },
    {
        "name": "Clinical and Experimental Gastroenterology",
        "category": "gi",
        "rss":  "https://www.tandfonline.com/feed/rss/dceg20",
        "home": "https://www.tandfonline.com/journals/dceg20",
    },
    {
        "name": "Gastroenterology",
        "category": "gi",
        "rss":  "https://rss.sciencedirect.com/publication/science/00165085",
        "home": "https://www.gastrojournal.org/",
    },
    {
        "name": "Gut",
        "category": "gi",
        "rss":  "https://gut.bmj.com/rss/current.xml",
        "home": "https://gut.bmj.com/",
    },
    {
        "name": "Inflammatory Bowel Diseases",
        "category": "gi",
        "rss":  _gnews("site:academic.oup.com/ibdjournal"),
        "home": "https://academic.oup.com/ibdjournal",
    },

    # --- Immunology ---
    {
        "name": "Clinical Immunology",
        "category": "immuno",
        "rss":  "https://rss.sciencedirect.com/publication/science/15216616",
        "home": "https://www.sciencedirect.com/journal/clinical-immunology",
    },
    {
        "name": "Frontiers in Immunology",
        "category": "immuno",
        "rss":  "https://www.frontiersin.org/journals/immunology/rss",
        "home": "https://www.frontiersin.org/journals/immunology",
    },
    {
        "name": "Immunopharmacology and Immunotoxicology",
        "category": "immuno",
        "rss":  "https://www.tandfonline.com/feed/rss/iipi20",
        "home": "https://www.tandfonline.com/journals/iipi20",
    },
    {
        "name": "Immunotherapy Advances",
        "category": "immuno",
        "rss":  _gnews("site:academic.oup.com/immunotherapyadv"),
        "home": "https://academic.oup.com/immunotherapyadv",
    },
    {
        "name": "Journal for ImmunoTherapy of Cancer",
        "category": "immuno",
        "rss":  "https://jitc.bmj.com/rss/current.xml",
        "home": "https://jitc.bmj.com/",
    },
    {
        "name": "The Journal of Immunology",
        "category": "immuno",
        "rss":  _gnews("%22The+Journal+of+Immunology%22+jimmunol"),
        "home": "https://journals.aai.org/jimmunol",
    },

    # --- Oncology ---
    {
        "name": "Annals of Oncology",
        "category": "onc",
        "rss":  "https://rss.sciencedirect.com/publication/science/09237534",
        "home": "https://www.annalsofoncology.org/",
    },
    {
        "name": "British Journal of Cancer",
        "category": "onc",
        "rss":  "https://www.nature.com/bjc.rss",
        "home": "https://www.nature.com/bjc",
    },
    {
        "name": "Cancer Discovery",
        "category": "onc",
        "rss":  _gnews("site:aacrjournals.org/cancerdiscovery"),
        "home": "https://aacrjournals.org/cancerdiscovery",
    },
    {
        "name": "Clinical Cancer Research",
        "category": "onc",
        "rss":  _gnews("site:aacrjournals.org/clincancerres"),
        "home": "https://aacrjournals.org/clincancerres",
    },
    {
        "name": "ESMO Open",
        "category": "onc",
        "rss":  "https://rss.sciencedirect.com/publication/science/20597029",
        "home": "https://www.esmoopen.com/",
    },
    {
        "name": "Journal of Clinical Oncology",
        "category": "onc",
        "rss":  "https://ascopubs.org/action/showFeed?type=etoc&feed=rss&jc=jco",
        "home": "https://ascopubs.org/journal/jco",
    },
    {
        "name": "The Lancet Oncology",
        "category": "onc",
        "rss":  "https://www.thelancet.com/rssfeed/lanonc_current.xml",
        "home": "https://www.thelancet.com/journals/lanonc/issue/current",
    },

    # --- Neuroscience ---
    {
        "name": "Alzheimer's & Dementia",
        "category": "neuro",
        "rss":  "https://onlinelibrary.wiley.com/feed/15525279/most-recent",
        "home": "https://alz-journals.onlinelibrary.wiley.com/journal/15525279",
    },
    {
        "name": "Annals of Neurology",
        "category": "neuro",
        "rss":  "https://onlinelibrary.wiley.com/feed/15318249/most-recent",
        "home": "https://onlinelibrary.wiley.com/journal/15318249",
    },
    {
        "name": "Brain",
        "category": "neuro",
        "rss":  _gnews("site:academic.oup.com/brain"),
        "home": "https://academic.oup.com/brain",
    },
    {
        "name": "Dialogues in Clinical Neuroscience",
        "category": "neuro",
        "rss":  "https://www.tandfonline.com/feed/rss/tdcn20",
        "home": "https://www.tandfonline.com/journals/tdcn20",
    },
    {
        "name": "Epilepsia",
        "category": "neuro",
        "rss":  "https://onlinelibrary.wiley.com/feed/15281167/most-recent",
        "home": "https://onlinelibrary.wiley.com/journal/15281167",
    },
    {
        "name": "Movement Disorders",
        "category": "neuro",
        "rss":  "https://onlinelibrary.wiley.com/feed/15318257/most-recent",
        "home": "https://onlinelibrary.wiley.com/journal/15318257",
    },
    {
        "name": "Multiple Sclerosis Journal",
        "category": "neuro",
        "rss":  "https://journals.sagepub.com/action/showFeed?type=etoc&feed=rss&jc=msja",
        "home": "https://journals.sagepub.com/home/msj",
    },
    {
        "name": "Neurology",
        "category": "neuro",
        "rss":  "https://www.neurology.org/action/showFeed?type=etoc&feed=rss&jc=wnl",
        "home": "https://www.neurology.org/",
    },
    {
        "name": "The Lancet Neurology",
        "category": "neuro",
        "rss":  "https://www.thelancet.com/rssfeed/laneur_current.xml",
        "home": "https://www.thelancet.com/journals/laneur/issue/current",
    },
]
