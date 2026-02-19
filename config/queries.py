"""
Query Variations Library for B2B Lead Generation
Organized by conversion intent and industry signals
"""

QUERY_CATEGORIES = {
    # HIGH INTENT - Direct B2B supplier signals
    "supplier_signals": [
        "{keyword} supplier",
        "{keyword} manufacturer",
        "{keyword} wholesaler",
        "wholesale {keyword}",
        "{keyword} distributor",
        "{keyword} factory",
        "{keyword} company",
        "bulk {keyword}",
        "{keyword} B2B",
        "corporate {keyword} supplier",
        "promotional {keyword}",
        "{keyword} trade",
    ],

    # MEDIUM INTENT - Custom/Print services
    "custom_print": [
        "custom {keyword}",
        "{keyword} printing",
        "personalized {keyword}",
        "{keyword} screen printing",
        "{keyword} embroidery",
        "printed {keyword}",
        "{keyword} customization",
        "custom printed {keyword}",
        "{keyword} design service",
        "{keyword} imprinting",
        "logo {keyword}",
        "branded {keyword}",
        "{keyword} branding",
    ],

    # INDUSTRY SPECIFIC - Vertical targeting
    "industry_verticals": [
        "conference {keyword}",
        "event {keyword}",
        "corporate {keyword}",
        "school {keyword}",
        "medical {keyword}",
        "security {keyword}",
        "safety {keyword}",
        "hospital {keyword}",
        "trade show {keyword}",
        "business {keyword}",
    ],
}

# Maps API specific queries (shorter, more local-focused)
MAPS_QUERIES = [
    "{keyword} supplier near me",
    "{keyword} printing",
    "custom {keyword}",
    "{keyword} manufacturer",
    "{keyword} wholesaler",
    "bulk {keyword}",
    "{keyword} company",
    "promotional {keyword}",
    "{keyword} screen printing",
    "{keyword} embroidery",
]

def get_all_search_queries():
    """Returns flat list of all search query variations"""
    queries = []
    for category in QUERY_CATEGORIES.values():
        queries.extend(category)
    return queries

def get_queries_by_priority(priority="all"):
    """
    Get queries filtered by priority level
    priority: 'high', 'medium', 'industry', or 'all'
    """
    if priority == "high":
        return QUERY_CATEGORIES["supplier_signals"]
    elif priority == "medium":
        return QUERY_CATEGORIES["custom_print"]
    elif priority == "industry":
        return QUERY_CATEGORIES["industry_verticals"]
    else:
        return get_all_search_queries()

def get_maps_queries():
    """Returns Maps API optimized queries"""
    return MAPS_QUERIES

# Total counts
TOTAL_SEARCH_QUERIES = len(get_all_search_queries())
TOTAL_MAPS_QUERIES = len(MAPS_QUERIES)

if __name__ == "__main__":
    print(f"Total Search Query Variations: {TOTAL_SEARCH_QUERIES}")
    print(f"Total Maps Query Variations: {TOTAL_MAPS_QUERIES}")
    print(f"\nBreakdown:")
    for category, queries in QUERY_CATEGORIES.items():
        print(f"  {category}: {len(queries)} queries")
