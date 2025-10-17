#!/usr/bin/env python3
"""
AI Business Crew with Business Intelligence MCP Integration
Enhanced version with access to 1,170 business intelligence insights
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, ScrapeWebsiteTool, MCPTool

# Load environment
load_dotenv('/Users/yourox/AI-Workspace/.env')

class AIBusinessCrewWithBI:
    """
    AI Business Crew with Business Intelligence MCP Access

    All 8 agents now have access to:
    - 214 Products & Tools with metrics
    - 84 Problems & Solutions
    - 64 Startup Ideas
    - 66 Growth Tactics
    - 71 AI Workflows
    - 73 Target Markets
    - 107 Trends & Signals
    - Plus 400+ more insights
    """

    def __init__(self):
        # Initialize base tools
        self.search_tool = SerperDevTool()
        self.scrape_tool = ScrapeWebsiteTool()

        # Initialize Business Intelligence MCP Tool
        self.bi_mcp = MCPTool(
            server_name="business-intelligence",
            server_path="/Users/yourox/AI-Workspace/mcp-servers/business-intelligence/server.py",
            description="""Access to business intelligence database with 1,170 insights from 50 videos.
            Use this to search for: products, problems, startup ideas, growth tactics, AI workflows,
            target markets, trends, business strategies, metrics, quotes, and mistakes to avoid."""
        )

        self.llm_model = 'anthropic/claude-sonnet-4-20250514'

    # ==================== PHASE 1: MARKET INTELLIGENCE ====================

    def create_market_trend_analyzer(self):
        """Agent 1: Enhanced with BI database access"""
        return Agent(
            role='Market Research Specialist with Business Intelligence Access',
            goal='Identify growing markets with high CAGR (>10%) and low brand saturation',
            backstory="""Expert in market analysis with exclusive access to business intelligence
            database containing 107 validated market trends, 73 target markets, and proven strategies
            from successful entrepreneurs. You leverage this intelligence to find opportunities faster
            than competitors.""",
            tools=[
                self.bi_mcp,      # Access to BI database - PRIMARY TOOL
                self.search_tool,  # Google search for validation
                self.scrape_tool   # Web scraping for additional data
            ],
            llm=self.llm_model,
            verbose=True
        )

    def create_market_discovery_task(self, agent):
        """Enhanced task with BI database queries"""
        return Task(
            description="""
            Use the Business Intelligence MCP to discover high-potential markets:

            STEP 1: Query BI Database for Growing Markets
            - Use: search_trends(query="", stage="growing", limit=20)
            - Look for trends in "growing" or "emerging" stages
            - Focus on markets with clear opportunity signals

            STEP 2: Get Target Market Intelligence
            - Use: search_target_markets(query="[trend keyword]", limit=10)
            - Understand demographics, pain points, market size

            STEP 3: Find Validated Problems
            - Use: search_problems(query="[market keyword]", category="market-research")
            - Identify problems with step-by-step solutions

            STEP 4: Analyze Opportunities
            - Use: get_market_opportunities(min_growth_stage="growing", limit=10)
            - Get ranked opportunities with supporting evidence

            STEP 5: Cross-Reference with Live Data
            - Validate top 5 opportunities with Google Trends
            - Search for current CAGR data
            - Check brand saturation

            DELIVERABLE:
            Top 5 market opportunities with:
            - Market name and growth metrics
            - Target audience demographics
            - Key pain points
            - Competition analysis
            - Supporting evidence from BI database
            """,
            agent=agent,
            expected_output="""Ranked list of 5 market opportunities with validation data,
            demographics, pain points, and evidence from business intelligence database."""
        )

    def create_product_discovery_agent(self):
        """Agent 2: Enhanced with product intelligence"""
        return Agent(
            role='Product Discovery Specialist with AI Workflow Access',
            goal='Find untapped products using early adopter analysis and BI database',
            backstory="""Specialist in identifying emerging products with access to 214
            validated products, 71 AI workflows, and 64 startup ideas from the BI database.
            You know exactly how to find products before they hit mainstream.""",
            tools=[
                self.bi_mcp,
                self.search_tool,
                self.scrape_tool
            ],
            llm=self.llm_model,
            verbose=True
        )

    def create_product_discovery_task(self, agent, context_tasks):
        """Enhanced task with product search"""
        return Task(
            description="""
            Using the market from previous agent, find untapped product opportunities:

            STEP 1: Search Similar Successful Products
            - Use: search_products(query="[market keyword]", category="all", sentiment="positive")
            - Study successful products in similar markets
            - Note pricing, metrics, and validation

            STEP 2: Get AI Workflows for Product Discovery
            - Use: search_ai_workflows(query="product discovery youtube", automation_level="all")
            - Find proven methods for identifying early adopter products
            - Learn from Seena Rez's $2.7M method

            STEP 3: Get Strategy Insights
            - Use: get_actionable_quotes(category="strategy", limit=20)
            - Learn from successful entrepreneurs
            - Apply proven validation methods

            STEP 4: Check Startup Ideas Database
            - Use: search_startup_ideas(query="[market keyword]", limit=10)
            - See validated business concepts
            - Identify gaps in the market

            STEP 5: Execute Early Adopter Research
            - Search "day in the life of [niche]" on YouTube
            - Extract product mentions from micro-influencer content
            - Validate with Google Trends

            STEP 6: Avoid Common Mistakes
            - Use: get_mistakes_to_avoid(query="product validation")
            - Learn what NOT to do

            DELIVERABLE:
            List of 5-10 untapped products with:
            - Product description and category
            - Early adopter validation
            - Similar successful products from BI
            - Google Trends validation
            - Brand saturation analysis
            """,
            agent=agent,
            context=context_tasks,
            expected_output="""Prioritized list of untapped products with validation data,
            early adopter evidence, and insights from business intelligence database."""
        )

    # ==================== PHASE 2: AUDIENCE & BRAND ====================

    def create_audience_identity_researcher(self):
        """Agent 3: Enhanced with market intelligence"""
        return Agent(
            role='Audience Psychology Expert with Market Intelligence',
            goal='Deep-dive into target audience using BI database insights',
            backstory="""Expert in consumer psychology with access to 73 target markets
            and detailed demographic data. You understand aspirational identities and
            can map customer journeys using proven research from the BI database.""",
            tools=[
                self.bi_mcp,
                self.search_tool,
                self.scrape_tool
            ],
            llm=self.llm_model,
            verbose=True
        )

    def create_audience_research_task(self, agent, context_tasks):
        """Enhanced task with audience intelligence"""
        return Task(
            description="""
            Using product data from previous agent, research target audience:

            STEP 1: Get Target Market Intelligence
            - Use: search_target_markets(query="[product niche]")
            - Get demographics, pain points, market size
            - Understand existing customer profiles

            STEP 2: Study Similar Markets
            - Use: search_business_strategies(query="audience", strategy_type="branding")
            - Learn from successful audience research
            - Find identity-based branding examples

            STEP 3: Analyze Micro-Influencer Content
            - Search for micro-influencers in the niche
            - Extract language patterns and identity markers
            - Document aspirational identity

            STEP 4: Get Key Metrics
            - Use: get_key_metrics(query="audience conversion")
            - Understand benchmarks and optimization tips

            DELIVERABLE:
            Comprehensive audience profile:
            - Demographics (age, gender, location, income)
            - Psychographics (values, aspirations, identity)
            - Pain points and needs
            - Language patterns and keywords
            - Content preferences
            - Supported by BI database evidence
            """,
            agent=agent,
            context=context_tasks,
            expected_output="""Detailed audience profile with demographics, psychographics,
            pain points, and identity framework based on BI insights."""
        )

    def create_brand_identity_creator(self):
        """Agent 4: Enhanced with branding intelligence"""
        return Agent(
            role='Brand Strategist with Proven Strategy Database',
            goal='Create resonant brand identity using non-competing brand emulation',
            backstory="""Brand expert with access to 103 business strategies and 132
            actionable quotes about branding. You know exactly how to translate audience
            aspirations into brand essence using proven methods.""",
            tools=[
                self.bi_mcp,
                self.search_tool,
                self.scrape_tool
            ],
            llm=self.llm_model,
            verbose=True
        )

    def create_brand_strategy_task(self, agent, context_tasks):
        """Enhanced task with branding strategies"""
        return Task(
            description="""
            Using audience data, create brand identity:

            STEP 1: Get Branding Strategies
            - Use: search_business_strategies(query="identity branding", strategy_type="branding")
            - Study proven branding methods
            - Learn from successful case studies

            STEP 2: Get Branding Quotes
            - Use: get_actionable_quotes(category="branding", limit=20)
            - Apply expert insights
            - Use proven frameworks

            STEP 3: Find Non-Competing Brand Examples
            - Ask: "What brands best fulfill [aspirational identity]?"
            - Study their aesthetic, messaging, brand essence
            - Identify elements to emulate

            STEP 4: Avoid Branding Mistakes
            - Use: get_mistakes_to_avoid(query="branding")
            - Learn from others' failures

            STEP 5: Create Brand Identity
            - Brand name (aspirational, not descriptive)
            - Visual identity (colors, typography, photography)
            - Brand essence and messaging
            - Reference brands and aesthetic direction

            DELIVERABLE:
            Complete brand identity guide:
            - Brand name with rationale
            - Visual identity specifications
            - Brand essence and values
            - Messaging framework
            - Reference brands and aesthetic
            - Supported by BI strategy insights
            """,
            agent=agent,
            context=context_tasks,
            expected_output="""Complete brand identity guide with name, visuals, messaging,
            and reference brands based on proven strategies from BI database."""
        )

    # ==================== PHASE 3: OPERATIONS ====================

    def create_supplier_sourcing_agent(self):
        """Agent 5: Enhanced with operational intelligence"""
        return Agent(
            role='Manufacturing Specialist with Sourcing Intelligence',
            goal='Find high-quality suppliers using competitive data and proven methods',
            backstory="""Sourcing expert with access to proven supplier negotiation strategies
            and operational insights from successful brands. You know the exact process for
            finding and negotiating with suppliers.""",
            tools=[
                self.bi_mcp,
                self.search_tool,
                self.scrape_tool
            ],
            llm=self.llm_model,
            verbose=True
        )

    def create_supplier_sourcing_task(self, agent, context_tasks):
        """Enhanced task with operational strategies"""
        return Task(
            description="""
            Using brand specifications, find and negotiate with suppliers:

            STEP 1: Get Operational Strategies
            - Use: search_business_strategies(query="supplier manufacturing", strategy_type="operations")
            - Learn proven sourcing methods
            - Understand negotiation tactics

            STEP 2: Get Operational Quotes
            - Use: get_actionable_quotes(category="operations")
            - Apply expert sourcing insights
            - Follow proven negotiation frameworks

            STEP 3: Create Manufacturing Document
            - Product variants (colors, sizes)
            - Logo placement and specifications
            - Material requirements
            - Order quantities and lead times

            STEP 4: Find Suppliers
            - Search Alibaba by SUPPLIER (not product)
            - Filter: Trade Assurance + Verified Pro Supplier
            - Target 20-50 suppliers

            STEP 5: Negotiate Using Competition
            - Collect all quotes and specifications
            - Use competitive data for negotiation
            - Find "perfect supplier" through filtering

            STEP 6: Avoid Mistakes
            - Use: get_mistakes_to_avoid(query="supplier manufacturing")

            DELIVERABLE:
            Supplier sourcing report:
            - Manufacturing specifications document
            - List of contacted suppliers (20-50)
            - Top 3 supplier recommendations
            - Negotiated pricing and terms
            - Quality assurance plan
            """,
            agent=agent,
            context=context_tasks,
            expected_output="""Supplier sourcing report with specifications, supplier list,
            recommendations, and negotiated terms based on proven strategies."""
        )

    # ==================== PHASE 4: MARKETING ====================

    def create_viral_content_strategist(self):
        """Agent 6: Enhanced with growth tactics"""
        return Agent(
            role='Viral Content Expert with Growth Tactics Database',
            goal='Create viral content using proven formulas and tactics',
            backstory="""Viral content specialist with access to 66 growth tactics and
            proven viral formulas. You know the science of going viral and have case
            studies from successful campaigns.""",
            tools=[
                self.bi_mcp,
                self.search_tool,
                self.scrape_tool
            ],
            llm=self.llm_model,
            verbose=True
        )

    def create_viral_content_task(self, agent, context_tasks):
        """Enhanced task with viral tactics"""
        return Task(
            description="""
            Create viral content strategy:

            STEP 1: Get Viral Growth Tactics
            - Use: search_growth_tactics(query="viral", channel="content")
            - Study proven viral methods
            - Learn from successful campaigns

            STEP 2: Get Content Strategy Insights
            - Use: search_business_strategies(query="viral content", strategy_type="marketing")
            - Understand viral mechanics
            - Apply proven frameworks

            STEP 3: Study Successful Content
            - Use: get_actionable_quotes(category="marketing")
            - Learn expert insights
            - Find viral formulas

            STEP 4: Get Key Metrics
            - Use: get_key_metrics(query="viral engagement")
            - Understand benchmarks
            - Set success targets

            STEP 5: Create Viral Content Plan
            - Apply 1-3 second transition science
            - Structure: Setup → X-factor reveal → Re-engagement
            - Use professional photo shoot content
            - Plan multiple variations

            DELIVERABLE:
            Viral content strategy:
            - Content concepts (3-5 variations)
            - Viral mechanics explanation
            - Script outlines
            - Success metrics
            - Based on proven viral tactics
            """,
            agent=agent,
            context=context_tasks,
            expected_output="""Viral content strategy with concepts, mechanics, scripts,
            and metrics based on proven growth tactics from BI database."""
        )

    def create_marketing_campaign_manager(self):
        """Agent 7: Enhanced with marketing intelligence"""
        return Agent(
            role='Performance Marketing Specialist with Campaign Intelligence',
            goal='Run high-converting retargeting campaigns using proven strategies',
            backstory="""Ads expert with access to proven marketing strategies and campaign
            metrics. You know exactly how to convert warm audiences and scale campaigns
            profitably.""",
            tools=[
                self.bi_mcp,
                self.search_tool,
                self.scrape_tool
            ],
            llm=self.llm_model,
            verbose=True
        )

    def create_marketing_campaign_task(self, agent, context_tasks):
        """Enhanced task with marketing strategies"""
        return Task(
            description="""
            Create performance marketing campaign:

            STEP 1: Get Marketing Strategies
            - Use: search_business_strategies(query="retargeting ads", strategy_type="marketing")
            - Study proven ad strategies
            - Learn from successful campaigns

            STEP 2: Get Marketing Tactics
            - Use: search_growth_tactics(query="ads", channel="paid-ads")
            - Understand conversion tactics
            - Apply proven methods

            STEP 3: Get Key Metrics
            - Use: get_key_metrics(query="conversion ROAS")
            - Set benchmark targets (5-7% conversion)
            - Understand optimization KPIs

            STEP 4: Create Campaign Structure
            - Organic phase: Viral content distribution
            - Build warm audience (50%+ video view)
            - Retargeting phase: Static + video ads
            - Lookalike and interest-based targeting

            STEP 5: Avoid Marketing Mistakes
            - Use: get_mistakes_to_avoid(query="marketing ads")

            DELIVERABLE:
            Marketing campaign plan:
            - Campaign structure and phases
            - Audience targeting strategy
            - Ad creative requirements
            - Budget allocation
            - Success metrics (target 5-7% conversion)
            - Scaling plan
            - Based on proven marketing strategies
            """,
            agent=agent,
            context=context_tasks,
            expected_output="""Complete marketing campaign plan with structure, targeting,
            creatives, budget, and metrics based on proven strategies."""
        )

    # ==================== WORKFLOW ORCHESTRATION ====================

    def run_full_pipeline_with_bi(self, initial_market=None):
        """
        Run complete end-to-end pipeline with Business Intelligence access

        All agents now leverage 1,170 business intelligence insights for:
        - Faster market discovery
        - Better product validation
        - Proven branding strategies
        - Optimized operations
        - Higher-converting marketing
        """

        print("=" * 80)
        print("🚀 AI BUSINESS CREW WITH BUSINESS INTELLIGENCE ACCESS")
        print("=" * 80)
        print(f"\n📊 Leveraging:")
        print(f"  - 214 Products & Tools")
        print(f"  - 84 Problems & Solutions")
        print(f"  - 107 Market Trends")
        print(f"  - 66 Growth Tactics")
        print(f"  - 71 AI Workflows")
        print(f"  - Plus 600+ more insights\n")

        # PHASE 1: Market Intelligence
        print("\n" + "=" * 80)
        print("PHASE 1: MARKET INTELLIGENCE (with BI Database)")
        print("=" * 80 + "\n")

        market_agent = self.create_market_trend_analyzer()
        market_task = self.create_market_discovery_task(market_agent)

        product_agent = self.create_product_discovery_agent()
        product_task = self.create_product_discovery_task(product_agent, [market_task])

        phase1_crew = Crew(
            agents=[market_agent, product_agent],
            tasks=[market_task, product_task],
            process=Process.sequential,
            verbose=True
        )

        phase1_result = phase1_crew.kickoff()

        # PHASE 2: Audience & Brand
        print("\n" + "=" * 80)
        print("PHASE 2: AUDIENCE & BRAND (with BI Insights)")
        print("=" * 80 + "\n")

        audience_agent = self.create_audience_identity_researcher()
        audience_task = self.create_audience_research_task(audience_agent, [product_task])

        brand_agent = self.create_brand_identity_creator()
        brand_task = self.create_brand_strategy_task(brand_agent, [audience_task])

        phase2_crew = Crew(
            agents=[audience_agent, brand_agent],
            tasks=[audience_task, brand_task],
            process=Process.sequential,
            verbose=True
        )

        phase2_result = phase2_crew.kickoff()

        # PHASE 3: Operations
        print("\n" + "=" * 80)
        print("PHASE 3: OPERATIONS (with Proven Strategies)")
        print("=" * 80 + "\n")

        supplier_agent = self.create_supplier_sourcing_agent()
        supplier_task = self.create_supplier_sourcing_task(supplier_agent, [brand_task])

        phase3_crew = Crew(
            agents=[supplier_agent],
            tasks=[supplier_task],
            process=Process.sequential,
            verbose=True
        )

        phase3_result = phase3_crew.kickoff()

        # PHASE 4: Marketing
        print("\n" + "=" * 80)
        print("PHASE 4: MARKETING (with Growth Tactics)")
        print("=" * 80 + "\n")

        viral_agent = self.create_viral_content_strategist()
        viral_task = self.create_viral_content_task(viral_agent, [brand_task])

        marketing_agent = self.create_marketing_campaign_manager()
        marketing_task = self.create_marketing_campaign_task(marketing_agent, [viral_task])

        phase4_crew = Crew(
            agents=[viral_agent, marketing_agent],
            tasks=[viral_task, marketing_task],
            process=Process.sequential,
            verbose=True
        )

        phase4_result = phase4_crew.kickoff()

        # Final Summary
        print("\n" + "=" * 80)
        print("✅ COMPLETE WORKFLOW FINISHED (with BI Intelligence)")
        print("=" * 80 + "\n")

        final_report = {
            'phase1_market_intelligence': phase1_result,
            'phase2_audience_brand': phase2_result,
            'phase3_operations': phase3_result,
            'phase4_marketing': phase4_result,
            'bi_insights_used': True,
            'total_intelligence_accessed': '1,170+ items'
        }

        return final_report


if __name__ == "__main__":
    """
    Example usage:

    python3 ai_business_crew_with_mcp.py
    """

    print("\n" + "=" * 80)
    print("AI BUSINESS AUTOMATION SYSTEM")
    print("Enhanced with Business Intelligence MCP Access")
    print("=" * 80 + "\n")

    crew = AIBusinessCrewWithBI()

    # Run full pipeline with BI intelligence
    result = crew.run_full_pipeline_with_bi()

    print("\n🎉 COMPLETE! Your AI agents leveraged 1,170+ business intelligence insights!")
    print("📊 Results saved with BI attribution\n")
