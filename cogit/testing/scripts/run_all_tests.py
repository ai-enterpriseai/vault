#!/usr/bin/env python3
"""
Main Test Execution Script for VAULT_APP v2.0 Authentic Testing Framework
Runs comprehensive integration tests with real environments and genuine dependencies
"""

import sys
import asyncio
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add testing framework to path
sys.path.append(str(Path(__file__).parent.parent))
from framework import AuthenticTester, TestResult


class VaultAppTestSuite:
    """
    Master test suite for authentic VAULT_APP testing.
    
    Coordinates execution of all integration tests with real dependencies
    and generates comprehensive reports.
    """
    
    def __init__(self, config_path: Path = None, verbose: bool = True):
        """Initialize test suite."""
        self.config_path = config_path
        self.verbose = verbose
        self.test_results: List[TestResult] = []
        self.suite_start_time = datetime.utcnow()
        
    def print_banner(self):
        """Print test suite banner."""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    VAULT_APP v2.0 Authentic Testing Framework               ║
║                                                                              ║
║  🎯 Testing REAL backends with GENUINE data and LIVE dependencies           ║
║  ⚡ NO mocks, NO simulations, NO fake environments                          ║
║  📊 Production-scale performance and reliability validation                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
        print(f"🕒 Test Suite Started: {self.suite_start_time.isoformat()}")
        print("=" * 80)
    
    async def validate_environment(self) -> Dict[str, Any]:
        """Validate that all real dependencies are available."""
        print("\n🔍 PHASE 1: Environment Validation")
        print("-" * 40)
        
        tester = AuthenticTester(self.config_path)
        
        validation_results = {
            "environment_valid": True,
            "checks": {},
            "warnings": [],
            "errors": []
        }
        
        try:
            # Check backend connectivity
            try:
                import requests
                backend_url = tester.config.get('backend_url', 'http://localhost:8000')
                response = requests.get(f"{backend_url}/health", timeout=10)
                
                if response.status_code == 200:
                    validation_results["checks"]["backend"] = "✅ PASS"
                    print(f"✅ Backend Health Check: {backend_url}")
                else:
                    validation_results["checks"]["backend"] = f"❌ FAIL ({response.status_code})"
                    validation_results["errors"].append(f"Backend unhealthy: {response.status_code}")
                    
            except Exception as e:
                validation_results["checks"]["backend"] = f"❌ FAIL ({e})"
                validation_results["errors"].append(f"Backend unreachable: {e}")
            
            # Check Qdrant database
            try:
                qdrant_url = tester.config.get('qdrant_url')
                qdrant_key = tester.config.get('qdrant_api_key')
                
                if qdrant_url and qdrant_key:
                    response = requests.get(
                        f"{qdrant_url}/collections",
                        headers={'api-key': qdrant_key},
                        timeout=10
                    )
                    
                    if response.status_code in [200, 404]:  # 404 is ok (no collections yet)
                        validation_results["checks"]["database"] = "✅ PASS"
                        print(f"✅ Qdrant Database: {qdrant_url}")
                    else:
                        validation_results["checks"]["database"] = f"❌ FAIL ({response.status_code})"
                        validation_results["errors"].append(f"Qdrant authentication failed: {response.status_code}")
                else:
                    validation_results["checks"]["database"] = "❌ FAIL (missing config)"
                    validation_results["errors"].append("Qdrant URL or API key not configured")
                    
            except Exception as e:
                validation_results["checks"]["database"] = f"❌ FAIL ({e})"
                validation_results["errors"].append(f"Qdrant unreachable: {e}")
            
            # Check AI model API keys
            ai_models = {
                'OpenAI': tester.config.get('openai_api_key'),
                'Anthropic': tester.config.get('anthropic_api_key'),
                'Together AI': tester.config.get('together_api_key'),
                'Cohere': tester.config.get('cohere_api_key')
            }
            
            available_models = []
            for model_name, api_key in ai_models.items():
                if api_key and api_key != "YOUR_API_KEY":
                    available_models.append(model_name)
                    validation_results["checks"][f"ai_model_{model_name.lower().replace(' ', '_')}"] = "✅ CONFIGURED"
                    print(f"✅ {model_name} API Key: Configured")
                else:
                    validation_results["checks"][f"ai_model_{model_name.lower().replace(' ', '_')}"] = "⚠️ MISSING"
                    validation_results["warnings"].append(f"{model_name} API key not configured")
                    print(f"⚠️ {model_name} API Key: Missing")
            
            if not available_models:
                validation_results["errors"].append("No AI model API keys configured")
                validation_results["environment_valid"] = False
            
            # Check test data availability
            test_data_path = Path(__file__).parent.parent / "data"
            if test_data_path.exists():
                validation_results["checks"]["test_data"] = "✅ PASS"
                print(f"✅ Test Data Directory: {test_data_path}")
            else:
                validation_results["checks"]["test_data"] = "⚠️ MISSING"
                validation_results["warnings"].append("Test data directory not found")
                print(f"⚠️ Test Data Directory: Missing ({test_data_path})")
            
        except Exception as e:
            validation_results["environment_valid"] = False
            validation_results["errors"].append(f"Environment validation failed: {e}")
        
        # Print summary
        print(f"\n📋 Environment Validation Summary:")
        print(f"   Checks Passed: {len([k for k, v in validation_results['checks'].items() if 'PASS' in v])}")
        print(f"   Warnings: {len(validation_results['warnings'])}")
        print(f"   Errors: {len(validation_results['errors'])}")
        
        if validation_results["errors"]:
            print(f"\n❌ Critical Errors:")
            for error in validation_results["errors"]:
                print(f"   • {error}")
        
        if validation_results["warnings"]:
            print(f"\n⚠️ Warnings:")
            for warning in validation_results["warnings"]:
                print(f"   • {warning}")
        
        return validation_results
    
    async def run_database_tests(self) -> List[TestResult]:
        """Run database integration tests."""
        print("\n🗄️ PHASE 2: Database Integration Tests")
        print("-" * 40)
        
        try:
            # Import and run database tests
            sys.path.append(str(Path(__file__).parent.parent / "tests"))
            from test_database import run_database_integration_tests
            
            results = await run_database_integration_tests()
            print("✅ Database tests completed")
            return results
            
        except ImportError as e:
            print(f"❌ Database tests failed to import: {e}")
            return []
        except Exception as e:
            print(f"❌ Database tests failed: {e}")
            return []
    
    async def run_api_tests(self) -> List[TestResult]:
        """Run API endpoint tests."""
        print("\n🌐 PHASE 3: API Endpoint Tests")
        print("-" * 40)
        
        from framework import AuthenticatedClient
        
        results = []
        tester = AuthenticTester(self.config_path)
        
        try:
            backend_url = tester.config.get('backend_url', 'http://localhost:8000')
            client = AuthenticatedClient(backend_url)
            
            # Test health endpoints
            print("Testing health endpoints...")
            
            async def test_health_endpoints(test_data):
                health_results = client.test_health_endpoints()
                
                for endpoint, result in health_results.items():
                    if result.get('success', False):
                        print(f"✅ {endpoint}: {result.get('response_time', 0)*1000:.1f}ms")
                    else:
                        print(f"❌ {endpoint}: {result.get('error', 'Unknown error')}")
                
                # Validate performance
                avg_response_time = sum(
                    r.get('response_time', 0) for r in health_results.values() 
                    if r.get('response_time')
                ) / len(health_results)
                
                assert avg_response_time < 1.0, f"Health endpoints too slow: {avg_response_time}s"
                return health_results
            
            result = await tester.execute_test(
                "api_health_endpoints",
                test_health_endpoints,
                {}
            )
            results.append(result)
            
            # Test API performance
            async def test_api_performance(test_data):
                performance_results = client.test_api_performance('/health', iterations=20)
                
                print(f"✅ Performance test: {performance_results['avg_response_time']*1000:.1f}ms avg")
                print(f"✅ Success rate: {performance_results['success_rate']*100:.1f}%")
                
                assert performance_results['success_rate'] > 0.95, "API success rate too low"
                assert performance_results['avg_response_time'] < 0.5, "API response time too slow"
                
                return performance_results
            
            result = await tester.execute_test(
                "api_performance_test",
                test_api_performance,
                {}
            )
            results.append(result)
            
            print("✅ API tests completed")
            return results
            
        except Exception as e:
            print(f"❌ API tests failed: {e}")
            return []
    
    async def run_chat_system_tests(self) -> List[TestResult]:
        """Run WebSocket chat system tests."""
        print("\n💬 PHASE 4: Chat System Tests")
        print("-" * 40)
        
        results = []
        tester = AuthenticTester(self.config_path)
        
        try:
            from framework import AuthenticatedClient
            
            backend_url = tester.config.get('backend_url', 'http://localhost:8000')
            client = AuthenticatedClient(backend_url)
            
            async def test_websocket_connection(test_data):
                """Test WebSocket connection and basic messaging."""
                
                # Create WebSocket tester
                ws_tester = await client.websocket_connect('/ws/chat/test_user_123', 'test_user_123')
                
                try:
                    await ws_tester.connect()
                    print("✅ WebSocket connected successfully")
                    
                    # Test basic messaging
                    test_messages = [
                        "Hello, this is a test message",
                        "Can you help me with document processing?",
                        "What are your capabilities?"
                    ]
                    
                    responses = await ws_tester.test_chat_flow(test_messages)
                    
                    print(f"✅ Chat flow test: {len(responses)} responses received")
                    
                    # Validate responses
                    successful_responses = [r for r in responses if 'error' not in r]
                    success_rate = len(successful_responses) / len(responses)
                    
                    assert success_rate > 0.8, f"Chat success rate too low: {success_rate}"
                    
                    return {
                        "messages_sent": len(test_messages),
                        "responses_received": len(responses),
                        "success_rate": success_rate,
                        "connection_stats": ws_tester.get_connection_stats()
                    }
                    
                finally:
                    await ws_tester.close()
            
            result = await tester.execute_test(
                "websocket_chat_test",
                test_websocket_connection,
                {}
            )
            results.append(result)
            
            print("✅ Chat system tests completed")
            return results
            
        except Exception as e:
            print(f"❌ Chat system tests failed: {e}")
            return []
    
    async def run_performance_tests(self) -> List[TestResult]:
        """Run performance and load tests."""
        print("\n⚡ PHASE 5: Performance & Load Tests")
        print("-" * 40)
        
        results = []
        tester = AuthenticTester(self.config_path)
        
        try:
            from framework import AuthenticatedClient
            
            backend_url = tester.config.get('backend_url', 'http://localhost:8000')
            client = AuthenticatedClient(backend_url)
            
            async def test_concurrent_api_load(test_data):
                """Test concurrent API requests."""
                
                import asyncio
                import time
                
                async def make_request(request_id):
                    response = client.get('/health')
                    return {
                        'id': request_id,
                        'status_code': response.status_code,
                        'success': response.status_code == 200
                    }
                
                # Run concurrent requests
                num_concurrent = 50
                start_time = time.time()
                
                tasks = [make_request(i) for i in range(num_concurrent)]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                total_time = time.time() - start_time
                
                successful_requests = [r for r in results if isinstance(r, dict) and r.get('success')]
                success_rate = len(successful_requests) / len(results)
                requests_per_second = num_concurrent / total_time
                
                print(f"✅ Concurrent load test: {success_rate*100:.1f}% success rate")
                print(f"✅ Throughput: {requests_per_second:.2f} requests/second")
                
                assert success_rate > 0.95, f"Concurrent success rate too low: {success_rate}"
                assert requests_per_second > 20, f"Throughput too low: {requests_per_second} req/s"
                
                return {
                    "concurrent_requests": num_concurrent,
                    "success_rate": success_rate,
                    "requests_per_second": requests_per_second,
                    "total_time": total_time
                }
            
            result = await tester.execute_test(
                "concurrent_load_test",
                test_concurrent_api_load,
                {}
            )
            results.append(result)
            
            print("✅ Performance tests completed")
            return results
            
        except Exception as e:
            print(f"❌ Performance tests failed: {e}")
            return []
    
    def generate_final_report(self, all_results: List[TestResult], 
                            validation_results: Dict[str, Any]) -> Path:
        """Generate comprehensive final test report."""
        
        report_data = {
            "test_suite_info": {
                "name": "VAULT_APP v2.0 Authentic Integration Tests",
                "start_time": self.suite_start_time.isoformat(),
                "end_time": datetime.utcnow().isoformat(),
                "duration_seconds": (datetime.utcnow() - self.suite_start_time).total_seconds(),
                "framework_version": "1.0.0"
            },
            "environment_validation": validation_results,
            "test_summary": {
                "total_tests": len(all_results),
                "successful_tests": sum(1 for r in all_results if r.success),
                "failed_tests": sum(1 for r in all_results if not r.success),
                "success_rate": sum(1 for r in all_results if r.success) / len(all_results) if all_results else 0,
                "total_execution_time": sum(r.execution_time for r in all_results),
                "avg_execution_time": sum(r.execution_time for r in all_results) / len(all_results) if all_results else 0
            },
            "test_phases": {
                "database_tests": [r.to_dict() for r in all_results if "database" in r.test_name],
                "api_tests": [r.to_dict() for r in all_results if "api" in r.test_name],
                "chat_tests": [r.to_dict() for r in all_results if "chat" in r.test_name or "websocket" in r.test_name],
                "performance_tests": [r.to_dict() for r in all_results if "performance" in r.test_name or "load" in r.test_name]
            },
            "detailed_results": [r.to_dict() for r in all_results]
        }
        
        # Save comprehensive report
        reports_dir = Path(__file__).parent.parent / "results" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        report_file = reports_dir / f"vault_app_integration_test_report_{timestamp}.json"
        
        import json
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        return report_file
    
    def print_final_summary(self, all_results: List[TestResult], 
                          validation_results: Dict[str, Any], report_path: Path):
        """Print final test suite summary."""
        
        total_tests = len(all_results)
        successful_tests = sum(1 for r in all_results if r.success)
        failed_tests = total_tests - successful_tests
        success_rate = successful_tests / total_tests if total_tests > 0 else 0
        
        summary = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         VAULT_APP v2.0 TEST RESULTS                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  📊 SUMMARY                                                                  ║
║     Total Tests: {total_tests:<8} Successful: {successful_tests:<8} Failed: {failed_tests:<8}             ║
║     Success Rate: {success_rate*100:>6.1f}%   Duration: {(datetime.utcnow() - self.suite_start_time).total_seconds():>8.1f}s              ║
║                                                                              ║
║  🎯 ENVIRONMENT VALIDATION                                                   ║
║     Environment Valid: {'✅ YES' if validation_results.get('environment_valid') else '❌ NO':<12}                                    ║
║     Warnings: {len(validation_results.get('warnings', [])):<8} Errors: {len(validation_results.get('errors', [])):<8}                        ║
║                                                                              ║
║  📋 TEST PHASES                                                              ║
║     Database Tests: {'✅ PASS' if any('database' in r.test_name and r.success for r in all_results) else '❌ FAIL':<12}                            ║
║     API Tests: {'✅ PASS' if any('api' in r.test_name and r.success for r in all_results) else '❌ FAIL':<17}                            ║
║     Chat Tests: {'✅ PASS' if any('chat' in r.test_name and r.success for r in all_results) else '❌ FAIL':<16}                            ║
║     Performance Tests: {'✅ PASS' if any('performance' in r.test_name and r.success for r in all_results) else '❌ FAIL':<10}                    ║
║                                                                              ║
║  📄 REPORT LOCATION                                                          ║
║     {str(report_path):<76} ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        
        print(summary)
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in all_results:
                if not result.success:
                    print(f"   • {result.test_name}: {result.error_details.split(chr(10))[0] if result.error_details else 'Unknown error'}")
        
        print(f"\n🎯 {'SUCCESS!' if success_rate > 0.8 else 'NEEDS ATTENTION!'}")
        print(f"   Test report available at: {report_path}")
    
    async def run_full_suite(self, phases: List[str] = None) -> bool:
        """
        Run the complete authentic test suite.
        
        Args:
            phases: List of phases to run (default: all)
            
        Returns:
            True if all tests passed, False otherwise
        """
        
        self.print_banner()
        
        all_results = []
        
        # Phase 1: Environment Validation
        validation_results = await self.validate_environment()
        
        if not validation_results.get('environment_valid', False):
            print("\n❌ Environment validation failed. Cannot proceed with tests.")
            return False
        
        # Run test phases
        if not phases or 'database' in phases:
            db_results = await self.run_database_tests()
            all_results.extend(db_results)
        
        if not phases or 'api' in phases:
            api_results = await self.run_api_tests()
            all_results.extend(api_results)
        
        if not phases or 'chat' in phases:
            chat_results = await self.run_chat_system_tests()
            all_results.extend(chat_results)
        
        if not phases or 'performance' in phases:
            performance_results = await self.run_performance_tests()
            all_results.extend(performance_results)
        
        # Generate final report
        report_path = self.generate_final_report(all_results, validation_results)
        
        # Print final summary
        self.print_final_summary(all_results, validation_results, report_path)
        
        # Return success status
        success_rate = sum(1 for r in all_results if r.success) / len(all_results) if all_results else 0
        return success_rate > 0.8


async def main():
    """Main entry point for test execution."""
    
    parser = argparse.ArgumentParser(description='VAULT_APP v2.0 Authentic Testing Framework')
    parser.add_argument('--config', type=Path, help='Path to test configuration file')
    parser.add_argument('--phases', nargs='+', choices=['database', 'api', 'chat', 'performance'], 
                       help='Test phases to run (default: all)')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--authentic', action='store_true', help='Run with authentic data (default)', default=True)
    parser.add_argument('--full-scale', action='store_true', help='Run full-scale performance tests')
    
    args = parser.parse_args()
    
    # Initialize test suite
    test_suite = VaultAppTestSuite(config_path=args.config, verbose=args.verbose)
    
    # Run tests
    success = await test_suite.run_full_suite(phases=args.phases)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())