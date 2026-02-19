"""
Site exclusions for filtering out non-targetable platforms
Used to focus on actual businesses rather than marketplaces/aggregators
"""

# Major marketplaces - exclude to find direct suppliers
MARKETPLACES = [
    "amazon.com",
    "ebay.com",
    "etsy.com",
    "walmart.com",
    "target.com",
    "alibaba.com",
    "aliexpress.com",
    "wish.com",
    "overstock.com",
    "wayfair.com",
    "homedepot.com",
    "lowes.com",
    "costco.com",
    "samsclub.com",
    "temu.com",
    "dhgate.com",
    "1688.com",
    "made-in-china.com",
]

# Social media & video platforms
SOCIAL_MEDIA = [
    "youtube.com",
    "facebook.com",
    "instagram.com",
    "pinterest.com",
    "tiktok.com",
    "twitter.com",
    "linkedin.com",
    "snapchat.com",
]

# Information & community sites
INFORMATION_SITES = [
    "wikipedia.org",
    "reddit.com",
    "quora.com",
    "wikihow.com",
    "answers.com",
]

# Review & rating sites
REVIEW_SITES = [
    "trustpilot.com",
    "bbb.org",
    "yelp.com",
    "sitejabber.com",
    "consumeraffairs.com",
    "bizrate.com",
]

# Search engines & directories
SEARCH_ENGINES = [
    "google.com",
    "yahoo.com",
    "bing.com",
    "duckduckgo.com",
]

# B2B directories and aggregator platforms - exclude to find direct suppliers
B2B_DIRECTORIES = [
    # Generic B2B directories
    "thomasnet.com",
    "mfg.com",
    "gobizkorea.com",
    "globalsources.com",

    # Turkish B2B platforms
    "turkishexporters.com",
    "turkeysuppliers.com",
    "turkishmachinery.net",
    "turkeyexporters.net",

    # Indian B2B platforms
    "indiamart.com",
    "exportersindia.com",
    "tradeindia.com",
    "dir.indiamart.com",

    # International B2B directories
    "tradekey.com",
    "ec21.com",
    "ecplaza.net",
    "b2bco.com",
    "manufacturers.com.tw",
    "kompass.com",
    "europages.com",
    "go4worldbusiness.com",

    # General business directories
    "yellowpages.com",
    "manta.com",
    "superpages.com",
    "hotfrog.com",
    "cylex.net",

    # Chambers of Commerce & Trade Associations (Ticaret Odaları ve İhracatçı Birlikleri)
    "tobb.org.tr",           # TOBB - Türkiye Odalar ve Borsalar Birliği
    "tim.org.tr",            # TİM - Türkiye İhracatçılar Meclisi
    "tobb.org",
    "iso.org.tr",            # İstanbul Sanayi Odası
    "ito.org.tr",            # İstanbul Ticaret Odası
    "ankaratso.org.tr",      # Ankara Ticaret ve Sanayi Odası
    "izto.org.tr",           # İzmir Ticaret Odası
    "itib.org.tr",           # İstanbul Tekstil ve Konfeksiyon İhracatçı Birlikleri
    "oaib.org.tr",           # Otomotiv Sanayii Derneği/İhracatçıları Birliği
    "chamber.org",           # Generic chamber of commerce
    "chamber.com",
    "uschamber.com",         # US Chamber of Commerce
    "britishchambers.org.uk", # British Chambers of Commerce
    "export.gov",            # US Export Portal
    "trade.gov",             # US Trade Portal
    "fita.org",              # Federation of International Trade Associations
]

# News & media sites
NEWS_MEDIA = [
    "nytimes.com",
    "wsj.com",
    "forbes.com",
    "bloomberg.com",
    "cnbc.com",
]

def get_exclusion_string(include_b2b_directories=False):
    """
    Generate the -site:xxx exclusion string for search queries

    Args:
        include_b2b_directories: Whether to exclude B2B directories too

    Returns:
        String of space-separated -site:domain.com exclusions
    """
    excluded_sites = (
        MARKETPLACES +
        SOCIAL_MEDIA +
        INFORMATION_SITES +
        REVIEW_SITES +
        SEARCH_ENGINES +
        NEWS_MEDIA
    )

    if include_b2b_directories:
        excluded_sites += B2B_DIRECTORIES

    return " ".join([f"-site:{site}" for site in excluded_sites])

def get_exclusion_list(include_b2b_directories=False):
    """
    Get list of excluded domains

    Args:
        include_b2b_directories: Whether to exclude B2B directories too

    Returns:
        List of domain strings
    """
    excluded_sites = (
        MARKETPLACES +
        SOCIAL_MEDIA +
        INFORMATION_SITES +
        REVIEW_SITES +
        SEARCH_ENGINES +
        NEWS_MEDIA
    )

    if include_b2b_directories:
        excluded_sites += B2B_DIRECTORIES

    return excluded_sites

# Pre-generated exclusion string (default - now includes B2B directories)
DEFAULT_EXCLUSIONS = get_exclusion_string(include_b2b_directories=True)
TOTAL_EXCLUSIONS = len(get_exclusion_list(include_b2b_directories=True))

if __name__ == "__main__":
    print(f"Total Excluded Sites: {TOTAL_EXCLUSIONS}")
    print(f"\nBreakdown:")
    print(f"  Marketplaces: {len(MARKETPLACES)}")
    print(f"  Social Media: {len(SOCIAL_MEDIA)}")
    print(f"  Information: {len(INFORMATION_SITES)}")
    print(f"  Reviews: {len(REVIEW_SITES)}")
    print(f"  Search Engines: {len(SEARCH_ENGINES)}")
    print(f"  News/Media: {len(NEWS_MEDIA)}")
    print(f"  B2B Directories: {len(B2B_DIRECTORIES)}")
    print(f"\nExclusion String Preview (first 200 chars):")
    print(f"{DEFAULT_EXCLUSIONS[:200]}...")
