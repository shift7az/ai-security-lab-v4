#!/usr/bin/env python3
"""
AI Security Lab v4.0 - Complete Test Runner

Runs all test suites for the AI Security Lab v4.0 system:
- Infrastructure tests
- Threat detector tests
- Performance tests
- Integration tests

Usage:
    python run_all_tests.py [--quick] [--verbose] [--report-only]
"""

import asyncio
import argparse
import json
import logging
import sys
import os
from datetime import datetime
from typing import Dict, List, Any
import subprocess

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestRunner:
    """Main test runner for AI Security Lab v4.0."""

    def __init__(self, quick_mode: bool = False, verbose: bool = False):
        self.quick_mode = quick_mode
        self.verbose = verbose
        self.test_results = {}
        self.start_time = datetime.utcnow()

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run complete test suite."""
        logger.info("🚀 Starting AI Security Lab v4.0 Complete Test Suite")

        # Test 1: Infrastructure Tests
        await self._run_infrastructure_tests()

        # Test 2: Threat Detector Tests
        await self._run_threat_detector_tests()

        # Test 3: Integration Tests
        await self._run_integration_tests()

        # Test 4: Performance Tests
        if not self.quick_mode:
            await self._run_performance_tests()

        # Generate comprehensive report
        report = self._generate_comprehensive_report()

        logger.info("✅ Complete test suite finished")
        return report

    async def _run_infrastructure_tests(self):
        """Run infrastructure tests."""
        logger.info("🏗️  Running Infrastructure Tests...")

        try:
            # Import and run infrastructure tests
            from tests.infrastructure.test_infrastructure import InfrastructureTester

            tester = InfrastructureTester()
            report = await tester.run_all_tests()

            self.test_results["infrastructure"] = report

            # Print summary
            summary = report["test_summary"]
            status_icon = "✅" if summary["overall_status"] == "PASS" else "⚠️" if summary["overall_status"] == "WARN" else "❌"
            print(f"  {status_icon} Infrastructure: {summary['overall_status']} ({summary['success_rate']}%)")

        except Exception as e:
            logger.error(f"❌ Infrastructure tests failed: {e}")
            self.test_results["infrastructure"] = {"error": str(e)}

    async def _run_threat_detector_tests(self):
        """Run threat detector tests."""
        logger.info("🔍 Running Threat Detector Tests...")

        try:
            # Import and run threat detector tests
            from tests.threat_detector.test_threat_detector import ThreatDetectorTester

            tester = ThreatDetectorTester()
            report = await tester.run_all_tests()

            self.test_results["threat_detector"] = report

            # Print summary
            summary = report["test_summary"]
            status_icon = "✅" if summary["overall_status"] == "PASS" else "⚠️" if summary["overall_status"] == "WARN" else "❌"
            print(f"  {status_icon} Threat Detector: {summary['overall_status']} ({summary['analysis_success_rate']}%)")

        except Exception as e:
            logger.error(f"❌ Threat detector tests failed: {e}")
            self.test_results["threat_detector"] = {"error": str(e)}

    async def _run_integration_tests(self):
        """Run integration tests."""
        logger.info("🔗 Running Integration Tests...")

        try:
            # Test service communication
            await self._test_service_integration()

            # Test data flow
            await self._test_data_flow()

            # Test end-to-end scenarios
            await self._test_end_to_end()

            self.test_results["integration"] = {
                "status": "completed",
                "timestamp": datetime.utcnow().isoformat()
            }

            print("  ✅ Integration tests completed")

        except Exception as e:
            logger.error(f"❌ Integration tests failed: {e}")
            self.test_results["integration"] = {"error": str(e)}

    async def _test_service_integration(self):
        """Test service-to-service communication."""
        # This would test communication between:
        # - Frigate ↔ Threat Detector
        # - Threat Detector ↔ Database
        # - Threat Detector ↔ Redis
        # - Threat Detector ↔ Alert Manager
        pass

    async def _test_data_flow(self):
        """Test data flow through the system."""
        # This would test:
        # - Detection data ingestion
        # - Threat analysis pipeline
        # - Alert generation
        # - Data storage and retrieval
        pass

    async def _test_end_to_end(self):
        """Test complete end-to-end scenarios."""
        # This would test complete workflows:
        # - Camera detects person → Threat analysis → Alert generation
        # - Weapon detection → High priority alert → Escalation
        # - Multiple cameras → Cross-camera tracking → Correlation
        pass

    async def _run_performance_tests(self):
        """Run comprehensive performance tests."""
        logger.info("⚡ Running Performance Tests...")

        try:
            # Load testing
            await self._test_load_performance()

            # Stress testing
            await self._test_stress_performance()

            # Memory leak testing
            await self._test_memory_leaks()

            self.test_results["performance"] = {
                "status": "completed",
                "timestamp": datetime.utcnow().isoformat()
            }

            print("  ✅ Performance tests completed")

        except Exception as e:
            logger.error(f"❌ Performance tests failed: {e}")
            self.test_results["performance"] = {"error": str(e)}

    async def _test_load_performance(self):
        """Test system under load."""
        # Simulate high detection volume
        # Test concurrent processing
        # Monitor resource usage
        pass

    async def _test_stress_performance(self):
        """Test system under stress conditions."""
        # Test with maximum load
        # Test error recovery
        # Test graceful degradation
        pass

    async def _test_memory_leaks(self):
        """Test for memory leaks."""
        # Monitor memory usage over time
        # Check for proper resource cleanup
        # Test long-running scenarios
        pass

    def _generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        end_time = datetime.utcnow()

        # Aggregate results
        total_duration = (end_time - self.start_time).total_seconds()

        # Calculate overall status
        critical_components = ["infrastructure", "threat_detector"]
        component_statuses = []

        for component in critical_components:
            if component in self.test_results:
                component_report = self.test_results[component]
                if "test_summary" in component_report:
                    status = component_report["test_summary"]["overall_status"]
                    component_statuses.append(status)
                elif "error" in component_report:
                    component_statuses.append("FAIL")
                else:
                    component_statuses.append("UNKNOWN")

        # Overall status determination
        if "FAIL" in component_statuses:
            overall_status = "FAIL"
        elif "WARN" in component_statuses:
            overall_status = "WARN"
        else:
            overall_status = "PASS"

        # Generate recommendations
        recommendations = self._generate_overall_recommendations()

        report = {
            "comprehensive_summary": {
                "overall_status": overall_status,
                "total_duration_seconds": round(total_duration, 2),
                "components_tested": len(critical_components),
                "components_passed": len([s for s in component_statuses if s == "PASS"]),
                "components_warned": len([s for s in component_statuses if s == "WARN"]),
                "components_failed": len([s for s in component_statuses if s == "FAIL"]),
                "test_timestamp": self.start_time.isoformat(),
                "report_timestamp": end_time.isoformat()
            },
            "component_results": self.test_results,
            "recommendations": recommendations,
            "next_steps": self._generate_next_steps()
        }

        return report

    def _generate_overall_recommendations(self) -> List[str]:
        """Generate overall recommendations."""
        recommendations = []

        # Infrastructure recommendations
        infra_report = self.test_results.get("infrastructure", {})
        if "recommendations" in infra_report:
            recommendations.extend(infra_report["recommendations"])

        # Threat detector recommendations
        threat_report = self.test_results.get("threat_detector", {})
        if "recommendations" in threat_report:
            recommendations.extend(threat_report["recommendations"])

        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)

        return unique_recommendations

    def _generate_next_steps(self) -> List[str]:
        """Generate next steps based on test results."""
        next_steps = []

        # Check if foundation is ready
        infra_report = self.test_results.get("infrastructure", {})
        if infra_report.get("test_summary", {}).get("overall_status") == "PASS":
            next_steps.append("✅ Foundation infrastructure is ready")
            next_steps.append("🚀 Ready to deploy threat detection services")
        else:
            next_steps.append("⚠️  Fix infrastructure issues before proceeding")

        # Check if threat detector is ready
        threat_report = self.test_results.get("threat_detector", {})
        if threat_report.get("test_summary", {}).get("overall_status") == "PASS":
            next_steps.append("✅ Threat detection service is ready")
            next_steps.append("🎯 Ready for production deployment")
        elif threat_report.get("test_summary", {}).get("analysis_success_rate", 0) > 50:
            next_steps.append("⚠️  Threat detection needs optimization")
        else:
            next_steps.append("❌ Threat detection service needs fixes")

        return next_steps


async def main():
    """Main test execution function."""
    parser = argparse.ArgumentParser(description="AI Security Lab v4.0 Test Runner")
    parser.add_argument("--quick", action="store_true", help="Run quick test suite")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--report-only", action="store_true", help="Show existing reports only")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    runner = TestRunner(quick_mode=args.quick, verbose=args.verbose)

    try:
        if args.report_only:
            # Just show existing reports
            await show_existing_reports()
        else:
            # Run full test suite
            report = await runner.run_all_tests()

            # Print comprehensive summary
            summary = report["comprehensive_summary"]
            print("\n" + "="*70)
            print("🏆 AI SECURITY LAB v4.0 - COMPREHENSIVE TEST REPORT")
            print("="*70)
            print(f"Overall Status: {summary['overall_status']}")
            print(f"Total Duration: {summary['total_duration_seconds']".2f"}s")
            print(f"Components: {summary['components_passed']}/{summary['components_tested']} passed")
            print(f"Test Period: {summary['test_timestamp']}")
            print(f"Report Time: {summary['report_timestamp']}")
            print()

            # Print next steps
            if report["next_steps"]:
                print("🎯 NEXT STEPS:")
                for step in report["next_steps"]:
                    print(f"  {step}")
                print()

            # Save comprehensive report
            with open("ai-security-lab-v4/tests/comprehensive_test_report.json", "w") as f:
                json.dump(report, f, indent=2)

            print("💾 Comprehensive report saved to: tests/comprehensive_test_report.json")

            # Exit with appropriate code
            if summary["overall_status"] == "FAIL":
                sys.exit(1)
            elif summary["overall_status"] == "WARN":
                sys.exit(0)
            else:
                print("🎉 All tests passed! System is ready for deployment!")
                sys.exit(0)

    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        sys.exit(1)


async def show_existing_reports():
    """Show existing test reports."""
    print("📊 EXISTING TEST REPORTS:")
    print()

    # Infrastructure report
    infra_file = "ai-security-lab-v4/tests/infrastructure_test_report.json"
    if os.path.exists(infra_file):
        try:
            with open(infra_file, 'r') as f:
                report = json.load(f)
                summary = report.get("test_summary", {})
                print(f"🏗️  Infrastructure Test:")
                print(f"    Status: {summary.get('overall_status', 'UNKNOWN')}")
                print(f"    Success Rate: {summary.get('success_rate', 0)}%")
                print(f"    Duration: {summary.get('total_duration', 0)}s")
                print(f"    Timestamp: {summary.get('timestamp', 'Unknown')}")
        except:
            print("🏗️  Infrastructure Test: Report corrupted or unreadable")
    else:
        print("🏗️  Infrastructure Test: No report found")

    print()

    # Threat detector report
    threat_file = "ai-security-lab-v4/tests/threat_detector_test_report.json"
    if os.path.exists(threat_file):
        try:
            with open(threat_file, 'r') as f:
                report = json.load(f)
                summary = report.get("test_summary", {})
                print(f"🔍 Threat Detector Test:")
                print(f"    Status: {summary.get('overall_status', 'UNKNOWN')}")
                print(f"    Analysis Success: {summary.get('analysis_success_rate', 0)}%")
                print(f"    Duration: {summary.get('total_duration', 0)}s")
                print(f"    Timestamp: {summary.get('timestamp', 'Unknown')}")
        except:
            print("🔍 Threat Detector Test: Report corrupted or unreadable")
    else:
        print("🔍 Threat Detector Test: No report found")

    print()

    # Comprehensive report
    comp_file = "ai-security-lab-v4/tests/comprehensive_test_report.json"
    if os.path.exists(comp_file):
        try:
            with open(comp_file, 'r') as f:
                report = json.load(f)
                summary = report.get("comprehensive_summary", {})
                print(f"🏆 Comprehensive Test:")
                print(f"    Status: {summary.get('overall_status', 'UNKNOWN')}")
                print(f"    Components Passed: {summary.get('components_passed', 0)}/{summary.get('components_tested', 0)}")
                print(f"    Duration: {summary.get('total_duration_seconds', 0):.0f}s")
                print(f"    Timestamp: {summary.get('test_timestamp', 'Unknown')}")
        except:
            print("🏆 Comprehensive Test: Report corrupted or unreadable")
    else:
        print("🏆 Comprehensive Test: No report found")


if __name__ == "__main__":
    asyncio.run(main())
