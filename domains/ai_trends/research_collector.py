#!/usr/bin/env python3
"""
Research Paper Collector for Domain Knowledge Bases
Collects papers from arXiv and Semantic Scholar
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Load environment
load_dotenv(project_root / '.env')


class DomainResearchCollector:
    """Collects research papers for a specific domain"""
    
    def __init__(self, domain_path: Path):
        self.domain_path = Path(domain_path)
        self.config = self._load_config()
        
        # Directories
        self.research_dir = self.domain_path / 'research'
        self.papers_dir = self.research_dir / 'papers'
        self.summaries_dir = self.research_dir / 'summaries'
        self.papers_metadata_file = self.research_dir / 'papers.json'
        
        # Ensure directories exist
        self.papers_dir.mkdir(parents=True, exist_ok=True)
        self.summaries_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📚 Research Collector for: {self.config['display_name']}")
    
    def _load_config(self) -> Dict:
        """Load domain configuration"""
        config_file = self.domain_path / 'config.json'
        with open(config_file, 'r') as f:
            return json.load(f)
    
    def search_arxiv(self, query: str, max_results: int = 100) -> List[Dict]:
        """Search arXiv for papers"""
        print(f"  🔍 Searching arXiv: {query}")
        
        papers = []
        base_url = 'http://export.arxiv.org/api/query'
        
        # Calculate date range
        days_back = self.config['research'].get('days_back', 90)
        start_date = datetime.now() - timedelta(days=days_back)
        
        # Build query with date filter
        search_query = f'all:{query} AND submittedDate:[{start_date.strftime("%Y%m%d")}0000 TO 20991231235959]'
        
        params = {
            'search_query': search_query,
            'start': 0,
            'max_results': max_results,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }
        
        try:
            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            
            # Parse XML response (simplified)
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            # Extract paper info
            namespace = {'atom': 'http://www.w3.org/2005/Atom'}
            entries = root.findall('atom:entry', namespace)
            
            for entry in entries:
                paper = {
                    'id': entry.find('atom:id', namespace).text.split('/abs/')[-1],
                    'title': entry.find('atom:title', namespace).text.strip(),
                    'summary': entry.find('atom:summary', namespace).text.strip(),
                    'published': entry.find('atom:published', namespace).text,
                    'authors': [author.find('atom:name', namespace).text 
                               for author in entry.findall('atom:author', namespace)],
                    'pdf_url': entry.find('atom:id', namespace).text.replace('/abs/', '/pdf/') + '.pdf',
                    'source': 'arxiv',
                    'categories': [cat.get('term') for cat in entry.findall('atom:category', namespace)]
                }
                papers.append(paper)
            
            print(f"    Found {len(papers)} papers")
            
        except Exception as e:
            print(f"    ✗ arXiv search failed: {e}")
        
        return papers
    
    def search_semantic_scholar(self, query: str, max_results: int = 100) -> List[Dict]:
        """Search Semantic Scholar for papers"""
        print(f"  🔍 Searching Semantic Scholar: {query}")
        
        if not self.config['research'].get('semantic_scholar', {}).get('enabled'):
            print("    ⚠️  Semantic Scholar disabled in config")
            return []
        
        papers = []
        base_url = 'https://api.semanticscholar.org/graph/v1/paper/search'
        
        # Calculate year range
        days_back = self.config['research'].get('days_back', 90)
        min_year = (datetime.now() - timedelta(days=days_back)).year
        
        params = {
            'query': query,
            'limit': min(max_results, 100),
            'year': f'{min_year}-',
            'fields': 'paperId,title,abstract,authors,year,citationCount,url,publicationDate'
        }
        
        try:
            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            for item in data.get('data', []):
                paper = {
                    'id': item.get('paperId'),
                    'title': item.get('title'),
                    'summary': item.get('abstract', ''),
                    'published': item.get('publicationDate', ''),
                    'authors': [author.get('name') for author in item.get('authors', [])],
                    'url': item.get('url'),
                    'citations': item.get('citationCount', 0),
                    'source': 'semantic_scholar'
                }
                papers.append(paper)
            
            print(f"    Found {len(papers)} papers")
            
        except Exception as e:
            print(f"    ✗ Semantic Scholar search failed: {e}")
        
        return papers
    
    def collect_all(self) -> Dict:
        """Collect papers from all configured sources"""
        print(f"\n{'='*60}")
        print(f"Starting research collection for: {self.config['display_name']}")
        print(f"{'='*60}\n")
        
        all_papers = []
        stats = {
            'queries_processed': 0,
            'arxiv_papers': 0,
            'semantic_scholar_papers': 0,
            'total_papers': 0
        }
        
        # Search arXiv
        print("📖 Searching arXiv...")
        for query in self.config['research']['search_queries']:
            max_results = self.config['research'].get('max_papers_per_query', 100)
            papers = self.search_arxiv(query, max_results)
            all_papers.extend(papers)
            stats['arxiv_papers'] += len(papers)
            stats['queries_processed'] += 1
        
        print()
        
        # Search Semantic Scholar
        print("🔬 Searching Semantic Scholar...")
        for query in self.config['research']['search_queries']:
            max_results = self.config['research'].get('max_papers_per_query', 100)
            papers = self.search_semantic_scholar(query, max_results)
            all_papers.extend(papers)
            stats['semantic_scholar_papers'] += len(papers)
        
        # Remove duplicates (by title)
        unique_papers = {}
        for paper in all_papers:
            title = paper.get('title', '').lower().strip()
            if title and title not in unique_papers:
                unique_papers[title] = paper
        
        all_papers = list(unique_papers.values())
        stats['total_papers'] = len(all_papers)
        
        # Save metadata
        with open(self.papers_metadata_file, 'w') as f:
            json.dump(all_papers, f, indent=2)
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"✅ Research Collection Complete!")
        print(f"{'='*60}")
        print(f"Queries processed: {stats['queries_processed']}")
        print(f"arXiv papers: {stats['arxiv_papers']}")
        print(f"Semantic Scholar papers: {stats['semantic_scholar_papers']}")
        print(f"Total unique papers: {stats['total_papers']}")
        print(f"\n📁 Saved to: {self.papers_metadata_file}")
        print(f"{'='*60}\n")
        
        return stats


def main():
    """Main execution"""
    if len(sys.argv) < 2:
        print("Usage: python research_collector.py <domain_path>")
        print("Example: python research_collector.py /Users/yourox/AI-Workspace/domains/ai_trends")
        sys.exit(1)
    
    domain_path = Path(sys.argv[1])
    
    if not domain_path.exists():
        print(f"✗ Domain path does not exist: {domain_path}")
        sys.exit(1)
    
    collector = DomainResearchCollector(domain_path)
    collector.collect_all()


if __name__ == '__main__':
    main()
