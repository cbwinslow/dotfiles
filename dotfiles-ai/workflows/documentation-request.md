---
description: Request and manage documentation for AI agents
tags: [documentation, research, knowledge, workflow]
---

# Documentation Request Workflow

## Purpose
Standard workflow for AI agents to request, fetch, and manage documentation on any topic.

## When to Use
- Agent encounters unfamiliar technology
- Need reference materials for implementation
- Researching best practices
- Learning new tools or frameworks
- Building knowledge base

## Workflow Steps

### Step 1: Identify Documentation Need

**Trigger:** Agent realizes it needs documentation

```python
# Example: Agent working with unfamiliar technology
def check_documentation_need(topic: str) -> bool:
    """Check if documentation exists and is fresh."""
    doc_path = Path(f"~/dotfiles/ai/docs/fetched/{topic}")
    
    if not doc_path.exists():
        return True  # Need to fetch
    
    # Check age
    metadata_file = doc_path / "metadata.json"
    if metadata_file.exists():
        with open(metadata_file) as f:
            data = json.load(f)
            fetch_date = datetime.fromisoformat(data['timestamp'])
            age_days = (datetime.now() - fetch_date).days
            
            if age_days > 30:  # Older than 30 days
                return True  # Should refresh
    
    return False
```

### Step 2: Request Documentation

**Action:** Fetch documentation using doc_fetcher skill

```bash
# Fetch for specific topic
python3 ~/dotfiles/ai/scripts/cbw_doc_fetch.py "kubernetes ingress"

# Or with shell alias
cbw-doc-fetch "kubernetes ingress"
```

**Alternative:** Use Python API

```python
from doc_fetcher import DocumentationFetcher

fetcher = DocumentationFetcher()
results = fetcher.fetch_documentation("kubernetes ingress")

print(f"Documentation saved to: {results['index_file']}")
```

### Step 3: Review Fetched Documentation

**Action:** Examine what was fetched

```bash
# View index
cat ~/dotfiles/ai/docs/fetched/kubernetes_ingress/INDEX.md

# List all files
ls -la ~/dotfiles/ai/docs/fetched/kubernetes_ingress/

# Check metadata
cat ~/dotfiles/ai/docs/fetched/kubernetes_ingress/metadata.json
```

### Step 4: Extract Relevant Information

**Action:** Read and understand the documentation

```python
def read_documentation(topic: str) -> str:
    """Read documentation for a topic."""
    safe_topic = topic.replace(' ', '_').lower()
    doc_dir = Path(f"~/dotfiles/ai/docs/fetched/{safe_topic}").expanduser()
    
    if not doc_dir.exists():
        return None
    
    # Read index
    index_file = doc_dir / "INDEX.md"
    if index_file.exists():
        with open(index_file) as f:
            return f.read()
    
    return None

# Usage
docs = read_documentation("kubernetes ingress")
# Process and extract key information
```

### Step 5: Save to Agent Memory

**Action:** Store documentation reference for future use

```bash
# Save location to Letta memory
letta-memory-cli memory save \
  --agent my_agent \
  --content "Documentation for kubernetes ingress: ~/dotfiles/ai/docs/fetched/kubernetes_ingress/" \
  --type core \
  --tags "docs,kubernetes,ingress,reference"

# Save key findings
letta-memory-cli memory save \
  --agent my_agent \
  --content "Key finding: Use nginx-ingress controller for production" \
  --type core \
  --tags "kubernetes,ingress,best-practice"
```

### Step 6: Apply Knowledge

**Action:** Use documentation in agent work

```python
# Example: Using fetched docs to implement
class K8sIngressSetup:
    def __init__(self):
        self.docs = read_documentation("kubernetes ingress")
    
    def create_ingress(self, service_name: str):
        """Create ingress based on documentation."""
        # Reference best practices from docs
        # Implement according to documentation
        pass
```

## Complete Automation

### Auto-Documentation Agent

```python
#!/usr/bin/env python3
"""Auto-fetch documentation for topics agents encounter."""

import sys
from pathlib import Path
sys.path.insert(0, '/home/cbwinslow/dotfiles/ai/scripts')

from cbw_doc_fetch import DocumentationFetcher

def auto_fetch_on_demand(topic: str, agent_name: str):
    """Automatically fetch documentation when needed."""
    fetcher = DocumentationFetcher()
    
    # Check if already exists
    doc_path = fetcher.get_doc_path(topic)
    
    if doc_path:
        print(f"Documentation already exists: {doc_path}")
        return doc_path
    
    # Fetch new documentation
    print(f"Fetching documentation for: {topic}")
    results = fetcher.fetch_documentation(topic)
    
    # Save reference to agent memory
    # (Integration with letta_memory skill)
    print(f"Documentation fetched: {results['index_file']}")
    
    return results['index_file']

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: auto_fetch.py <topic> <agent_name>")
        sys.exit(1)
    
    topic = sys.argv[1]
    agent_name = sys.argv[2]
    
    auto_fetch_on_demand(topic, agent_name)
```

## Integration Patterns

### Pattern 1: On-Demand Fetching

```python
# Agent code
class MyAgent:
    def process_request(self, request: str):
        # Detect unknown topics
        topics = self.extract_topics(request)
        
        for topic in topics:
            if not self.has_documentation(topic):
                self.fetch_documentation(topic)
        
        # Now process with full knowledge
        return self.solve_with_docs(request, topics)
```

### Pattern 2: Pre-Fetching Common Topics

```bash
#!/bin/bash
# prefetch_common.sh

# List of common topics agents need
COMMON_TOPICS=(
  "docker compose"
  "kubernetes"
  "terraform"
  "ansible"
  "python asyncio"
  "fastapi"
  "postgresql"
  "redis"
  "nginx"
  "prometheus"
)

for topic in "${COMMON_TOPICS[@]}"; do
  echo "Prefetching: $topic"
  python3 ~/dotfiles/ai/scripts/cbw_doc_fetch.py "$topic" 2>/dev/null || true
done
```

### Pattern 3: Documentation Verification

```python
def verify_documentation(topic: str) -> bool:
    """Verify documentation is helpful."""
    doc_path = Path(f"~/dotfiles/ai/docs/fetched/{topic}")
    
    if not doc_path.exists():
        return False
    
    # Check files exist
    required_files = ['INDEX.md', 'metadata.json']
    for f in required_files:
        if not (doc_path / f).exists():
            return False
    
    # Check content quality
    index_file = doc_path / 'INDEX.md'
    with open(index_file) as f:
        content = f.read()
        if len(content) < 100:  # Too short
            return False
    
    return True
```

## Quality Checklist

After fetching documentation, verify:

- [ ] INDEX.md exists and is readable
- [ ] Multiple sources were searched
- [ ] Content is relevant to topic
- [ ] No major errors in metadata
- [ ] Files are properly structured
- [ ] Information is current
- [ ] Key concepts are covered

## Error Handling

### No Documentation Found

```python
if not results['sources']:
    # Try alternative search terms
    alt_topic = topic.replace(' ', '-')
    results = fetcher.fetch_documentation(alt_topic)
```

### Partial Failures

```python
for source, data in results['sources'].items():
    if 'error' in data:
        print(f"Warning: {source} failed: {data['error']}")
        # Continue with other sources
```

## Related Workflows

- **research** - Deep research beyond documentation
- **knowledge** - Building knowledge base
- **memory-operations** - Storing doc references
- **cross-agent-coordination** - Sharing docs between agents

## Success Criteria

Documentation workflow successful when:
- ✅ Documentation fetched for requested topic
- ✅ INDEX.md provides clear overview
- ✅ Multiple sources provide coverage
- ✅ Agent can understand and apply knowledge
- ✅ Documentation reference saved to memory
- ✅ Future agents can find and use the docs

## Metrics

Track documentation effectiveness:
- Number of topics documented
- Age of documentation
- Usage frequency
- Agent satisfaction with docs
- Time saved by having docs available
