#!/usr/bin/env python3
"""
Crew.AI Domain Knowledge Orchestrator
Orchestrates data collection agents for a domain knowledge base
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

try:
    from crewai import Agent, Task, Crew, Process
    from langchain_anthropic import ChatAnthropic
except ImportError:
    print("⚠️  Missing dependencies. Installing...")
    os.system("pip install crewai crewai-tools langchain-anthropic")
    from crewai import Agent, Task, Crew, Process
    from langchain_anthropic import ChatAnthropic

# Load environment
load_dotenv(project_root / '.env')


class DomainKnowledgeCrew:
    """Crew.AI orchestration for domain knowledge collection"""
    
    def __init__(self, domain_path: Path):
        self.domain_path = Path(domain_path)
        self.domain_name = self.domain_path.name
        
        # Initialize LLM
        self.llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        
        # Create agents
        self.youtube_agent = self._create_youtube_agent()
        self.research_agent = self._create_research_agent()
        self.social_agent = self._create_social_agent()
        self.knowledge_agent = self._create_knowledge_agent()
        
        print(f"🤖 Crew.AI Orchestrator initialized for: {self.domain_name}")
    
    def _create_youtube_agent(self) -> Agent:
        """Create YouTube content collection agent"""
        return Agent(
            role='YouTube Content Curator',
            goal=f'Collect and transcribe the latest YouTube videos about {self.domain_name}',
            backstory=f"""You are an expert at finding high-quality educational content 
            on YouTube. You know which channels produce the best content about {self.domain_name} 
            and you're skilled at extracting valuable information from video transcripts.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def _create_research_agent(self) -> Agent:
        """Create research paper collection agent"""
        return Agent(
            role='Research Paper Analyst',
            goal=f'Find and analyze the latest scientific papers about {self.domain_name}',
            backstory=f"""You are a research analyst who excels at finding cutting-edge 
            scientific papers. You understand how to search arXiv, Semantic Scholar, and 
            other academic databases to find the most relevant and impactful papers about 
            {self.domain_name}.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def _create_social_agent(self) -> Agent:
        """Create social media monitoring agent"""
        return Agent(
            role='Social Media Monitor',
            goal=f'Track discussions and sentiment about {self.domain_name} on social media',
            backstory=f"""You are a social media analyst who monitors Reddit, Twitter, 
            and other platforms to understand what people are saying about {self.domain_name}. 
            You're skilled at sentiment analysis and identifying trends in online discussions.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def _create_knowledge_agent(self) -> Agent:
        """Create knowledge base engineering agent"""
        return Agent(
            role='Knowledge Engineer',
            goal=f'Organize and structure collected data into a searchable knowledge base',
            backstory=f"""You are a knowledge engineer who excels at structuring and 
            organizing information. You know how to process raw data from various sources 
            and transform it into a well-organized, searchable knowledge base using vector 
            embeddings and graph relationships.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def _create_tasks(self) -> list:
        """Create tasks for the crew"""
        tasks = []
        
        # Task 1: Collect YouTube content
        youtube_task = Task(
            description=f"""Collect the latest YouTube videos about {self.domain_name}.
            
            Steps:
            1. Access configured YouTube channels from domain config
            2. Get videos from the last 30 days
            3. Download transcripts for each video
            4. Save metadata and transcripts to the youtube/ directory
            
            Output: Summary of videos collected and transcripts downloaded""",
            agent=self.youtube_agent,
            expected_output="Number of videos and transcripts collected"
        )
        tasks.append(youtube_task)
        
        # Task 2: Collect research papers
        research_task = Task(
            description=f"""Find and collect the latest research papers about {self.domain_name}.
            
            Steps:
            1. Search arXiv for papers in relevant categories
            2. Search Semantic Scholar for additional papers
            3. Collect paper metadata (title, abstract, authors, citations)
            4. Save to research/papers/ directory
            
            Output: Summary of papers collected from each source""",
            agent=self.research_agent,
            expected_output="Number of papers collected from arXiv and Semantic Scholar"
        )
        tasks.append(research_task)
        
        # Task 3: Collect social media data
        social_task = Task(
            description=f"""Monitor social media discussions about {self.domain_name}.
            
            Steps:
            1. Collect posts from configured Reddit subreddits
            2. Analyze sentiment of each post
            3. Calculate overall sentiment distribution
            4. Save posts and sentiment analysis to social/ directory
            
            Output: Summary of posts collected and sentiment breakdown""",
            agent=self.social_agent,
            expected_output="Number of posts and sentiment distribution percentages"
        )
        tasks.append(social_task)
        
        # Task 4: Build knowledge base
        knowledge_task = Task(
            description=f"""Process all collected data and build a searchable knowledge base.
            
            Steps:
            1. Review all collected YouTube transcripts, research papers, and social posts
            2. Chunk content into meaningful segments
            3. Generate embeddings for semantic search
            4. Store in vector database (Qdrant)
            5. Create relationships and metadata
            
            Output: Summary of knowledge base statistics""",
            agent=self.knowledge_agent,
            expected_output="Total items processed and stored in knowledge base"
        )
        tasks.append(knowledge_task)
        
        return tasks
    
    def run(self):
        """Execute the crew workflow"""
        print(f"\n{'='*60}")
        print(f"🚀 Starting Crew.AI Knowledge Collection")
        print(f"   Domain: {self.domain_name}")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        # Create tasks
        tasks = self._create_tasks()
        
        # Create crew
        crew = Crew(
            agents=[
                self.youtube_agent,
                self.research_agent,
                self.social_agent,
                self.knowledge_agent
            ],
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )
        
        # Execute
        try:
            result = crew.kickoff()
            
            print(f"\n{'='*60}")
            print(f"✅ Crew Execution Complete!")
            print(f"{'='*60}")
            print(result)
            print(f"{'='*60}\n")
            
            return result
            
        except Exception as e:
            print(f"\n✗ Crew execution failed: {e}")
            raise


def main():
    """Main execution"""
    if len(sys.argv) < 2:
        print("Usage: python crew_orchestrator.py <domain_path>")
        print("Example: python crew_orchestrator.py /Users/yourox/AI-Workspace/domains/ai_trends")
        sys.exit(1)
    
    domain_path = Path(sys.argv[1])
    
    if not domain_path.exists():
        print(f"✗ Domain path does not exist: {domain_path}")
        sys.exit(1)
    
    crew_orchestrator = DomainKnowledgeCrew(domain_path)
    crew_orchestrator.run()


if __name__ == '__main__':
    main()
