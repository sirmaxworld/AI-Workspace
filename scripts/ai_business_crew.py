#!/usr/bin/env python3
"""
AI Business Automation Crew
Complete end-to-end system from market research to sales

Based on Seena Rez's $2.7M brand strategy
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai_tools import (
    SerperDevTool,
    ScrapeWebsiteTool,
    YoutubeVideoSearchTool,
    BrowserbaseLoadTool
)

load_dotenv('/Users/yourox/AI-Workspace/.env')

# Initialize tools
search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()
youtube_tool = YoutubeVideoSearchTool()
browserbase_tool = BrowserbaseLoadTool()


class AIBusinessCrew:
    """Complete AI Business Automation System"""

    def __init__(self):
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.workspace_dir = Path('/Users/yourox/AI-Workspace')

    # ========== PHASE 1: MARKET INTELLIGENCE ==========

    def create_market_trend_analyzer(self):
        """Agent 1: Market Trend Analyzer"""
        return Agent(
            role='Market Research Specialist',
            goal='Identify growing markets with high CAGR (>10%) and low brand saturation',
            backstory="""You are an expert market analyst who uses Google Trends,
            industry reports, and growth metrics to spot high-potential opportunities.
            You have a keen eye for emerging markets before they become mainstream.""",
            tools=[search_tool, scrape_tool],
            verbose=True,
            allow_delegation=False,
            llm='anthropic/claude-sonnet-4-20250514'
        )

    def create_product_discovery_agent(self):
        """Agent 2: Product Discovery Agent"""
        return Agent(
            role='Early Adopter Product Hunter',
            goal='Find untapped products mentioned by micro-influencers before mainstream adoption',
            backstory="""You are a specialist in identifying emerging products by
            analyzing micro-influencer content. You know how to spot "early adopter products"
            - products that have awareness but no strong brand saturation. You look for
            customers describing products generically ('those grippy socks') not by brand names.""",
            tools=[youtube_tool, browserbase_tool, search_tool],
            verbose=True,
            allow_delegation=False,
            llm='anthropic/claude-sonnet-4-20250514'
        )

    # ========== PHASE 2: AUDIENCE & BRAND ==========

    def create_audience_identity_researcher(self):
        """Agent 3: Audience Identity Researcher"""
        return Agent(
            role='Target Audience Psychologist',
            goal='Deep-dive into target audience to understand their aspirational identity',
            backstory="""You are an expert in consumer psychology who studies language
            patterns, identity movements, and aspirational behaviors. You can identify
            the 'tribal essence' and aspirational identity (like 'that girl' movement)
            that drives purchasing decisions.""",
            tools=[youtube_tool, scrape_tool, browserbase_tool],
            verbose=True,
            allow_delegation=False,
            llm='anthropic/claude-sonnet-4-20250514'
        )

    def create_brand_identity_creator(self):
        """Agent 4: Brand Identity Creator"""
        return Agent(
            role='Brand Strategist & Identity Designer',
            goal='Create brand that resonates with target identity using non-competing brand emulation',
            backstory="""You are a brand expert who understands how to translate
            audience aspirations into brand essence. You know how to study successful
            non-competing brands (like Glossier) and emulate their aesthetic for different
            product categories. You create aspirational brand names that reflect desired
            outcomes, not product descriptions.""",
            tools=[search_tool, scrape_tool],
            verbose=True,
            allow_delegation=False,
            llm='anthropic/claude-sonnet-4-20250514'
        )

    # ========== PHASE 3: PRODUCT SOURCING ==========

    def create_supplier_sourcing_agent(self):
        """Agent 5: Supplier Sourcing & Negotiation Agent"""
        return Agent(
            role='Manufacturing Specialist & Negotiator',
            goal='Find high-quality suppliers and negotiate best prices using competitive data',
            backstory="""You are a sourcing expert who knows how to create detailed
            manufacturing specs and leverage competition for better pricing. You contact
            20-50 suppliers to gather competitive data and negotiate the best terms.
            You focus on premium quality to match premium brand positioning.""",
            tools=[search_tool, scrape_tool],
            verbose=True,
            allow_delegation=False,
            llm='anthropic/claude-sonnet-4-20250514'
        )

    # ========== PHASE 4: CONTENT CREATION ==========

    def create_content_director_agent(self):
        """Agent 6: Photo Shoot Director & Content Creator"""
        return Agent(
            role='Creative Director & Content Strategist',
            goal='Create professional visual content that matches target identity aesthetic',
            backstory="""You are a photography expert who knows how to match visual
            content to brand identity. You source the right photographers, models,
            and props to create 4 content types: hero images, product images, ad content,
            and video clips.""",
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
            llm='anthropic/claude-sonnet-4-20250514'
        )

    # ========== PHASE 5: MARKETING ==========

    def create_viral_video_agent(self):
        """Agent 7: Viral Video Creation Agent"""
        return Agent(
            role='Viral Content Strategist',
            goal='Create viral videos using the "1-3 second transition" science',
            backstory="""You are an expert in viral mechanics who understands the
            science of going viral. You know that the 1-3 second mark is critical -
            this is where the X-factor/product function must be revealed. You structure
            videos for maximum engagement and re-watch value.""",
            tools=[youtube_tool, search_tool],
            verbose=True,
            allow_delegation=False,
            llm='anthropic/claude-sonnet-4-20250514'
        )

    def create_marketing_campaign_agent(self):
        """Agent 8: Marketing Campaign Manager"""
        return Agent(
            role='Performance Marketing Specialist',
            goal='Run retargeting campaigns to warm audiences from viral content',
            backstory="""You are an ads expert who understands the viral-to-retargeting
            funnel. You know how to build warm audiences with organic content, then
            retarget them with static and video ads for high conversion rates (5-7%+).
            You optimize for profitable ROAS and scale to 6-figure revenue.""",
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
            llm='anthropic/claude-sonnet-4-20250514'
        )

    # ========== TASKS ==========

    def create_market_research_task(self, agent):
        """Task 1: Market Research"""
        return Task(
            description="""Research and identify growing markets with the following criteria:
            1. Search for markets with positive year-over-year growth on Google Trends
            2. Validate market has CAGR > 10%
            3. Check Google Trends trajectory is growing (not declining)
            4. Look for markets with emerging product categories

            Focus on: fitness, wellness, lifestyle, beauty, fashion, productivity markets

            Output a detailed report with:
            - Top 3 growing markets
            - CAGR data for each
            - Google Trends trajectory
            - Emerging product opportunities within each market
            """,
            agent=agent,
            expected_output="Detailed market research report with 3 validated markets"
        )

    def create_product_discovery_task(self, agent, market_context):
        """Task 2: Product Discovery"""
        return Task(
            description=f"""Using the market: {market_context}

            Find untapped products using this methodology:
            1. Search YouTube for "day in the life of [niche]" videos
            2. Find 10-20 micro-influencer videos (not mainstream influencers)
            3. Analyze what products they mention in their daily routines
            4. Identify products that are:
               - Recently emerged (check Google Trends)
               - Customers describe generically (not by brand name)
               - Multiple micro-influencers mention
               - Low competition from established brands

            Look for "product awareness without brand saturation" - when customers
            say things like "those grippy socks" or "that workout band" instead of
            brand names.

            Output:
            - Top 5 untapped products
            - Google Trends validation for each
            - Customer language analysis
            - Micro-influencer mentions count
            - Competition assessment
            """,
            agent=agent,
            expected_output="Product discovery report with 5 validated untapped products",
            context=[market_context] if market_context else []
        )

    def create_audience_research_task(self, agent, product_context):
        """Task 3: Audience Identity Research"""
        return Task(
            description=f"""For the product: {product_context}

            Deep-dive into the target audience:
            1. Analyze micro-influencer profiles who mention this product
            2. Extract their language patterns and identity keywords
            3. Identify the aspirational identity/movement (like "that girl", "clean girl", etc.)
            4. Map demographics, psychographics, and pain points
            5. Document exact customer language for the product

            Look for:
            - Identity movements in their video titles
            - Aspirational lifestyle they portray
            - Language they use to describe products
            - Pain points they mention
            - Their daily routines and values

            Output:
            - Comprehensive audience profile
            - Aspirational identity framework
            - Customer language documentation
            - Pain points list
            - Demographics and psychographics
            """,
            agent=agent,
            expected_output="Detailed audience identity research report",
            context=[product_context] if product_context else []
        )

    def create_brand_identity_task(self, agent, audience_context):
        """Task 4: Brand Identity Creation"""
        return Task(
            description=f"""Using audience research: {audience_context}

            Create a complete brand identity:
            1. Research: "What brands best fulfill upon [aspirational identity]?"
            2. Study 3-5 non-competing brands serving same identity
            3. Analyze their aesthetic, messaging, and brand essence
            4. Create aspirational brand name (not product description)
               - Example: "Grounded" (outcome) not "Grip Socks" (product)
               - Example: "Glossier" (outcome) not "Face Cream" (product)
            5. Define visual identity (colors, typography, photography style)
            6. Create brand messaging framework

            Emulate the essence of successful brands but in different product category.

            Output:
            - Brand name with rationale
            - Visual identity guide (colors, fonts, style)
            - Reference brands analysis
            - Brand messaging framework
            - Photography/aesthetic direction
            """,
            agent=agent,
            expected_output="Complete brand identity guide",
            context=[audience_context] if audience_context else []
        )

    def create_supplier_sourcing_task(self, agent, brand_context):
        """Task 5: Supplier Sourcing"""
        return Task(
            description=f"""Using brand specs: {brand_context}

            Source and negotiate with suppliers:
            1. Create detailed manufacturing document with:
               - Product variants (colors, sizes)
               - Logo placement specifications
               - Material requirements
               - Pattern/grip details
               - Order quantities (start with 500-1000 units)
               - Lead times

            2. Search Alibaba by SUPPLIER (not product):
               - Filter: Trade Assurance + Verified Pro Supplier
               - Message 20-50 suppliers with manufacturing doc

            3. Collect competitive data:
               - All quotes and specifications
               - Sample quality information
               - MOQ (Minimum Order Quantity)
               - Lead times

            4. Negotiate using competitive data:
               - Use quotes to negotiate with each supplier
               - Focus on quality to match premium positioning
               - Get samples from top 3 suppliers

            Output:
            - Manufacturing specifications document
            - Supplier comparison spreadsheet (20+ suppliers)
            - Top 3 supplier recommendations with terms
            - Negotiated pricing and terms
            - Sample request plan
            """,
            agent=agent,
            expected_output="Supplier sourcing report with top 3 recommendations",
            context=[brand_context] if brand_context else []
        )

    def create_content_creation_task(self, agent, brand_visual_context):
        """Task 6: Content Creation"""
        return Task(
            description=f"""Using brand visual identity: {brand_visual_context}

            Plan professional photo shoot:
            1. Find director of photography specializing in target aesthetic
               - Search for fashion/lifestyle photographers
               - Match style to reference brands

            2. Source props and backdrop:
               - Match backdrop to reference brands (e.g., Glossier's dreamy clouds)
               - Source relevant props

            3. Model casting:
               - Select models that look like target audience
               - Match to micro-influencer appearance

            4. Plan 4 content types:
               - Full body lifestyle images (website hero)
               - Product images (featured products)
               - Ad hero images (Meta/TikTok ads)
               - Video clips (website + organic content)

            5. Shot list and timeline:
               - List all required shots
               - Plan shoot timeline (typically 4-6 hours)

            Output:
            - Photographer recommendations (3)
            - Props and backdrop sourcing plan
            - Model casting brief
            - Complete shot list by content type
            - Budget estimate
            - Timeline and logistics plan
            """,
            agent=agent,
            expected_output="Complete photo shoot plan with budget",
            context=[brand_visual_context] if brand_visual_context else []
        )

    def create_viral_video_task(self, agent, photo_content_context):
        """Task 7: Viral Video Strategy"""
        return Task(
            description=f"""Using photo shoot content: {photo_content_context}

            Create viral video strategy:
            1. Find viral video in niche to stitch/reference
               - Must have 1M+ views
               - Related to product use case

            2. Structure the video:
               - 0-1 sec: Hook/context setup
               - 1-3 sec: **CRITICAL** - Reveal X-factor/product function
               - Rest: Engagement and product demo

            3. **The 1-3 Second Transition is EVERYTHING**:
               - This is the secret of going viral
               - Beat drop / reveal moment
               - Product function clearly shown
               - X-factor of entire video

            4. Multiple video variations:
               - Create 5-10 video concepts
               - Different hooks and angles
               - All following 1-3 sec transition rule

            5. Content elements:
               - Use photo shoot images/clips
               - Product demonstration
               - Stitch setup if applicable
               - Background music/sound strategy

            Output:
            - 5 viral video concepts with scripts
            - 1-3 second transition clearly marked
            - Stitch video recommendations
            - Music and sound strategy
            - Production timeline
            """,
            agent=agent,
            expected_output="Viral video strategy with 5 concepts",
            context=[photo_content_context] if photo_content_context else []
        )

    def create_marketing_campaign_task(self, agent, viral_content_context):
        """Task 8: Marketing Campaign"""
        return Task(
            description=f"""Using viral content: {viral_content_context}

            Plan complete marketing campaign:

            **Phase 1: Organic Viral**
            1. Publish viral videos to TikTok, Instagram Reels, YouTube Shorts
            2. Track engagement metrics
            3. Build warm audience (50%+ video view)

            **Phase 2: Retargeting Campaign**
            1. Create static image ads using photo shoot content
            2. Create video ads (shorter cuts of viral videos)
            3. Set up retargeting:
               - Target: 50%+ video view audience
               - Platforms: Meta (Instagram/Facebook), TikTok
               - Budget: Start $100-500/day, scale based on ROAS

            4. Campaign structure:
               - Retargeting to warm audience (priority)
               - Lookalike audiences (1-2%)
               - Interest-based targeting (test)

            5. Optimization targets:
               - 5-7%+ conversion rate on retargeting
               - 2-3x+ ROAS minimum
               - Scale to $1000+/day profitably

            Output:
            - Organic content calendar (30 days)
            - Ad creative specifications (static + video)
            - Retargeting campaign setup guide
            - Budget allocation plan
            - Scaling strategy
            - Success metrics and KPIs
            """,
            agent=agent,
            expected_output="Complete marketing campaign plan",
            context=[viral_content_context] if viral_content_context else []
        )

    # ========== RUN CREW ==========

    def run_market_discovery(self):
        """Phase 1: Market Research & Product Discovery"""
        print("\n" + "="*70)
        print("🚀 PHASE 1: MARKET INTELLIGENCE")
        print("="*70 + "\n")

        # Create agents
        market_agent = self.create_market_trend_analyzer()
        product_agent = self.create_product_discovery_agent()

        # Create tasks
        market_task = self.create_market_research_task(market_agent)

        # Create crew for market research
        market_crew = Crew(
            agents=[market_agent],
            tasks=[market_task],
            process=Process.sequential,
            verbose=True
        )

        # Run market research
        market_result = market_crew.kickoff()

        print("\n📊 Market Research Complete!")
        print(f"Results:\n{market_result}\n")

        # Now run product discovery with market context
        product_task = self.create_product_discovery_task(product_agent, market_result)

        product_crew = Crew(
            agents=[product_agent],
            tasks=[product_task],
            process=Process.sequential,
            verbose=True
        )

        product_result = product_crew.kickoff()

        print("\n💡 Product Discovery Complete!")
        print(f"Results:\n{product_result}\n")

        return {
            'market_research': market_result,
            'product_discovery': product_result
        }

    def run_full_pipeline(self, initial_market=None):
        """Run complete end-to-end pipeline"""
        print("\n" + "="*70)
        print("🚀 AI BUSINESS AUTOMATION - FULL PIPELINE")
        print("="*70 + "\n")

        # Phase 1: Market Intelligence
        phase1_results = self.run_market_discovery()

        # Phase 2: Audience & Brand
        print("\n" + "="*70)
        print("🎯 PHASE 2: AUDIENCE & BRAND IDENTITY")
        print("="*70 + "\n")

        audience_agent = self.create_audience_identity_researcher()
        brand_agent = self.create_brand_identity_creator()

        audience_task = self.create_audience_research_task(
            audience_agent,
            phase1_results['product_discovery']
        )

        audience_crew = Crew(
            agents=[audience_agent],
            tasks=[audience_task],
            process=Process.sequential,
            verbose=True
        )

        audience_result = audience_crew.kickoff()

        print("\n👥 Audience Research Complete!")

        # Brand Identity
        brand_task = self.create_brand_identity_task(brand_agent, audience_result)

        brand_crew = Crew(
            agents=[brand_agent],
            tasks=[brand_task],
            process=Process.sequential,
            verbose=True
        )

        brand_result = brand_crew.kickoff()

        print("\n🎨 Brand Identity Complete!")

        # Phase 3: Supplier Sourcing
        print("\n" + "="*70)
        print("🏭 PHASE 3: SUPPLIER SOURCING")
        print("="*70 + "\n")

        supplier_agent = self.create_supplier_sourcing_agent()
        supplier_task = self.create_supplier_sourcing_task(supplier_agent, brand_result)

        supplier_crew = Crew(
            agents=[supplier_agent],
            tasks=[supplier_task],
            process=Process.sequential,
            verbose=True
        )

        supplier_result = supplier_crew.kickoff()

        print("\n🤝 Supplier Sourcing Complete!")

        # Save all results
        results = {
            'market_research': phase1_results['market_research'],
            'product_discovery': phase1_results['product_discovery'],
            'audience_research': audience_result,
            'brand_identity': brand_result,
            'supplier_sourcing': supplier_result
        }

        # Save to file
        output_file = self.workspace_dir / 'data' / 'crew_results.json'
        import json
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n✅ Results saved to: {output_file}")

        return results


if __name__ == "__main__":
    import sys

    crew = AIBusinessCrew()

    if len(sys.argv) > 1 and sys.argv[1] == 'full':
        # Run complete pipeline
        results = crew.run_full_pipeline()
    else:
        # Run just Phase 1
        results = crew.run_market_discovery()

    print("\n" + "="*70)
    print("✅ CREW EXECUTION COMPLETE")
    print("="*70 + "\n")
