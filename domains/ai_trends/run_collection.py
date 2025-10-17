#!/usr/bin/env python3
"""
Master Runner for Domain Knowledge Collection
Executes all collectors for a domain
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def run_collector(script_name: str, domain_path: Path):
    """Run a collector script"""
    script_path = domain_path / script_name
    
    if not script_path.exists():
        print(f"⚠️  Script not found: {script_name}")
        return False
    
    print(f"\n{'='*60}")
    print(f"🚀 Running: {script_name}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path), str(domain_path)],
            check=True,
            capture_output=False
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ {script_name} failed with error code {e.returncode}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_collection.py <domain_path>")
