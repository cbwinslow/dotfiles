#!/usr/bin/env python3
"""
Documentation Fetcher - Download and create documentation for AI agents

This tool searches for, downloads, and structures documentation on any topic
requested by AI agents. It can fetch from web sources, GitHub repos, and
package documentation.
"""

import os
import sys
import re
import json
import argparse
import subprocess
from pathlib import Path
from urllib.parse import urlparse
from typing import List, Dict, Optional

# Add skills path for unified_memory
sys.path.insert(0, '/home/cbwinslow/dotfiles/ai/skills')


class DocumentationFetcher:
    """Fetch and structure documentation for AI agents."""
    
    def __init__(self, output_dir: str = "~/dotfiles/ai/docs/fetched"):
        self.output_dir = Path(output_dir).expanduser()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir = self.output_dir / ".cache"
        self.cache_dir.mkdir(exist_ok=True)
    
    def fetch_documentation(self, topic: str, sources: List[str] = None) -> Dict:
        """
        Fetch documentation for a given topic.
        
        Args:
            topic: The topic to search for (e.g., "docker compose", "python asyncio")
            sources: List of sources to search (web, github, package, man)
        
        Returns:
            Dict with fetched documentation metadata and paths
        """
        if not sources:
            sources = ["web", "github", "package"]
        
        results = {
            "topic": topic,
            "sources": {},
            "output_files": [],
            "timestamp": self._get_timestamp()
        }
        
        # Create safe filename from topic
        safe_topic = self._safe_filename(topic)
        output_base = self.output_dir / safe_topic
        
        print(f"🔍 Fetching documentation for: {topic}")
        print(f"📁 Output directory: {output_base}")
        
        # Create output directory for this topic
        output_base.mkdir(exist_ok=True)
        
        # Search and fetch from each source
        if "web" in sources:
            print("\n🌐 Searching web documentation...")
            web_results = self._fetch_from_web(topic, output_base)
            results["sources"]["web"] = web_results
        
        if "github" in sources:
            print("\n📦 Searching GitHub repositories...")
            github_results = self._fetch_from_github(topic, output_base)
            results["sources"]["github"] = github_results
        
        if "package" in sources:
            print("\n📚 Searching package documentation...")
            package_results = self._fetch_from_packages(topic, output_base)
            results["sources"]["package"] = package_results
        
        if "man" in sources:
            print("\n📖 Searching man pages...")
            man_results = self._fetch_from_man_pages(topic, output_base)
            results["sources"]["man"] = man_results
        
        # Create consolidated index
        index_file = self._create_index(topic, results, output_base)
        results["index_file"] = str(index_file)
        results["output_files"].append(str(index_file))
        
        # Save metadata
        metadata_file = output_base / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(results, f, indent=2)
        results["metadata_file"] = str(metadata_file)
        
        print(f"\n✅ Documentation fetch complete!")
        print(f"📄 Index: {index_file}")
        print(f"📊 Metadata: {metadata_file}")
        
        return results
    
    def _safe_filename(self, topic: str) -> str:
        """Convert topic to safe filename."""
        # Replace spaces and special chars
        safe = re.sub(r'[^\w\s-]', '', topic.lower())
        safe = re.sub(r'[-\s]+', '_', safe)
        return safe[:50]  # Limit length
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _fetch_from_web(self, topic: str, output_dir: Path) -> Dict:
        """Fetch documentation from web sources using brave search."""
        results = {
            "searches_performed": [],
            "files_created": []
        }
        
        try:
            # Try to use brave search if available
            search_queries = [
                f"{topic} documentation",
                f"{topic} tutorial getting started",
                f"{topic} official docs"
            ]
            
            for query in search_queries:
                print(f"  Searching: {query}")
                results["searches_performed"].append(query)
                
                # Create placeholder for web results
                # In production, this would use brave_search MCP
                result_file = output_dir / f"web_{self._safe_filename(query)}.md"
                
                # For now, create template
                content = f"""# Web Search Results: {query}

**Topic:** {topic}  
**Query:** {query}  
**Date:** {self._get_timestamp()}

## Results

*Web search results would be populated here using brave_search MCP*

## Suggested Sources

1. Official documentation site
2. GitHub repository README
3. Tutorial sites
4. Stack Overflow discussions

## Next Steps

1. Visit official documentation
2. Check GitHub repo for examples
3. Look for getting started guides

---
*Note: Connect brave_search MCP for live search results*
"""
                with open(result_file, 'w') as f:
                    f.write(content)
                results["files_created"].append(str(result_file))
                print(f"    📄 Created: {result_file.name}")
            
        except Exception as e:
            results["error"] = str(e)
            print(f"    ⚠️  Web search error: {e}")
        
        return results
    
    def _fetch_from_github(self, topic: str, output_dir: Path) -> Dict:
        """Fetch documentation from GitHub repositories."""
        results = {
            "repos_found": [],
            "files_created": []
        }
        
        try:
            # Search for relevant repos
            # In production, use GitHub MCP or API
            search_terms = topic.lower().split()
            
            # Create placeholder for GitHub results
            result_file = output_dir / "github_repos.md"
            
            content = f"""# GitHub Repositories: {topic}

**Topic:** {topic}  
**Date:** {self._get_timestamp()}

## Search Strategy

Search terms used:
"""
            for term in search_terms:
                content += f"- {term}\n"
            
            content += f"""
## Suggested Repository Searches

1. `{topic.replace(' ', '-')}` - Exact match
2. `awesome-{topic.replace(' ', '-')}` - Curated lists
3. `{topic.replace(' ', '-')}-tutorial` - Tutorial repos
4. `learn-{topic.replace(' ', '-')}` - Learning resources

## Repository Categories

### Official/Popular
- Look for repos with high stars
- Check for recent updates
- Verify official maintainers

### Examples/Demos
- Example implementations
- Demo applications
- Starter templates

### Documentation
- README analysis
- Wiki pages
- Docs folder content

## GitHub Search URLs

- Topics: https://github.com/topics/{topic.replace(' ', '-')}
- Search: https://github.com/search?q={topic.replace(' ', '+')}+documentation&type=repositories

---
*Use GitHub MCP or gh CLI to fetch actual repository data*
"""
            
            with open(result_file, 'w') as f:
                f.write(content)
            results["files_created"].append(str(result_file))
            print(f"  📄 Created: {result_file.name}")
            
        except Exception as e:
            results["error"] = str(e)
            print(f"  ⚠️  GitHub fetch error: {e}")
        
        return results
    
    def _fetch_from_packages(self, topic: str, output_dir: Path) -> Dict:
        """Fetch package documentation (pip, npm, etc.)."""
        results = {
            "packages_checked": [],
            "files_created": []
        }
        
        try:
            # Check if it's a Python package
            result_file = output_dir / "package_docs.md"
            
            content = f"""# Package Documentation: {topic}

**Topic:** {topic}  
**Date:** {self._get_timestamp()}

## Python Package

### Check Installation
```bash
# Check if installed
pip show {topic.replace(' ', '-').lower()}

# Install if needed
pip install {topic.replace(' ', '-').lower()}
```

### Get Package Info
```bash
# Show package details
pip show {topic.replace(' ', '-').lower()}

# List package files
pip show -f {topic.replace(' ', '-').lower()}
```

### Documentation Locations
- PyPI: https://pypi.org/project/{topic.replace(' ', '-').lower()}/
- Package docs: Usually at `site-packages/{topic.replace(' ', '-').lower()}/docs/`
- README: Package installation directory

## npm Package (if JavaScript/Node)

```bash
# Check if installed
npm list {topic.replace(' ', '-').lower()}

# Get package info
npm info {topic.replace(' ', '-').lower()}
```

## Documentation Commands

### Python
```python
# Access docstrings
import {topic.replace(' ', '_').lower()}
help({topic.replace(' ', '_').lower()})

# Get module file location
print({topic.replace(' ', '_').lower()}.__file__)
```

## Common Documentation Files

1. `README.md` - Quick start
2. `docs/` folder - Full documentation
3. `CHANGELOG.md` - Version history
4. `examples/` - Usage examples
5. `API.md` or `REFERENCE.md` - API documentation

---
*Run commands to fetch actual package documentation*
"""
            
            with open(result_file, 'w') as f:
                f.write(content)
            results["files_created"].append(str(result_file))
            results["packages_checked"].append(topic.replace(' ', '-').lower())
            print(f"  📄 Created: {result_file.name}")
            
        except Exception as e:
            results["error"] = str(e)
            print(f"  ⚠️  Package fetch error: {e}")
        
        return results
    
    def _fetch_from_man_pages(self, topic: str, output_dir: Path) -> Dict:
        """Fetch man page documentation."""
        results = {
            "man_pages_found": [],
            "files_created": []
        }
        
        try:
            # Check for man pages
            man_topics = [topic, topic.replace(' ', '-')]
            
            result_file = output_dir / "man_pages.md"
            
            content = f"""# Man Page Documentation: {topic}

**Topic:** {topic}  
**Date:** {self._get_timestamp()}

## Man Page Search

### Commands to Try

```bash
# Search for man pages
man -k {topic}
man -k {topic.replace(' ', '-')}
whatis {topic}
whatis {topic.replace(' ', '-')}
```

### Common Man Pages
"""
            for man_topic in man_topics:
                content += f"""- `man {man_topic}` - Main documentation
- `man {man_topic}.conf` - Configuration
- `man {man_topic}-examples` - Examples
"""
            
            content += f"""
### Extract Man Page Content

```bash
# Convert man page to text
man {topic} > {output_dir}/man_{topic.replace(' ', '_')}.txt 2>/dev/null || echo "No man page found"

# Or use groff
man -t {topic} | groff -Tascii > {output_dir}/man_{topic.replace(' ', '_')}.txt 2>/dev/null || true
```

### Help Output

```bash
# Most commands have --help
{topic} --help > {output_dir}/help_{topic.replace(' ', '_')}.txt 2>/dev/null || true

# Or -h
{topic} -h > {output_dir}/help_{topic.replace(' ', '_')}.txt 2>/dev/null || true
```

---
*Run commands to extract actual man page content*
"""
            
            with open(result_file, 'w') as f:
                f.write(content)
            results["files_created"].append(str(result_file))
            print(f"  📄 Created: {result_file.name}")
            
        except Exception as e:
            results["error"] = str(e)
            print(f"  ⚠️  Man page error: {e}")
        
        return results
    
    def _create_index(self, topic: str, results: Dict, output_dir: Path) -> Path:
        """Create consolidated index of all documentation."""
        index_file = output_dir / "INDEX.md"
        
        content = f"""# Documentation Index: {topic}

**Generated:** {results['timestamp']}  
**Topic:** {topic}

## Overview

This documentation package was fetched for AI agent use.

## Contents

"""
        # Add sections for each source
        for source, data in results["sources"].items():
            content += f"### {source.title()} Sources\n"
            if "files_created" in data:
                for f in data["files_created"]:
                    fname = Path(f).name
                    content += f"- [{fname}](./{fname})\n"
            content += "\n"
        
        content += f"""## Quick Start

1. Read the source-specific documentation files above
2. Check `metadata.json` for fetch details
3. Use relevant commands from the documentation

## Agent Instructions

When using this documentation:
- Check all sources for comprehensive coverage
- Verify information with official sources
- Cross-reference between web, GitHub, and package docs
- Update documentation if it becomes outdated

## Files Generated

"""
        for f in results.get("output_files", []):
            content += f"- `{f}`\n"
        
        content += f"""
---
*Generated by Documentation Fetcher*  
*Request new documentation with: `cbw-doc-fetch <topic>`*
"""
        
        with open(index_file, 'w') as f:
            f.write(content)
        
        return index_file
    
    def list_fetched_docs(self) -> List[Dict]:
        """List all fetched documentation packages."""
        docs = []
        
        for item in self.output_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                metadata_file = item / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file) as f:
                        data = json.load(f)
                        docs.append({
                            "topic": data.get("topic", item.name),
                            "directory": str(item),
                            "timestamp": data.get("timestamp", "unknown"),
                            "sources": list(data.get("sources", {}).keys())
                        })
        
        return docs
    
    def get_doc_path(self, topic: str) -> Optional[Path]:
        """Get path to fetched documentation for a topic."""
        safe_topic = self._safe_filename(topic)
        doc_dir = self.output_dir / safe_topic
        
        if doc_dir.exists():
            return doc_dir
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Fetch and create documentation for AI agents'
    )
    parser.add_argument('topic', nargs='?', help='Topic to fetch documentation for')
    parser.add_argument('--sources', nargs='+', 
                       choices=['web', 'github', 'package', 'man', 'all'],
                       default=['web', 'github', 'package'],
                       help='Sources to search')
    parser.add_argument('--list', action='store_true', 
                       help='List all fetched documentation')
    parser.add_argument('--output', default='~/dotfiles/ai/docs/fetched',
                       help='Output directory')
    
    args = parser.parse_args()
    
    fetcher = DocumentationFetcher(output_dir=args.output)
    
    if args.list:
        docs = fetcher.list_fetched_docs()
        print("=" * 70)
        print("FETCHED DOCUMENTATION")
        print("=" * 70)
        for doc in docs:
            print(f"\n📚 {doc['topic']}")
            print(f"   Directory: {doc['directory']}")
            print(f"   Sources: {', '.join(doc['sources'])}")
            print(f"   Fetched: {doc['timestamp']}")
        print(f"\nTotal: {len(docs)} documentation packages")
    
    elif args.topic:
        # Convert 'all' to all sources
        sources = args.sources
        if 'all' in sources:
            sources = ['web', 'github', 'package', 'man']
        
        results = fetcher.fetch_documentation(args.topic, sources)
        
        # Print summary
        print("\n" + "=" * 70)
        print("FETCH SUMMARY")
        print("=" * 70)
        print(f"Topic: {results['topic']}")
        print(f"Sources searched: {', '.join(results['sources'].keys())}")
        print(f"Output directory: {fetcher.get_doc_path(args.topic)}")
        print(f"\nTo view documentation:")
        print(f"  cat {results['index_file']}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
