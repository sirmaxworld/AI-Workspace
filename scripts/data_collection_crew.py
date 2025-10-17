#!/usr/bin/env python3
"""
Data Collection Crew - Multi-domain Knowledge Base Builder
Orchestrates specialized agents to collect data from multiple sources
"""

from crewai import Agent, Task, Crew, Process
from crewai_tools import (
    SerperDevTool,  # Google search
    WebsiteSearchTool,
    FileReadTool,
    DirectoryReadTool
)
import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

# Load environment
load_dotenv('/Users/yourox/AI-Workspace/.env')


logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=os.getenv('DATA_COLLECTION_CREW_LOG_LEVEL', 'INFO'))

# Paths
BASE_PATH = Path('/Users/yourox/AI-Workspace')
CONFIG_PATH = BASE_PATH / 'config' / 'knowledge_domains.json'
DATA_PATH = BASE_PATH / 'data'

# Load knowledge domains
with open(CONFIG_PATH, 'r') as f:
    DOMAINS = json.load(f)['knowledge_domains']


class OutputValidationError(Exception):
    """Raised when a task output cannot be parsed or validated."""


TASK_SCHEMAS: Dict[str, Dict[str, Any]] = {
    'youtube': {
        'required_keys': ['videos', 'summary'],
        'list_key': 'videos',
        'item_keys': ['url', 'title', 'channel'],
    },
    'academic': {
        'required_keys': ['papers', 'insights'],
        'list_key': 'papers',
        'item_keys': ['title', 'url', 'summary'],
    },
    'social': {
        'required_keys': ['posts', 'trends'],
        'list_key': 'posts',
        'item_keys': ['source', 'url', 'sentiment'],
    },
    'industry': {
        'required_keys': ['articles', 'highlights'],
        'list_key': 'articles',
        'item_keys': ['title', 'url', 'summary'],
    },
    'synthesizer': {
        'required_keys': ['knowledge_base', 'topic_map'],
    },
}


class DataCollectionCrew:
    """Manages specialized agents for multi-source data collection"""

    def __init__(self, domain_key: str):
        if domain_key not in DOMAINS:
            raise KeyError(f"Unknown domain: {domain_key}")

        self.domain_key = domain_key
        self.domain = DOMAINS[domain_key]
        self.collection_name = self.domain['qdrant_collection']
        self.tools = self._create_tools()

    def _create_tools(self) -> Dict[str, Any]:
        """Initialise shared toolset for tasks."""

        tools: Dict[str, Optional[Any]] = {
            'serper': None,
            'website': None,
            'file_reader': None,
            'directory_reader': None,
        }

        try:
            tools['serper'] = SerperDevTool()
        except Exception as exc:  # noqa: BLE001
            logger.warning("SerperDevTool unavailable: %s", exc)

        try:
            tools['website'] = WebsiteSearchTool()
        except Exception as exc:  # noqa: BLE001
            logger.warning("WebsiteSearchTool unavailable: %s", exc)

        tools['file_reader'] = FileReadTool()
        tools['directory_reader'] = DirectoryReadTool()

        ordered_tools = {
            name: tool for name, tool in tools.items() if tool is not None
        }

        if not ordered_tools:
            logger.warning("No external tools available – crew will operate in LLM-only mode")

        return ordered_tools

    def create_agents(self):
        """Create specialized agents for each data source"""
        
        # Agent 1: YouTube Researcher
        youtube_agent = Agent(
            role='YouTube Content Researcher',
            goal=f'Find and analyze the best YouTube videos about {self.domain["name"]}',
            backstory=f"""You are an expert at finding high-quality educational 
            content on YouTube. You specialize in {self.domain["description"]}. 
            You know which channels produce the most valuable, accurate content.""",
            verbose=True,
            allow_delegation=False,
            llm='anthropic/claude-sonnet-4-20250514'
        )
        
        # Agent 2: Academic Researcher
        academic_agent = Agent(
            role='Academic Research Specialist',
            goal=f'Find and summarize cutting-edge research papers on {self.domain["name"]}',
            backstory=f"""You are a PhD-level researcher specializing in 
            {self.domain["description"]}. You excel at finding relevant papers 
            on arXiv, IEEE, and academic journals. You understand research 
            methodology and can identify breakthrough papers.""",
            verbose=True,
            allow_delegation=False,
            llm='anthropic/claude-sonnet-4-20250514'
        )
        
        # Agent 3: Social Media Analyst
        social_media_agent = Agent(
            role='Social Media Sentiment Analyst',
            goal=f'Monitor social media discussions and sentiment about {self.domain["name"]}',
            backstory=f"""You are a social media intelligence expert. You track 
            discussions on Reddit, Twitter, and forums about {self.domain["description"]}. 
            You identify trends, community concerns, and emerging topics.""",
            verbose=True,
            allow_delegation=False,
            llm='anthropic/claude-sonnet-4-20250514'
        )
        
        # Agent 4: Industry News Monitor
        industry_agent = Agent(
            role='Industry News & Blog Monitor',
            goal=f'Track industry news, blog posts, and developments in {self.domain["name"]}',
            backstory=f"""You are an industry analyst who follows the latest news 
            and blog posts about {self.domain["description"]}. You know which 
            sources are authoritative and which announcements matter.""",
            verbose=True,
            allow_delegation=False,
            llm='anthropic/claude-sonnet-4-20250514'
        )
        
        # Agent 5: Data Synthesizer
        synthesizer_agent = Agent(
            role='Knowledge Synthesizer',
            goal='Organize and structure all collected data into the knowledge base',
            backstory=f"""You are a knowledge management expert. You take raw data 
            from multiple sources and organize it into a coherent, searchable 
            knowledge base. You create metadata, tags, and relationships.""",
            verbose=True,
            allow_delegation=True,
            llm='anthropic/claude-sonnet-4-20250514'
        )
        
        return {
            'youtube': youtube_agent,
            'academic': academic_agent,
            'social': social_media_agent,
            'industry': industry_agent,
            'synthesizer': synthesizer_agent
        }
    
    def create_tasks(self, agents):
        """Create tasks for data collection"""
        
        common_tools = list(self.tools.values())

        # Task 1: YouTube Collection
        youtube_task = Task(
            description=f"""
            Search for and collect the best YouTube videos about {self.domain["name"]}.
            
            Target channels: {', '.join(self.domain['data_sources']['youtube_channels'])}
            
            For each channel:
            1. Find recent videos (last 30 days)
            2. Identify most popular/educational videos
            3. Extract video IDs and titles
            4. Assess content quality
            
            Respond with **valid JSON only** using this schema:
            {{
              "videos": [
                {{"url": str, "title": str, "channel": str, "published": str, "summary": str, "relevance": float}}
              ],
              "summary": str,
              "notes": str
            }}
            """,
            expected_output="JSON object with 'videos' array (url/title/channel/published/summary/relevance), plus 'summary' and 'notes' strings",
            agent=agents['youtube'],
            tools=common_tools,
            output_file=f"{self.domain_key}_youtube.json"
        )
        
        # Task 2: Academic Research
        academic_task = Task(
            description=f"""
            Find cutting-edge research papers about {self.domain["name"]}.
            
            Search sources: {', '.join(self.domain['data_sources']['research_sources'])}
            
            For each source:
            1. Search for papers from last 90 days
            2. Identify high-impact papers (citations, venue)
            3. Extract abstracts and key findings
            4. Note methodology and results
            
            Respond with **valid JSON only** using this schema:
            {{
              "papers": [
                {{"title": str, "url": str, "authors": [str], "summary": str, "source": str, "published": str}}
              ],
              "insights": [str]
            }}
            """,
            expected_output="JSON object with 'papers' array (title/url/authors/summary/source/published) and 'insights' list",
            agent=agents['academic'],
            tools=common_tools,
            output_file=f"{self.domain_key}_research.json"
        )
        
        # Task 3: Social Media Monitoring
        social_task = Task(
            description=f"""
            Monitor social media discussions about {self.domain["name"]}.
            
            Sources:
            - Reddit: {', '.join(self.domain['data_sources']['social_media']['reddit'])}
            - Twitter keywords: {', '.join(self.domain['data_sources']['social_media']['twitter_keywords'])}
            
            For each source:
            1. Find trending discussions (last 7 days)
            2. Analyze sentiment (positive/negative/neutral)
            3. Identify common questions/concerns
            4. Note emerging trends
            
            Respond with **valid JSON only** using this schema:
            {{
              "posts": [
                {{"source": "reddit"|"twitter", "url": str, "title": str, "summary": str, "sentiment": "positive"|"neutral"|"negative"}}
              ],
              "trends": [str],
              "warnings": [str]
            }}
            """,
            expected_output="JSON object with 'posts' array (source/url/title/summary/sentiment) plus 'trends' and 'warnings' lists",
            agent=agents['social'],
            tools=common_tools,
            output_file=f"{self.domain_key}_social.json"
        )
        
        # Task 4: Industry News
        industry_task = Task(
            description=f"""
            Track industry news and blog posts about {self.domain["name"]}.
            
            Sources: {', '.join(self.domain['data_sources']['industry_blogs'])}
            
            For each source:
            1. Find latest articles (last 14 days)
            2. Identify major announcements
            3. Note product releases or updates
            4. Track industry partnerships
            
            Respond with **valid JSON only** using this schema:
            {{
              "articles": [
                {{"title": str, "url": str, "publisher": str, "summary": str, "impact": str}}
              ],
              "highlights": [str]
            }}
            """,
            expected_output="JSON object with 'articles' array (title/url/publisher/summary/impact) and 'highlights' list",
            agent=agents['industry'],
            tools=common_tools,
            output_file=f"{self.domain_key}_industry.json"
        )
        
        # Task 5: Knowledge Synthesis
        synthesis_task = Task(
            description=f"""
            Synthesize all collected data into a structured knowledge base.
            
            Input: Results from YouTube, academic, social media, and industry tasks
            
            Process:
            1. Remove duplicates and low-quality content
            2. Create unified metadata schema
            3. Extract key topics and themes
            4. Build topic hierarchy
            5. Generate searchable tags
            6. Create relationships between items
            
            Respond with **valid JSON only** using this schema:
            {{
              "knowledge_base": [
                {{
                  "id": str,
                  "title": str,
                  "content": str,
                  "source_type": "youtube"|"research"|"social"|"industry",
                  "source_url": str,
                  "tags": [str],
                  "timestamp": str
                }}
              ],
              "topic_map": {{"primary_topics": [str], "emerging": [str]}},
              "quality_score": float
            }}
            """,
            expected_output="JSON object with 'knowledge_base' array (id/title/content/source_type/source_url/tags/timestamp), 'topic_map', and 'quality_score'",
            agent=agents['synthesizer'],
            context=[youtube_task, academic_task, social_task, industry_task],
            tools=common_tools,
            output_file=f"{self.domain_key}_synthesis.json"
        )
        
        return [youtube_task, academic_task, social_task, industry_task, synthesis_task]
    
    def run_collection(self):
        """Execute the data collection crew"""
        
        print(f"\n{'='*60}")
        print(f"🚀 Starting Data Collection for: {self.domain['name']}")
        print(f"{'='*60}\n")
        
        # Create agents and tasks
        agents = self.create_agents()
        tasks = self.create_tasks(agents)
        
        # Create crew
        crew = Crew(
            agents=list(agents.values()),
            tasks=tasks,
            process=Process.sequential,  # Can be 'hierarchical' for more autonomy
            verbose=True
        )
        
        # Execute
        crew_result = crew.kickoff()

        structured_outputs = self._collect_outputs(tasks)

        run_summary = {
            'domain_key': self.domain_key,
            'domain_name': self.domain['name'],
            'collection_name': self.collection_name,
            'run_started_at': datetime.now().isoformat(),
            'raw_result': crew_result,
            'outputs': structured_outputs,
        }

        print(f"\n{'='*60}")
        print(f"✅ Data Collection Complete!")
        print(f"{'='*60}\n")

        return run_summary

    def _collect_outputs(self, tasks: List[Task]) -> Dict[str, Any]:
        """Extract, parse, and validate structured outputs from tasks."""

        results: Dict[str, Any] = {}

        task_mapping = ['youtube', 'academic', 'social', 'industry', 'synthesizer']

        for key, task in zip(task_mapping, tasks):
            raw = self._extract_raw_output(task)

            try:
                parsed = self._parse_structured_output(raw)
                self._validate_output(key, parsed)
            except OutputValidationError as exc:
                logger.error("Task '%s' produced invalid output: %s", key, exc)
                raise

            results[key] = parsed

        return results

    @staticmethod
    def _extract_raw_output(task: Task) -> str:
        """Pull the raw textual output from a CrewAI task."""

        output_obj = getattr(task, 'output', None)

        if output_obj is None:
            raise OutputValidationError("Task returned no output")

        for attr in ('raw_output', 'final_result', 'value', 'content'):
            if hasattr(output_obj, attr):
                data = getattr(output_obj, attr)
                if data:
                    return str(data)

        return str(output_obj)

    @staticmethod
    def _parse_structured_output(raw_text: str) -> Dict[str, Any]:
        """Convert raw text to JSON dict, handling fenced blocks."""

        if not raw_text:
            raise OutputValidationError("Empty output")

        cleaned = raw_text.strip()

        if cleaned.startswith('```'):
            cleaned = re.sub(r'^```json\s*', '', cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r'^```\s*', '', cleaned)
            cleaned = cleaned.rsplit('```', 1)[0]

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise OutputValidationError(f"JSON parsing failed: {exc}") from exc

    def _validate_output(self, task_key: str, payload: Dict[str, Any]) -> None:
        """Validate payload against minimal schema expectations."""

        schema = TASK_SCHEMAS.get(task_key)
        if not schema:
            return

        for key in schema.get('required_keys', []):
            if key not in payload:
                raise OutputValidationError(f"Missing required key '{key}'")

        list_key = schema.get('list_key')
        if list_key:
            items = payload.get(list_key, [])
            if not isinstance(items, list):
                raise OutputValidationError(f"'{list_key}' must be a list")

            required_item_keys = schema.get('item_keys', [])
            for idx, item in enumerate(items):
                if not isinstance(item, dict):
                    raise OutputValidationError(f"{list_key}[{idx}] must be an object")
                for item_key in required_item_keys:
                    if item_key not in item:
                        raise OutputValidationError(
                            f"{list_key}[{idx}] missing '{item_key}'"
                        )

        list_fields = ['summary', 'notes', 'insights', 'trends', 'warnings', 'highlights']
        for field in list_fields:
            if field in payload and not isinstance(payload[field], (str, list)):
                raise OutputValidationError(f"'{field}' must be a string or list")


def main():
    """Main execution"""
    import sys
    
    if len(sys.argv) < 2:
        print("""
╔══════════════════════════════════════════════════════════╗
║     DATA COLLECTION CREW - Knowledge Base Builder       ║
╚══════════════════════════════════════════════════════════╝

USAGE:
  python3 data_collection_crew.py <domain_key>

AVAILABLE DOMAINS:
  - 3d_printing          : 3D Printing & Additive Manufacturing
  - robotics             : Robotics & Automation
  - manufacturing_automation : Manufacturing & Industry 4.0
  - visual_ai            : Visual AI & Computer Vision
  - multimedia           : Multimedia Production & AI Tools
  - mental_health        : Mental Health & Psychology
  - business_strategy    : Business Strategy & Growth
  - ai_trends            : AI Trends & Emerging Technologies

EXAMPLES:
  python3 data_collection_crew.py robotics
  python3 data_collection_crew.py visual_ai
  python3 data_collection_crew.py ai_trends

WHAT IT DOES:
  1. Deploys 5 specialized AI agents
  2. Collects data from YouTube, research papers, social media
  3. Analyzes sentiment and trends
  4. Synthesizes into structured knowledge base
  5. Ready for ingestion into Qdrant vector database

════════════════════════════════════════════════════════════
        """)
        sys.exit(1)
    
    domain_key = sys.argv[1]
    
    if domain_key not in DOMAINS:
        print(f"❌ Unknown domain: {domain_key}")
        print(f"Available: {', '.join(DOMAINS.keys())}")
        sys.exit(1)
    
    # Run collection
    crew = DataCollectionCrew(domain_key)
    result = crew.run_collection()
    
    # Save result
    output_path = DATA_PATH / 'crew_results' / f'{domain_key}_collection.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n✅ Results saved to: {output_path}")


if __name__ == "__main__":
    main()
