#!/usr/bin/env python3
"""
Agent Task Tracker - Track and manage AI agent tasks and TODOs
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path
sys.path.insert(0, '/home/cbwinslow/dotfiles/ai/skills')

from unified_memory.queries import search_files_content


class TaskTracker:
    """Track tasks from TODOs, FIXMEs, and comments in code."""
    
    def __init__(self, base_path='~/dotfiles'):
        self.base_path = Path(base_path).expanduser()
        self.tasks_file = self.base_path / 'ai' / 'TASKS.json'
        self.tasks_file.parent.mkdir(parents=True, exist_ok=True)
    
    def scan_for_todos(self) -> list:
        """Scan all files for TODO, FIXME, XXX comments."""
        todos = []
        
        # Search patterns
        patterns = [
            (r'TODO[:\s]+(.+)$', 'TODO'),
            (r'FIXME[:\s]+(.+)$', 'FIXME'),
            (r'XXX[:\s]+(.+)$', 'XXX'),
            (r'HACK[:\s]+(.+)$', 'HACK'),
            (r'NOTE[:\s]+(.+)$', 'NOTE'),
        ]
        
        for pattern, category in patterns:
            results = search_files_content(pattern, max_results=50)
            for r in results:
                text = r.get('chunk_text', '')
                lines = text.split('\n')
                for line in lines:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        todos.append({
                            'file': r['file_path'],
                            'line': r.get('line_start', 0),
                            'category': category,
                            'task': match.group(1).strip(),
                            'context': line.strip(),
                            'found_at': datetime.now().isoformat()
                        })
        
        return todos
    
    def scan_for_incomplete(self) -> list:
        """Find incomplete implementations."""
        incomplete = []
        
        # Search for incomplete patterns
        patterns = [
            (r'(pass|# TODO|NotImplemented)', 'Python incomplete'),
            (r'(# shellcheck disable|# FIXME)', 'Shell incomplete'),
        ]
        
        for pattern, desc in patterns:
            results = search_files_content(pattern, max_results=30)
            for r in results:
                incomplete.append({
                    'file': r['file_path'],
                    'type': desc,
                    'context': r.get('chunk_text', '')[:100],
                    'found_at': datetime.now().isoformat()
                })
        
        return incomplete
    
    def load_tasks(self) -> dict:
        """Load existing tasks from JSON file."""
        if self.tasks_file.exists():
            with open(self.tasks_file, 'r') as f:
                return json.load(f)
        return {'tasks': [], 'archived': [], 'version': '1.0'}
    
    def save_tasks(self, data: dict):
        """Save tasks to JSON file."""
        with open(self.tasks_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_task(self, task: dict):
        """Add a new task."""
        data = self.load_tasks()
        
        # Check for duplicates
        existing = [t['task'] for t in data['tasks']]
        if task['task'] not in existing:
            task['id'] = f"task_{len(data['tasks']) + 1}"
            task['status'] = 'pending'
            task['created_at'] = datetime.now().isoformat()
            data['tasks'].append(task)
            self.save_tasks(data)
            print(f"Added task: {task['task'][:60]}")
        else:
            print(f"Task already exists: {task['task'][:60]}")
    
    def complete_task(self, task_id: str):
        """Mark a task as complete."""
        data = self.load_tasks()
        
        for task in data['tasks']:
            if task['id'] == task_id:
                task['status'] = 'completed'
                task['completed_at'] = datetime.now().isoformat()
                data['archived'].append(task)
                data['tasks'].remove(task)
                self.save_tasks(data)
                print(f"Completed: {task['task'][:60]}")
                return
        
        print(f"Task not found: {task_id}")
    
    def list_tasks(self, status='all', category=None) -> list:
        """List tasks with optional filtering."""
        data = self.load_tasks()
        tasks = data['tasks']
        
        if status != 'all':
            tasks = [t for t in tasks if t['status'] == status]
        
        if category:
            tasks = [t for t in tasks if t.get('category') == category]
        
        return tasks
    
    def scan_and_update(self):
        """Scan code for TODOs and update the task list."""
        print("Scanning for TODOs, FIXMEs, and tasks...")
        
        todos = self.scan_for_todos()
        incomplete = self.scan_for_incomplete()
        
        print(f"Found {len(todos)} TODOs/FIXMEs")
        print(f"Found {len(incomplete)} incomplete implementations")
        
        # Add new todos as tasks
        added = 0
        for todo in todos:
            self.add_task(todo)
            added += 1
        
        print(f"\nUpdated task list. Run 'cbw-tasks --list' to view.")
    
    def report(self):
        """Generate a task report."""
        data = self.load_tasks()
        
        print("=" * 70)
        print("AGENT TASK TRACKER REPORT")
        print("=" * 70)
        
        pending = [t for t in data['tasks'] if t['status'] == 'pending']
        completed = data['archived']
        
        print(f"\n📋 PENDING TASKS ({len(pending)})")
        print("-" * 70)
        
        # Group by category
        by_category = {}
        for task in pending:
            cat = task.get('category', 'UNKNOWN')
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(task)
        
        for cat, tasks in sorted(by_category.items()):
            print(f"\n  [{cat}] {len(tasks)} tasks")
            for t in tasks[:5]:
                print(f"    - {t['task'][:50]}")
                print(f"      File: {t['file']}:{t.get('line', 0)}")
            if len(tasks) > 5:
                print(f"    ... and {len(tasks) - 5} more")
        
        print(f"\n✅ COMPLETED TASKS ({len(completed)})")
        print("-" * 70)
        print(f"  {len(completed)} tasks completed and archived")
        
        print("\n" + "=" * 70)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Agent Task Tracker')
    parser.add_argument('--scan', action='store_true', help='Scan code for TODOs')
    parser.add_argument('--list', action='store_true', help='List pending tasks')
    parser.add_argument('--complete', type=str, help='Mark task as complete by ID')
    parser.add_argument('--report', action='store_true', help='Generate full report')
    parser.add_argument('--add', type=str, help='Add manual task')
    parser.add_argument('--category', type=str, default='MANUAL', help='Task category')
    args = parser.parse_args()
    
    tracker = TaskTracker()
    
    if args.scan:
        tracker.scan_and_update()
    
    elif args.list:
        tasks = tracker.list_tasks()
        print(f"\n📋 Pending Tasks ({len(tasks)})")
        print("=" * 70)
        for t in tasks:
            print(f"\n[{t['id']}] [{t.get('category', 'UNKNOWN')}]")
            print(f"  {t['task'][:60]}")
            print(f"  File: {t['file']}")
    
    elif args.complete:
        tracker.complete_task(args.complete)
    
    elif args.add:
        tracker.add_task({
            'task': args.add,
            'category': args.category,
            'file': 'manual',
            'line': 0
        })
    
    elif args.report:
        tracker.report()
    
    else:
        tracker.report()


if __name__ == '__main__':
    main()
