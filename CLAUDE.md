# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

B2B lead generation system using Serper API (Google Search + Maps) with AI-powered query optimization. Targets multi-country business discovery with location-based search and deduplication.

**Core Use Case**: Finding targetable e-commerce sites, suppliers, and custom print shops for cold email outreach campaigns.

## Development Commands

### Running the Applications

**Interactive UI (Streamlit - Primary)**
```bash
streamlit run app.py
# Opens browser at http://localhost:8501
```

**Flask Web Interface (Alternative)**
```bash
python app_flask_v2.py
# Opens at http://localhost:3000 (changed from 8080 to avoid conflicts)
```

**CLI Orchestrator (Full Pipeline)**
```bash
python orchestrator.py
# Interactive prompts guide through Phase 1 (Search) + Phase 2 (Maps)
```

**Standalone Components**
```bash
# Multi-location search (Phase 1 only)
python serper_search_v2.py

# Maps API local business search (Phase 2 only)
python serper_maps.py

# AI query generator (standalone testing)
python ai_query_generator_v2.py
```

### Dependencies

```bash
# For CLI tools (original)
pip install -r requirements.txt

# For Streamlit UI
pip install -r requirements_ui.txt

# For Flask web interface
pip install -r requirements_flask.txt
```

## Architecture

### Two-Phase Search Strategy

**Phase 1: Search API** (`serper_search_v2.py`)
- Web search across multiple cities
- 35 query variations organized by intent (supplier signals, custom/print, industry verticals)
- Excludes major marketplaces (Amazon, eBay, Etsy, etc.)
- Returns: domain, URL, title, description, source_type, query, city, position

**Phase 2: Maps API** (`serper_maps.py`)
- Supplements Phase 1 with local business data
- Targets cities with low Phase 1 coverage
- 10 Maps-optimized queries per city
- Returns: business_name, address, phone, website, rating, review_count, category

**Orchestrator** (`orchestrator.py`)
- Coordinates both phases
- Analyzes Phase 1 coverage to determine Phase 2 targets
- Merges and deduplicates results by domain
- Saves to `results/` directory with timestamps

### AI Query Generation

**Module**: `ai_query_generator.py` and `ai_query_generator_v2.py`

Uses OpenAI (gpt-4o-mini) to:
1. Generate 15-25 targeted search queries based on sector and customer profile
2. Prioritize queries by conversion potential (HIGH/MEDIUM/LOW)
3. Translate queries to native languages for each country
4. Calculate optimal city selection per country
5. Balance query coverage vs. API budget constraints
6. Provide reasoning and optimization recommendations

**Interactive Workflow** (in Streamlit UI):
1. User provides sector, customer profile, countries, budget
2. AI generates query plan
3. User reviews and can provide feedback for regeneration
4. Approved plan executes searches
5. Results downloaded as CSV

### Configuration System

**`config/queries.py`**
- 35 search query variations in 3 categories:
  - `supplier_signals` (12 queries): HIGH intent B2B signals
  - `custom_print` (13 queries): MEDIUM intent custom/print services
  - `industry_verticals` (10 queries): Vertical targeting
- 10 Maps-specific queries
- Functions: `get_queries_by_priority()`, `get_maps_queries()`

**`config/locations.py`**
- 50 US cities in 4 tiers (major hubs to manufacturing centers)
- Functions: `get_cities(count)` returns top N cities
- Used for geographic targeting in Phase 1

**`config/countries.py`**
- 9 pre-configured countries (US, UK, DE, FR, CA, AU, ES, IT, NL)
- 200+ cities database
- Country metadata: name, code, language, currency, top_cities
- Functions: `get_all_country_names()`, `get_cities_for_country()`, `get_language_for_country()`

**`config/exclusions.py`**
- Site exclusion lists for marketplace filtering
- Categories: marketplaces, social media, information sites, review sites, search engines
- Auto-appended to all queries to focus on targetable small businesses

**`utils/deduplicator.py`**
- Domain-based deduplication across Phase 1 and Phase 2
- URL-level deduplication within phases
- Function: `merge_csv_files()` for cross-phase merging

## Data Flow

```
User Input → AI Query Generator → Query Plan
                                        ↓
                     Phase 1: Search API (web results)
                                        ↓
                     Coverage Analysis → Identify low-coverage cities
                                        ↓
                     Phase 2: Maps API (local businesses)
                                        ↓
                     Domain Deduplication → Final CSV
```

**Output Files** (in `results/` directory):
- `phase1_search_YYYYMMDD_HHMMSS.csv`
- `phase2_maps_YYYYMMDD_HHMMSS.csv`
- `final_merged_YYYYMMDD_HHMMSS.csv`
- `serper_results_YYYYMMDD_HHMMSS.csv` (from original `serper_search.py`)

## API Keys

**Hardcoded in scripts** (consider moving to environment variables):
- Serper API key: `7d96d845cbccec41f1f2b35b0d0da05cef94c149`
- OpenAI API key: Present in `app.py:90` (should be redacted in production)

**Best Practice**: Use environment variables for production:
```python
import os
serper_key = os.getenv('SERPER_API_KEY')
openai_key = os.getenv('OPENAI_API_KEY')
```

## Key Optimization Patterns

### Query Variations
Each base keyword (e.g., "lanyard") generates multiple variations:
- Direct B2B: "lanyard supplier", "wholesale lanyard", "lanyard manufacturer"
- Custom/Print: "custom lanyard", "lanyard printing", "personalized lanyard"
- Industry: "conference lanyard", "corporate lanyard", "event lanyard"

All queries auto-append site exclusions to filter out major marketplaces.

### Location Targeting
- **Top 5 cities**: Quick test (~175 API calls)
- **Top 10 cities**: Pilot run (~350 API calls)
- **Top 20 cities**: Conservative production (~700 API calls)
- Cities selected by business density and tier priority

### Budget Management
The orchestrator calculates:
```
estimated_calls = keywords × cities × query_variations × (results_per_query / 10)
```

AI generator optimizes to stay within `max_total_queries` budget by:
- Selecting optimal cities_per_country
- Prioritizing HIGH intent queries
- Balancing coverage vs. cost

### Deduplication Strategy
1. **Within Phase 1**: URL-level (same URL appears only once)
2. **Within Phase 2**: Business name + address
3. **Cross-Phase**: Domain-level (keeps first occurrence with most detail)

## Multi-Country Support

**Streamlit UI supports**:
- Country selection from 9 pre-configured options
- Native language toggle (queries translated per country)
- Per-country city selection
- Language-aware query generation

**Workflow**:
1. User selects countries (e.g., US, UK, DE)
2. AI generates queries in English
3. If native language enabled, AI translates queries (e.g., "supplier" → "lieferant" for DE)
4. Searches executed with appropriate `gl` (country) and `hl` (language) parameters

## Common Patterns

### Adding New Query Variations
Edit `config/queries.py`:
```python
QUERY_CATEGORIES["your_category"] = [
    "{keyword} your variation",
    "another {keyword} variation",
]
```

### Adding New Countries
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

### Customizing AI Prompts
Edit `ai_query_generator.py` - modify the prompt template in `generate_queries()` method around lines 48-120.

### Adjusting Search Parameters
In any searcher class:
- `results_per_query`: Total results to fetch (paginated in groups of 10)
- `gl`: Country code (e.g., "us", "uk", "de")
- `hl`: Language code (e.g., "en", "de", "fr")
- `query_priority`: "all", "high", "medium", "industry"

## Performance Expectations

**Search API (Phase 1)**:
- 100 queries: ~2-3 minutes
- 1000 queries: ~15-20 minutes
- 5000 queries: ~60-90 minutes

**AI Generation**:
- gpt-4o-mini: 5-10 seconds
- gpt-4: 20-40 seconds

**Results Volume** (1 keyword, 20 cities):
- Phase 1: ~12,000 web results
- Phase 2: ~2,500 Maps businesses
- Final deduplicated: ~14,000 unique domains

**Cost Estimates**:
- AI query generation: ~$0.05 per campaign
- Serper API: ~$10 per 1000 queries
- Example: 5000 query campaign ≈ $50

## File Organization

```
SerperDev/
├── config/                  # Configuration modules
│   ├── countries.py         # Multi-country setup (9 countries, 200+ cities)
│   ├── queries.py           # Query variations library (35 search + 10 maps)
│   ├── locations.py         # US cities database (50 cities, 4 tiers)
│   └── exclusions.py        # Marketplace filtering
├── utils/                   # Utilities
│   └── deduplicator.py      # Domain-based deduplication
├── templates/               # Flask HTML templates
├── static/                  # Flask static assets
├── results/                 # Output CSVs (auto-created)
├── app.py                   # Streamlit UI (primary interface)
├── app_flask_v2.py          # Flask web interface (alternative)
├── orchestrator.py          # Two-phase pipeline CLI
├── serper_search_v2.py      # Multi-location search (Phase 1)
├── serper_maps.py           # Maps API integration (Phase 2)
├── ai_query_generator_v2.py # AI query optimizer
├── requirements_ui.txt      # Streamlit dependencies
├── requirements_flask.txt   # Flask dependencies
├── README.md                # Main documentation
├── QUICKSTART.md            # 5-minute setup guide
└── CLAUDE.md                # This file
```

## Recent Updates (January 2026)

### New Features Added

**1. Related Searches Capture** (`serper_search_v2.py`)
- Automatically captures Google's "Related Searches" from each query
- Stored in `self.related_searches` dictionary
- Exported to separate CSV: `results/related_searches_TIMESTAMP.csv`
- Available in both Streamlit and Flask interfaces
- Zero additional API cost (included in search response)

**2. Autocomplete API** (`serper_search_v2.py`)
- New `get_autocomplete_suggestions()` method
- Fetches Google autocomplete suggestions for partial queries
- Useful for query expansion and keyword research
- Endpoint: `https://google.serper.dev/autocomplete`
- Cost: ~1 API call per suggestion request

**3. Streamlit Interface Enhancements** (`app.py`)
- **Fixed**: Feedback loop session key error (line 409)
- **Added**: Real search execution (replaced demo mode)
- **Added**: Real-time progress bar during search
- **Added**: Actual CSV file download
- **Fixed**: API keys now stored in `session_state.config`
- **Integrated**: Related searches and autocomplete features
- Search execution now fully functional with background processing

**4. Flask Port Change** (`app_flask_v2.py`)
- **Changed**: Port 8080 → 3000 (to avoid FEMA website conflict)
- **Fixed**: Import bug for `AIQueryGeneratorV2`
- **Fixed**: Business context parameter mismatch

### API Enhancement Details

**Related Searches Usage:**
```python
searcher = EnhancedSerperSearcher(API_KEY)
searcher.search_single_query("custom lanyard manufacturer")

# Access related searches
related = searcher.related_searches["custom lanyard manufacturer"]
# ['Custom lanyard manufacturer usa', 'Custom lanyard manufacturer wholesale', ...]

# Export to CSV
searcher.export_related_searches()
```

**Autocomplete Usage:**
```python
searcher = EnhancedSerperSearcher(API_KEY)
suggestions = searcher.get_autocomplete_suggestions("lanyard sup")
# ['lanyard supplier', 'lanyard supplier wholesale', ...]
```

### File Updates

**Modified Files:**
- `serper_search_v2.py` - Added related searches + autocomplete
- `app.py` - Fixed feedback loop, enabled search execution
- `app_flask_v2.py` - Port change, import fixes
- `ai_query_generator_v2.py` - Parameter fixes for both UIs

**New Output Files:**
- `results/related_searches_TIMESTAMP.csv` - Related search suggestions
- `results/streamlit_results_TIMESTAMP.csv` - Streamlit search results

## Important Notes

- Flask runs on port 3000 (changed from 8080)
- Streamlit runs on port 8501
- All scripts use the same Serper API key (consider per-environment configuration)
- Results automatically save to `results/` with timestamps
- CSV encoding is UTF-8
- Domain extraction uses basic parsing (may need enhancement for edge cases)
- Rate limiting handled via sequential processing (consider adding explicit delays for large campaigns)
- The system is optimized for B2B outreach, not consumer retail discovery
- Related searches are captured automatically at zero additional cost
- Autocomplete API costs ~$0.01 per request

---

## Recent Updates (February 2026)

### Major Feature: Maps API Integration in Streamlit

**Status:** ✅ COMPLETED

#### What Was Added:

**1. Full Maps API Support in app.py (lines 660-820)**
- Integrated `SerperMapsSearcher` alongside `EnhancedSerperSearcher`
- Three search modes:
  - **"Both (Recommended)"** - Search API + Maps API combined
  - **"Search API Only"** - Web results only
  - **"Maps API Only"** - Local businesses only
- Two-phase execution:
  - Phase 1: Search API with exclusions
  - Phase 2: Maps API for local businesses
- Combined CSV export with all fields from both APIs

**2. Enhanced Site Exclusions (config/exclusions.py)**
- Expanded from 46 to **87 excluded sites**
- Added categories:
  - Turkish B2B platforms (turkishexporters.com, turkeysuppliers.com, etc.)
  - Indian B2B platforms (indiamart.com, exportersindia.com, etc.)
  - International directories (tradekey.com, ec21.com, etc.)
  - **Chambers of Commerce & Trade Associations**:
    - TOBB (tobb.org.tr) - Turkish Chambers Union
    - TİM (tim.org.tr) - Turkish Exporters Assembly
    - ISO, İTO, Ankara TSO, İzmir TO
    - US Chamber, British Chambers
    - export.gov, trade.gov, fita.org
- All exclusions now apply by default (`include_b2b_directories=True` in serper_search_v2.py:248)

**3. Country Support Expansion**
- Expanded from 9 to **174 countries**
- Organized by geographic regions (North America, Europe, Asia, etc.)
- Removed hardcoded city lists (now AI-selected per search)

**4. Maps API Data Fields**
When Maps API is used, results include:
- `business_name` - Company name
- `address` - Physical address
- `phone` - Phone number
- `website` - Website URL
- `domain` - Extracted domain
- `rating` - Google rating (e.g., 4.5)
- `review_count` - Number of reviews
- `category` - Business category
- `place_id` - Google Maps place ID
- `source: 'maps'` - Source identifier

**5. Search Execution Flow (app.py lines 660-820)**
```python
# Step 1: Initialize searchers based on search_type
if search_type in ["Both", "Search API Only"]:
    searcher = EnhancedSerperSearcher(serper_key)

if search_type in ["Both", "Maps API Only"]:
    maps_searcher = SerperMapsSearcher(serper_key)

# Step 2: Phase 1 - Search API (if enabled)
# - Applies 87 site exclusions
# - Pagination support (pages_per_query)
# - Progress tracking

# Step 3: Phase 2 - Maps API (if enabled)
# - Local business search
# - 10 Maps queries per city
# - No pagination (direct results)

# Step 4: Merge results
all_results = searcher.all_results + maps_searcher.all_results

# Step 5: Export combined CSV with all fields
```

**6. Results Page Updates (app.py lines 831-860)**
- Shows search type used
- Combined metrics (Search + Maps)
- Unique domain count across both sources
- Country breakdown

#### Cost Implications:

**"Both (Recommended)" Mode:**
```
Total API Calls = (Search API calls) + (Maps API calls)
                = (cities × queries × pages) + (cities × queries)

Example: 10 cities, 13 queries, 1 page
- Search: 10 × 13 × 1 = 130 calls
- Maps: 10 × 13 = 130 calls
- Total: 260 calls (~$2.60)
```

#### Files Modified:
- `app.py` - Added Maps integration (lines 19, 660-820, 831-860)
- `serper_search_v2.py` - Enabled B2B directory exclusions (line 248)
- `config/exclusions.py` - Expanded to 87 sites with chambers/associations
- `config/countries.py` - Expanded to 174 countries, removed city arrays

#### Testing Status:
- ✅ Import successful
- ✅ Search type dropdown functional
- ✅ Phase 1 (Search API) execution
- ✅ Phase 2 (Maps API) execution
- ✅ Result merging and CSV export
- ✅ Results page display
- ⚠️ Needs user testing with real API calls

---

## Next Steps (Short-term)

### Priority 1: User Testing & Validation
- [ ] Test "Both (Recommended)" mode with small query count (3 cities, 5 queries)
- [ ] Validate Maps API results quality (phone numbers, addresses, ratings)
- [ ] Check CSV export has all fields from both APIs
- [ ] Verify exclusions working (no TOBB, alibaba, turkishexporters in results)

### Priority 2: Performance Optimization
- [ ] Add rate limiting for large Maps API campaigns (currently sequential)
- [ ] Implement retry logic for failed Maps API calls
- [ ] Add timeout handling for slow responses

### Priority 3: UX Improvements
- [ ] Show separate progress for Search vs Maps phases
- [ ] Add "Preview Results" before download
- [ ] Display Maps-specific fields in results table (phone, rating, address)
- [ ] Add filtering by source type (Search vs Maps)

### Priority 4: Data Quality
- [ ] Implement smarter domain deduplication (currently basic)
- [ ] Add phone number validation/formatting
- [ ] Filter out PO boxes and virtual addresses
- [ ] Score results by data completeness (has phone + website + rating = higher score)

### Known Issues:
1. **Session State Conflicts** - Old saved plans may have missing fields (search_type, results_by_country)
   - Solution: Add migration logic or clear old plans
2. **Maps API No Exclusions** - Maps returns direct businesses, can't filter by domain
   - Mitigation: Post-process to remove known marketplace addresses
3. **Cost Visibility** - Users may not realize "Both" mode doubles API costs
   - Solution: Show estimated cost breakdown before execution

---

## Current System State (February 4, 2026)

**Working Features:**
- ✅ 174-country support with AI city selection
- ✅ AI query generation with OpenAI GPT-4o-mini
- ✅ 87-site exclusion list (marketplaces, B2B directories, chambers)
- ✅ Search API with pagination (1-10 pages per query)
- ✅ Maps API integration with business details
- ✅ Three search modes (Both/Search Only/Maps Only)
- ✅ Combined CSV export with all fields
- ✅ Query/city selection UI with checkboxes
- ✅ Saved plans feature (JSON persistence)

**Active Components:**
- `app.py` - Streamlit UI (primary interface) - Port 8501
- `serper_search_v2.py` - Search API with exclusions
- `serper_maps.py` - Maps API for local businesses
- `ai_query_generator_v2.py` - OpenAI query generation
- `config/exclusions.py` - 87-site filter list
- `config/countries.py` - 174-country database

**Deprecated/Removed:**
- Flask interface (`app_flask_v2.py`) - kept but not maintained
- Hardcoded city lists in countries.py (now AI-selected)

**Next Chat Context:**
If starting a fresh chat, focus areas should be:
1. User testing results and feedback
2. Performance optimization for large-scale searches
3. Data quality improvements (deduplication, validation)
4. Cost optimization strategies
