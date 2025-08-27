#!/usr/bin/env python3
"""
Performance test script for OpenMRS Bridge API
Compares optimized vs standard version
"""

import requests
import time
import asyncio
import aiohttp
import statistics
import json
from datetime import datetime
from typing import List, Dict, Any
import concurrent.futures

# Configuration
BASE_URL = "http://localhost:1221"
API_KEY = "omrs_abc123def456ghi789"  # Replace with your actual API key

# Headers for authentication
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


class PerformanceTester:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.results = {}
    
    def test_sync_endpoint(self, endpoint: str, method: str = "GET", data: dict = None, iterations: int = 100) -> Dict[str, Any]:
        """Test a synchronous endpoint"""
        print(f"🔍 Testing {method} {endpoint} ({iterations} iterations)...")
        
        times = []
        errors = 0
        
        for i in range(iterations):
            try:
                start_time = time.time()
                
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", headers=self.headers)
                elif method == "POST":
                    response = requests.post(f"{self.base_url}{endpoint}", headers=self.headers, json=data)
                elif method == "PATCH":
                    response = requests.patch(f"{self.base_url}{endpoint}", headers=self.headers, json=data)
                elif method == "PUT":
                    response = requests.put(f"{self.base_url}{endpoint}", headers=self.headers, json=data)
                
                end_time = time.time()
                
                if response.status_code == 200:
                    times.append(end_time - start_time)
                else:
                    errors += 1
                    
            except Exception as e:
                errors += 1
                print(f"   Error on iteration {i}: {e}")
        
        if times:
            return {
                "endpoint": endpoint,
                "method": method,
                "iterations": iterations,
                "successful_requests": len(times),
                "errors": errors,
                "average_time": statistics.mean(times),
                "median_time": statistics.median(times),
                "min_time": min(times),
                "max_time": max(times),
                "p95_time": statistics.quantiles(times, n=20)[18] if len(times) >= 20 else max(times),
                "p99_time": statistics.quantiles(times, n=100)[98] if len(times) >= 100 else max(times),
                "requests_per_second": len(times) / sum(times) if sum(times) > 0 else 0
            }
        else:
            return {
                "endpoint": endpoint,
                "method": method,
                "iterations": iterations,
                "successful_requests": 0,
                "errors": errors,
                "error": "All requests failed"
            }
    
    async def test_async_endpoint(self, session: aiohttp.ClientSession, endpoint: str, method: str = "GET", data: dict = None) -> float:
        """Test a single async request"""
        try:
            start_time = time.time()
            
            if method == "GET":
                async with session.get(f"{self.base_url}{endpoint}", headers=self.headers) as response:
                    await response.json()
            elif method == "POST":
                async with session.post(f"{self.base_url}{endpoint}", headers=self.headers, json=data) as response:
                    await response.json()
            elif method == "PATCH":
                async with session.patch(f"{self.base_url}{endpoint}", headers=self.headers, json=data) as response:
                    await response.json()
            elif method == "PUT":
                async with session.put(f"{self.base_url}{endpoint}", headers=self.headers, json=data) as response:
                    await response.json()
            
            end_time = time.time()
            return end_time - start_time
            
        except Exception as e:
            print(f"   Async error: {e}")
            return None
    
    async def test_concurrent_endpoint(self, endpoint: str, method: str = "GET", data: dict = None, concurrency: int = 10, total_requests: int = 100) -> Dict[str, Any]:
        """Test endpoint with concurrent requests"""
        print(f"🔍 Testing {method} {endpoint} (concurrent: {concurrency}, total: {total_requests})...")
        
        async with aiohttp.ClientSession() as session:
            # Create tasks
            tasks = []
            for i in range(total_requests):
                task = self.test_async_endpoint(session, endpoint, method, data)
                tasks.append(task)
            
            # Execute tasks with concurrency limit
            times = []
            semaphore = asyncio.Semaphore(concurrency)
            
            async def limited_task(task):
                async with semaphore:
                    return await task
            
            limited_tasks = [limited_task(task) for task in tasks]
            results = await asyncio.gather(*limited_tasks, return_exceptions=True)
            
            # Process results
            for result in results:
                if isinstance(result, (int, float)) and result is not None:
                    times.append(result)
            
            if times:
                return {
                    "endpoint": endpoint,
                    "method": method,
                    "concurrency": concurrency,
                    "total_requests": total_requests,
                    "successful_requests": len(times),
                    "errors": total_requests - len(times),
                    "average_time": statistics.mean(times),
                    "median_time": statistics.median(times),
                    "min_time": min(times),
                    "max_time": max(times),
                    "p95_time": statistics.quantiles(times, n=20)[18] if len(times) >= 20 else max(times),
                    "p99_time": statistics.quantiles(times, n=100)[98] if len(times) >= 100 else max(times),
                    "requests_per_second": len(times) / sum(times) if sum(times) > 0 else 0
                }
            else:
                return {
                    "endpoint": endpoint,
                    "method": method,
                    "concurrency": concurrency,
                    "total_requests": total_requests,
                    "successful_requests": 0,
                    "errors": total_requests,
                    "error": "All requests failed"
                }
    
    def run_basic_tests(self) -> Dict[str, Any]:
        """Run basic performance tests"""
        print("🚀 Running basic performance tests...")
        
        tests = [
            ("/health", "GET"),
            ("/api/v1/orders/", "GET"),
            ("/api/v1/observations/", "GET"),
            ("/stats", "GET"),
            ("/performance", "GET"),
        ]
        
        results = {}
        for endpoint, method in tests:
            result = self.test_sync_endpoint(endpoint, method, iterations=50)
            results[f"{method}_{endpoint}"] = result
        
        return results
    
    async def run_concurrent_tests(self) -> Dict[str, Any]:
        """Run concurrent performance tests"""
        print("🚀 Running concurrent performance tests...")
        
        tests = [
            ("/health", "GET"),
            ("/api/v1/orders/", "GET"),
            ("/api/v1/observations/", "GET"),
        ]
        
        results = {}
        for endpoint, method in tests:
            result = await self.test_concurrent_endpoint(endpoint, method, concurrency=20, total_requests=100)
            results[f"concurrent_{method}_{endpoint}"] = result
        
        return results
    
    def run_load_test(self) -> Dict[str, Any]:
        """Run load test with multiple concurrent users"""
        print("🚀 Running load test...")
        
        def simulate_user(user_id: int) -> Dict[str, Any]:
            """Simulate a single user making requests"""
            user_results = {}
            
            # Simulate user behavior
            endpoints = [
                ("/health", "GET"),
                ("/api/v1/orders/", "GET"),
                ("/api/v1/observations/", "GET"),
            ]
            
            for endpoint, method in endpoints:
                result = self.test_sync_endpoint(endpoint, method, iterations=10)
                user_results[f"user_{user_id}_{method}_{endpoint}"] = result
            
            return user_results
        
        # Simulate 5 concurrent users
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(simulate_user, i) for i in range(5)]
            results = {}
            
            for future in concurrent.futures.as_completed(futures):
                user_results = future.result()
                results.update(user_results)
        
        return results


async def main():
    """Run all performance tests"""
    print("🚀 OpenMRS Bridge API Performance Test")
    print("=" * 60)
    
    tester = PerformanceTester(BASE_URL, API_KEY)
    
    # Test 1: Basic performance tests
    print("\n📊 Test 1: Basic Performance Tests")
    print("-" * 40)
    basic_results = tester.run_basic_tests()
    
    # Test 2: Concurrent performance tests
    print("\n📊 Test 2: Concurrent Performance Tests")
    print("-" * 40)
    concurrent_results = await tester.run_concurrent_tests()
    
    # Test 3: Load test
    print("\n📊 Test 3: Load Test (5 Concurrent Users)")
    print("-" * 40)
    load_results = tester.run_load_test()
    
    # Combine all results
    all_results = {
        "basic_tests": basic_results,
        "concurrent_tests": concurrent_results,
        "load_tests": load_results,
        "timestamp": datetime.now().isoformat()
    }
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 PERFORMANCE TEST SUMMARY")
    print("=" * 60)
    
    # Basic tests summary
    print("\n🔍 Basic Tests Summary:")
    for test_name, result in basic_results.items():
        if "error" not in result:
            print(f"  {test_name}:")
            print(f"    Avg: {result['average_time']:.3f}s")
            print(f"    Median: {result['median_time']:.3f}s")
            print(f"    P95: {result['p95_time']:.3f}s")
            print(f"    RPS: {result['requests_per_second']:.1f}")
            print(f"    Success: {result['successful_requests']}/{result['iterations']}")
    
    # Concurrent tests summary
    print("\n🔍 Concurrent Tests Summary:")
    for test_name, result in concurrent_results.items():
        if "error" not in result:
            print(f"  {test_name}:")
            print(f"    Concurrency: {result['concurrency']}")
            print(f"    Avg: {result['average_time']:.3f}s")
            print(f"    Median: {result['median_time']:.3f}s")
            print(f"    P95: {result['p95_time']:.3f}s")
            print(f"    RPS: {result['requests_per_second']:.1f}")
            print(f"    Success: {result['successful_requests']}/{result['total_requests']}")
    
    # Save results to file
    with open(f"performance_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n💾 Results saved to performance_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    # Performance recommendations
    print("\n💡 Performance Recommendations:")
    print("  1. If average response time > 500ms: Consider database optimization")
    print("  2. If P95 > 2s: Consider caching or query optimization")
    print("  3. If RPS < 10: Consider connection pooling or async operations")
    print("  4. If error rate > 5%: Check database connectivity and API key validity")


if __name__ == "__main__":
    asyncio.run(main()) 