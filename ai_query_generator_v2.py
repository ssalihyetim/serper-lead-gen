#!/usr/bin/env python3
"""
AI-Powered Query Generator V2
Free-form business context input for better AI understanding
"""

import json
from typing import List, Dict
from openai import OpenAI


class AIQueryGeneratorV2:
    """Generate and optimize search queries using AI with free-form context"""

    def __init__(self, api_key: str, model: str = "gpt-4.1-mini"):
        """
        Initialize AI query generator

        Args:
            api_key: OpenAI API key
            model: Model to use
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate_queries(self,
                        business_context: str,
                        countries: List[str],
                        cities_per_country: int,
                        max_total_queries: int,
                        use_native_language: bool = True) -> Dict:
        """
        Generate search queries based on free-form business context

        Args:
            business_context: Free-form text describing business, target customers, goals
            countries: List of country codes
            cities_per_country: Number of cities per country
            max_total_queries: Maximum total API calls allowed
            use_native_language: Use native language for each country

        Returns:
            Dict with queries, cities, strategy, and detailed explanations
        """

        prompt = f"""You are an expert B2B lead generation strategist specializing in search query optimization.

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

Example:
If context says: "We sell SaaS to custom lanyard manufacturers"
- GOOD queries: "custom lanyard manufacturer", "lanyard printing company", "bulk lanyard supplier"
- BAD queries: "SaaS for manufacturers", "business software"

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
Provide a detailed, human-readable explanation of:
- How you interpreted the business context
- Why you chose these specific queries
- How queries map to target customer characteristics
- Budget allocation and prioritization logic
- Suggested execution approach

**OUTPUT FORMAT (JSON):**
{{
    "context_analysis": {{
        "user_business": "Brief description of what the user sells/does",
        "target_customer_profile": "Detailed profile of who we're trying to find",
        "key_customer_signals": [
            "Characteristic/signal 1",
            "Characteristic/signal 2",
            "Characteristic/signal 3"
        ],
        "search_strategy_summary": "1-2 sentence summary of overall approach"
    }},

    "query_variations": [
        {{
            "query_template": "custom lanyard manufacturer",
            "priority": "HIGH",
            "reasoning": "Direct match for businesses that manufacture custom lanyards - core target profile",
            "customer_signal": "Indicates bulk manufacturing capability and B2B focus",
            "translations": {{
                "US": "custom lanyard manufacturer",
                "DE": "individuelle schlüsselband hersteller",
                "FR": "fabricant de lanyard personnalisé",
                "ES": "fabricante de lanyard personalizado"
            }}
        }},
        {{
            "query_template": "promotional products supplier lanyard",
            "priority": "MEDIUM",
            "reasoning": "Broader category that often includes lanyard manufacturers",
            "customer_signal": "B2B supplier with likely lanyard offerings",
            "translations": {{
                "US": "promotional products supplier lanyard",
                "DE": "werbeartikel lieferant schlüsselband",
                "FR": "fournisseur articles promotionnels lanyard"
            }}
        }}
    ],

    "city_recommendations": {{
        "US": {{
            "cities": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"],
            "reasoning": "Major metro areas with high concentration of manufacturing and B2B promotional product companies"
        }},
        "DE": {{
            "cities": ["Berlin", "München", "Hamburg", "Frankfurt"],
            "reasoning": "German manufacturing and export hubs"
        }}
    }},

    "optimization_plan": {{
        "total_combinations": 450,
        "estimated_api_calls": 4200,
        "within_budget": true,
        "priority_distribution": {{
            "HIGH": 8,
            "MEDIUM": 7,
            "LOW": 3
        }},
        "recommended_execution": {{
            "phase_1": "HIGH priority queries in top 3 cities per country (600 calls, ~70% of results expected)",
            "phase_2": "MEDIUM priority queries in remaining cities (1400 calls, ~25% of results)",
            "phase_3": "LOW priority exploratory queries if budget permits (800 calls, ~5% of results)"
        }}
    }},

    "strategy_explanation": {{
        "context_interpretation": "Detailed explanation of how you understood the business context and identified target customer",
        "query_strategy": "Why these specific queries target the right customers, how they map to customer characteristics",
        "priority_logic": "How and why priorities were assigned, what makes HIGH different from MEDIUM",
        "city_selection": "Why these specific cities, what makes them ideal for this target customer",
        "budget_optimization": "How the plan maximizes results within budget constraints",
        "execution_recommendations": "Specific advice on how to run the search for best results",
        "expected_outcomes": "What types of businesses you expect to find, quality vs quantity trade-offs"
    }}
}}

**REMEMBER:**
- Your queries should FIND the target customers described in the context
- NOT queries about the user's own business
- Focus on terminology and patterns TARGET CUSTOMERS use
- Prioritize based on how well a query identifies the target profile

Generate the complete strategy now:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert B2B lead generation strategist. Analyze business context deeply and create highly targeted search strategies. Always respond with valid, complete JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            print(f"AI Generation Error: {e}")
            return self._fallback_response(business_context, countries)

    def optimize_queries(self,
                        initial_plan: Dict,
                        user_feedback: str,
                        business_context: str,
                        max_total_queries: int) -> Dict:
        """
        Re-optimize queries based on user feedback

        Args:
            initial_plan: Initial AI-generated plan
            user_feedback: User's feedback/requirements
            business_context: Original business context
            max_total_queries: Max query budget

        Returns:
            Revised optimization plan
        """

        prompt = f"""You previously generated this search query plan:

{json.dumps(initial_plan, indent=2)}

**ORIGINAL BUSINESS CONTEXT:**
{business_context}

**USER FEEDBACK ON THE PLAN:**
{user_feedback}

**MAX QUERY BUDGET:** {max_total_queries}

**YOUR TASK:**
The user has reviewed your plan and provided feedback. Revise the plan based on their feedback while:
1. Staying true to the original business context
2. Staying within the max query budget
3. Addressing all points in the user feedback
4. Maintaining the same JSON format
5. Explaining what you changed and why

Provide updated JSON in the same complete format as before, including:
- Updated context_analysis if needed
- Modified query_variations
- Adjusted priorities
- Updated city recommendations
- New optimization_plan
- Detailed strategy_explanation covering the changes

Generate the revised plan:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert B2B lead generation strategist. Incorporate user feedback while maintaining strategic coherence. Always respond with valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            print(f"AI Optimization Error: {e}")
            return initial_plan

    def select_cities(self,
                     business_context: str,
                     countries: List[str],
                     cities_per_country: int) -> Dict:
        """
        AI selects optimal cities for each country based on business context

        This is a separate AI call from query generation to allow flexibility

        Args:
            business_context: Free-form text describing business and target customers
            countries: List of country codes (e.g., ['US', 'TR', 'DE'])
            cities_per_country: Number of cities to select per country

        Returns:
            Dict with city selections and reasoning per country
            {
                "US": {
                    "cities": ["New York", "Los Angeles", "Chicago"],
                    "reasoning": "Major manufacturing and B2B hubs"
                },
                "TR": {
                    "cities": ["Istanbul", "Ankara", "Izmir"],
                    "reasoning": "Turkey's economic and industrial centers"
                }
            }
        """

        from config.countries import get_country

        # Get country details
        country_details = []
        for code in countries:
            country = get_country(code)
            if country:
                country_details.append(f"- {country['name']} ({code}): language={country['language']}, currency={country['currency']}")

        prompt = f"""You are an expert in global business geography and market intelligence.

**BUSINESS CONTEXT:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{business_context}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**TASK:**
For each country below, select the {cities_per_country} BEST cities to find businesses matching the target customer profile described above.

**COUNTRIES:**
{chr(10).join(country_details)}

**SELECTION CRITERIA:**
1. **Industry Relevance**: Cities with high concentration of the target industry/sector
2. **Business Activity**: Economic hubs, manufacturing centers, or service clusters relevant to target
3. **Market Size**: Cities with sufficient business density for meaningful results
4. **Strategic Value**: Consider ports, tech hubs, manufacturing zones based on business type

**IMPORTANT NOTES:**
- Do NOT just pick the largest cities by population
- Pick cities where the TARGET CUSTOMER type is most concentrated
- Consider industry clusters (e.g., tech in San Francisco, manufacturing in Detroit, finance in NYC)
- For each country, select cities that maximize finding the target customer
- Use real city names (proper spelling and capitalization)

**EXAMPLES OF GOOD REASONING:**
- "Selected Houston because of high concentration of industrial suppliers and manufacturing"
- "Chose Shenzhen for electronics manufacturing cluster, not just for population"
- "Istanbul chosen as Turkey's main commercial and manufacturing hub"

**OUTPUT FORMAT (JSON):**
{{
    "US": {{
        "cities": ["New York", "Los Angeles", "Chicago"],
        "reasoning": "Major commercial hubs with diverse B2B presence and high business density"
    }},
    "TR": {{
        "cities": ["Istanbul", "Ankara", "Izmir"],
        "reasoning": "Turkey's primary economic centers - Istanbul for commerce, Ankara for government/institutional, Izmir for manufacturing and exports"
    }}
}}

Generate city selections now:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in global business geography. Select cities strategically based on target customer concentration, not just population. Always respond with valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,  # Lower temperature for more consistent geographic selection
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            print(f"AI City Selection Error: {e}")
            # Fallback: return capital/major cities for each country
            fallback = {}
            for code in countries:
                country = get_country(code)
                if country:
                    # Simple fallback - would need actual city data
                    fallback[code] = {
                        "cities": [f"Capital of {country['name']}"],
                        "reasoning": "AI error - fallback to capital city"
                    }
            return fallback

    def _fallback_response(self, business_context: str, countries: List[str]) -> Dict:
        """Fallback response if AI fails"""
        return {
            "context_analysis": {
                "user_business": "Unable to analyze (AI error)",
                "target_customer_profile": "Unable to analyze (AI error)",
                "key_customer_signals": ["AI generation failed - using fallback"],
                "search_strategy_summary": "Fallback to basic queries due to AI error"
            },
            "query_variations": [
                {
                    "query_template": "supplier",
                    "priority": "HIGH",
                    "reasoning": "Fallback query - AI generation failed",
                    "customer_signal": "Basic supplier signal",
                    "translations": {c: "supplier" for c in countries}
                }
            ],
            "city_recommendations": {c: {"cities": [], "reasoning": "AI error"} for c in countries},
            "optimization_plan": {
                "total_combinations": 0,
                "estimated_api_calls": 0,
                "within_budget": True,
                "priority_distribution": {"HIGH": 1},
                "recommended_execution": {"phase_1": "Please retry - AI error occurred"}
            },
            "strategy_explanation": {
                "context_interpretation": "AI generation failed - please try again",
                "query_strategy": "Fallback response active",
                "priority_logic": "N/A",
                "city_selection": "N/A",
                "budget_optimization": "N/A",
                "execution_recommendations": "Please retry the query generation",
                "expected_outcomes": "N/A - fallback mode"
            }
        }


if __name__ == "__main__":
    print("AI Query Generator V2 - Free-form Context")
    print("=" * 60)
    print("Supports detailed business context for better targeting")
    print("=" * 60)
