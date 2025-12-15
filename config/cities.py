"""
Major US Cities Configuration
50+ cities organized by region for comprehensive market coverage
"""

# Format: (city, state_abbreviation)
MAJOR_CITIES = [
    # Northeast
    ("New York", "NY"),
    ("Philadelphia", "PA"),
    ("Boston", "MA"),
    ("Pittsburgh", "PA"),
    ("Newark", "NJ"),
    ("Hartford", "CT"),
    ("Providence", "RI"),
    ("Buffalo", "NY"),
    
    # Southeast
    ("Atlanta", "GA"),
    ("Miami", "FL"),
    ("Tampa", "FL"),
    ("Orlando", "FL"),
    ("Charlotte", "NC"),
    ("Raleigh", "NC"),
    ("Nashville", "TN"),
    ("Jacksonville", "FL"),
    ("Memphis", "TN"),
    ("Louisville", "KY"),
    ("Richmond", "VA"),
    ("Birmingham", "AL"),
    
    # Midwest
    ("Chicago", "IL"),
    ("Detroit", "MI"),
    ("Minneapolis", "MN"),
    ("Cleveland", "OH"),
    ("Columbus", "OH"),
    ("Cincinnati", "OH"),
    ("Indianapolis", "IN"),
    ("Milwaukee", "WI"),
    ("Kansas City", "MO"),
    ("St. Louis", "MO"),
    ("Omaha", "NE"),
    
    # Southwest
    ("Dallas", "TX"),
    ("Houston", "TX"),
    ("San Antonio", "TX"),
    ("Austin", "TX"),
    ("Phoenix", "AZ"),
    ("Tucson", "AZ"),
    ("Albuquerque", "NM"),
    ("El Paso", "TX"),
    ("Oklahoma City", "OK"),
    ("Tulsa", "OK"),
    
    # West Coast
    ("Los Angeles", "CA"),
    ("San Francisco", "CA"),
    ("San Diego", "CA"),
    ("San Jose", "CA"),
    ("Sacramento", "CA"),
    ("Seattle", "WA"),
    ("Portland", "OR"),
    ("Las Vegas", "NV"),
    ("Denver", "CO"),
    ("Salt Lake City", "UT"),
    
    # Additional Markets
    ("Washington", "DC"),
    ("Baltimore", "MD"),
    ("New Orleans", "LA"),
    ("Honolulu", "HI"),
    ("Anchorage", "AK"),
]

# Subset for quick testing (3 cities)
TEST_CITIES = MAJOR_CITIES[:3]

# Regional groupings for targeted scraping
REGIONS = {
    'northeast': MAJOR_CITIES[:8],
    'southeast': MAJOR_CITIES[8:20],
    'midwest': MAJOR_CITIES[20:31],
    'southwest': MAJOR_CITIES[31:41],
    'west': MAJOR_CITIES[41:51],
}

# High-demand markets (typically higher pay rates)
HIGH_DEMAND_MARKETS = [
    ("San Francisco", "CA"),
    ("New York", "NY"),
    ("Los Angeles", "CA"),
    ("Boston", "MA"),
    ("Seattle", "WA"),
    ("San Jose", "CA"),
    ("Washington", "DC"),
    ("Chicago", "IL"),
    ("Miami", "FL"),
    ("Denver", "CO"),
]
