"""
Multi-country configuration with 195 countries
Cities will be dynamically selected by AI based on business context
"""

COUNTRIES = {
    # North America
    "US": {"name": "United States", "code": "us", "language": "en", "currency": "USD"},
    "CA": {"name": "Canada", "code": "ca", "language": "en", "currency": "CAD"},
    "MX": {"name": "Mexico", "code": "mx", "language": "es", "currency": "MXN"},

    # Central America & Caribbean
    "GT": {"name": "Guatemala", "code": "gt", "language": "es", "currency": "GTQ"},
    "HN": {"name": "Honduras", "code": "hn", "language": "es", "currency": "HNL"},
    "SV": {"name": "El Salvador", "code": "sv", "language": "es", "currency": "USD"},
    "NI": {"name": "Nicaragua", "code": "ni", "language": "es", "currency": "NIO"},
    "CR": {"name": "Costa Rica", "code": "cr", "language": "es", "currency": "CRC"},
    "PA": {"name": "Panama", "code": "pa", "language": "es", "currency": "PAB"},
    "BZ": {"name": "Belize", "code": "bz", "language": "en", "currency": "BZD"},
    "CU": {"name": "Cuba", "code": "cu", "language": "es", "currency": "CUP"},
    "JM": {"name": "Jamaica", "code": "jm", "language": "en", "currency": "JMD"},
    "HT": {"name": "Haiti", "code": "ht", "language": "fr", "currency": "HTG"},
    "DO": {"name": "Dominican Republic", "code": "do", "language": "es", "currency": "DOP"},
    "TT": {"name": "Trinidad and Tobago", "code": "tt", "language": "en", "currency": "TTD"},
    "BS": {"name": "Bahamas", "code": "bs", "language": "en", "currency": "BSD"},
    "BB": {"name": "Barbados", "code": "bb", "language": "en", "currency": "BBD"},

    # South America
    "BR": {"name": "Brazil", "code": "br", "language": "pt", "currency": "BRL"},
    "AR": {"name": "Argentina", "code": "ar", "language": "es", "currency": "ARS"},
    "CO": {"name": "Colombia", "code": "co", "language": "es", "currency": "COP"},
    "VE": {"name": "Venezuela", "code": "ve", "language": "es", "currency": "VES"},
    "PE": {"name": "Peru", "code": "pe", "language": "es", "currency": "PEN"},
    "CL": {"name": "Chile", "code": "cl", "language": "es", "currency": "CLP"},
    "EC": {"name": "Ecuador", "code": "ec", "language": "es", "currency": "USD"},
    "BO": {"name": "Bolivia", "code": "bo", "language": "es", "currency": "BOB"},
    "PY": {"name": "Paraguay", "code": "py", "language": "es", "currency": "PYG"},
    "UY": {"name": "Uruguay", "code": "uy", "language": "es", "currency": "UYU"},
    "GY": {"name": "Guyana", "code": "gy", "language": "en", "currency": "GYD"},
    "SR": {"name": "Suriname", "code": "sr", "language": "nl", "currency": "SRD"},

    # Western Europe
    "GB": {"name": "United Kingdom", "code": "uk", "language": "en", "currency": "GBP"},
    "IE": {"name": "Ireland", "code": "ie", "language": "en", "currency": "EUR"},
    "FR": {"name": "France", "code": "fr", "language": "fr", "currency": "EUR"},
    "DE": {"name": "Germany", "code": "de", "language": "de", "currency": "EUR"},
    "NL": {"name": "Netherlands", "code": "nl", "language": "nl", "currency": "EUR"},
    "BE": {"name": "Belgium", "code": "be", "language": "nl", "currency": "EUR"},
    "LU": {"name": "Luxembourg", "code": "lu", "language": "fr", "currency": "EUR"},
    "CH": {"name": "Switzerland", "code": "ch", "language": "de", "currency": "CHF"},
    "AT": {"name": "Austria", "code": "at", "language": "de", "currency": "EUR"},

    # Southern Europe
    "ES": {"name": "Spain", "code": "es", "language": "es", "currency": "EUR"},
    "PT": {"name": "Portugal", "code": "pt", "language": "pt", "currency": "EUR"},
    "IT": {"name": "Italy", "code": "it", "language": "it", "currency": "EUR"},
    "GR": {"name": "Greece", "code": "gr", "language": "el", "currency": "EUR"},
    "MT": {"name": "Malta", "code": "mt", "language": "en", "currency": "EUR"},
    "CY": {"name": "Cyprus", "code": "cy", "language": "el", "currency": "EUR"},

    # Northern Europe
    "SE": {"name": "Sweden", "code": "se", "language": "sv", "currency": "SEK"},
    "NO": {"name": "Norway", "code": "no", "language": "no", "currency": "NOK"},
    "DK": {"name": "Denmark", "code": "dk", "language": "da", "currency": "DKK"},
    "FI": {"name": "Finland", "code": "fi", "language": "fi", "currency": "EUR"},
    "IS": {"name": "Iceland", "code": "is", "language": "is", "currency": "ISK"},

    # Eastern Europe
    "PL": {"name": "Poland", "code": "pl", "language": "pl", "currency": "PLN"},
    "CZ": {"name": "Czech Republic", "code": "cz", "language": "cs", "currency": "CZK"},
    "SK": {"name": "Slovakia", "code": "sk", "language": "sk", "currency": "EUR"},
    "HU": {"name": "Hungary", "code": "hu", "language": "hu", "currency": "HUF"},
    "RO": {"name": "Romania", "code": "ro", "language": "ro", "currency": "RON"},
    "BG": {"name": "Bulgaria", "code": "bg", "language": "bg", "currency": "BGN"},
    "HR": {"name": "Croatia", "code": "hr", "language": "hr", "currency": "EUR"},
    "SI": {"name": "Slovenia", "code": "si", "language": "sl", "currency": "EUR"},
    "RS": {"name": "Serbia", "code": "rs", "language": "sr", "currency": "RSD"},
    "BA": {"name": "Bosnia and Herzegovina", "code": "ba", "language": "bs", "currency": "BAM"},
    "MK": {"name": "North Macedonia", "code": "mk", "language": "mk", "currency": "MKD"},
    "AL": {"name": "Albania", "code": "al", "language": "sq", "currency": "ALL"},
    "ME": {"name": "Montenegro", "code": "me", "language": "sr", "currency": "EUR"},
    "XK": {"name": "Kosovo", "code": "xk", "language": "sq", "currency": "EUR"},
    "EE": {"name": "Estonia", "code": "ee", "language": "et", "currency": "EUR"},
    "LV": {"name": "Latvia", "code": "lv", "language": "lv", "currency": "EUR"},
    "LT": {"name": "Lithuania", "code": "lt", "language": "lt", "currency": "EUR"},
    "BY": {"name": "Belarus", "code": "by", "language": "be", "currency": "BYN"},
    "UA": {"name": "Ukraine", "code": "ua", "language": "uk", "currency": "UAH"},
    "MD": {"name": "Moldova", "code": "md", "language": "ro", "currency": "MDL"},

    # Russia
    "RU": {"name": "Russia", "code": "ru", "language": "ru", "currency": "RUB"},

    # Middle East
    "TR": {"name": "Turkey", "code": "tr", "language": "tr", "currency": "TRY"},
    "IL": {"name": "Israel", "code": "il", "language": "he", "currency": "ILS"},
    "SA": {"name": "Saudi Arabia", "code": "sa", "language": "ar", "currency": "SAR"},
    "AE": {"name": "United Arab Emirates", "code": "ae", "language": "ar", "currency": "AED"},
    "QA": {"name": "Qatar", "code": "qa", "language": "ar", "currency": "QAR"},
    "KW": {"name": "Kuwait", "code": "kw", "language": "ar", "currency": "KWD"},
    "BH": {"name": "Bahrain", "code": "bh", "language": "ar", "currency": "BHD"},
    "OM": {"name": "Oman", "code": "om", "language": "ar", "currency": "OMR"},
    "JO": {"name": "Jordan", "code": "jo", "language": "ar", "currency": "JOD"},
    "LB": {"name": "Lebanon", "code": "lb", "language": "ar", "currency": "LBP"},
    "SY": {"name": "Syria", "code": "sy", "language": "ar", "currency": "SYP"},
    "IQ": {"name": "Iraq", "code": "iq", "language": "ar", "currency": "IQD"},
    "IR": {"name": "Iran", "code": "ir", "language": "fa", "currency": "IRR"},
    "YE": {"name": "Yemen", "code": "ye", "language": "ar", "currency": "YER"},

    # Central Asia
    "KZ": {"name": "Kazakhstan", "code": "kz", "language": "kk", "currency": "KZT"},
    "UZ": {"name": "Uzbekistan", "code": "uz", "language": "uz", "currency": "UZS"},
    "TM": {"name": "Turkmenistan", "code": "tm", "language": "tk", "currency": "TMT"},
    "KG": {"name": "Kyrgyzstan", "code": "kg", "language": "ky", "currency": "KGS"},
    "TJ": {"name": "Tajikistan", "code": "tj", "language": "tg", "currency": "TJS"},
    "AF": {"name": "Afghanistan", "code": "af", "language": "fa", "currency": "AFN"},
    "PK": {"name": "Pakistan", "code": "pk", "language": "ur", "currency": "PKR"},

    # South Asia
    "IN": {"name": "India", "code": "in", "language": "hi", "currency": "INR"},
    "BD": {"name": "Bangladesh", "code": "bd", "language": "bn", "currency": "BDT"},
    "LK": {"name": "Sri Lanka", "code": "lk", "language": "si", "currency": "LKR"},
    "NP": {"name": "Nepal", "code": "np", "language": "ne", "currency": "NPR"},
    "BT": {"name": "Bhutan", "code": "bt", "language": "dz", "currency": "BTN"},
    "MV": {"name": "Maldives", "code": "mv", "language": "dv", "currency": "MVR"},

    # East Asia
    "CN": {"name": "China", "code": "cn", "language": "zh", "currency": "CNY"},
    "JP": {"name": "Japan", "code": "jp", "language": "ja", "currency": "JPY"},
    "KR": {"name": "South Korea", "code": "kr", "language": "ko", "currency": "KRW"},
    "KP": {"name": "North Korea", "code": "kp", "language": "ko", "currency": "KPW"},
    "MN": {"name": "Mongolia", "code": "mn", "language": "mn", "currency": "MNT"},
    "TW": {"name": "Taiwan", "code": "tw", "language": "zh", "currency": "TWD"},
    "HK": {"name": "Hong Kong", "code": "hk", "language": "zh", "currency": "HKD"},
    "MO": {"name": "Macau", "code": "mo", "language": "zh", "currency": "MOP"},

    # Southeast Asia
    "TH": {"name": "Thailand", "code": "th", "language": "th", "currency": "THB"},
    "VN": {"name": "Vietnam", "code": "vn", "language": "vi", "currency": "VND"},
    "SG": {"name": "Singapore", "code": "sg", "language": "en", "currency": "SGD"},
    "MY": {"name": "Malaysia", "code": "my", "language": "ms", "currency": "MYR"},
    "ID": {"name": "Indonesia", "code": "id", "language": "id", "currency": "IDR"},
    "PH": {"name": "Philippines", "code": "ph", "language": "en", "currency": "PHP"},
    "MM": {"name": "Myanmar", "code": "mm", "language": "my", "currency": "MMK"},
    "KH": {"name": "Cambodia", "code": "kh", "language": "km", "currency": "KHR"},
    "LA": {"name": "Laos", "code": "la", "language": "lo", "currency": "LAK"},
    "BN": {"name": "Brunei", "code": "bn", "language": "ms", "currency": "BND"},
    "TL": {"name": "Timor-Leste", "code": "tl", "language": "pt", "currency": "USD"},

    # Oceania
    "AU": {"name": "Australia", "code": "au", "language": "en", "currency": "AUD"},
    "NZ": {"name": "New Zealand", "code": "nz", "language": "en", "currency": "NZD"},
    "PG": {"name": "Papua New Guinea", "code": "pg", "language": "en", "currency": "PGK"},
    "FJ": {"name": "Fiji", "code": "fj", "language": "en", "currency": "FJD"},

    # North Africa
    "EG": {"name": "Egypt", "code": "eg", "language": "ar", "currency": "EGP"},
    "DZ": {"name": "Algeria", "code": "dz", "language": "ar", "currency": "DZD"},
    "MA": {"name": "Morocco", "code": "ma", "language": "ar", "currency": "MAD"},
    "TN": {"name": "Tunisia", "code": "tn", "language": "ar", "currency": "TND"},
    "LY": {"name": "Libya", "code": "ly", "language": "ar", "currency": "LYD"},
    "SD": {"name": "Sudan", "code": "sd", "language": "ar", "currency": "SDG"},

    # West Africa
    "NG": {"name": "Nigeria", "code": "ng", "language": "en", "currency": "NGN"},
    "GH": {"name": "Ghana", "code": "gh", "language": "en", "currency": "GHS"},
    "CI": {"name": "Ivory Coast", "code": "ci", "language": "fr", "currency": "XOF"},
    "SN": {"name": "Senegal", "code": "sn", "language": "fr", "currency": "XOF"},
    "ML": {"name": "Mali", "code": "ml", "language": "fr", "currency": "XOF"},
    "BF": {"name": "Burkina Faso", "code": "bf", "language": "fr", "currency": "XOF"},
    "NE": {"name": "Niger", "code": "ne", "language": "fr", "currency": "XOF"},
    "GN": {"name": "Guinea", "code": "gn", "language": "fr", "currency": "GNF"},
    "SL": {"name": "Sierra Leone", "code": "sl", "language": "en", "currency": "SLL"},
    "LR": {"name": "Liberia", "code": "lr", "language": "en", "currency": "LRD"},
    "TG": {"name": "Togo", "code": "tg", "language": "fr", "currency": "XOF"},
    "BJ": {"name": "Benin", "code": "bj", "language": "fr", "currency": "XOF"},
    "MR": {"name": "Mauritania", "code": "mr", "language": "ar", "currency": "MRU"},
    "GM": {"name": "Gambia", "code": "gm", "language": "en", "currency": "GMD"},
    "GW": {"name": "Guinea-Bissau", "code": "gw", "language": "pt", "currency": "XOF"},
    "CV": {"name": "Cape Verde", "code": "cv", "language": "pt", "currency": "CVE"},

    # Central Africa
    "CM": {"name": "Cameroon", "code": "cm", "language": "fr", "currency": "XAF"},
    "TD": {"name": "Chad", "code": "td", "language": "fr", "currency": "XAF"},
    "CF": {"name": "Central African Republic", "code": "cf", "language": "fr", "currency": "XAF"},
    "CG": {"name": "Republic of the Congo", "code": "cg", "language": "fr", "currency": "XAF"},
    "CD": {"name": "Democratic Republic of the Congo", "code": "cd", "language": "fr", "currency": "CDF"},
    "GA": {"name": "Gabon", "code": "ga", "language": "fr", "currency": "XAF"},
    "GQ": {"name": "Equatorial Guinea", "code": "gq", "language": "es", "currency": "XAF"},
    "ST": {"name": "Sao Tome and Principe", "code": "st", "language": "pt", "currency": "STN"},

    # East Africa
    "KE": {"name": "Kenya", "code": "ke", "language": "sw", "currency": "KES"},
    "TZ": {"name": "Tanzania", "code": "tz", "language": "sw", "currency": "TZS"},
    "UG": {"name": "Uganda", "code": "ug", "language": "en", "currency": "UGX"},
    "RW": {"name": "Rwanda", "code": "rw", "language": "rw", "currency": "RWF"},
    "BI": {"name": "Burundi", "code": "bi", "language": "fr", "currency": "BIF"},
    "ET": {"name": "Ethiopia", "code": "et", "language": "am", "currency": "ETB"},
    "SO": {"name": "Somalia", "code": "so", "language": "so", "currency": "SOS"},
    "DJ": {"name": "Djibouti", "code": "dj", "language": "fr", "currency": "DJF"},
    "ER": {"name": "Eritrea", "code": "er", "language": "ti", "currency": "ERN"},
    "SS": {"name": "South Sudan", "code": "ss", "language": "en", "currency": "SSP"},

    # Southern Africa
    "ZA": {"name": "South Africa", "code": "za", "language": "en", "currency": "ZAR"},
    "ZW": {"name": "Zimbabwe", "code": "zw", "language": "en", "currency": "ZWL"},
    "ZM": {"name": "Zambia", "code": "zm", "language": "en", "currency": "ZMW"},
    "MW": {"name": "Malawi", "code": "mw", "language": "en", "currency": "MWK"},
    "MZ": {"name": "Mozambique", "code": "mz", "language": "pt", "currency": "MZN"},
    "BW": {"name": "Botswana", "code": "bw", "language": "en", "currency": "BWP"},
    "NA": {"name": "Namibia", "code": "na", "language": "en", "currency": "NAD"},
    "LS": {"name": "Lesotho", "code": "ls", "language": "en", "currency": "LSL"},
    "SZ": {"name": "Eswatini", "code": "sz", "language": "en", "currency": "SZL"},
    "AO": {"name": "Angola", "code": "ao", "language": "pt", "currency": "AOA"},
    "MG": {"name": "Madagascar", "code": "mg", "language": "mg", "currency": "MGA"},
    "MU": {"name": "Mauritius", "code": "mu", "language": "en", "currency": "MUR"},
    "SC": {"name": "Seychelles", "code": "sc", "language": "en", "currency": "SCR"},
    "KM": {"name": "Comoros", "code": "km", "language": "ar", "currency": "KMF"},
}


def get_country(country_code: str):
    """Get country data by code"""
    return COUNTRIES.get(country_code.upper())


def get_all_country_codes():
    """Get list of all country codes"""
    return sorted(COUNTRIES.keys())


def get_all_country_names():
    """Get list of all country names sorted alphabetically"""
    return sorted([(code, data['name']) for code, data in COUNTRIES.items()], key=lambda x: x[1])


def get_countries_by_region():
    """Get countries grouped by region"""
    regions = {
        "North America": ["US", "CA", "MX"],
        "Central America & Caribbean": ["GT", "HN", "SV", "NI", "CR", "PA", "BZ", "CU", "JM", "HT", "DO", "TT", "BS", "BB"],
        "South America": ["BR", "AR", "CO", "VE", "PE", "CL", "EC", "BO", "PY", "UY", "GY", "SR"],
        "Western Europe": ["GB", "IE", "FR", "DE", "NL", "BE", "LU", "CH", "AT"],
        "Southern Europe": ["ES", "PT", "IT", "GR", "MT", "CY"],
        "Northern Europe": ["SE", "NO", "DK", "FI", "IS"],
        "Eastern Europe": ["PL", "CZ", "SK", "HU", "RO", "BG", "HR", "SI", "RS", "BA", "MK", "AL", "ME", "XK", "EE", "LV", "LT", "BY", "UA", "MD"],
        "Russia": ["RU"],
        "Middle East": ["TR", "IL", "SA", "AE", "QA", "KW", "BH", "OM", "JO", "LB", "SY", "IQ", "IR", "YE"],
        "Central Asia": ["KZ", "UZ", "TM", "KG", "TJ", "AF", "PK"],
        "South Asia": ["IN", "BD", "LK", "NP", "BT", "MV"],
        "East Asia": ["CN", "JP", "KR", "KP", "MN", "TW", "HK", "MO"],
        "Southeast Asia": ["TH", "VN", "SG", "MY", "ID", "PH", "MM", "KH", "LA", "BN", "TL"],
        "Oceania": ["AU", "NZ", "PG", "FJ"],
        "North Africa": ["EG", "DZ", "MA", "TN", "LY", "SD"],
        "West Africa": ["NG", "GH", "CI", "SN", "ML", "BF", "NE", "GN", "SL", "LR", "TG", "BJ", "MR", "GM", "GW", "CV"],
        "Central Africa": ["CM", "TD", "CF", "CG", "CD", "GA", "GQ", "ST"],
        "East Africa": ["KE", "TZ", "UG", "RW", "BI", "ET", "SO", "DJ", "ER", "SS"],
        "Southern Africa": ["ZA", "ZW", "ZM", "MW", "MZ", "BW", "NA", "LS", "SZ", "AO", "MG", "MU", "SC", "KM"],
    }
    return regions


def get_language_for_country(country_code: str):
    """Get primary language for country"""
    country = get_country(country_code)
    return country['language'] if country else 'en'


if __name__ == "__main__":
    print(f"Total countries: {len(COUNTRIES)}")
    print("\nCountries by region:")
    regions = get_countries_by_region()
    for region, codes in regions.items():
        print(f"  {region}: {len(codes)} countries")

    print("\nAll countries:")
    for code, name in get_all_country_names():
        country = get_country(code)
        print(f"  {code} - {name} ({country['language']}, {country['currency']})")
