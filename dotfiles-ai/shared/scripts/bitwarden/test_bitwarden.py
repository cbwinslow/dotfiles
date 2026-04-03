#!/usr/bin/env python3
"""
Bitwarden Integration Test Script

Tests the complete Bitwarden integration for AI agents.
"""

import os
import json
import subprocess
import logging
import sys
import site
from pathlib import Path
from typing import Dict, Any, List

# Add tools directory to Python path
tools_dir = Path("/home/cbwinslow/dotfiles/ai/tools")
if tools_dir.exists():
    site.addsitedir(str(tools_dir))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BitwardenTester:
    """Tests Bitwarden integration components"""
    
    def __init__(self):
        self.base_path = Path("/home/cbwinslow/dotfiles/ai")
        self.skills_dir = self.base_path / "skills" / "integration" / "bitwarden"
        self.tools_dir = self.base_path / "tools" / "api_tools" / "bitwarden"
        self.scripts_dir = self.base_path / "scripts" / "bitwarden"
        
        # Test results
        self.results = {
            "bitwarden_cli": False,
            "session_token": False,
            "skill_definition": False,
            "tool_implementation": False,
            "scripts": False,
            "integration": False,
            "overall": False
        }
    
    def test_bitwarden_cli(self) -> bool:
        """Test if Bitwarden CLI is installed and working"""
        logger.info("Testing Bitwarden CLI installation...")
        
        try:
            # Check if bw command exists
            result = subprocess.run(
                ["bw", "--version"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"✓ Bitwarden CLI found: {result.stdout.strip()}")
                self.results["bitwarden_cli"] = True
                return True
            else:
                logger.warning("✗ Bitwarden CLI not found")
                return False
        
        except Exception as e:
            logger.error(f"✗ Error testing Bitwarden CLI: {e}")
            return False
    
    def test_session_token(self) -> bool:
        """Test if Bitwarden session token is available"""
        logger.info("Testing Bitwarden session token...")
        
        try:
            session_token = os.getenv("BW_SESSION")
            
            if session_token:
                logger.info("✓ BW_SESSION environment variable is set")
                self.results["session_token"] = True
                return True
            else:
                logger.warning("✗ BW_SESSION environment variable not set")
                return False
        
        except Exception as e:
            logger.error(f"✗ Error testing session token: {e}")
            return False
    
    def test_skill_definition(self) -> bool:
        """Test if skill definition exists and is valid"""
        logger.info("Testing skill definition...")
        
        try:
            skill_file = self.skills_dir / "SKILL.md"
            
            if skill_file.exists():
                logger.info("✓ Skill definition file exists")
                
                # Check if it contains required operations
                with open(skill_file, 'r') as f:
                    content = f.read()
                    required_ops = [
                        "get_api_key",
                        "populate_env_file",
                        "list_vaults",
                        "search_credentials",
                        "validate_configuration"
                    ]
                    
                    all_ops_found = all(op in content for op in required_ops)
                    
                    if all_ops_found:
                        logger.info("✓ All required operations defined")
                        self.results["skill_definition"] = True
                        return True
                    else:
                        logger.warning("✗ Some required operations missing")
                        return False
            else:
                logger.warning("✗ Skill definition file not found")
                return False
        
        except Exception as e:
            logger.error(f"✗ Error testing skill definition: {e}")
            return False
    
    def test_tool_implementation(self) -> bool:
        """Test if tool implementation exists and is valid"""
        logger.info("Testing tool implementation...")
        
        try:
            tool_file = self.tools_dir / "bitwarden_client.py"
            
            if tool_file.exists():
                logger.info("✓ Tool implementation file exists")
                
                # Check if it contains required functions
                with open(tool_file, 'r') as f:
                    content = f.read()
                    required_funcs = [
                        "get_api_key",
                        "populate_env_file",
                        "list_vaults",
                        "search_credentials",
                        "validate_configuration"
                    ]
                    
                    all_funcs_found = all(func in content for func in required_funcs)
                    
                    if all_funcs_found:
                        logger.info("✓ All required functions implemented")
                        self.results["tool_implementation"] = True
                        return True
                    else:
                        logger.warning("✗ Some required functions missing")
                        return False
            else:
                logger.warning("✗ Tool implementation file not found")
                return False
        
        except Exception as e:
            logger.error(f"✗ Error testing tool implementation: {e}")
            return False
    
    def test_scripts(self) -> bool:
        """Test if scripts exist and are executable"""
        logger.info("Testing scripts...")
        
        try:
            # Test setup script
            setup_script = self.scripts_dir / "setup_bitwarden.sh"
            if setup_script.exists() and os.access(setup_script, os.X_OK):
                logger.info("✓ Setup script exists and is executable")
            else:
                logger.warning("✗ Setup script missing or not executable")
                return False
            
            # Test skill wrapper
            wrapper_script = self.scripts_dir / "bitwarden_skill_wrapper.py"
            if wrapper_script.exists():
                logger.info("✓ Skill wrapper script exists")
            else:
                logger.warning("✗ Skill wrapper script not found")
                return False
            
            # Test example usage
            example_file = self.skills_dir / "example_usage.yaml"
            if example_file.exists():
                logger.info("✓ Example usage file exists")
            else:
                logger.warning("✗ Example usage file not found")
                return False
            
            self.results["scripts"] = True
            return True
        
        except Exception as e:
            logger.error(f"✗ Error testing scripts: {e}")
            return False
    
    def test_integration(self) -> bool:
        """Test if all components work together"""
        logger.info("Testing integration...")
        
        try:
            # Test if we can import and use the tool
            try:
                # Import from local file
                import sys
                import os
                from pathlib import Path
                
                # Add tools directory to path
                tools_dir = Path("/home/cbwinslow/dotfiles/ai/tools")
                if tools_dir.exists():
                    sys.path.append(str(tools_dir))
                
                # Try to import from the correct path
                try:
                    from bitwarden_client import BitwardenClient
                except ImportError:
                    # Try relative import
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(
                        "bitwarden_client",
                        "/home/cbwinslow/dotfiles/ai/tools/api_tools/bitwarden/bitwarden_client.py"
                    )
                    if spec is not None:
                        bitwarden_client = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(bitwarden_client)
                        BitwardenClient = bitwarden_client.BitwardenClient
                    else:
                        raise ImportError("Could not find bitwarden_client module")
                
                # Test basic functionality
                client = BitwardenClient()
                validation = client.validate_configuration()
                
                if validation.get("valid", False):
                    logger.info("✓ Tool integration successful")
                    self.results["integration"] = True
                    return True
                else:
                    logger.warning("✗ Tool integration failed validation")
                    return False
            
            except Exception as e:
                logger.error(f"✗ Error importing tool: {e}")
                return False
        
        except Exception as e:
            logger.error(f"✗ Error testing integration: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return results"""
        logger.info("=" * 60)
        logger.info("Bitwarden Integration Test Suite")
        logger.info("=" * 60)
        
        # Run individual tests
        tests = [
            self.test_bitwarden_cli,
            self.test_session_token,
            self.test_skill_definition,
            self.test_tool_implementation,
            self.test_scripts,
            self.test_integration
        ]
        
        all_passed = True
        for test in tests:
            if not test():
                all_passed = False
        
        # Determine overall result
        self.results["overall"] = all_passed
        
        # Print summary
        logger.info("=" * 60)
        logger.info("Test Summary")
        logger.info("=" * 60)
        
        passed = sum(1 for v in self.results.values() if v)
        total = len(self.results)
        
        logger.info(f"Passed: {passed}/{total}")
        
        for test_name, result in self.results.items():
            status = "✓" if result else "✗"
            logger.info(f"{status} {test_name}")
        
        if all_passed:
            logger.info("🎉 All tests passed! Bitwarden integration is working correctly.")
        else:
            logger.warning("⚠ Some tests failed. Please check the issues above.")
        
        logger.info("=" * 60)
        
        return self.results
    
    def create_report(self) -> bool:
        """Create a test report"""
        logger.info("Creating test report...")
        
        try:
            report_path = self.base_path / "logs" / "bitwarden_test_report.json"
            report_path.parent.mkdir(exist_ok=True)
            
            report = {
                "timestamp": str(Path.home().stat().st_mtime),
                "results": self.results,
                "system_info": {
                    "os": os.name,
                    "python_version": ".".join(map(str, sys.version_info[:3])),
                    "bitwarden_cli": self._get_bitwarden_version()
                },
                "recommendations": self._get_recommendations()
            }
            
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"✓ Test report saved to {report_path}")
            return True
        
        except Exception as e:
            logger.error(f"✗ Error creating test report: {e}")
            return False
    
    def _get_bitwarden_version(self) -> str:
        """Get Bitwarden CLI version"""
        try:
            result = subprocess.run(
                ["bw", "--version"],
                capture_output=True,
                text=True
            )
            return result.stdout.strip() if result.returncode == 0 else "Unknown"
        except:
            return "Unknown"
    
    def _get_recommendations(self) -> List[str]:
        """Get recommendations based on test results"""
        recommendations = []
        
        if not self.results["bitwarden_cli"]:
            recommendations.append("Install Bitwarden CLI: ./scripts/bitwarden/setup_bitwarden.sh")
        
        if not self.results["session_token"]:
            recommendations.append("Set up Bitwarden session: bw login && bw unlock")
        
        if not self.results["skill_definition"]:
            recommendations.append("Check skill definition in skills/integration/bitwarden/SKILL.md")
        
        if not self.results["tool_implementation"]:
            recommendations.append("Check tool implementation in tools/api_tools/bitwarden/bitwarden_client.py")
        
        if not self.results["scripts"]:
            recommendations.append("Check scripts in scripts/bitwarden/")
        
        if not self.results["integration"]:
            recommendations.append("Test tool integration manually")
        
        return recommendations


def main():
    """Main entry point for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Bitwarden Integration Test Suite")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--report", action="store_true", help="Create test report")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    tester = BitwardenTester()
    results = tester.run_all_tests()
    
    if args.report:
        tester.create_report()
    
    # Return exit code based on overall result
    if results["overall"]:
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    main()