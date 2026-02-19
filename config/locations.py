"""
Geographic targeting configuration for US markets
Prioritized by business density and manufacturing presence
"""

# Top 20 US cities for B2B targeting (Conservative approach)
TOP_20_CITIES = [
    # Tier 1: Major Business Hubs (5)
    {"city": "New York", "state": "NY", "tier": 1},
    {"city": "Los Angeles", "state": "CA", "tier": 1},
    {"city": "Chicago", "state": "IL", "tier": 1},
    {"city": "Houston", "state": "TX", "tier": 1},
    {"city": "Dallas", "state": "TX", "tier": 1},

    # Tier 2: Manufacturing & Tech Centers (5)
    {"city": "Philadelphia", "state": "PA", "tier": 2},
    {"city": "Phoenix", "state": "AZ", "tier": 2},
    {"city": "San Diego", "state": "CA", "tier": 2},
    {"city": "San Jose", "state": "CA", "tier": 2},
    {"city": "Austin", "state": "TX", "tier": 2},

    # Tier 3: Regional Important (5)
    {"city": "Atlanta", "state": "GA", "tier": 3},
    {"city": "Boston", "state": "MA", "tier": 3},
    {"city": "Seattle", "state": "WA", "tier": 3},
    {"city": "Denver", "state": "CO", "tier": 3},
    {"city": "Miami", "state": "FL", "tier": 3},

    # Tier 4: Manufacturing Hubs (5)
    {"city": "Detroit", "state": "MI", "tier": 4},
    {"city": "Milwaukee", "state": "WI", "tier": 4},
    {"city": "Minneapolis", "state": "MN", "tier": 4},
    {"city": "Charlotte", "state": "NC", "tier": 4},
    {"city": "Portland", "state": "OR", "tier": 4},
]

# Extended list (for future expansion to 50 cities)
EXTENDED_CITIES = [
    {"city": "San Francisco", "state": "CA", "tier": 2},
    {"city": "Indianapolis", "state": "IN", "tier": 3},
    {"city": "Columbus", "state": "OH", "tier": 3},
    {"city": "Jacksonville", "state": "FL", "tier": 3},
    {"city": "Fort Worth", "state": "TX", "tier": 3},
    {"city": "San Antonio", "state": "TX", "tier": 3},
    {"city": "Nashville", "state": "TN", "tier": 3},
    {"city": "Memphis", "state": "TN", "tier": 4},
    {"city": "Louisville", "state": "KY", "tier": 4},
    {"city": "Baltimore", "state": "MD", "tier": 3},
    {"city": "Cleveland", "state": "OH", "tier": 4},
    {"city": "Pittsburgh", "state": "PA", "tier": 4},
    {"city": "Cincinnati", "state": "OH", "tier": 4},
    {"city": "Buffalo", "state": "NY", "tier": 4},
    {"city": "Rochester", "state": "NY", "tier": 4},
    {"city": "Grand Rapids", "state": "MI", "tier": 4},
    {"city": "Kansas City", "state": "MO", "tier": 3},
    {"city": "Salt Lake City", "state": "UT", "tier": 3},
    {"city": "Las Vegas", "state": "NV", "tier": 3},
    {"city": "Raleigh", "state": "NC", "tier": 3},
    {"city": "Orlando", "state": "FL", "tier": 3},
    {"city": "Tampa", "state": "FL", "tier": 3},
    {"city": "Sacramento", "state": "CA", "tier": 3},
    {"city": "Fresno", "state": "CA", "tier": 4},
    {"city": "Omaha", "state": "NE", "tier": 4},
    {"city": "Tucson", "state": "AZ", "tier": 4},
    {"city": "Albuquerque", "state": "NM", "tier": 4},
    {"city": "Mesa", "state": "AZ", "tier": 4},
    {"city": "Oklahoma City", "state": "OK", "tier": 4},
    {"city": "Toledo", "state": "OH", "tier": 4},
]

def get_cities(tier=None, limit=None):
    """
    Get cities filtered by tier and/or limit

    Args:
        tier: Filter by tier (1, 2, 3, 4) or None for all
        limit: Maximum number of cities to return

    Returns:
        List of city dictionaries
    """
    cities = TOP_20_CITIES.copy()

    if tier:
        cities = [c for c in cities if c["tier"] == tier]

    if limit:
        cities = cities[:limit]

    return cities

def get_city_string(city_dict, format="full"):
    """
    Format city for query insertion

    Args:
        city_dict: City dictionary with 'city' and 'state' keys
        format: 'full' (City, ST), 'city' (City), 'state' (ST)

    Returns:
        Formatted string
    """
    if format == "full":
        return f"{city_dict['city']}, {city_dict['state']}"
    elif format == "city":
        return city_dict['city']
    elif format == "state":
        return city_dict['state']
    else:
        return f"{city_dict['city']}, {city_dict['state']}"

def get_all_cities(include_extended=False):
    """Get all cities including extended list if requested"""
    if include_extended:
        return TOP_20_CITIES + EXTENDED_CITIES
    return TOP_20_CITIES

# Statistics
TOTAL_TOP_CITIES = len(TOP_20_CITIES)
TOTAL_EXTENDED_CITIES = len(EXTENDED_CITIES)
TOTAL_ALL_CITIES = TOTAL_TOP_CITIES + TOTAL_EXTENDED_CITIES

if __name__ == "__main__":
    print(f"Top 20 Cities: {TOTAL_TOP_CITIES}")
    print(f"Extended Cities: {TOTAL_EXTENDED_CITIES}")
    print(f"Total Available: {TOTAL_ALL_CITIES}")
    print(f"\nTier Breakdown (Top 20):")
    for tier in [1, 2, 3, 4]:
        tier_cities = get_cities(tier=tier)
        print(f"  Tier {tier}: {len(tier_cities)} cities")
        for city in tier_cities:
            print(f"    - {get_city_string(city)}")
