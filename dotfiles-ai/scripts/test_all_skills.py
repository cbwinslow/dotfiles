#!/usr/bin/env python3
"""
Comprehensive Skill Test Suite - Test all AI agent skills
"""

import os
import sys
import subprocess
import json
from pathlib import Path

# Add skills path
sys.path.insert(0, '/home/cbwinslow/dotfiles/ai/skills')
sys.path.insert(0, '/home/cbwinslow/dotfiles/ai/scripts')

class SkillTestSuite:
    """Test all available skills."""
    
    def __init__(self):
        self.results = {
            "passed": [],
            "failed": [],
            "skipped": []
        }
        self.skills_dir = Path("/home/cbwinslow/dotfiles/ai/skills")
        self.scripts_dir = Path("/home/cbwinslow/dotfiles/ai/scripts")
    
    def run_all_tests(self):
        """Run all skill tests."""
        print("=" * 70)
        print("COMPREHENSIVE SKILL TEST SUITE")
        print("=" * 70)
        
        # Test skill discovery
        self.test_skill_discovery()
        
        # Test debug skill
        self.test_debug_skill()
        
        # Test analyze skill
        self.test_analyze_skill()
        
        # Test visualize skill
        self.test_visualize_skill()
        
        # Test doc_fetcher skill
        self.test_doc_fetcher_skill()
        
        # Test Letta skills (if server available)
        self.test_letta_skills()
        
        # Test shell integration
        self.test_shell_integration()
        
        # Print summary
        self.print_summary()
    
    def test_skill_discovery(self):
        """Test skill discovery tool."""
        print("\n--- Testing Skill Discovery ---")
        try:
            result = subprocess.run(
                ['python3', str(self.scripts_dir / 'cbw_skills.py'), '--list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and 'skills available' in result.stdout:
                self.results["passed"].append("skill_discovery")
                print("✅ Skill discovery working")
            else:
                self.results["failed"].append(("skill_discovery", "Tool not responding"))
                print("❌ Skill discovery failed")
        except Exception as e:
            self.results["failed"].append(("skill_discovery", str(e)))
            print(f"❌ Skill discovery error: {e}")
    
    def test_debug_skill(self):
        """Test debug skill with a sample script."""
        print("\n--- Testing Debug Skill ---")
        try:
            # Create a test script with issues
            test_script = "/tmp/test_debug_script.sh"
            with open(test_script, 'w') as f:
                f.write("#!/bin/bash\necho $1\n")  # Missing quotes
            
            result = subprocess.run(
                ['python3', str(self.scripts_dir / 'cbw_debug.py'), test_script],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            os.remove(test_script)
            
            if result.returncode == 0:
                self.results["passed"].append("debug")
                print("✅ Debug skill working")
            else:
                self.results["failed"].append(("debug", "Non-zero exit"))
                print("❌ Debug skill failed")
        except Exception as e:
            self.results["failed"].append(("debug", str(e)))
            print(f"❌ Debug skill error: {e}")
    
    def test_analyze_skill(self):
        """Test analyze skill."""
        print("\n--- Testing Analyze Skill ---")
        try:
            result = subprocess.run(
                ['python3', str(self.scripts_dir / 'cbw_analyze.py'), 
                 '--path', str(self.scripts_dir), '--structure'],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0 and 'Structure' in result.stdout:
                self.results["passed"].append("analyze")
                print("✅ Analyze skill working")
            else:
                self.results["failed"].append(("analyze", "No structure output"))
                print("❌ Analyze skill failed")
        except Exception as e:
            self.results["failed"].append(("analyze", str(e)))
            print(f"❌ Analyze skill error: {e}")
    
    def test_visualize_skill(self):
        """Test visualize skill."""
        print("\n--- Testing Visualize Skill ---")
        try:
            result = subprocess.run(
                ['python3', str(self.scripts_dir / 'cbw_visualize.py'),
                 '--path', str(self.scripts_dir), '--tree'],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                self.results["passed"].append("visualize")
                print("✅ Visualize skill working")
            else:
                self.results["failed"].append(("visualize", "Non-zero exit"))
                print("❌ Visualize skill failed")
        except Exception as e:
            self.results["failed"].append(("visualize", str(e)))
            print(f"❌ Visualize skill error: {e}")
    
    def test_doc_fetcher_skill(self):
        """Test doc_fetcher skill."""
        print("\n--- Testing Doc Fetcher Skill ---")
        try:
            result = subprocess.run(
                ['python3', str(self.scripts_dir / 'cbw_doc_fetch.py'), '--list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.results["passed"].append("doc_fetcher")
                print("✅ Doc fetcher skill working")
            else:
                self.results["failed"].append(("doc_fetcher", "Non-zero exit"))
                print("❌ Doc fetcher skill failed")
        except Exception as e:
            self.results["failed"].append(("doc_fetcher", str(e)))
            print(f"❌ Doc fetcher error: {e}")
    
    def test_letta_skills(self):
        """Test Letta memory skills."""
        print("\n--- Testing Letta Skills ---")
        
        # Check if Letta server is available
        try:
            result = subprocess.run(
                ['python3', str(self.scripts_dir / 'cbw_letta.py'), 'health'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.results["passed"].append("letta_health")
                print("✅ Letta health check working")
                
                # Test agent list
                result = subprocess.run(
                    ['python3', str(self.scripts_dir / 'cbw_letta.py'), 'agent', 'list'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    self.results["passed"].append("letta_agent_list")
                    print("✅ Letta agent list working")
                else:
                    self.results["skipped"].append(("letta_agent_list", "No agents or error"))
                    print("⚠️  Letta agent list skipped")
            else:
                self.results["skipped"].append(("letta_skills", "Server not available"))
                print("⚠️  Letta skills skipped - server not available")
        except Exception as e:
            self.results["skipped"].append(("letta_skills", str(e)))
            print(f"⚠️  Letta skills skipped - {e}")
    
    def test_shell_integration(self):
        """Test shell integration functions."""
        print("\n--- Testing Shell Integration ---")
        try:
            # Check if shell integration file exists and is valid bash
            result = subprocess.run(
                ['bash', '-n', str(self.scripts_dir / 'cbw-shell-integration.sh')],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.results["passed"].append("shell_integration")
                print("✅ Shell integration valid")
            else:
                self.results["failed"].append(("shell_integration", "Bash syntax error"))
                print("❌ Shell integration has syntax errors")
        except Exception as e:
            self.results["failed"].append(("shell_integration", str(e)))
            print(f"❌ Shell integration error: {e}")
    
    def test_skill_md_files(self):
        """Verify all skills have SKILL.md files."""
        print("\n--- Testing SKILL.md Files ---")
        
        skills_with_md = []
        skills_without_md = []
        
        for item in self.skills_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                skill_md = item / 'SKILL.md'
                if skill_md.exists():
                    skills_with_md.append(item.name)
                else:
                    skills_without_md.append(item.name)
        
        print(f"Skills with SKILL.md: {len(skills_with_md)}")
        if skills_without_md:
            print(f"Skills missing SKILL.md: {skills_without_md}")
            self.results["failed"].append(("skill_md_files", f"Missing: {skills_without_md}"))
        else:
            self.results["passed"].append("skill_md_files")
            print("✅ All skills have SKILL.md")
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"✅ Passed: {len(self.results['passed'])}")
        print(f"❌ Failed: {len(self.results['failed'])}")
        print(f"⚠️  Skipped: {len(self.results['skipped'])}")
        
        if self.results["failed"]:
            print("\nFailed Tests:")
            for test, error in self.results["failed"]:
                print(f"  - {test}: {error}")
        
        if self.results["skipped"]:
            print("\nSkipped Tests:")
            for test, reason in self.results["skipped"]:
                print(f"  - {test}: {reason}")
        
        total = len(self.results["passed"]) + len(self.results["failed"])
        if total > 0:
            success_rate = len(self.results["passed"]) / total * 100
            print(f"\nSuccess Rate: {success_rate:.1f}%")
        
        return len(self.results["failed"]) == 0


def main():
    suite = SkillTestSuite()
    suite.run_all_tests()


if __name__ == '__main__':
    main()
