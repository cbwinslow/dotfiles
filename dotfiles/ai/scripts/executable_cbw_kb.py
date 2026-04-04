#!/usr/bin/env python3
"""
CBW Knowledge Base - Query your indexed data with natural language
"""

import os
import sys
import argparse
sys.path.insert(0, '/home/cbwinslow/dotfiles/ai/skills')

from unified_memory.queries import (
    search_files_content, 
    find_similar_code,
    get_python_files,
    get_shell_files,
    get_config_files,
    quick_search
)


class KnowledgeBase:
    """Query indexed data with natural language."""
    
    def __init__(self):
        self.query_handlers = {
            'how do i': self._handle_how_to,
            'how to': self._handle_how_to,
            'what is': self._handle_what_is,
            'where is': self._handle_where_is,
            'find': self._handle_find,
            'show me': self._handle_show_me,
            'list': self._handle_list,
            'example': self._handle_example,
        }
    
    def query(self, question: str) -> dict:
        """Process a natural language query."""
        question_lower = question.lower().strip()
        
        # Find matching handler
        for prefix, handler in self.query_handlers.items():
            if question_lower.startswith(prefix):
                return handler(question)
        
        # Default: semantic search
        return self._default_search(question)
    
    def _handle_how_to(self, question: str) -> dict:
        """Handle 'how do I' questions."""
        # Extract the task
        task = question.lower()
        for prefix in ['how do i ', 'how to ']:
            task = task.replace(prefix, '')
        
        # Search for relevant patterns
        results = search_files_content(task, max_results=10)
        
        # Find code examples
        examples = []
        for r in results:
            text = r.get('chunk_text', '')
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                # Look for command lines
                if line and not line.startswith('#'):
                    if any(cmd in line for cmd in ['psql', 'curl', 'docker', 'python', 'npm', 'pip']):
                        if len(line) < 150:
                            examples.append({
                                'command': line,
                                'source': r['file_path'],
                                'context': text[:200]
                            })
                            break
        
        return {
            'type': 'how_to',
            'question': question,
            'task': task,
            'examples': examples[:5],
            'sources': list(set(r['file_path'] for r in results))[:5]
        }
    
    def _handle_what_is(self, question: str) -> dict:
        """Handle 'what is' questions."""
        # Extract the term
        term = question.lower().replace('what is ', '').replace('what are ', '').strip()
        
        # Search for definitions/explanations
        results = search_files_content(term, max_results=10)
        
        # Look for markdown documentation
        explanations = []
        for r in results:
            if r['file_path'].endswith('.md'):
                text = r.get('chunk_text', '')
                if len(text) > 50:
                    explanations.append({
                        'text': text[:300],
                        'source': r['file_path']
                    })
        
        return {
            'type': 'definition',
            'term': term,
            'explanations': explanations[:3],
            'related_files': list(set(r['file_path'] for r in results))[:5]
        }
    
    def _handle_where_is(self, question: str) -> dict:
        """Handle 'where is' questions."""
        # Extract what we're looking for
        term = question.lower().replace('where is ', '').replace('where are ', '').strip()
        
        # Search across all files
        results = search_files_content(term, max_results=20)
        
        # Group by directory
        locations = {}
        for r in results:
            path = r['file_path']
            dir_path = os.path.dirname(path)
            if dir_path not in locations:
                locations[dir_path] = []
            locations[dir_path].append(os.path.basename(path))
        
        return {
            'type': 'location',
            'term': term,
            'locations': {k: v[:5] for k, v in locations.items()},
            'total_files': len(set(r['file_path'] for r in results))
        }
    
    def _handle_find(self, question: str) -> dict:
        """Handle 'find' questions."""
        # Extract search term
        term = question.lower().replace('find ', '').strip()
        
        # Use semantic search
        results = search_files_content(term, max_results=15)
        
        return {
            'type': 'search',
            'term': term,
            'results': [
                {
                    'file': r['file_path'],
                    'line': r.get('line_start', 0),
                    'preview': r.get('chunk_text', '')[:100]
                }
                for r in results[:10]
            ],
            'total': len(results)
        }
    
    def _handle_show_me(self, question: str) -> dict:
        """Handle 'show me' questions."""
        term = question.lower().replace('show me ', '').strip()
        
        # Find code examples
        results = find_similar_code(term, max_results=10)
        
        return {
            'type': 'examples',
            'term': term,
            'examples': [
                {
                    'code': r.get('chunk_text', '')[:200],
                    'file': r['file_path'],
                    'language': r.get('file_path', '').split('.')[-1] if '.' in r['file_path'] else 'unknown'
                }
                for r in results[:5]
            ]
        }
    
    def _handle_list(self, question: str) -> dict:
        """Handle 'list' questions."""
        term = question.lower().replace('list ', '').strip()
        
        # Determine what to list
        if 'script' in term or 'shell' in term:
            files = get_shell_files(limit=30)
            file_type = 'shell scripts'
        elif 'python' in term or '.py' in term:
            files = get_python_files(limit=30)
            file_type = 'Python files'
        elif 'config' in term:
            files = get_config_files(limit=30)
            file_type = 'config files'
        else:
            # Search for the term
            results = search_files_content(term, max_results=30)
            files = [{'file_path': r['file_path'], 'file_name': os.path.basename(r['file_path'])} for r in results]
            file_type = f'files matching "{term}"'
        
        return {
            'type': 'list',
            'file_type': file_type,
            'files': [
                {
                    'name': f['file_name'],
                    'path': f['file_path']
                }
                for f in files[:20]
            ],
            'total': len(files)
        }
    
    def _handle_example(self, question: str) -> dict:
        """Handle 'example' questions."""
        term = question.lower().replace('example of ', '').replace('example ', '').strip()
        
        # Find code examples
        results = search_files_content(term, max_results=15)
        
        examples = []
        for r in results:
            text = r.get('chunk_text', '')
            # Extract code blocks or command lines
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line.startswith('$') or line.startswith('./') or 
                           any(cmd in line for cmd in ['def ', 'function', 'class ', 'if ', 'for '])):
                    if len(line) < 120:
                        examples.append({
                            'code': line,
                            'file': r['file_path'],
                            'full_context': text[:150]
                        })
                        break
        
        return {
            'type': 'example',
            'term': term,
            'examples': examples[:8]
        }
    
    def _default_search(self, question: str) -> dict:
        """Default semantic search."""
        results = quick_search(question)
        
        return {
            'type': 'semantic_search',
            'query': question,
            'results': [
                {
                    'file': r['file_path'],
                    'preview': r.get('chunk_text', '')[:150],
                    'line': r.get('line_start', 0)
                }
                for r in results[:10]
            ],
            'total': len(results)
        }
    
    def format_response(self, result: dict) -> str:
        """Format the response for display."""
        response = []
        
        if result['type'] == 'how_to':
            response.append(f"\n💡 How to: {result['task']}")
            response.append("=" * 60)
            if result['examples']:
                response.append("\nExamples from your scripts:")
                for i, ex in enumerate(result['examples'][:5], 1):
                    response.append(f"\n{i}. {ex['command'][:80]}")
                    response.append(f"   From: {ex['source']}")
            else:
                response.append("\nNo direct examples found. Try searching for related terms.")
        
        elif result['type'] == 'definition':
            response.append(f"\n📖 What is: {result['term']}")
            response.append("=" * 60)
            if result['explanations']:
                for exp in result['explanations'][:3]:
                    response.append(f"\n{exp['text']}")
                    response.append(f"   Source: {exp['source']}")
            else:
                response.append("\nFound in these files:")
                for f in result['related_files'][:5]:
                    response.append(f"  - {f}")
        
        elif result['type'] == 'location':
            response.append(f"\n📍 Where is: {result['term']}")
            response.append("=" * 60)
            response.append(f"\nFound in {result['total_files']} files:")
            for dir_path, files in result['locations'].items():
                response.append(f"\n  {dir_path}/")
                for f in files[:3]:
                    response.append(f"    - {f}")
        
        elif result['type'] == 'search':
            response.append(f"\n🔍 Search: {result['term']}")
            response.append("=" * 60)
            response.append(f"Found {result['total']} matches:")
            for r in result['results'][:10]:
                response.append(f"\n  {r['file']}:{r['line']}")
                response.append(f"    {r['preview'][:70]}...")
        
        elif result['type'] == 'examples':
            response.append(f"\n💻 Examples of: {result['term']}")
            response.append("=" * 60)
            for ex in result['examples']:
                response.append(f"\n[{ex['language']}] {ex['file']}")
                response.append(f"```")
                response.append(ex['code'])
                response.append("```")
        
        elif result['type'] == 'list':
            response.append(f"\n📋 {result['file_type'].title()}")
            response.append("=" * 60)
            for f in result['files'][:15]:
                response.append(f"  - {f['name']}")
            if result['total'] > 15:
                response.append(f"\n  ... and {result['total'] - 15} more")
        
        else:
            response.append(f"\n🔎 Results for: {result['query']}")
            response.append("=" * 60)
            for r in result['results'][:10]:
                response.append(f"\n  {r['file']}")
                response.append(f"    {r['preview'][:60]}...")
        
        return '\n'.join(response)


def main():
    parser = argparse.ArgumentParser(description='CBW Knowledge Base')
    parser.add_argument('query', nargs='?', help='Natural language query')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    args = parser.parse_args()
    
    kb = KnowledgeBase()
    
    if args.interactive:
        print("\n🧠 CBW Knowledge Base")
        print("Ask me about your indexed files. Type 'quit' to exit.")
        print("Examples:")
        print("  - 'how do I backup postgresql'")
        print("  - 'what is cbw_rag'")
        print("  - 'find docker compose examples'")
        print("  - 'list shell scripts'")
        print()
        
        while True:
            try:
                question = input("❓ ").strip()
                if question.lower() in ['quit', 'exit', 'q']:
                    break
                if not question:
                    continue
                
                result = kb.query(question)
                print(kb.format_response(result))
                print()
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
        
        print("\nGoodbye!")
    
    elif args.query:
        result = kb.query(args.query)
        print(kb.format_response(result))
    
    else:
        print("CBW Knowledge Base")
        print("Usage:")
        print("  cbw-kb 'how do I backup postgresql'")
        print("  cbw-kb --interactive")


if __name__ == '__main__':
    main()
