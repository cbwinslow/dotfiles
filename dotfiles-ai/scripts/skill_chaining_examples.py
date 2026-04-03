#!/usr/bin/env python3
"""
Skill Chaining Examples - Show how to compose multiple skills
"""

import subprocess
import sys
from pathlib import Path

class SkillComposer:
    """Demonstrate skill composition patterns."""
    
    def __init__(self):
        self.scripts_dir = Path("/home/cbwinslow/dotfiles/ai/scripts")
    
    def chain_analyze_then_visualize(self, project_path):
        """
        Chain: analyze → visualize
        Analyze code, then visualize its structure.
        """
        print("=== Pattern: Analyze → Visualize ===")
        
        # Step 1: Analyze
        print("\n1. Analyzing codebase...")
        result = subprocess.run(
            ['python3', str(self.scripts_dir / 'cbw_analyze.py'),
             '--path', project_path, '--structure'],
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            print("❌ Analysis failed")
            return False
        
        # Step 2: Visualize (using analysis insights)
        print("\n2. Visualizing architecture...")
        result = subprocess.run(
            ['python3', str(self.scripts_dir / 'cbw_visualize.py'),
             '--path', project_path, '--mermaid'],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            print("✅ Analysis → Visualize chain complete")
            return True
        return False
    
    def chain_debug_then_analyze(self, script_path):
        """
        Chain: debug → analyze
        Debug a script, then analyze its structure.
        """
        print("\n=== Pattern: Debug → Analyze ===")
        
        # Step 1: Debug
        print(f"\n1. Debugging {script_path}...")
        result = subprocess.run(
            ['python3', str(self.scripts_dir / 'cbw_debug.py'), script_path],
            capture_output=True, text=True
        )
        
        # Step 2: Analyze (only if no critical errors)
        if 'error' not in result.stdout.lower():
            print("\n2. Analyzing structure...")
            result = subprocess.run(
                ['python3', str(self.scripts_dir / 'cbw_analyze.py'),
                 '--path', script_path, '--metrics'],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                print("✅ Debug → Analyze chain complete")
                return True
        else:
            print("⚠️  Critical errors found - fix before analyzing")
        
        return False
    
    def chain_multi_skill_refactor(self, project_path):
        """
        Chain: analyze → debug → visualize → [refactor]
        Complete refactoring workflow.
        """
        print("\n=== Pattern: Multi-Skill Refactor Chain ===")
        
        results = {}
        
        # Phase 1: Analyze
        print("\n[Phase 1] Analysis...")
        result = subprocess.run(
            ['python3', str(self.scripts_dir / 'cbw_analyze.py'),
             '--path', project_path, '--report'],
            capture_output=True, text=True
        )
        results['analysis'] = result.returncode == 0
        
        # Phase 2: Debug
        print("\n[Phase 2] Debugging...")
        # Find all scripts
        scripts = list(Path(project_path).glob('**/*.sh'))
        debug_ok = True
        for script in scripts[:5]:  # Limit to first 5
            result = subprocess.run(
                ['python3', str(self.scripts_dir / 'cbw_debug.py'), str(script)],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                debug_ok = False
        results['debug'] = debug_ok
        
        # Phase 3: Visualize
        print("\n[Phase 3] Visualization...")
        result = subprocess.run(
            ['python3', str(self.scripts_dir / 'cbw_visualize.py'),
             '--path', project_path, '--mermaid'],
            capture_output=True, text=True
        )
        results['visualize'] = result.returncode == 0
        
        # Summary
        print("\n[Results]")
        for phase, success in results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {phase}")
        
        return all(results.values())
    
    def chain_research_then_document(self, topic):
        """
        Chain: doc_fetcher → knowledge
        Research topic, then add to knowledge base.
        """
        print("\n=== Pattern: Research → Document ===")
        
        # Step 1: Fetch documentation
        print(f"\n1. Fetching docs for '{topic}'...")
        result = subprocess.run(
            ['python3', str(self.scripts_dir / 'cbw_doc_fetch.py'), topic],
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            print("❌ Doc fetch failed")
            return False
        
        # Step 2: Add to knowledge (would integrate with knowledge skill)
        print("\n2. Adding to knowledge base...")
        print("  (Would save to knowledge base)")
        
        print("✅ Research → Document chain complete")
        return True
    
    def chain_letta_workflow(self, agent_name):
        """
        Chain: letta_agents → letta_memory → letta_backup
        Complete Letta workflow.
        """
        print("\n=== Pattern: Letta Workflow Chain ===")
        
        # Step 1: Check agent exists
        print(f"\n1. Checking agent '{agent_name}'...")
        result = subprocess.run(
            ['python3', str(self.scripts_dir / 'cbw_letta.py'),
             'agent', 'list'],
            capture_output=True, text=True
        )
        
        if agent_name not in result.stdout:
            print(f"  Creating agent: {agent_name}")
            # Would create agent here
        
        # Step 2: Save memory
        print("\n2. Saving to memory...")
        print("  (Would save important context)")
        
        # Step 3: Backup
        print("\n3. Creating backup...")
        print("  (Would backup memories)")
        
        print("✅ Letta workflow chain complete")
        return True
    
    def demo_all_patterns(self):
        """Demonstrate all skill chaining patterns."""
        print("=" * 70)
        print("SKILL CHAINING DEMONSTRATIONS")
        print("=" * 70)
        
        # Pattern 1: Analyze → Visualize
        self.chain_analyze_then_visualize("/home/cbwinslow/dotfiles/ai/scripts")
        
        # Pattern 2: Debug → Analyze
        test_script = str(self.scripts_dir / 'cbw_debug.py')
        self.chain_debug_then_analyze(test_script)
        
        # Pattern 3: Multi-skill refactor
        self.chain_multi_skill_refactor("/home/cbwinslow/dotfiles/ai")
        
        # Pattern 4: Research → Document
        self.chain_research_then_document("docker compose")
        
        # Pattern 5: Letta workflow
        self.chain_letta_workflow("demo_agent")
        
        print("\n" + "=" * 70)
        print("All patterns demonstrated!")
        print("=" * 70)


def main():
    composer = SkillComposer()
    composer.demo_all_patterns()


if __name__ == '__main__':
    main()
