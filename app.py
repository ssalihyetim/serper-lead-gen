#!/usr/bin/env python3
"""
AI-Powered Lead Generation UI
Interactive interface for multi-country business discovery
"""

import streamlit as st
import sys
import os
import json
import pandas as pd
from datetime import datetime

# Add modules to path
sys.path.insert(0, os.path.dirname(__file__))

from config.countries import get_all_country_names, get_language_for_country
from ai_query_generator_v2 import AIQueryGeneratorV2 as AIQueryGenerator
from serper_search_v2 import EnhancedSerperSearcher
from serper_maps import SerperMapsSearcher
from cloud_storage import CloudStorage

# Page configuration
st.set_page_config(
    page_title="AI Lead Generation System",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .step-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2ca02c;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff7f0e;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2ca02c;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'ai_plan' not in st.session_state:
    st.session_state.ai_plan = None
if 'search_results' not in st.session_state:
    st.session_state.search_results = None

# Initialize cloud storage (shared across all steps)
@st.cache_resource
def get_cloud_storage():
    return CloudStorage()


def main():
    """Main application"""

    # Header
    st.markdown('<div class="main-header">🎯 AI-Powered Lead Generation System</div>', unsafe_allow_html=True)

    # Sidebar - API Keys
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Load defaults from Streamlit Secrets if available
        default_openai_key = st.secrets.get("OPENAI_API_KEY", "") if hasattr(st, "secrets") else ""
        default_serper_key = st.secrets.get("SERPER_API_KEY", "") if hasattr(st, "secrets") else ""

        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=default_openai_key,
            help="Required for AI query generation"
        )

        serper_key = st.text_input(
            "Serper API Key",
            type="password",
            value=default_serper_key,
            help="Required for search execution"
        )

        st.divider()

        # Saved Plans section
        st.header("💾 Saved Plans")

        saved_plans_dir = "saved_plans"
        if os.path.exists(saved_plans_dir):
            saved_files = [f for f in os.listdir(saved_plans_dir) if f.endswith('.json')]

            if saved_files:
                selected_plan = st.selectbox(
                    "Load Previous Plan",
                    options=[""] + sorted(saved_files, reverse=True),
                    format_func=lambda x: "Select a plan..." if x == "" else x.replace('.json', '').replace('_', ' ')
                )

                if selected_plan and st.button("📂 Load Plan"):
                    with open(os.path.join(saved_plans_dir, selected_plan), 'r') as f:
                        loaded_data = json.load(f)
                        st.session_state.config = loaded_data['config']
                        st.session_state.ai_plan = loaded_data['ai_plan']
                        st.session_state.step = 3  # Go to review step
                        st.success(f"✅ Loaded: {selected_plan}")
                        st.rerun()
            else:
                st.caption("No saved plans yet")

        st.divider()

        # Cloud Past Searches
        st.header("☁️ Past Searches")
        cs = get_cloud_storage()
        if cs.available:
            past_searches = cs.get_past_searches(limit=10)
            if past_searches:
                for s in past_searches:
                    started = s.get('started_at', '')[:10] if s.get('started_at') else ''
                    label = f"{started} | {s.get('sector','?')} | {s.get('total_results',0):,} results"
                    with st.expander(label):
                        st.caption(f"Status: {s.get('status','?')} | Search type: {s.get('search_type','?')}")
                        countries_list = s.get('countries', [])
                        if countries_list:
                            st.caption(f"Countries: {', '.join(countries_list)}")
                        if st.button(f"⬇️ Download CSV", key=f"dl_{s['id']}"):
                            csv_data = cs.get_results_as_csv(s['id'])
                            if csv_data:
                                st.download_button(
                                    label="📥 Save CSV",
                                    data=csv_data,
                                    file_name=f"results_{s['id'][:8]}.csv",
                                    mime="text/csv",
                                    key=f"save_{s['id']}"
                                )
                            else:
                                st.warning("No results in cloud for this search.")
            else:
                st.caption("No cloud searches yet")

            stats = cs.get_search_stats()
            if stats:
                st.caption(f"Total: {stats.get('total_searches',0)} searches, {stats.get('total_results',0):,} results")
        else:
            st.caption("Cloud storage offline")

        st.divider()

        st.header("📊 Progress")
        progress_map = {
            1: "Configuration",
            2: "AI Generation",
            3: "Review & Approval",
            4: "Execution",
            5: "Results"
        }

        for step_num, step_name in progress_map.items():
            if st.session_state.step == step_num:
                st.markdown(f"**→ Step {step_num}: {step_name}**")
            elif st.session_state.step > step_num:
                st.markdown(f"✅ Step {step_num}: {step_name}")
            else:
                st.markdown(f"⚪ Step {step_num}: {step_name}")

        st.divider()

        if st.button("🔄 Reset Application"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # Main content
    if st.session_state.step == 1:
        show_configuration_step(openai_key, serper_key)
    elif st.session_state.step == 2:
        show_ai_generation_step(openai_key)
    elif st.session_state.step == 3:
        show_review_step()
    elif st.session_state.step == 4:
        show_execution_step(serper_key)
    elif st.session_state.step == 5:
        show_results_step()


def show_configuration_step(openai_key, serper_key):
    """Step 1: User configuration"""

    st.markdown('<div class="step-header">Step 1: Configuration</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎯 Target Market")

        # Sector
        sector = st.text_input(
            "Sector / Industry",
            placeholder="e.g., lanyard, promotional products, custom printing",
            help="What industry/product are you targeting?"
        )

        # Customer profile
        customer_profile = st.text_area(
            "Ideal Customer Profile",
            placeholder="e.g., B2B suppliers who sell custom lanyards in bulk to conferences and events",
            help="Describe your ideal customer in detail",
            height=100
        )

        # Max queries
        max_queries = st.number_input(
            "Maximum Total Queries",
            min_value=100,
            max_value=50000,
            value=5000,
            step=500,
            help="Budget for total API calls"
        )

    with col2:
        st.subheader("🌍 Geographic Targeting")

        # Countries
        all_countries = get_all_country_names()
        selected_countries = st.multiselect(
            "Target Countries",
            options=[code for code, name in all_countries],
            format_func=lambda code: f"{code} - {dict(all_countries)[code]}",
            default=["US"],
            help="Select countries to search in"
        )

        # Cities per country
        cities_per_country = st.slider(
            "Cities per Country",
            min_value=3,
            max_value=30,
            value=10,
            help="AI will select this many cities per country based on business context"
        )

        # Search type
        search_type = st.selectbox(
            "Search Type",
            options=["Both (Recommended)", "Search API Only", "Maps API Only"],
            help="Search API: Web results | Maps API: Local businesses | Both: Combined results"
        )

        # Pages per query
        pages_per_query = st.slider(
            "Pages per Query (Serper API)",
            min_value=1,
            max_value=10,
            value=1,
            help="Number of result pages to fetch per query. Each page = ~10 results. Cost: 1 page = 1 API call."
        )

        # Native language
        use_native_language = st.checkbox(
            "Use Native Language for Each Country",
            value=True,
            help="Generate queries in the native language of each country"
        )

        st.subheader("🤖 AI Model")

        ai_model = st.selectbox(
            "Model for Query Generation",
            options=[
                # GPT-5 family (latest)
                "gpt-5",
                "gpt-5-mini",
                # GPT-4.1 family (April 2025)
                "gpt-4.1",
                "gpt-4.1-mini",
                "gpt-4.1-nano",
                # GPT-4o family
                "gpt-4o",
                "gpt-4o-mini",
                # o-series reasoning models
                "o4-mini",
                "o3",
                "o3-mini",
            ],
            index=0,
            help=(
                "GPT-5: Most capable model | "
                "GPT-5 mini: Fast & capable | "
                "GPT-4.1: Best instruction-following, 1M context (~$0.08/1K) | "
                "GPT-4.1 mini: Fast & balanced (~$0.02/1K) | "
                "GPT-4.1 nano: Fastest & cheapest (~$0.005/1K) | "
                "GPT-4o: Strong all-rounder (~$0.05/1K) | "
                "GPT-4o-mini: Budget option (~$0.003/1K) | "
                "o4-mini: Fast reasoning (~$0.04/1K) | "
                "o3: Deep reasoning, best for complex queries (~$0.30/1K)"
            )
        )

        # Show selected cities preview
        if selected_countries:
            st.info(f"**Preview:** You'll search in {len(selected_countries)} countries × {cities_per_country} cities = {len(selected_countries) * cities_per_country} total cities")

    # Validation and proceed
    st.divider()

    if not openai_key:
        st.warning("⚠️ Please enter your OpenAI API key in the sidebar to continue")
        return

    if not serper_key:
        st.warning("⚠️ Please enter your Serper API key in the sidebar to continue")
        return

    if not sector or not customer_profile:
        st.warning("⚠️ Please fill in Sector and Customer Profile to continue")
        return

    if not selected_countries:
        st.warning("⚠️ Please select at least one country")
        return

    # Save configuration
    if st.button("➡️ Generate AI Query Plan", type="primary"):
        st.session_state.config = {
            'sector': sector,
            'customer_profile': customer_profile,
            'max_queries': max_queries,
            'countries': selected_countries,
            'cities_per_country': cities_per_country,
            'search_type': search_type,
            'pages_per_query': pages_per_query,
            'use_native_language': use_native_language,
            'ai_model': ai_model,
            'openai_key': openai_key,
            'serper_key': serper_key
        }
        st.session_state.step = 2
        st.rerun()


def build_prompt_preview(config: dict) -> str:
    """Build the exact prompt that will be sent to the AI, for user preview."""
    business_context = f"""Sector/Industry: {config['sector']}

Target Customer Profile:
{config['customer_profile']}"""

    countries = config['countries']
    cities_per_country = config['cities_per_country']
    max_total_queries = config['max_queries']
    use_native_language = config['use_native_language']

    return f"""You are an expert B2B lead generation strategist specializing in search query optimization.

**BUSINESS CONTEXT PROVIDED BY USER:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{business_context}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**SEARCH PARAMETERS:**
- Target Countries: {', '.join(countries)}
- Cities per country: {cities_per_country}
- Max total API queries: {max_total_queries}
- Use native language per country: {use_native_language}

**YOUR TASK:**

**STEP 1: ANALYZE THE CONTEXT**
Carefully read the business context above. Identify:
- What sector/industry is the USER in? (what they sell)
- Who is the TARGET CUSTOMER? (who they want to find)
- What are the key characteristics, signals, and terminology of TARGET CUSTOMERS?
- What should be prioritized? What should be avoided?

**STEP 2: GENERATE SEARCH QUERIES**
Create 15-25 highly targeted search query variations that will FIND the TARGET CUSTOMER.

CRITICAL RULES:
- Queries should find the TARGET CUSTOMER, NOT the user's sector
- Use terminology and language patterns that TARGET CUSTOMERS use in their business
- Include industry-specific terms, business types, and buying signals
- Think: "How can I identify businesses matching this target customer profile?"

**STEP 3: PRIORITIZE & EXPLAIN**
For each query:
- Assign priority: HIGH (strongest buyer signals), MEDIUM (relevant), LOW (exploratory)
- Provide clear reasoning: WHY this query identifies the target customer
- If native language enabled, provide accurate translations

**STEP 4: SELECT CITIES**
Recommend cities based on:
- Target customer industry concentration (not just population)
- Business hubs and clusters for this industry
- Budget optimization within max_total_queries

**STEP 5: EXPLAIN YOUR STRATEGY**
Provide a detailed explanation covering: context interpretation, query choices, city selection, budget allocation."""


def show_ai_generation_step(openai_key):
    """Step 2: AI generates query plan"""

    st.markdown('<div class="step-header">Step 2: AI Query Generation</div>', unsafe_allow_html=True)

    config = st.session_state.config
    ai_model = config.get('ai_model', 'gpt-4o-mini')

    st.info(f"🤖 Model: **{ai_model}** · Sector: **{config['sector']}** · {len(config['countries'])} countries")

    # Show the exact prompt that will be sent
    with st.expander("📄 View prompt being sent to AI", expanded=False):
        st.caption("This is the exact prompt the AI will receive. You can go back to Step 1 to adjust your inputs before generating.")
        st.code(build_prompt_preview(config), language="markdown")

    # Show configuration summary
    with st.expander("📋 Configuration Summary", expanded=False):
        st.json({k: v for k, v in config.items() if k not in ('openai_key', 'serper_key')})

    # Generate queries
    try:
        with st.spinner(f"Generating AI query plan with {ai_model}... This may take 10-30 seconds"):
            generator = AIQueryGenerator(api_key=openai_key, model=ai_model)

            # Combine sector and customer_profile into business_context
            business_context = f"""Sector/Industry: {config['sector']}

Target Customer Profile:
{config['customer_profile']}"""

            ai_plan = generator.generate_queries(
                business_context=business_context,
                countries=config['countries'],
                cities_per_country=config['cities_per_country'],
                max_total_queries=config['max_queries'],
                use_native_language=config['use_native_language']
            )

            st.session_state.ai_plan = ai_plan

            # Save plan to file
            saved_plans_dir = "saved_plans"
            os.makedirs(saved_plans_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            sector_slug = config['sector'].replace(' ', '_')[:20]  # First 20 chars
            filename = f"{timestamp}_{sector_slug}.json"
            filepath = os.path.join(saved_plans_dir, filename)

            plan_data = {
                'config': config,
                'ai_plan': ai_plan,
                'created_at': timestamp
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(plan_data, f, indent=2, ensure_ascii=False)

            st.success(f"✅ AI query plan generated and saved as: {filename}")
            st.session_state.step = 3
            st.rerun()

    except Exception as e:
        st.error(f"❌ Error generating AI plan: {e}")
        st.warning("Please check your OpenAI API key and try again")

        if st.button("← Back to Configuration"):
            st.session_state.step = 1
            st.rerun()


def show_review_step():
    """Step 3: Review and approve AI plan"""

    st.markdown('<div class="step-header">Step 3: Review & Approve AI Plan</div>', unsafe_allow_html=True)

    ai_plan = st.session_state.ai_plan
    config = st.session_state.config

    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Query Variations",
            len(ai_plan.get('query_variations', []))
        )

    with col2:
        opt = ai_plan.get('optimization_plan', {})
        st.metric(
            "Estimated API Calls",
            f"{opt.get('estimated_api_calls', 0):,}"
        )

    with col3:
        st.metric(
            "Total Cities",
            sum(len(cities) for cities in ai_plan.get('city_recommendations', {}).values())
        )

    with col4:
        high_pri = len([q for q in ai_plan.get('query_variations', []) if q.get('priority') == 'HIGH'])
        st.metric(
            "High Priority Queries",
            high_pri
        )

    st.divider()

    # Query variations
    st.subheader("🔍 Generated Query Variations")

    # Group by priority
    queries_by_priority = {
        'HIGH': [],
        'MEDIUM': [],
        'LOW': []
    }

    for query in ai_plan.get('query_variations', []):
        priority = query.get('priority', 'MEDIUM')
        queries_by_priority[priority].append(query)

    # Display in tabs
    tab_high, tab_medium, tab_low = st.tabs([
        f"🔴 HIGH Priority ({len(queries_by_priority['HIGH'])})",
        f"🟡 MEDIUM Priority ({len(queries_by_priority['MEDIUM'])})",
        f"⚪ LOW Priority ({len(queries_by_priority['LOW'])})"
    ])

    with tab_high:
        display_query_list(queries_by_priority['HIGH'], config['countries'], 'HIGH')

    with tab_medium:
        display_query_list(queries_by_priority['MEDIUM'], config['countries'], 'MEDIUM')

    with tab_low:
        display_query_list(queries_by_priority['LOW'], config['countries'], 'LOW')

    st.divider()

    # City recommendations with selection
    st.subheader("🏙️ Select Cities to Search")
    st.caption("AI recommended cities based on your business context. Select which ones to include:")

    city_recommendations = ai_plan.get('city_recommendations', {})

    # Initialize session state for selected cities
    if 'selected_cities' not in st.session_state:
        st.session_state.selected_cities = {}

    if city_recommendations:
        for country in config['countries']:
            st.write(f"**{country}:**")
            country_data = city_recommendations.get(country, {})

            # Handle both formats
            if isinstance(country_data, dict):
                cities = country_data.get('cities', [])
                reasoning = country_data.get('reasoning', '')
            else:
                cities = country_data if isinstance(country_data, list) else []
                reasoning = ''

            if reasoning:
                st.caption(f"💡 {reasoning}")

            # Initialize or validate country selection
            if country not in st.session_state.selected_cities:
                # First time: select up to cities_per_country
                st.session_state.selected_cities[country] = cities[:config['cities_per_country']]
            else:
                # Validate existing selection (remove cities that are no longer in options)
                existing_selection = st.session_state.selected_cities[country]
                valid_selection = [city for city in existing_selection if city in cities]
                st.session_state.selected_cities[country] = valid_selection

            # Multiselect for cities
            selected = st.multiselect(
                f"Cities for {country}",
                options=cities,
                default=st.session_state.selected_cities[country],
                key=f"cities_{country}",
                help=f"Select up to {config['cities_per_country']} cities"
            )
            st.session_state.selected_cities[country] = selected

            st.write("")  # Spacing
    else:
        st.warning("No city recommendations available in AI plan")

    st.divider()

    # AI reasoning
    st.subheader("🤖 AI Optimization Strategy")
    st.info(ai_plan.get('reasoning', 'No reasoning provided'))

    opt = ai_plan.get('optimization_plan', {})
    st.write(f"**Recommendation:** {opt.get('recommended_action', 'N/A')}")

    st.divider()

    # Approval or feedback
    st.subheader("✅ Approval")

    col1, col2 = st.columns([2, 1])

    with col1:
        approval = st.radio(
            "Is this query plan acceptable?",
            options=["✅ Yes, proceed with this plan", "❌ No, I want to modify it"],
            index=0
        )

    with col2:
        pass

    if approval == "❌ No, I want to modify it":
        st.divider()
        st.subheader("📝 Provide Feedback")

        feedback = st.text_area(
            "What would you like to change?",
            placeholder="e.g., Focus more on manufacturing queries, add more cities in Germany, prioritize custom printing...",
            height=100
        )

        if st.button("🔄 Regenerate with Feedback", type="primary"):
            if feedback:
                with st.spinner("Re-generating plan based on your feedback..."):
                    try:
                        # Get openai_key from config (now saved there)
                        openai_key = config.get('openai_key')
                        if not openai_key:
                            st.error("OpenAI API key not found. Please go back to configuration.")
                            st.stop()

                        generator = AIQueryGenerator(api_key=openai_key)
                        revised_plan = generator.optimize_queries(
                            initial_plan=ai_plan,
                            user_feedback=feedback,
                            business_context=f"{config['sector']}\n\n{config['customer_profile']}",
                            max_total_queries=config['max_queries']
                        )
                        st.session_state.ai_plan = revised_plan

                        # Save revised plan
                        saved_plans_dir = "saved_plans"
                        os.makedirs(saved_plans_dir, exist_ok=True)

                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        sector_slug = config['sector'].replace(' ', '_')[:20]
                        filename = f"{timestamp}_{sector_slug}_revised.json"
                        filepath = os.path.join(saved_plans_dir, filename)

                        plan_data = {
                            'config': config,
                            'ai_plan': revised_plan,
                            'feedback': feedback,
                            'created_at': timestamp
                        }

                        with open(filepath, 'w', encoding='utf-8') as f:
                            json.dump(plan_data, f, indent=2, ensure_ascii=False)

                        st.success(f"✅ Plan revised and saved as: {filename}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Please provide feedback first")
    else:
        if st.button("➡️ Start Search Execution", type="primary"):
            st.session_state.step = 4
            st.rerun()

    # Back button
    if st.button("← Back to Configuration"):
        st.session_state.step = 1
        st.rerun()


def display_query_list(queries, countries, priority_level):
    """Display list of queries with translations and selection checkboxes"""
    if not queries:
        st.write("No queries in this priority level")
        return

    # Initialize selected queries in session state
    if 'selected_queries' not in st.session_state:
        st.session_state.selected_queries = {}

    for idx, query in enumerate(queries, 1):
        query_template = query.get('query_template', 'N/A')
        query_key = f"{priority_level}_{idx}_{query_template}"

        # Default: all queries selected
        if query_key not in st.session_state.selected_queries:
            st.session_state.selected_queries[query_key] = True

        col1, col2 = st.columns([0.1, 0.9])

        with col1:
            selected = st.checkbox(
                "✓",
                value=st.session_state.selected_queries[query_key],
                key=f"checkbox_{query_key}",
                label_visibility="collapsed"
            )
            st.session_state.selected_queries[query_key] = selected
            query['selected'] = selected  # Store selection in query object

        with col2:
            with st.expander(f"{idx}. {query_template}", expanded=False):
                st.write(f"**Reasoning:** {query.get('reasoning', 'N/A')}")

                if query.get('translations'):
                    st.write("**Translations:**")
                    for country in countries:
                        translation = query.get('translations', {}).get(country, 'N/A')
                        st.write(f"  • {country}: `{translation}`")


def show_execution_step(serper_key):
    """Step 4: Execute searches"""

    st.markdown('<div class="step-header">Step 4: Search Execution</div>', unsafe_allow_html=True)

    config = st.session_state.config
    ai_plan = st.session_state.ai_plan

    # Get SELECTED queries (not just HIGH priority)
    all_queries = ai_plan.get('query_variations', [])
    selected_queries = [q for q in all_queries if q.get('selected', True)]  # Default True if not set

    # Get SELECTED cities from session state
    selected_cities_dict = st.session_state.get('selected_cities', {})
    total_selected_cities = sum(len(cities) for cities in selected_cities_dict.values())

    # If no cities selected, fallback to AI recommendations
    if total_selected_cities == 0:
        selected_cities_dict = {}
        city_recommendations = ai_plan.get('city_recommendations', {})
        for country in config['countries']:
            country_data = city_recommendations.get(country, {})
            if isinstance(country_data, dict):
                cities = country_data.get('cities', [])
            else:
                cities = country_data if isinstance(country_data, list) else []
            selected_cities_dict[country] = cities[:config['cities_per_country']]
        total_selected_cities = sum(len(cities) for cities in selected_cities_dict.values())

    # Calculate with pages_per_query
    pages_per_query = config.get('pages_per_query', 1)
    search_type = config.get('search_type', 'Both (Recommended)')

    # Calculate API calls based on search type
    search_api_calls = 0
    maps_api_calls = 0

    if search_type in ["Both (Recommended)", "Search API Only"]:
        search_api_calls = len(selected_queries) * total_selected_cities * pages_per_query

    if search_type in ["Both (Recommended)", "Maps API Only"]:
        maps_api_calls = len(selected_queries) * total_selected_cities * pages_per_query

    total_estimated_calls = search_api_calls + maps_api_calls

    # Build execution plan message
    plan_message = f"""**Execution Plan:**
- {len(selected_queries)} selected queries
- {total_selected_cities} selected cities across {len(config['countries'])} countries
- {pages_per_query} pages per query
- Search type: {search_type}
"""

    if search_api_calls > 0 and maps_api_calls > 0:
        plan_message += f"""- Search API calls: ~{search_api_calls}
- Maps API calls: ~{maps_api_calls}
- **Total API calls: ~{total_estimated_calls}**
"""
    elif search_api_calls > 0:
        plan_message += f"- Estimated API calls: ~{search_api_calls}\n"
    elif maps_api_calls > 0:
        plan_message += f"- Estimated API calls: ~{maps_api_calls}\n"

    plan_message += f"- Estimated time: {total_estimated_calls // 60 + 1}-{total_estimated_calls // 30 + 1} minutes"

    st.info(plan_message)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🚀 Start Real Search", type="primary"):
            # Initialize progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Get serper key from config
            serper_key = config.get('serper_key')

            try:
                # Track start time
                import time
                start_time = time.time()

                # Get search type
                search_type = config.get('search_type', 'Both (Recommended)')

                # Create cloud search session
                cs = get_cloud_storage()
                cloud_search_id = cs.create_search(
                    sector=config.get('sector', ''),
                    countries=config.get('countries', []),
                    queries=[q.get('query_template') for q in selected_queries],
                    search_type=search_type,
                )

                # Initialize searchers
                searcher = None
                maps_searcher = None

                if search_type in ["Both (Recommended)", "Search API Only"]:
                    searcher = EnhancedSerperSearcher(serper_key)

                if search_type in ["Both (Recommended)", "Maps API Only"]:
                    maps_searcher = SerperMapsSearcher(serper_key)

                # Collect SELECTED cities
                all_cities = []
                for country_code in config['countries']:
                    city_list = selected_cities_dict.get(country_code, [])
                    all_cities.extend([
                        {'city': city_name, 'country': country_code}
                        for city_name in city_list
                    ])

                # Calculate total tasks
                search_tasks = 0
                maps_tasks = 0

                if searcher:
                    search_tasks = len(all_cities) * len(selected_queries) * pages_per_query
                if maps_searcher:
                    maps_tasks = len(all_cities) * len(selected_queries) * pages_per_query

                total_tasks = search_tasks + maps_tasks
                completed = 0

                # Flush city results to Supabase then CLEAR from RAM
                total_saved_count = 0

                def flush_and_clear(results_list):
                    """Save batch to Supabase and clear from RAM to prevent memory buildup."""
                    nonlocal total_saved_count
                    if not results_list:
                        return
                    if cloud_search_id and cs.available:
                        cs.save_results(cloud_search_id, results_list)
                        total_saved_count += len(results_list)
                        cs.update_search_count(cloud_search_id, total_saved_count)
                    # Always clear from RAM regardless of cloud availability
                    del results_list[:]

                # Phase 1: Execute Search API (if enabled)
                if searcher:
                    status_text.text("Phase 1: Search API...")

                    for city_info in all_cities:
                        city_name = city_info['city']
                        country = city_info['country']

                        status_text.text(f"Search API: {city_name}, {country}...")

                        for query in selected_queries:
                            query_template = query.get('query_template', '')
                            translations = query.get('translations', {})
                            query_text = translations.get(country, query_template)
                            # Append city name so Google returns city-specific results
                            query_with_city = f"{query_text} {city_name}"

                            for page_num in range(1, pages_per_query + 1):
                                searcher.search_single_query(
                                    query=query_with_city,
                                    gl=country.lower(),
                                    hl='en',
                                    total_results=10,
                                    city=f"{city_name}, {country}",
                                    silent=True
                                )
                                completed += 1
                                progress_bar.progress(completed / total_tasks)
                                status_text.text(f"Search API: {city_name}, {country}... ({completed}/{total_tasks})")

                        # Flush city results to cloud + clear from RAM
                        flush_and_clear(searcher.all_results)

                # Phase 2: Execute Maps API (if enabled)
                if maps_searcher:
                    status_text.text("Phase 2: Maps API...")

                    for city_info in all_cities:
                        city_name = city_info['city']
                        country = city_info['country']

                        status_text.text(f"Maps API: {city_name}, {country}...")

                        for query in selected_queries:
                            query_template = query.get('query_template', '')
                            translations = query.get('translations', {})
                            query_text = translations.get(country, query_template)
                            # Append city name so Maps returns city-specific results
                            query_with_city = f"{query_text} {city_name}"

                            for page_num in range(1, pages_per_query + 1):
                                response = maps_searcher.search_maps(
                                    query=query_with_city,
                                    location=f"{city_name}, {country}",
                                    gl=country.lower(),
                                    hl='en',
                                    page=page_num
                                )
                                if response:
                                    places = response.get('places', [])
                                    if places:
                                        batch = maps_searcher.extract_maps_results(
                                            places, query_text, f"{city_name}, {country}"
                                        )
                                        maps_searcher.all_results.extend(batch)

                                completed += 1
                                progress_bar.progress(completed / total_tasks)
                                status_text.text(f"Maps API: {city_name}, {country}... ({completed}/{total_tasks})")

                        # Flush city results to cloud + clear from RAM
                        flush_and_clear(maps_searcher.all_results)

                # All results were flushed to Supabase per city and cleared from RAM.
                # Use total_saved_count for stats; download comes from cloud.
                total_api_calls = 0
                if searcher:
                    total_api_calls += searcher.api_call_count
                if maps_searcher:
                    total_api_calls += maps_searcher.api_call_count

                # Also export related searches if any (Search API only)
                if searcher and searcher.related_searches:
                    searcher.export_related_searches()

                # Mark search as complete in Supabase
                if cloud_search_id:
                    cs.complete_search(
                        cloud_search_id,
                        total_results=total_saved_count,
                        api_calls_used=total_api_calls,
                    )

                # Calculate duration
                duration_seconds = time.time() - start_time
                duration_minutes = duration_seconds / 60

                # results_by_country: approximate from cloud (avoid re-fetching all rows)
                results_by_country = {c: len(cities) for c, cities in
                                      {ci['country']: [ci for ci in all_cities
                                                        if ci['country'] == c]
                                       for c in set(ci['country'] for ci in all_cities)}.items()}

                output_file = None  # Results are in cloud, not local file

                # Store only lightweight summary in session state (no bulk result data)
                st.session_state.search_results = {
                    'total_results': total_saved_count,
                    'api_calls_used': total_api_calls,
                    'duration_minutes': duration_minutes,
                    'search_type': search_type,
                    'results_by_country': results_by_country,
                    'cloud_search_id': cloud_search_id,
                }

                st.success(f"✅ Search completed in {duration_minutes:.1f} minutes! Found {total_saved_count:,} results")
                st.session_state.step = 5
                st.rerun()

            except Exception as e:
                # Mark search as interrupted; results flushed per-city are already in Supabase
                if 'cloud_search_id' in locals() and cloud_search_id:
                    try:
                        saved_so_far = locals().get('total_saved_count', 0)
                        api_so_far = getattr(locals().get('searcher'), 'api_call_count', 0) + \
                                     getattr(locals().get('maps_searcher'), 'api_call_count', 0)
                        cs.complete_search(
                            cloud_search_id,
                            total_results=saved_so_far,
                            api_calls_used=api_so_far,
                            status='interrupted',
                        )
                    except Exception:
                        pass
                st.error(f"❌ Search interrupted: {e}")
                st.warning("⚠️ Results saved up to the last completed city are in cloud. Check Past Searches in the sidebar.")
                import traceback
                st.code(traceback.format_exc())

    with col2:
        if st.button("← Back to Review"):
            st.session_state.step = 3
            st.rerun()


def show_results_step():
    """Step 5: Show results"""

    st.markdown('<div class="step-header">Step 5: Results</div>', unsafe_allow_html=True)

    results = st.session_state.search_results

    st.success("✅ Search completed successfully!")

    # Show search type
    search_type = results.get('search_type', 'Both (Recommended)')
    st.info(f"🔍 Search Type: **{search_type}**")

    # Metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Results Saved", f"{results['total_results']:,}")

    with col2:
        st.metric("API Calls Used", f"{results['api_calls_used']:,}")

    with col3:
        st.metric("Duration", f"{results['duration_minutes']:.1f} min")

    st.divider()

    # Results by country (city count approximation)
    st.subheader("📊 Cities Searched by Country")
    results_by_country = results.get('results_by_country', {})
    if results_by_country:
        results_df = pd.DataFrame([
            {'Country': country, 'Cities': count}
            for country, count in results_by_country.items()
        ])
        st.bar_chart(results_df.set_index('Country'))

    st.divider()

    # Download from cloud
    st.subheader("📥 Download Results")
    cloud_search_id = results.get('cloud_search_id')

    if cloud_search_id:
        st.info(f"☁️ All results saved to cloud (ID: `{cloud_search_id[:8]}...`)")
        cs = get_cloud_storage()
        if cs.available:
            with st.spinner("Fetching results from cloud..."):
                csv_data = cs.get_results_as_csv(cloud_search_id)
            if csv_data:
                st.download_button(
                    label="📥 Download Full Results CSV",
                    data=csv_data,
                    file_name=f"leads_{config.get('sector','results')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No results found in cloud for this search.")
        else:
            st.warning("Cloud storage offline - results may not be available.")
    else:
        st.warning("No cloud search ID found. Results may not have been saved.")

    if st.button("🔄 Start New Search"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


if __name__ == "__main__":
    main()
