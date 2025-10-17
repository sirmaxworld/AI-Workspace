#!/usr/bin/env python3
"""
Master Knowledge Base Orchestrator
Manages all knowledge domains and coordinates data collection crews
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import argparse
from dotenv import load_dotenv

from knowledge_pipeline import KnowledgePipeline, OutputValidationError

# Load environment
load_dotenv('/Users/yourox/AI-Workspace/.env')

# Paths
BASE_PATH = Path('/Users/yourox/AI-Workspace')
CONFIG_PATH = BASE_PATH / 'config' / 'knowledge_domains.json'
DATA_PATH = BASE_PATH / 'data'

# Load configuration
with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)
    DOMAINS = CONFIG['knowledge_domains']

# Initialise pipeline once per process
PIPELINE = KnowledgePipeline(BASE_PATH)


def print_header():
    """Print system header"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     🧠 MULTI-DOMAIN KNOWLEDGE BASE ORCHESTRATOR 🧠            ║
║                                                                  ║
║  Intelligent Data Collection & Knowledge Management System      ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)


def list_domains():
    """List all available knowledge domains"""
    print("\n📚 AVAILABLE KNOWLEDGE DOMAINS:\n")
    print(f"{'Key':<25} {'Name':<40} {'Priority':<12}")
    print("="*80)
    
    for key, domain in DOMAINS.items():
        priority = domain.get('priority', 'medium').upper()
        priority_emoji = {
            'VERY_HIGH': '🔴',
            'HIGH': '🟠', 
            'MEDIUM': '🟡',
            'LOW': '🟢'
        }.get(priority, '⚪')
        
        print(f"{key:<25} {domain['name'][:38]:<40} {priority_emoji} {priority:<10}")
    
    print("="*80)
    print(f"\nTotal domains: {len(DOMAINS)}")


def show_domain_details(domain_key: str):
    """Show detailed information about a domain"""
    if domain_key not in DOMAINS:
        print(f"❌ Unknown domain: {domain_key}")
        return
    
    domain = DOMAINS[domain_key]
    
    print(f"\n{'='*70}")
    print(f"📖 DOMAIN: {domain['name']}")
    print(f"{'='*70}")
    print(f"\nDescription: {domain['description']}")
    print(f"Collection: {domain['qdrant_collection']}")
    print(f"Update Frequency: {domain['update_frequency']}")
    print(f"Priority: {domain['priority']}")
    
    print(f"\n🎥 YouTube Channels ({len(domain['data_sources']['youtube_channels'])}):")
    for channel in domain['data_sources']['youtube_channels']:
        print(f"   • {channel}")
    
    print(f"\n📚 Research Sources ({len(domain['data_sources']['research_sources'])}):")
    for source in domain['data_sources']['research_sources']:
        print(f"   • {source}")
    
    print(f"\n📱 Social Media:")
    print(f"   Reddit: {', '.join(domain['data_sources']['social_media']['reddit'])}")
    print(f"   Twitter: {', '.join(domain['data_sources']['social_media']['twitter_keywords'])}")
    
    print(f"\n📰 Industry Blogs ({len(domain['data_sources']['industry_blogs'])}):")
    for blog in domain['data_sources']['industry_blogs']:
        print(f"   • {blog}")
    
    print(f"\n{'='*70}")


def run_collection(domain_key: str, sources: list = None):
    """Run data collection for a domain"""
    if domain_key not in DOMAINS:
        print(f"❌ Unknown domain: {domain_key}")
        return
    
    print(f"\n🚀 Starting data collection for: {DOMAINS[domain_key]['name']}")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    # Import and run the crew
    try:
        result = PIPELINE.run(domain_key)

        # Legacy results directory for backward compatibility
        output_dir = DATA_PATH / 'crew_results'
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f'{domain_key}_{timestamp}.json'

        with open(output_file, 'w') as f:
            json.dump({
                'domain': domain_key,
                'timestamp': timestamp,
                'result': result
            }, f, indent=2)

        print(f"\n✅ Collection complete! Pipeline summary saved to:")
        print(f"   {result['artifact_dir']}")
        print(f"   {output_file}")

    except OutputValidationError as e:
        print(f"❌ Structured output validation failed: {e}")
    except Exception as e:
        print(f"❌ Error during collection: {e}")


def run_all_collections(priority_filter: str = None):
    """Run data collection for all domains (optionally filtered by priority)"""
    print(f"\n🔥 BATCH COLLECTION MODE")
    
    # Filter domains by priority if specified
    domains_to_run = []
    for key, domain in DOMAINS.items():
        if priority_filter is None or domain.get('priority') == priority_filter:
            domains_to_run.append(key)
    
    if not domains_to_run:
        print(f"❌ No domains found with priority: {priority_filter}")
        return
    
    print(f"   Running {len(domains_to_run)} domains")
    if priority_filter:
        print(f"   Priority filter: {priority_filter}")
    print(f"{'='*70}\n")
    
    results = {}
    for i, domain_key in enumerate(domains_to_run, 1):
        print(f"\n[{i}/{len(domains_to_run)}] Processing: {domain_key}")
        print("="*70)
        
        try:
            run_collection(domain_key)
            results[domain_key] = 'success'
        except Exception as e:
            print(f"❌ Failed: {e}")
            results[domain_key] = f'failed: {str(e)}'
        
        print()
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 BATCH COLLECTION SUMMARY")
    print(f"{'='*70}")
    
    successes = sum(1 for v in results.values() if v == 'success')
    failures = len(results) - successes
    
    print(f"   Total: {len(results)}")
    print(f"   ✅ Successful: {successes}")
    print(f"   ❌ Failed: {failures}")
    
    if failures > 0:
        print(f"\n   Failed domains:")
        for domain, status in results.items():
            if status != 'success':
                print(f"      • {domain}: {status}")


def show_statistics():
    """Show knowledge base statistics"""
    print(f"\n📊 KNOWLEDGE BASE STATISTICS")
    print(f"{'='*70}")
    
    # Count domains by priority
    priority_counts = {}
    for domain in DOMAINS.values():
        priority = domain.get('priority', 'unknown')
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
    
    print(f"\n📈 Domains by Priority:")
    for priority, count in sorted(priority_counts.items()):
        print(f"   {priority.upper()}: {count}")
    
    # Count total sources
    total_youtube = sum(len(d['data_sources']['youtube_channels']) for d in DOMAINS.values())
    total_research = sum(len(d['data_sources']['research_sources']) for d in DOMAINS.values())
    total_reddit = sum(len(d['data_sources']['social_media']['reddit']) for d in DOMAINS.values())
    total_blogs = sum(len(d['data_sources']['industry_blogs']) for d in DOMAINS.values())
    
    print(f"\n📁 Total Data Sources:")
    print(f"   YouTube Channels: {total_youtube}")
    print(f"   Research Sources: {total_research}")
    print(f"   Reddit Communities: {total_reddit}")
    print(f"   Industry Blogs: {total_blogs}")
    print(f"   TOTAL: {total_youtube + total_research + total_reddit + total_blogs}")
    
    # Check for collected data
    results_dir = DATA_PATH / 'crew_results'
    if results_dir.exists():
        result_files = list(results_dir.glob('*.json'))
        print(f"\n💾 Collection Results:")
        print(f"   Total runs: {len(result_files)}")
        
        if result_files:
            # Group by domain
            domain_runs = {}
            for f in result_files:
                domain = f.stem.split('_')[0]
                domain_runs[domain] = domain_runs.get(domain, 0) + 1
            
            print(f"\n   Runs by domain:")
            for domain, count in sorted(domain_runs.items()):
                print(f"      {domain}: {count}")
    
    print(f"\n{'='*70}")


def main():
    """Main CLI"""
    parser = argparse.ArgumentParser(
        description='Multi-Domain Knowledge Base Orchestrator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list                    # List all domains
  %(prog)s info robotics           # Show domain details
  %(prog)s collect ai_trends       # Collect data for one domain
  %(prog)s collect-all             # Collect data for all domains
  %(prog)s collect-all --priority high  # Collect only high priority
  %(prog)s stats                   # Show statistics
        """
    )
    
    parser.add_argument('command', 
                       choices=['list', 'info', 'collect', 'collect-all', 'stats'],
                       help='Command to execute')
    parser.add_argument('domain', nargs='?', help='Domain key (for info/collect)')
    parser.add_argument('--priority', help='Priority filter for collect-all')
    parser.add_argument('--sources', nargs='+', 
                       help='Specific sources to collect (youtube, academic, social, industry)')
    
    args = parser.parse_args()
    
    print_header()
    
    if args.command == 'list':
        list_domains()
    
    elif args.command == 'info':
        if not args.domain:
            print("❌ Domain key required for 'info' command")
            print("   Usage: orchestrator.py info <domain_key>")
            sys.exit(1)
        show_domain_details(args.domain)
    
    elif args.command == 'collect':
        if not args.domain:
            print("❌ Domain key required for 'collect' command")
            print("   Usage: orchestrator.py collect <domain_key>")
            sys.exit(1)
        run_collection(args.domain, args.sources)
    
    elif args.command == 'collect-all':
        run_all_collections(args.priority)
    
    elif args.command == 'stats':
        show_statistics()


if __name__ == "__main__":
    main()
