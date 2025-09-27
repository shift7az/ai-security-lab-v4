#!/usr/bin/env python3
"""
Infrastructure Testing Suite for AI Security Lab v4.0

Comprehensive testing of foundation infrastructure including:
- Docker services health
- GPU acceleration
- Database connectivity
- Network communication
- Storage systems
- Monitoring stack
"""

import asyncio
import aiohttp
import socket
import time
import json
import logging
from typing import Dict, List, Tuple, Any
from datetime import datetime
import subprocess
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InfrastructureTester:
    """Comprehensive infrastructure testing suite."""

    def __init__(self):
        self.base_url = "http://localhost"
        self.test_results = {}
        self.start_time = time.time()

        # Service endpoints to test
        self.services = {
            "frigate": {"port": 5000, "health_path": "/api/version"},
            "timescaledb": {"port": 5432, "health_check": self._test_postgres},
            "redis": {"port": 6379, "health_check": self._test_redis},
            "qdrant": {"port": 6333, "health_path": "/health"},
            "minio": {"port": 9000, "health_path": "/minio/health/live"},
            "prometheus": {"port": 9090, "health_path": "/-/healthy"},
            "grafana": {"port": 3000, "health_path": "/api/health"},
            "loki": {"port": 3100, "health_path": "/ready"},
            "tempo": {"port": 3200, "health_path": "/ready"},
        }

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run complete infrastructure test suite."""
        logger.info("🚀 Starting AI Security Lab v4.0 Infrastructure Tests")

        # Test 1: GPU Availability
        await self._test_gpu_availability()

        # Test 2: Docker Services
        await self._test_docker_services()

        # Test 3: Network Connectivity
        await self._test_network_connectivity()

        # Test 4: Database Systems
        await self._test_database_systems()

        # Test 5: Storage Systems
        await self._test_storage_systems()

        # Test 6: Monitoring Stack
        await self._test_monitoring_stack()

        # Test 7: Performance Benchmarks
        await self._test_performance_benchmarks()

        # Generate test report
        report = self._generate_test_report()

        logger.info("✅ Infrastructure testing completed")
        return report

    async def _test_gpu_availability(self):
        """Test GPU availability and CUDA functionality."""
        logger.info("Testing GPU availability...")

        try:
            # Test 1: Check if nvidia-smi is available
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                gpu_names = result.stdout.strip().split('\n')
                self.test_results["gpu_available"] = True
                self.test_results["gpu_count"] = len(gpu_names)
                self.test_results["gpu_names"] = gpu_names
                logger.info(f"✅ GPU detected: {gpu_names}")
            else:
                self.test_results["gpu_available"] = False
                logger.warning("⚠️  No GPU detected")

            # Test 2: Test CUDA functionality with Docker
            cuda_test = subprocess.run([
                "docker", "run", "--rm", "--gpus", "all",
                "nvidia/cuda:11.8-base-ubuntu20.04", "nvidia-smi"
            ], capture_output=True, timeout=30)

            if cuda_test.returncode == 0:
                self.test_results["cuda_working"] = True
                logger.info("✅ CUDA functionality verified")
            else:
                self.test_results["cuda_working"] = False
                logger.warning("⚠️  CUDA test failed")

        except Exception as e:
            logger.error(f"GPU test failed: {e}")
            self.test_results["gpu_error"] = str(e)

    async def _test_docker_services(self):
        """Test Docker services health."""
        logger.info("Testing Docker services...")

        try:
            # Check if Docker Compose is running
            result = subprocess.run(
                ["docker-compose", "ps", "-q"],
                cwd="..",
                capture_output=True, text=True
            )

            if result.returncode == 0:
                running_containers = len(result.stdout.strip().split('\n'))
                self.test_results["docker_running"] = True
                self.test_results["container_count"] = running_containers
                logger.info(f"✅ Docker services running: {running_containers} containers")
            else:
                self.test_results["docker_running"] = False
                logger.error("❌ Docker services not running")

        except Exception as e:
            logger.error(f"Docker test failed: {e}")
            self.test_results["docker_error"] = str(e)

    async def _test_network_connectivity(self):
        """Test network connectivity between services."""
        logger.info("Testing network connectivity...")

        async with aiohttp.ClientSession() as session:
            for service_name, config in self.services.items():
                try:
                    if "health_check" in config:
                        # Custom health check function
                        success = await config["health_check"](config["port"])
                    else:
                        # Standard HTTP health check
                        url = f"{self.base_url}:{config['port']}{config.get('health_path', '/health')}"
                        success = await self._test_http_endpoint(session, url)

                    self.test_results[f"{service_name}_healthy"] = success

                    if success:
                        logger.info(f"✅ {service_name} is healthy")
                    else:
                        logger.warning(f"⚠️  {service_name} health check failed")

                except Exception as e:
                    logger.error(f"❌ {service_name} connectivity test failed: {e}")
                    self.test_results[f"{service_name}_error"] = str(e)

    async def _test_http_endpoint(self, session: aiohttp.ClientSession, url: str) -> bool:
        """Test HTTP endpoint availability."""
        try:
            async with session.get(url, timeout=10) as response:
                return response.status < 400
        except:
            return False

    async def _test_postgres(self, port: int) -> bool:
        """Test PostgreSQL/TimescaleDB connectivity."""
        try:
            # This would require asyncpg or similar
            # For now, just test TCP connectivity
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0
        except:
            return False

    async def _test_redis(self, port: int) -> bool:
        """Test Redis connectivity."""
        try:
            # Simple TCP connectivity test
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0
        except:
            return False

    async def _test_database_systems(self):
        """Test database connectivity and functionality."""
        logger.info("Testing database systems...")

        # Test TimescaleDB
        await self._test_timescaledb()

        # Test Redis
        await self._test_redis_functionality()

        # Test Qdrant
        await self._test_qdrant()

    async def _test_timescaledb(self):
        """Test TimescaleDB functionality."""
        try:
            # Test basic connectivity
            success = await self._test_postgres(5432)

            if success:
                # Test database operations (would need asyncpg)
                logger.info("✅ TimescaleDB connectivity verified")
                self.test_results["timescaledb_healthy"] = True
            else:
                logger.warning("⚠️  TimescaleDB connection failed")
                self.test_results["timescaledb_healthy"] = False

        except Exception as e:
            logger.error(f"TimescaleDB test failed: {e}")
            self.test_results["timescaledb_error"] = str(e)

    async def _test_redis_functionality(self):
        """Test Redis functionality."""
        try:
            success = await self._test_redis(6379)

            if success:
                logger.info("✅ Redis connectivity verified")
                self.test_results["redis_healthy"] = True
            else:
                logger.warning("⚠️  Redis connection failed")
                self.test_results["redis_healthy"] = False

        except Exception as e:
            logger.error(f"Redis test failed: {e}")
            self.test_results["redis_error"] = str(e)

    async def _test_qdrant(self):
        """Test Qdrant vector database."""
        try:
            url = f"{self.base_url}:6333/health"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    success = response.status == 200

            if success:
                logger.info("✅ Qdrant is healthy")
                self.test_results["qdrant_healthy"] = True
            else:
                logger.warning("⚠️  Qdrant health check failed")
                self.test_results["qdrant_healthy"] = False

        except Exception as e:
            logger.error(f"Qdrant test failed: {e}")
            self.test_results["qdrant_error"] = str(e)

    async def _test_storage_systems(self):
        """Test storage systems (MinIO, volumes)."""
        logger.info("Testing storage systems...")

        # Test MinIO
        await self._test_minio()

        # Test Docker volumes
        await self._test_docker_volumes()

    async def _test_minio(self):
        """Test MinIO object storage."""
        try:
            url = f"{self.base_url}:9000/minio/health/live"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    success = response.status == 200

            if success:
                logger.info("✅ MinIO is healthy")
                self.test_results["minio_healthy"] = True
            else:
                logger.warning("⚠️  MinIO health check failed")
                self.test_results["minio_healthy"] = False

        except Exception as e:
            logger.error(f"MinIO test failed: {e}")
            self.test_results["minio_error"] = str(e)

    async def _test_docker_volumes(self):
        """Test Docker volume functionality."""
        try:
            # Check if volumes exist and are accessible
            result = subprocess.run(
                ["docker", "volume", "ls", "--format", "table {{.Name}}"],
                capture_output=True, text=True
            )

            if result.returncode == 0:
                volumes = result.stdout.strip().split('\n')[1:]  # Skip header
                ai_security_volumes = [v for v in volumes if 'ai-security' in v]

                self.test_results["docker_volumes_count"] = len(volumes)
                self.test_results["ai_security_volumes"] = len(ai_security_volumes)

                logger.info(f"✅ Found {len(volumes)} Docker volumes, {len(ai_security_volumes)} AI Security volumes")
            else:
                logger.warning("⚠️  Docker volume check failed")

        except Exception as e:
            logger.error(f"Docker volume test failed: {e}")

    async def _test_monitoring_stack(self):
        """Test monitoring stack (Prometheus, Grafana, Loki, Tempo)."""
        logger.info("Testing monitoring stack...")

        # Test Prometheus
        await self._test_prometheus()

        # Test Grafana
        await self._test_grafana()

    async def _test_prometheus(self):
        """Test Prometheus metrics collection."""
        try:
            url = f"{self.base_url}:9090/-/healthy"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    success = response.status == 200

            if success:
                logger.info("✅ Prometheus is healthy")
                self.test_results["prometheus_healthy"] = True
            else:
                logger.warning("⚠️  Prometheus health check failed")
                self.test_results["prometheus_healthy"] = False

        except Exception as e:
            logger.error(f"Prometheus test failed: {e}")
            self.test_results["prometheus_error"] = str(e)

    async def _test_grafana(self):
        """Test Grafana dashboard."""
        try:
            url = f"{self.base_url}:3000/api/health"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    success = response.status == 200

            if success:
                logger.info("✅ Grafana is healthy")
                self.test_results["grafana_healthy"] = True
            else:
                logger.warning("⚠️  Grafana health check failed")
                self.test_results["grafana_healthy"] = False

        except Exception as e:
            logger.error(f"Grafana test failed: {e}")
            self.test_results["grafana_error"] = str(e)

    async def _test_performance_benchmarks(self):
        """Run basic performance benchmarks."""
        logger.info("Running performance benchmarks...")

        start_time = time.time()

        # Test 1: Service response times
        await self._benchmark_service_response_times()

        # Test 2: Memory usage
        await self._benchmark_memory_usage()

        # Test 3: Network latency
        await self._benchmark_network_latency()

        end_time = time.time()
        self.test_results["benchmark_duration"] = end_time - start_time

    async def _benchmark_service_response_times(self):
        """Benchmark service response times."""
        response_times = {}

        async with aiohttp.ClientSession() as session:
            for service_name, config in self.services.items():
                if "health_path" in config:
                    url = f"{self.base_url}:{config['port']}{config['health_path']}"

                    start_time = time.time()
                    try:
                        async with session.get(url, timeout=10) as response:
                            end_time = time.time()
                            response_time = (end_time - start_time) * 1000  # ms

                            response_times[service_name] = response_time
                            logger.info(f"📊 {service_name}: {response_time:.1f}ms")

                    except Exception as e:
                        response_times[service_name] = -1
                        logger.error(f"❌ {service_name} response time test failed: {e}")

        self.test_results["response_times"] = response_times

    async def _benchmark_memory_usage(self):
        """Benchmark memory usage."""
        try:
            # Get Docker container memory usage
            result = subprocess.run(
                ["docker", "stats", "--no-stream", "--format", "table {{.Name}}\\t{{.MemUsage}}"],
                capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                memory_usage = {}

                for line in lines:
                    if line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            container_name = parts[0].strip()
                            memory = parts[1].strip()
                            memory_usage[container_name] = memory

                self.test_results["memory_usage"] = memory_usage
                logger.info(f"📊 Memory usage captured for {len(memory_usage)} containers")
            else:
                logger.warning("⚠️  Memory usage check failed")

        except Exception as e:
            logger.error(f"Memory benchmark failed: {e}")

    async def _benchmark_network_latency(self):
        """Benchmark network latency."""
        try:
            # Simple ping test to key services
            latency_results = {}

            for service_name, config in self.services.items():
                port = config["port"]

                start_time = time.time()
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)

                try:
                    result = sock.connect_ex(('localhost', port))
                    end_time = time.time()

                    if result == 0:
                        latency = (end_time - start_time) * 1000  # ms
                        latency_results[service_name] = latency
                        logger.info(f"📊 {service_name} latency: {latency:.1f}ms")
                    else:
                        latency_results[service_name] = -1

                except Exception as e:
                    latency_results[service_name] = -1
                finally:
                    sock.close()

            self.test_results["network_latency"] = latency_results

        except Exception as e:
            logger.error(f"Network latency benchmark failed: {e}")

    def _generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        end_time = time.time()
        duration = end_time - self.start_time

        # Calculate summary statistics
        total_tests = len([k for k in self.test_results.keys() if k.endswith('_healthy')])
        passed_tests = len([k for k, v in self.test_results.items() if k.endswith('_healthy') and v is True])
        failed_tests = total_tests - passed_tests

        # Determine overall status
        critical_services = ["frigate", "timescaledb", "redis"]
        critical_healthy = all(
            self.test_results.get(f"{service}_healthy", False)
            for service in critical_services
        )

        overall_status = "PASS" if critical_healthy and failed_tests == 0 else "WARN"
        if failed_tests > total_tests // 2:
            overall_status = "FAIL"

        report = {
            "test_summary": {
                "overall_status": overall_status,
                "total_duration": round(duration, 2),
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": round(passed_tests / total_tests * 100, 1) if total_tests > 0 else 0,
                "timestamp": datetime.utcnow().isoformat()
            },
            "detailed_results": self.test_results,
            "recommendations": self._generate_recommendations()
        }

        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []

        if not self.test_results.get("gpu_available", False):
            recommendations.append("⚠️  No GPU detected - install NVIDIA drivers and CUDA toolkit")

        if not self.test_results.get("docker_running", False):
            recommendations.append("❌ Docker services not running - start with 'make dev'")

        if not self.test_results.get("timescaledb_healthy", False):
            recommendations.append("❌ TimescaleDB not accessible - check database configuration")

        if not self.test_results.get("redis_healthy", False):
            recommendations.append("❌ Redis not accessible - check Redis configuration")

        # Performance recommendations
        slow_services = [
            service for service, time_ms in self.test_results.get("response_times", {}).items()
            if time_ms > 1000  # Slower than 1 second
        ]

        if slow_services:
            recommendations.append(f"🐌 Slow services detected: {', '.join(slow_services)} - check system resources")

        if not recommendations:
            recommendations.append("✅ All systems operational - ready for threat detection testing")

        return recommendations


async def main():
    """Main test execution function."""
    tester = InfrastructureTester()

    try:
        report = await tester.run_all_tests()

        # Print summary
        summary = report["test_summary"]
        print("\n" + "="*60)
        print("🏗️  AI SECURITY LAB v4.0 - INFRASTRUCTURE TEST REPORT")
        print("="*60)
        print(f"Status: {summary['overall_status']}")
        print(f"Duration: {summary['total_duration']".2f"}s")
        print(f"Tests: {summary['passed_tests']}/{summary['total_tests']} passed ({summary['success_rate']}%)")
        print(f"Timestamp: {summary['timestamp']}")
        print()

        # Print recommendations
        if report["recommendations"]:
            print("📋 RECOMMENDATIONS:")
            for rec in report["recommendations"]:
                print(f"  {rec}")
            print()

        # Save detailed report
        with open("ai-security-lab-v4/tests/infrastructure_test_report.json", "w") as f:
            json.dump(report, f, indent=2)

        print("💾 Detailed report saved to: tests/infrastructure_test_report.json")

        # Exit with appropriate code
        if summary["overall_status"] == "FAIL":
            sys.exit(1)
        elif summary["overall_status"] == "WARN":
            sys.exit(0)  # Warning but not failure
        else:
            print("🎉 All infrastructure tests passed!")
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
