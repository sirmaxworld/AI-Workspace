# Business Intelligence Schema v1.0.0
Last Updated: 2025-10-15

## Data Categories

### products_tools
**Description:** Products and tools mentioned with sentiment analysis
**Fields:** name, category, use_case, sentiment, pricing, metrics
**Categories:** saas, ai-tool, mobile-app, service, physical-product, platform, market-research-tool, sourcing-platform, automation-platform, content-generator, api-service, all
**Sentiments:** positive, negative, neutral, recommended, positive/recommended, highly-recommended, all

### business_strategies
**Description:** Business strategies with implementation details
**Fields:** strategy_type, strategy, implementation, expected_results, case_study

### problems_solutions
**Description:** Problems with step-by-step solutions
**Fields:** problem, category, solution, steps, tools_needed, difficulty, time_estimate
**Categories:** technical, business, marketing, product, market-research, branding, operations, sales
**Difficulties:** beginner, intermediate, advanced

### startup_ideas
**Description:** Startup ideas with validation and business models
**Fields:** idea, target_market, problem_solved, business_model, validation, investment_needed

### mistakes_to_avoid
**Description:** Common mistakes with prevention strategies
**Fields:** mistake, consequences, prevention, example

### growth_tactics
**Description:** Growth tactics across marketing channels
**Fields:** channel, tactic, steps, cost_estimate, results_expected

### ai_workflows
**Description:** AI workflows with automation details
**Fields:** workflow_name, tools_used, steps, automation_level, use_case

### metrics_kpis
**Description:** Key metrics and KPIs with benchmarks
**Fields:** metric, benchmark, tracking_method, optimization_tip

### trends_signals
**Description:** Market trends with stage and opportunity analysis
**Fields:** trend, category, stage, opportunity
**Categories:** technology, market, consumer-behavior, fitness, business, all

### actionable_quotes
**Description:** Actionable quotes with context and category
**Fields:** quote, context, category, actionability
**Categories:** strategy, mindset, tactical, branding, operations, marketing, all

### key_statistics
**Description:** Key statistics with source reliability
**Fields:** statistic, context, source_reliability

### meta
**Description:** Video metadata and extraction details
**Fields:** video_id, title, extracted_at, model, transcript_length, processing_time_seconds


## MCP Tool Mappings

### search_products
**Data Category:** `products_tools`

**Description:** Search products and tools with filtering

**Filter Fields:** category, sentiment

**Search Fields:** name, use_case, metrics

### search_problems
**Data Category:** `problems_solutions`

**Description:** Search problems with solutions

**Filter Fields:** category, difficulty

**Search Fields:** problem, solution, steps

### search_startup_ideas
**Data Category:** `startup_ideas`

**Description:** Search startup ideas

**Filter Fields:** target_market, business_model

**Search Fields:** idea, problem_solved

### search_growth_tactics
**Data Category:** `growth_tactics`

**Description:** Search growth tactics

**Filter Fields:** channel

**Search Fields:** tactic, steps, results_expected

### search_ai_workflows
**Data Category:** `ai_workflows`

**Description:** Search AI workflows

**Filter Fields:** automation_level

**Search Fields:** workflow_name, tools_used, use_case

### search_target_markets
**Data Category:** `market_intelligence.target_markets`

**Description:** Search target markets

**Filter Fields:** None

**Search Fields:** market_description, demographics, pain_points

### search_trends
**Data Category:** `trends_signals`

**Description:** Search market trends

**Filter Fields:** category, stage

**Search Fields:** trend, opportunity

### search_business_strategies
**Data Category:** `business_strategies`

**Description:** Search business strategies

**Filter Fields:** strategy_type

**Search Fields:** strategy, implementation, case_study

### get_actionable_quotes
**Data Category:** `actionable_quotes`

**Description:** Get actionable quotes

**Filter Fields:** category

**Search Fields:** quote, context, actionability

### get_key_metrics
**Data Category:** `metrics_kpis`

**Description:** Get key metrics and KPIs

**Filter Fields:** None

**Search Fields:** metric, benchmark, optimization_tip

### get_mistakes_to_avoid
**Data Category:** `mistakes_to_avoid`

**Description:** Get mistakes to avoid

**Filter Fields:** None

**Search Fields:** mistake, prevention, example

