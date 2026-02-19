# Serper AI Lead Generation System

AI-powered B2B lead generation tool using Serper API (Google Search + Maps) with OpenAI query optimization. Multi-country support with native language translations.

## Quick Start

```bash
# Install dependencies
pip install -r requirements_ui.txt

# Launch UI
streamlit run app.py
# Opens at http://localhost:8501
```

**5-Minute Setup**: See [QUICKSTART.md](QUICKSTART.md)

## Features

### AI-Powered Query Generation
- **Free-form business context** - Describe your business and ideal customer in natural language
- **Smart query optimization** - GPT-4 generates 15-25 targeted search queries
- **Priority ranking** - Queries prioritized by conversion potential (HIGH/MEDIUM/LOW)
- **Native language support** - Auto-translates queries for 9 countries

### Multi-Country Search
- **9 pre-configured countries**: US, UK, Germany, France, Canada, Australia, Spain, Italy, Netherlands
- **200+ cities database** with business density rankings
- **Geo-targeted search** - Location-specific results per city
- **Budget optimization** - AI balances coverage vs. API costs

### Two-Phase Discovery
**Phase 1: Search API** - Web discovery across query variations
- 35 query variations in 3 categories (supplier signals, custom/print, industry verticals)
- Auto-excludes major marketplaces (Amazon, eBay, Etsy, etc.)
- Pagination support (up to 100 results per query)

**Phase 2: Maps API** - Local business supplement
- Targets cities with low Phase 1 coverage
- 10 Maps-optimized queries per city
- Rich business data (address, phone, ratings, reviews)

### Deduplication & Export
- Domain-based deduplication across all phases
- CSV export with: domain, URL, title, description, location, query, position
- Results saved to `results/` directory with timestamps

### NEW: Query Intelligence (January 2026)
- **Related Searches** - Automatically captures Google's "Related Searches" suggestions
- **Autocomplete API** - Fetch Google autocomplete suggestions for keyword expansion
- **Zero Cost** - Related searches included in existing API calls
- **Separate Export** - Related searches saved to dedicated CSV files

## Use Cases

**Cold Email Outreach**
```
Business: SaaS CRM provider
Target: Custom lanyard manufacturers for B2B conferences
Result: 15,000-25,000 targetable businesses across 20 cities
```

**Service Provider Discovery**
```
Business: Digital marketing agency
Target: Shopify e-commerce stores in specific regions
Result: Location-tagged businesses with contact info
```

**Supplier Research**
```
Business: Import/export company
Target: Wholesale promotional product suppliers
Result: Filtered B2B suppliers excluding marketplaces
```

## Architecture

```
User Input → AI Query Generator → Query Plan (15-25 variations)
                                        ↓
                     Phase 1: Search API (web results)
                                        ↓
                     Coverage Analysis → Low-coverage cities identified
                                        ↓
                     Phase 2: Maps API (local businesses)
                                        ↓
                     Domain Deduplication → CSV Export
```

### Key Components

**`app.py`** - Streamlit interactive UI (primary interface)
- Step-by-step workflow with AI plan review
- Real-time progress tracking
- Interactive feedback and regeneration

**`app_flask_v2.py`** - Flask web interface (alternative)
- RESTful API backend
- JSON response format
- Suitable for integration

**`orchestrator.py`** - CLI pipeline coordinator
- Two-phase execution with prompts
- Coverage analysis between phases
- Suitable for automation

**`serper_search_v2.py`** - Enhanced Search API
- Multi-location support
- Query variation engine
- Site exclusion filtering

**`serper_maps.py`** - Maps API integration
- Local business discovery
- Rich metadata extraction
- Place ID tracking

**`ai_query_generator_v2.py`** - OpenAI query optimizer
- Free-form context analysis
- Strategy explanation with reasoning
- Budget-aware recommendations

### Configuration

**`config/queries.py`** - 35 search + 10 maps query variations
```python
QUERY_CATEGORIES = {
    "supplier_signals": [    # HIGH priority (12 queries)
        "{keyword} supplier", "{keyword} manufacturer", ...
    ],
    "custom_print": [        # MEDIUM priority (13 queries)
        "custom {keyword}", "{keyword} printing", ...
    ],
    "industry_verticals": [  # Industry specific (10 queries)
        "conference {keyword}", "corporate {keyword}", ...
    ]
}
```

**`config/countries.py`** - 9 countries, 200+ cities
```python
COUNTRIES = {
    "US": {"name": "United States", "code": "us", "language": "en", ...},
    "DE": {"name": "Germany", "code": "de", "language": "de", ...},
    # ... 7 more countries
}
```

**`config/locations.py`** - 50 US cities in 4 tiers
```python
TOP_20_CITIES = [
    {"city": "New York", "state": "NY", "tier": 1},
    {"city": "Los Angeles", "state": "CA", "tier": 1},
    # ... 48 more cities
]
```

**`config/exclusions.py`** - Site filtering
```python
MARKETPLACES = ["amazon.com", "ebay.com", "etsy.com", ...]
SOCIAL_MEDIA = ["facebook.com", "instagram.com", ...]
# Auto-appended to all queries
```

## Usage Examples

### Streamlit UI (Recommended)

```bash
streamlit run app.py
```

**Workflow:**
1. **Configure** - Enter business context, select countries, set budget
2. **AI Generation** - AI creates query plan (10-30 seconds)
3. **Review** - Examine queries, cities, strategy explanation
4. **Feedback** (optional) - Request modifications, AI regenerates
5. **Execute** - Run searches (10-90 minutes depending on budget)
6. **Export** - Download CSV with all results

**Example Business Context:**
```
Our business: SaaS CRM for small businesses

Target customer profile: Custom promotional product manufacturers
- B2B focused (wholesale, bulk orders)
- 10-50 employees, $500K-5M revenue
- Serve conference/event market
- Offer custom printing, embroidery, screen printing
- Use terms like "supplier", "manufacturer", "bulk order"

Must have:
- Online ordering capability
- Corporate client portfolio
- Custom design services

Avoid:
- Pure marketplace sellers (Alibaba, Amazon)
- Retail-only businesses
- Very small (<5 employees) or very large (>500)
```

### CLI Orchestrator

```bash
python orchestrator.py
```

**Interactive prompts:**
```
Enter keywords (one per line): lanyard
Select cities: 1) Top 5  2) Top 10  3) Top 20
Select priority: 1) All  2) High  3) Medium
Run Phase 2 Maps supplement? (Y/n): Y
```

**Output:**
- `results/phase1_search_YYYYMMDD_HHMMSS.csv`
- `results/phase2_maps_YYYYMMDD_HHMMSS.csv`
- `results/final_merged_YYYYMMDD_HHMMSS.csv`

### Standalone Components

**Search API only:**
```bash
python serper_search_v2.py
```

**Maps API only:**
```bash
python serper_maps.py
```

**AI query generator testing:**
```bash
python ai_query_generator_v2.py
```

## Performance & Costs

### Speed
- AI query generation: 10-30 seconds
- 100 queries: 2-3 minutes
- 1,000 queries: 15-20 minutes
- 5,000 queries: 60-90 minutes

### Results Volume (1 keyword, 20 cities)
- Phase 1: ~12,000 web results
- Phase 2: ~2,500 Maps businesses
- Final deduplicated: ~14,000 unique domains

### API Costs
- **OpenAI**: ~$0.05 per campaign (gpt-4o-mini)
- **Serper**: ~$10 per 1,000 queries
- **Example**: 5,000 query campaign ≈ $50 total

### Budget Configurations

**Small Test:**
```
Countries: 1
Cities: 3
Max Queries: 500
Duration: 5-8 minutes
Cost: ~$5
Results: ~1,500
```

**Medium Campaign:**
```
Countries: 2-3
Cities: 10
Max Queries: 2,000
Duration: 20-30 minutes
Cost: ~$20
Results: ~8,000
```

**Large Campaign:**
```
Countries: 5+
Cities: 20
Max Queries: 10,000
Duration: 90-120 minutes
Cost: ~$100
Results: ~40,000
```

## Installation

### Requirements

**Python 3.9+** required

### Dependencies

```bash
# For Streamlit UI (recommended)
pip install -r requirements_ui.txt

# For Flask interface
pip install -r requirements_flask.txt
```

**Installed packages:**
- `streamlit` - Interactive web UI
- `openai` - AI query generation
- `requests` - API calls
- `pandas` - Data processing
- `plotly` - Visualization
- `flask` - Web server (Flask version)

### API Keys

**Required:**
1. **OpenAI API Key** - https://platform.openai.com/api-keys
2. **Serper API Key** - https://serper.dev (included: `7d96d845cbccec41f1f2b35b0d0da05cef94c149`)

**Configuration:**
- Enter via UI sidebar, or
- Set environment variables:
  ```bash
  export OPENAI_API_KEY='your-key'
  export SERPER_API_KEY='your-key'
  ```

## Customization

### Adding Countries

Edit `config/countries.py`:
```python
COUNTRIES["BR"] = {
    "name": "Brazil",
    "code": "br",
    "language": "pt",
    "currency": "BRL",
    "top_cities": [
        {"city": "São Paulo", "state": "SP", "population": 12300000},
        # ... more cities
    ]
}
```

### Adding Query Variations

Edit `config/queries.py`:
```python
QUERY_CATEGORIES["your_category"] = [
    "{keyword} your variation",
    "another {keyword} pattern",
]
```

### Customizing AI Prompts

Edit `ai_query_generator_v2.py` - modify prompt templates around lines 48-150.

### Adjusting Site Exclusions

Edit `config/exclusions.py`:
```python
MARKETPLACES.append("newsite.com")
```

## Output Format

### CSV Columns

**Search API results:**
```csv
domain,url,title,description,source_type,query,city,position
customlanyard.net,https://...,Custom Lanyards Inc,...,organic,"lanyard supplier",New York NY,1
```

**Maps API results:**
```csv
business_name,address,phone,website,domain,rating,review_count,category,city,query,place_id,source
ABC Lanyard Co,123 Main St...,555-1234,https://...,abclanyard.com,4.5,42,Printing service,New York NY,...,...,maps
```

## Troubleshooting

### Streamlit Won't Start
```bash
# Try with python -m
python -m streamlit run app.py

# Or reinstall
pip install --upgrade streamlit
```

### OpenAI API Errors
- Verify API key at https://platform.openai.com/api-keys
- Check billing is enabled
- Remove extra spaces from key

### No Results
- Verify Serper API key is valid
- Check internet connection
- Try reducing `results_per_query`
- Test with different keywords

### High Duplicate Count
- Deduplication uses domain-level matching
- Subdomains treated separately (shop.example.com vs example.com)
- Modify `utils/deduplicator.py` for stricter matching

## File Structure

```
SerperDev/
├── app.py                      # Streamlit UI (primary)
├── app_flask_v2.py             # Flask web interface
├── orchestrator.py             # CLI pipeline
├── serper_search_v2.py         # Search API
├── serper_maps.py              # Maps API
├── ai_query_generator_v2.py    # AI query optimizer
├── config/
│   ├── countries.py            # 9 countries, 200+ cities
│   ├── queries.py              # 35 search + 10 maps queries
│   ├── locations.py            # 50 US cities, 4 tiers
│   └── exclusions.py           # Marketplace filtering
├── utils/
│   └── deduplicator.py         # Domain deduplication
├── templates/                  # Flask HTML templates
├── static/                     # Flask static assets
├── results/                    # CSV outputs (auto-created)
├── requirements_ui.txt         # Streamlit dependencies
├── requirements_flask.txt      # Flask dependencies
├── README.md                   # This file
├── QUICKSTART.md               # 5-minute setup guide
└── CLAUDE.md                   # AI assistant context
```

## Notes

- All results auto-save to `results/` with timestamps (YYYYMMDD_HHMMSS format)
- CSV encoding: UTF-8
- Rate limiting: Sequential processing (consider adding delays for very large campaigns)
- System optimized for B2B discovery, not consumer retail
- Domain extraction uses basic URL parsing

## Documentation

- **Quick Start**: [QUICKSTART.md](QUICKSTART.md) - Get running in 5 minutes
- **AI Assistant Context**: [CLAUDE.md](CLAUDE.md) - For Claude Code integration

## License

Proprietary - For internal use

## API Documentation

- **Serper API**: https://serper.dev/docs
- **OpenAI API**: https://platform.openai.com/docs
