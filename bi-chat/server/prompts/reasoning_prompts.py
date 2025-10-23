#!/usr/bin/env python3
"""
Reasoning prompts for different thinking modes
"""

from typing import Dict, Any


def get_system_prompt(thinking_mode: str = "quick") -> str:
    """Get system prompt based on thinking mode"""

    base_prompt = """You are a helpful AI assistant with expertise in business intelligence, product development, and market analysis.

Your communication style:
- Clear, well-formatted markdown responses
- Use headers (##, ###) to organize sections
- Use bullet points and numbered lists for readability
- Use **bold** for emphasis on key points
- Keep paragraphs short (2-3 sentences max)
- Include specific examples when relevant

Response structure:
1. Direct answer first (2-3 sentences)
2. Supporting details with clear sections
3. Actionable recommendations at the end

Always format your responses professionally with proper markdown."""

    mode_instructions = {
        "quick": "\n\nMode: Provide concise, focused answers. Get straight to the point.",
        "deep": "\n\nMode: Provide comprehensive analysis with multiple perspectives and detailed reasoning.",
        "critical": "\n\nMode: Provide thorough evaluation including risks, counterarguments, and balanced assessment."
    }

    return base_prompt + mode_instructions.get(thinking_mode, mode_instructions["quick"])


def get_builder_context_prompt() -> str:
    """Additional context for builder-focused queries"""
    return """
Builder Context:
- Focus: Solo developer or small team
- Goal: Build successful SaaS or products
- Constraints: Bootstrap-friendly, 3-6 month timeline
- Needs: Product ideas, market validation, GTM strategy

When analyzing opportunities, consider:
1. Can this be built by a solo developer?
2. Is market timing right (not too early/late)?
3. Is there validated demand?
4. What's the competitive landscape?
5. How would you go to market?
6. What's the risk/reward profile?
"""


def format_tool_results_for_context(tool_results: Dict[str, Any]) -> str:
    """Format MCP tool results for model context"""
    formatted_parts = []

    for tool_call, result in tool_results.items():
        formatted_parts.append(f"=== {tool_call} ===")
        formatted_parts.append(str(result))
        formatted_parts.append("")

    return "\n".join(formatted_parts)


def get_example_queries() -> Dict[str, str]:
    """Example queries for different use cases"""
    return {
        "opportunity_discovery": "What are the best opportunities in AI agents right now?",
        "market_timing": "Is it too late to build a content repurposing AI tool?",
        "idea_validation": "Validate my idea: AI-powered meeting summarizer for remote teams",
        "gtm_strategy": "How should I launch a SaaS for small agencies?",
        "trend_analysis": "What's the trajectory of the 'AI agents' trend? Where is it heading?",
        "competitive_landscape": "What tools exist in the AI automation space?",
        "pain_discovery": "What are the biggest validated pain points in productivity tools?",
        "niche_finding": "Find me underserved niches with growing trends"
    }


def suggest_follow_up_queries(original_query: str, analysis_result: str) -> list[str]:
    """Suggest relevant follow-up queries based on the conversation"""
    # This could be enhanced with AI to generate contextual suggestions
    default_suggestions = [
        "What are the risks with this opportunity?",
        "Show me similar successful examples",
        "How would I validate this with users?",
        "What's the competitive landscape?"
    ]
    return default_suggestions
