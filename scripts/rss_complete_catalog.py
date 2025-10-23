#!/usr/bin/env python3
"""
Complete RSS/Scraping Catalog Collector
Expands from 26 to 76 sources covering all categories:
- AI Tools & News (existing)
- Business Trends (existing)
- Marketing & Sales (existing)
- Meditation & Manifestation (NEW)
- Quantum Physics (NEW)
- Humor & Comedy (NEW)
- SME Content (NEW)
"""

import sys
sys.path.append('/Users/yourox/AI-Workspace')

# Import existing Tier 1/2 sources
from scripts.rss_expanded_collector import TIER1_SOURCES, TIER2_SOURCES, ExpandedRSSCollector

# NEW CATEGORIES

# Meditation & Manifestation (10 sources)
MEDITATION_SOURCES = {
    "insighttimer": {
        "name": "Insight Timer",
        "domain": "insighttimer.com",
        "rss_url": None,  # API-based, requires special handling
        "category": "meditation",
        "priority": "medium",
        "base_weight": 0.6
    },
    "wildmind": {
        "name": "Wildmind",
        "domain": "wildmind.org",
        "rss_url": "https://www.wildmind.org/feed",
        "category": "meditation",
        "priority": "medium",
        "base_weight": 0.6
    },
    "aboutmeditation": {
        "name": "About Meditation",
        "domain": "about-meditation.com",
        "rss_url": None,  # Scraping required
        "category": "meditation",
        "priority": "medium",
        "base_weight": 0.5
    },
    "manifestlovers": {
        "name": "Manifest Lovers",
        "domain": "manifestlovers.com",
        "rss_url": "https://www.manifestlovers.com/blog/feed",
        "category": "manifestation",
        "priority": "medium",
        "base_weight": 0.5
    },
    "millennialgrind": {
        "name": "The Millennial Grind",
        "domain": "millennial-grind.com",
        "rss_url": "https://millennial-grind.com/feed",
        "category": "manifestation",
        "priority": "medium",
        "base_weight": 0.5
    },
    "mindmovies": {
        "name": "Mind Movies Blog",
        "domain": "mindmovies.com",
        "rss_url": None,  # Scraping required
        "category": "manifestation",
        "priority": "medium",
        "base_weight": 0.5
    },
    "bigmanifestation": {
        "name": "Big Manifestation",
        "domain": "bigmanifestation.com",
        "rss_url": None,  # Scraping required
        "category": "manifestation",
        "priority": "medium",
        "base_weight": 0.5
    },
    "tarabrach": {
        "name": "Tara Brach",
        "domain": "tarabrach.com",
        "rss_url": "https://www.tarabrach.com/feed/podcast/",
        "category": "meditation",
        "priority": "medium",
        "base_weight": 0.7
    },
    "declutterthemind": {
        "name": "Declutter The Mind",
        "domain": "declutterthemind.com",
        "rss_url": "https://declutterthemind.com/blog/feed/",
        "category": "mindfulness",
        "priority": "medium",
        "base_weight": 0.6
    }
}

# Quantum Physics (10 sources)
QUANTUM_SOURCES = {
    "mitocw": {
        "name": "MIT OpenCourseWare",
        "domain": "ocw.mit.edu",
        "rss_url": None,  # Scraping required
        "category": "education",
        "priority": "medium",
        "base_weight": 0.8
    },
    "coursera_quantum": {
        "name": "Coursera Quantum Physics",
        "domain": "coursera.org",
        "rss_url": None,  # API-based
        "category": "education",
        "priority": "medium",
        "base_weight": 0.7
    },
    "edx_quantum": {
        "name": "edX Quantum Mechanics",
        "domain": "edx.org",
        "rss_url": None,  # API-based
        "category": "education",
        "priority": "medium",
        "base_weight": 0.7
    },
    "stanford_online": {
        "name": "Stanford Online",
        "domain": "online.stanford.edu",
        "rss_url": None,  # Scraping required
        "category": "education",
        "priority": "medium",
        "base_weight": 0.8
    },
    "pbslearning": {
        "name": "PBS LearningMedia",
        "domain": "pbslearningmedia.org",
        "rss_url": None,  # Scraping required
        "category": "education",
        "priority": "medium",
        "base_weight": 0.6
    },
    "classcentral": {
        "name": "Class Central Quantum",
        "domain": "classcentral.com",
        "rss_url": None,  # Scraping required
        "category": "education",
        "priority": "medium",
        "base_weight": 0.6
    },
    "learnqm": {
        "name": "Learn QM Georgia Tech",
        "domain": "learnqm.gatech.edu",
        "rss_url": None,  # Scraping required
        "category": "education",
        "priority": "medium",
        "base_weight": 0.7
    },
    "udemy_quantum": {
        "name": "Udemy Free Quantum",
        "domain": "udemy.com",
        "rss_url": None,  # API-based
        "category": "education",
        "priority": "medium",
        "base_weight": 0.6
    },
    "compadre": {
        "name": "ComPADRE Digital Library",
        "domain": "compadre.org",
        "rss_url": None,  # Scraping required
        "category": "education",
        "priority": "medium",
        "base_weight": 0.6
    }
}

# Humor & Comedy (10 sources)
HUMOR_SOURCES = {
    "cracked": {
        "name": "Cracked",
        "domain": "cracked.com",
        "rss_url": "https://www.cracked.com/feeds/latest.xml",
        "category": "humor",
        "priority": "low",
        "base_weight": 0.4
    },
    "deadfrog": {
        "name": "Dead-Frog Comedy Database",
        "domain": "dead-frog.com",
        "rss_url": None,  # Scraping required
        "category": "comedy",
        "priority": "low",
        "base_weight": 0.4
    },
    "9gag": {
        "name": "9GAG",
        "domain": "9gag.com",
        "rss_url": None,  # Scraping required
        "category": "humor",
        "priority": "low",
        "base_weight": 0.3
    },
    "reddit_jokes": {
        "name": "Reddit r/Jokes",
        "domain": "reddit.com",
        "rss_url": "https://www.reddit.com/r/jokes/.rss",
        "category": "humor",
        "priority": "low",
        "base_weight": 0.4
    },
    "theonion": {
        "name": "The Onion",
        "domain": "theonion.com",
        "rss_url": "https://www.theonion.com/rss",
        "category": "satire",
        "priority": "low",
        "base_weight": 0.5
    },
    "vimeo_comedy": {
        "name": "Vimeo Comedy",
        "domain": "vimeo.com",
        "rss_url": None,  # API-based
        "category": "comedy",
        "priority": "low",
        "base_weight": 0.4
    },
    "comedycentral": {
        "name": "Comedy Central Standup",
        "domain": "cc.com",
        "rss_url": None,  # Scraping required
        "category": "comedy",
        "priority": "low",
        "base_weight": 0.5
    },
    "funnyordie": {
        "name": "Funny or Die",
        "domain": "funnyordie.com",
        "rss_url": None,  # Scraping required
        "category": "comedy",
        "priority": "low",
        "base_weight": 0.4
    }
}

# SME Content (9 additional sources beyond Small Business Trends)
SME_SOURCES = {
    "businessmatters": {
        "name": "Business Matters",
        "domain": "bmmagazine.co.uk",
        "rss_url": "https://bmmagazine.co.uk/feed/",
        "category": "sme",
        "priority": "high",
        "base_weight": 0.7
    },
    "smeweb": {
        "name": "SME Web",
        "domain": "smeweb.com",
        "rss_url": "https://www.smeweb.com/feed/",
        "category": "sme",
        "priority": "high",
        "base_weight": 0.6
    },
    "realbusiness": {
        "name": "Real Business",
        "domain": "realbusiness.co.uk",
        "rss_url": "https://realbusiness.co.uk/feed",
        "category": "sme",
        "priority": "high",
        "base_weight": 0.7
    },
    "mybusiness_au": {
        "name": "My Business Australia",
        "domain": "mybusiness.com.au",
        "rss_url": None,  # Scraping required
        "category": "sme",
        "priority": "medium",
        "base_weight": 0.6
    },
    "noobpreneur": {
        "name": "Noobpreneur",
        "domain": "noobpreneur.com",
        "rss_url": "https://www.noobpreneur.com/feed",
        "category": "sme",
        "priority": "medium",
        "base_weight": 0.5
    },
    "sageblog": {
        "name": "Sage Business Blog",
        "domain": "sage.com",
        "rss_url": "https://www.sage.com/blog/feed/",
        "category": "sme",
        "priority": "medium",
        "base_weight": 0.6
    },
    "isme": {
        "name": "ISME Ireland",
        "domain": "isme.ie",
        "rss_url": "https://isme.ie/feed/",
        "category": "sme",
        "priority": "medium",
        "base_weight": 0.6
    },
    "zeebiz": {
        "name": "Zee Business Small Business",
        "domain": "zeebiz.com",
        "rss_url": None,  # Scraping required
        "category": "sme",
        "priority": "medium",
        "base_weight": 0.5
    },
    "smestrategy": {
        "name": "SME Strategy",
        "domain": "smestrategy.net",
        "rss_url": None,  # Scraping required
        "category": "sme",
        "priority": "medium",
        "base_weight": 0.5
    }
}

# Additional Business sources (from original catalog but not in Tier 1/2)
BUSINESS_ADDITIONAL = {
    "forbes": {
        "name": "Forbes",
        "domain": "forbes.com",
        "rss_url": "https://www.forbes.com/real-time/feed2/",
        "category": "business",
        "priority": "high",
        "base_weight": 0.8
    },
    "bloomberg": {
        "name": "Bloomberg Businessweek",
        "domain": "bloomberg.com",
        "rss_url": None,  # Scraping required (limited free access)
        "category": "business",
        "priority": "high",
        "base_weight": 0.8
    },
    "mckinsey": {
        "name": "McKinsey Quarterly",
        "domain": "mckinsey.com",
        "rss_url": None,  # Scraping required
        "category": "consulting",
        "priority": "high",
        "base_weight": 0.8
    },
    "ceoworld": {
        "name": "CEOWORLD Magazine",
        "domain": "ceoworld.biz",
        "rss_url": None,  # Scraping required
        "category": "executive",
        "priority": "high",
        "base_weight": 0.7
    },
    "googleaiblog": {
        "name": "Google AI Blog",
        "domain": "blog.google",
        "rss_url": "https://blog.google/technology/ai/rss/",
        "category": "ai",
        "priority": "high",
        "base_weight": 0.8
    },
    "linkedinsales": {
        "name": "LinkedIn Sales Blog",
        "domain": "linkedin.com",
        "rss_url": None,  # Scraping required
        "category": "sales",
        "priority": "high",
        "base_weight": 0.7
    },
    "gong": {
        "name": "Gong Blog",
        "domain": "gong.io",
        "rss_url": None,  # Scraping required
        "category": "sales",
        "priority": "high",
        "base_weight": 0.7
    }
}

# Combine all sources
ALL_SOURCES_COMPLETE = {
    **TIER1_SOURCES,
    **TIER2_SOURCES,
    **MEDITATION_SOURCES,
    **QUANTUM_SOURCES,
    **HUMOR_SOURCES,
    **SME_SOURCES,
    **BUSINESS_ADDITIONAL
}

print(f"\n📊 Total sources in complete catalog: {len(ALL_SOURCES_COMPLETE)}")
print(f"   - Tier 1 (Marketing/AI): {len(TIER1_SOURCES)}")
print(f"   - Tier 2 (Business/AI/Marketing): {len(TIER2_SOURCES)}")
print(f"   - Meditation & Manifestation: {len(MEDITATION_SOURCES)}")
print(f"   - Quantum Physics: {len(QUANTUM_SOURCES)}")
print(f"   - Humor & Comedy: {len(HUMOR_SOURCES)}")
print(f"   - SME Content: {len(SME_SOURCES)}")
print(f"   - Additional Business: {len(BUSINESS_ADDITIONAL)}\n")

def count_rss_vs_scraping():
    """Count how many sources have RSS vs require scraping"""
    rss_count = 0
    scraping_count = 0
    api_count = 0

    for source_id, config in ALL_SOURCES_COMPLETE.items():
        if config.get('rss_url'):
            rss_count += 1
        elif 'api' in config.get('domain', '') or 'youtube' in source_id:
            api_count += 1
        else:
            scraping_count += 1

    print(f"📈 Extraction Methods:")
    print(f"   - RSS feeds: {rss_count}")
    print(f"   - Scraping required: {scraping_count}")
    print(f"   - API-based: {api_count}")
    print(f"   - TOTAL: {rss_count + scraping_count + api_count}\n")

if __name__ == "__main__":
    count_rss_vs_scraping()

    print("\n✅ Complete catalog configuration ready!")
    print("   Next steps:")
    print("   1. Add RSS sources to database")
    print("   2. Collect from all RSS feeds")
    print("   3. Build scrapers for non-RSS sources")
