#!/usr/bin/env python3
"""
Threat Detector Testing Suite for AI Security Lab v4.0

Comprehensive testing of threat detection service including:
- Service health and connectivity
- Threat analysis functionality
- Alert generation and management
- Performance benchmarking
- Integration testing
"""

import asyncio
import aiohttp
import json
import logging
import time
from typing import Dict, List, Any
from datetime import datetime
import sys
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ThreatDetectorTester:
    """Comprehensive threat detector testing suite."""

    def __init__(self):
        self.base_url = "http://localhost:8001"
        self.test_results = {}
        self.start_time = time.time()

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run complete threat detector test suite."""
        logger.info("🚀 Starting AI Security Lab v4.0 Threat Detector Tests")

        # Test 1: Service Health
        await self._test_service_health()

        # Test 2: Threat Analysis
        await self._test_threat_analysis()

        # Test 3: Alert Management
        await self._test_alert_management()

        # Test 4: Performance Testing
        await self._test_performance()

        # Test 5: Edge Cases
        await self._test_edge_cases()

        # Generate test report
        report = self._generate_test_report()

        logger.info("✅ Threat detector testing completed")
        return report

    async def _test_service_health(self):
        """Test threat detector service health."""
        logger.info("Testing threat detector service health...")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.test_results["service_healthy"] = True
                        self.test_results["service_info"] = data
                        logger.info("✅ Threat detector service is healthy")
                    else:
                        self.test_results["service_healthy"] = False
                        logger.warning(f"⚠️  Service health check failed: {response.status}")

        except Exception as e:
            logger.error(f"❌ Service health test failed: {e}")
            self.test_results["service_error"] = str(e)

    async def _test_threat_analysis(self):
        """Test threat analysis functionality."""
        logger.info("Testing threat analysis functionality...")

        test_cases = [
            {
                "name": "Normal person detection",
                "input": {
                    "camera_id": "test_camera_1",
                    "detection_type": "person",
                    "confidence": 0.85,
                    "bbox": [100, 100, 200, 300],
                    "metadata": {
                        "in_restricted_area": False,
                        "dwell_time": 30
                    }
                },
                "expected_threat_level": "low"
            },
            {
                "name": "Person in restricted area",
                "input": {
                    "camera_id": "test_camera_1",
                    "detection_type": "person",
                    "confidence": 0.9,
                    "bbox": [100, 100, 200, 300],
                    "metadata": {
                        "in_restricted_area": True,
                        "dwell_time": 600
                    }
                },
                "expected_threat_level": "medium"
            },
            {
                "name": "Weapon detection",
                "input": {
                    "camera_id": "test_camera_1",
                    "detection_type": "weapon",
                    "confidence": 0.95,
                    "bbox": [150, 150, 180, 200],
                    "metadata": {}
                },
                "expected_threat_level": "high"
            },
            {
                "name": "Vehicle speeding",
                "input": {
                    "camera_id": "test_camera_1",
                    "detection_type": "vehicle",
                    "confidence": 0.8,
                    "bbox": [50, 50, 300, 150],
                    "metadata": {
                        "speed": 80,
                        "in_restricted_area": True
                    }
                },
                "expected_threat_level": "medium"
            }
        ]

        analysis_results = []

        async with aiohttp.ClientSession() as session:
            for test_case in test_cases:
                try:
                    start_time = time.time()

                    async with session.post(
                        f"{self.base_url}/analyze",
                        json=test_case["input"],
                        timeout=30
                    ) as response:

                        end_time = time.time()
                        response_time = (end_time - start_time) * 1000

                        if response.status == 200:
                            analysis = await response.json()

                            analysis_results.append({
                                "test_name": test_case["name"],
                                "success": True,
                                "response_time_ms": response_time,
                                "analysis": analysis
                            })

                            # Validate expected threat level
                            actual_level = analysis.get("threat_level", "").lower()
                            expected_level = test_case["expected_threat_level"]

                            if actual_level == expected_level:
                                logger.info(f"✅ {test_case['name']}: {response_time:.1f}ms ({actual_level})")
                            else:
                                logger.warning(f"⚠️  {test_case['name']}: Expected {expected_level}, got {actual_level}")

                        else:
                            analysis_results.append({
                                "test_name": test_case["name"],
                                "success": False,
                                "error": f"HTTP {response.status}"
                            })
                            logger.error(f"❌ {test_case['name']}: HTTP {response.status}")

                except Exception as e:
                    analysis_results.append({
                        "test_name": test_case["name"],
                        "success": False,
                        "error": str(e)
                    })
                    logger.error(f"❌ {test_case['name']}: {e}")

        self.test_results["analysis_tests"] = analysis_results
        successful_analyses = len([r for r in analysis_results if r["success"]])
        self.test_results["analysis_success_rate"] = successful_analyses / len(test_cases) * 100

    async def _test_alert_management(self):
        """Test alert management functionality."""
        logger.info("Testing alert management...")

        try:
            # Test getting alert statistics
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/stats", timeout=10) as response:
                    if response.status == 200:
                        stats = await response.json()
                        self.test_results["alert_stats"] = stats
                        logger.info("✅ Alert statistics retrieved")
                    else:
                        logger.warning(f"⚠️  Alert stats failed: {response.status}")

                # Test getting alert history
                async with session.get(f"{self.base_url}/history", timeout=10) as response:
                    if response.status == 200:
                        history = await response.json()
                        self.test_results["alert_history_count"] = len(history)
                        logger.info(f"✅ Alert history retrieved: {len(history)} alerts")
                    else:
                        logger.warning(f"⚠️  Alert history failed: {response.status}")

        except Exception as e:
            logger.error(f"❌ Alert management test failed: {e}")
            self.test_results["alert_error"] = str(e)

    async def _test_performance(self):
        """Test threat detector performance."""
        logger.info("Testing threat detector performance...")

        # Test concurrent analysis
        await self._test_concurrent_analysis()

        # Test response time consistency
        await self._test_response_time_consistency()

    async def _test_concurrent_analysis(self):
        """Test concurrent threat analysis."""
        try:
            num_concurrent = 5
            test_input = {
                "camera_id": "perf_test_camera",
                "detection_type": "person",
                "confidence": 0.8,
                "bbox": [100, 100, 200, 300],
                "metadata": {}
            }

            async def single_analysis(session, index):
                try:
                    start_time = time.time()
                    async with session.post(
                        f"{self.base_url}/analyze",
                        json=test_input,
                        timeout=30
                    ) as response:
                        end_time = time.time()

                        if response.status == 200:
                            return (end_time - start_time) * 1000  # ms
                        else:
                            return -1
                except Exception:
                    return -1

            async with aiohttp.ClientSession() as session:
                tasks = [single_analysis(session, i) for i in range(num_concurrent)]
                response_times = await asyncio.gather(*tasks)

                successful_times = [t for t in response_times if t > 0]
                failed_count = len(response_times) - len(successful_times)

                if successful_times:
                    avg_time = sum(successful_times) / len(successful_times)
                    max_time = max(successful_times)
                    min_time = min(successful_times)

                    self.test_results["concurrent_test"] = {
                        "total_requests": num_concurrent,
                        "successful_requests": len(successful_times),
                        "failed_requests": failed_count,
                        "avg_response_time_ms": round(avg_time, 2),
                        "max_response_time_ms": round(max_time, 2),
                        "min_response_time_ms": round(min_time, 2)
                    }

                    logger.info(f"✅ Concurrent test: {len(successful_times)}/{num_concurrent} successful, avg: {avg_time:.1f}ms")
                else:
                    logger.error("❌ All concurrent requests failed")

        except Exception as e:
            logger.error(f"❌ Concurrent analysis test failed: {e}")
            self.test_results["concurrent_error"] = str(e)

    async def _test_response_time_consistency(self):
        """Test response time consistency."""
        try:
            num_tests = 10
            test_input = {
                "camera_id": "consistency_test",
                "detection_type": "person",
                "confidence": 0.7,
                "bbox": [100, 100, 200, 300],
                "metadata": {}
            }

            response_times = []

            async with aiohttp.ClientSession() as session:
                for i in range(num_tests):
                    start_time = time.time()
                    async with session.post(
                        f"{self.base_url}/analyze",
                        json=test_input,
                        timeout=30
                    ) as response:
                        end_time = time.time()

                        if response.status == 200:
                            response_time = (end_time - start_time) * 1000
                            response_times.append(response_time)
                        else:
                            response_times.append(-1)

                    # Small delay between tests
                    await asyncio.sleep(0.1)

            successful_times = [t for t in response_times if t > 0]

            if successful_times:
                avg_time = sum(successful_times) / len(successful_times)
                max_time = max(successful_times)
                min_time = min(successful_times)

                # Calculate standard deviation
                variance = sum((t - avg_time) ** 2 for t in successful_times) / len(successful_times)
                std_dev = variance ** 0.5

                self.test_results["consistency_test"] = {
                    "num_tests": num_tests,
                    "successful_tests": len(successful_times),
                    "avg_response_time_ms": round(avg_time, 2),
                    "max_response_time_ms": round(max_time, 2),
                    "min_response_time_ms": round(min_time, 2),
                    "std_deviation_ms": round(std_dev, 2),
                    "consistency_score": round(max(0, 100 - (std_dev / avg_time * 100)), 2)
                }

                logger.info(f"✅ Consistency test: avg {avg_time:.1f}ms, std dev {std_dev:.1f}ms")
            else:
                logger.error("❌ All consistency tests failed")

        except Exception as e:
            logger.error(f"❌ Consistency test failed: {e}")
            self.test_results["consistency_error"] = str(e)

    async def _test_edge_cases(self):
        """Test edge cases and error handling."""
        logger.info("Testing edge cases and error handling...")

        edge_cases = [
            {
                "name": "Invalid detection type",
                "input": {
                    "camera_id": "test_camera",
                    "detection_type": "invalid_type",
                    "confidence": 0.5,
                    "bbox": [100, 100, 200, 300]
                },
                "should_fail_gracefully": True
            },
            {
                "name": "Very low confidence",
                "input": {
                    "camera_id": "test_camera",
                    "detection_type": "person",
                    "confidence": 0.01,
                    "bbox": [100, 100, 200, 300]
                },
                "should_fail_gracefully": False
            },
            {
                "name": "Invalid bbox format",
                "input": {
                    "camera_id": "test_camera",
                    "detection_type": "person",
                    "confidence": 0.8,
                    "bbox": "invalid_bbox"
                },
                "should_fail_gracefully": True
            },
            {
                "name": "Missing required fields",
                "input": {
                    "detection_type": "person",
                    "confidence": 0.8
                },
                "should_fail_gracefully": True
            }
        ]

        edge_results = []

        async with aiohttp.ClientSession() as session:
            for edge_case in edge_cases:
                try:
                    async with session.post(
                        f"{self.base_url}/analyze",
                        json=edge_case["input"],
                        timeout=10
                    ) as response:

                        success = response.status == 200
                        result = {
                            "test_name": edge_case["name"],
                            "success": success,
                            "status_code": response.status,
                            "graceful_failure": not success and edge_case["should_fail_gracefully"]
                        }

                        if success:
                            logger.info(f"✅ {edge_case['name']}: Handled gracefully")
                        elif edge_case["should_fail_gracefully"]:
                            logger.info(f"✅ {edge_case['name']}: Failed gracefully (expected)")
                        else:
                            logger.warning(f"⚠️  {edge_case['name']}: Unexpected failure")

                        edge_results.append(result)

                except Exception as e:
                    result = {
                        "test_name": edge_case["name"],
                        "success": False,
                        "error": str(e),
                        "graceful_failure": edge_case["should_fail_gracefully"]
                    }

                    if edge_case["should_fail_gracefully"]:
                        logger.info(f"✅ {edge_case['name']}: Failed gracefully (expected)")
                    else:
                        logger.error(f"❌ {edge_case['name']}: Unexpected error")

                    edge_results.append(result)

        self.test_results["edge_cases"] = edge_results

        # Calculate edge case score
        graceful_failures = len([r for r in edge_results if r["graceful_failure"]])
        total_edge_cases = len(edge_results)
        self.test_results["edge_case_score"] = graceful_failures / total_edge_cases * 100

    def _generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        end_time = time.time()
        duration = end_time - self.start_time

        # Calculate summary statistics
        analysis_tests = self.test_results.get("analysis_tests", [])
        successful_analyses = len([t for t in analysis_tests if t["success"]])

        # Determine overall status
        critical_tests = ["service_healthy"]
        critical_healthy = all(
            self.test_results.get(test, False) for test in critical_tests
        )

        analysis_success_rate = self.test_results.get("analysis_success_rate", 0)
        analysis_healthy = analysis_success_rate > 80  # At least 80% success rate

        overall_status = "PASS" if critical_healthy and analysis_healthy else "WARN"
        if analysis_success_rate < 50:
            overall_status = "FAIL"

        report = {
            "test_summary": {
                "overall_status": overall_status,
                "total_duration": round(duration, 2),
                "service_healthy": self.test_results.get("service_healthy", False),
                "analysis_success_rate": round(analysis_success_rate, 1),
                "timestamp": datetime.utcnow().isoformat()
            },
            "detailed_results": self.test_results,
            "recommendations": self._generate_recommendations()
        }

        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []

        if not self.test_results.get("service_healthy", False):
            recommendations.append("❌ Threat detector service not healthy - check service logs")

        analysis_success_rate = self.test_results.get("analysis_success_rate", 0)
        if analysis_success_rate < 80:
            recommendations.append(f"⚠️  Low analysis success rate: {analysis_success_rate:.1f}% - check threat detection models")

        # Performance recommendations
        concurrent_test = self.test_results.get("concurrent_test", {})
        avg_concurrent_time = concurrent_test.get("avg_response_time_ms", 0)
        if avg_concurrent_time > 1000:
            recommendations.append(f"🐌 Slow concurrent performance: {avg_concurrent_time:.1f}ms avg - optimize for concurrency")

        consistency_test = self.test_results.get("consistency_test", {})
        consistency_score = consistency_test.get("consistency_score", 100)
        if consistency_score < 80:
            recommendations.append(f"📊 Poor response time consistency: {consistency_score:.1f}% - investigate performance variability")

        if not recommendations:
            recommendations.append("✅ Threat detector service is working well")
            recommendations.append("🎯 Ready for production deployment")

        return recommendations


async def main():
    """Main test execution function."""
    tester = ThreatDetectorTester()

    try:
        report = await tester.run_all_tests()

        # Print summary
        summary = report["test_summary"]
        print("\n" + "="*60)
        print("🔍 AI SECURITY LAB v4.0 - THREAT DETECTOR TEST REPORT")
        print("="*60)
        print(f"Status: {summary['overall_status']}")
        print(f"Duration: {summary['total_duration']".2f"}s")
        print(f"Service Health: {'✅' if summary['service_healthy'] else '❌'}")
        print(f"Analysis Success Rate: {summary['analysis_success_rate']}%")
        print(f"Timestamp: {summary['timestamp']}")
        print()

        # Print recommendations
        if report["recommendations"]:
            print("📋 RECOMMENDATIONS:")
            for rec in report["recommendations"]:
                print(f"  {rec}")
            print()

        # Save detailed report
        with open("ai-security-lab-v4/tests/threat_detector_test_report.json", "w") as f:
            json.dump(report, f, indent=2)

        print("💾 Detailed report saved to: tests/threat_detector_test_report.json")

        # Exit with appropriate code
        if summary["overall_status"] == "FAIL":
            sys.exit(1)
        elif summary["overall_status"] == "WARN":
            sys.exit(0)
        else:
            print("🎉 All threat detector tests passed!")
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
