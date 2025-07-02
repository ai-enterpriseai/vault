"""
Real Qdrant Database Integration Tests
Tests actual database operations with live Qdrant instance and authentic data
"""

import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, List

# Add framework to path
sys.path.append(str(Path(__file__).parent.parent))
from framework import AuthenticTester, TestResult

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent / "backend"))

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False


class DatabaseIntegrationTester(AuthenticTester):
    """Test real Qdrant database operations with live connections."""
    
    def __init__(self, config_path=None):
        """Initialize database tester with real Qdrant connection."""
        super().__init__(config_path)
        self.qdrant_client = None
        self.test_collection_name = f"test_collection_{self.session_id}"
        
    async def setup_real_database_connection(self):
        """Setup connection to real Qdrant instance."""
        if not QDRANT_AVAILABLE:
            raise RuntimeError("Qdrant client not available - install qdrant-client")
        
        try:
            self.qdrant_client = QdrantClient(
                url=self.config.get('qdrant_url'),
                api_key=self.config.get('qdrant_api_key'),
                timeout=30.0
            )
            
            # Test connection
            collections = self.qdrant_client.get_collections()
            print(f"✅ Connected to Qdrant: {len(collections.collections)} collections found")
            
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Qdrant: {e}")
    
    async def test_collection_operations(self, test_data: Dict[str, Any]):
        """Test real collection create, update, delete operations."""
        
        # Create test collection
        collection_config = models.VectorParams(
            size=test_data.get('vector_size', 768),
            distance=models.Distance.COSINE
        )
        
        self.qdrant_client.create_collection(
            collection_name=self.test_collection_name,
            vectors_config=collection_config
        )
        
        # Verify collection exists
        collections = self.qdrant_client.get_collections()
        collection_names = [col.name for col in collections.collections]
        assert self.test_collection_name in collection_names, "Collection not created"
        
        # Get collection info
        collection_info = self.qdrant_client.get_collection(self.test_collection_name)
        assert collection_info.config.params.vectors.size == test_data.get('vector_size', 768)
        
        print(f"✅ Collection {self.test_collection_name} created successfully")
    
    async def test_vector_operations(self, test_data: Dict[str, Any]):
        """Test real vector insert, search, and delete operations."""
        
        # Generate test vectors
        vector_size = test_data.get('vector_size', 768)
        num_vectors = test_data.get('num_vectors', 100)
        
        # Create authentic-like vectors (random but consistent)
        import random
        random.seed(42)  # Reproducible test data
        
        test_points = []
        for i in range(num_vectors):
            vector = [random.uniform(-1.0, 1.0) for _ in range(vector_size)]
            test_points.append(models.PointStruct(
                id=i,
                vector=vector,
                payload={
                    "text": f"Test document {i}",
                    "category": f"category_{i % 5}",
                    "timestamp": f"2024-01-{(i % 28) + 1:02d}",
                    "source": "authentic_test_data"
                }
            ))
        
        # Insert vectors
        operation_info = self.qdrant_client.upsert(
            collection_name=self.test_collection_name,
            points=test_points
        )
        
        assert operation_info.status == models.UpdateStatus.COMPLETED
        print(f"✅ Inserted {num_vectors} vectors successfully")
        
        # Test search operations
        query_vector = [random.uniform(-1.0, 1.0) for _ in range(vector_size)]
        
        search_result = self.qdrant_client.search(
            collection_name=self.test_collection_name,
            query_vector=query_vector,
            limit=10
        )
        
        assert len(search_result) > 0, "Search returned no results"
        assert all(hasattr(point, 'score') for point in search_result), "Search results missing scores"
        
        print(f"✅ Vector search returned {len(search_result)} results")
        
        # Test filtering
        filtered_search = self.qdrant_client.search(
            collection_name=self.test_collection_name,
            query_vector=query_vector,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="category",
                        match=models.MatchValue(value="category_0")
                    )
                ]
            ),
            limit=5
        )
        
        assert len(filtered_search) > 0, "Filtered search returned no results"
        print(f"✅ Filtered search returned {len(filtered_search)} results")
    
    async def test_performance_benchmarks(self, test_data: Dict[str, Any]):
        """Test database performance with production-like loads."""
        
        # Test batch operations
        batch_size = test_data.get('batch_size', 1000)
        vector_size = test_data.get('vector_size', 768)
        
        import time
        import random
        random.seed(42)
        
        # Generate larger batch for performance testing
        large_batch = []
        for i in range(batch_size):
            vector = [random.uniform(-1.0, 1.0) for _ in range(vector_size)]
            large_batch.append(models.PointStruct(
                id=i + 10000,  # Avoid ID conflicts
                vector=vector,
                payload={
                    "text": f"Performance test document {i}",
                    "batch_id": "performance_test",
                    "size": len(f"Performance test document {i}")
                }
            ))
        
        # Time batch insert
        start_time = time.time()
        operation_info = self.qdrant_client.upsert(
            collection_name=self.test_collection_name,
            points=large_batch
        )
        insert_time = time.time() - start_time
        
        assert operation_info.status == models.UpdateStatus.COMPLETED
        
        # Performance metrics
        vectors_per_second = batch_size / insert_time
        print(f"✅ Batch insert performance: {vectors_per_second:.2f} vectors/second")
        
        # Test search performance
        query_vector = [random.uniform(-1.0, 1.0) for _ in range(vector_size)]
        
        search_times = []
        for _ in range(10):
            start_time = time.time()
            search_result = self.qdrant_client.search(
                collection_name=self.test_collection_name,
                query_vector=query_vector,
                limit=50
            )
            search_time = time.time() - start_time
            search_times.append(search_time)
            
            assert len(search_result) > 0
        
        avg_search_time = sum(search_times) / len(search_times)
        print(f"✅ Average search time: {avg_search_time * 1000:.2f}ms")
        
        # Validate performance benchmarks
        assert vectors_per_second > 100, f"Insert performance too slow: {vectors_per_second} vectors/sec"
        assert avg_search_time < 0.5, f"Search performance too slow: {avg_search_time}s"
        
        return {
            "insert_performance": vectors_per_second,
            "avg_search_time": avg_search_time,
            "batch_size": batch_size
        }
    
    async def test_concurrent_operations(self, test_data: Dict[str, Any]):
        """Test concurrent database operations with real load."""
        
        async def concurrent_search(query_id: int):
            """Perform concurrent search operation."""
            import random
            random.seed(query_id)
            
            vector_size = test_data.get('vector_size', 768)
            query_vector = [random.uniform(-1.0, 1.0) for _ in range(vector_size)]
            
            search_result = self.qdrant_client.search(
                collection_name=self.test_collection_name,
                query_vector=query_vector,
                limit=20
            )
            
            return len(search_result)
        
        # Run concurrent searches
        num_concurrent = test_data.get('concurrent_requests', 20)
        
        import time
        start_time = time.time()
        
        # Use asyncio.gather for concurrent execution
        tasks = [concurrent_search(i) for i in range(num_concurrent)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        concurrent_time = time.time() - start_time
        
        # Validate results
        successful_results = [r for r in results if isinstance(r, int)]
        failed_results = [r for r in results if not isinstance(r, int)]
        
        assert len(successful_results) > 0, "No concurrent searches succeeded"
        
        success_rate = len(successful_results) / len(results)
        print(f"✅ Concurrent operations: {success_rate * 100:.1f}% success rate")
        print(f"✅ Concurrent performance: {num_concurrent / concurrent_time:.2f} operations/second")
        
        # Performance validation
        assert success_rate > 0.9, f"Concurrent success rate too low: {success_rate}"
        
        return {
            "concurrent_requests": num_concurrent,
            "success_rate": success_rate,
            "total_time": concurrent_time,
            "failed_requests": len(failed_results)
        }
    
    async def cleanup_test_resources(self):
        """Clean up test collection and resources."""
        try:
            if self.qdrant_client and self.test_collection_name:
                # Delete test collection
                self.qdrant_client.delete_collection(self.test_collection_name)
                print(f"✅ Cleaned up test collection: {self.test_collection_name}")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")


async def run_database_integration_tests():
    """Execute comprehensive database integration tests."""
    
    tester = DatabaseIntegrationTester()
    
    # Test configuration
    test_config = {
        'vector_size': 768,
        'num_vectors': 500,
        'batch_size': 1000,
        'concurrent_requests': 25
    }
    
    try:
        # Setup
        await tester.setup_real_database_connection()
        
        # Execute tests
        test_results = []
        
        # Test 1: Collection Operations
        result = await tester.execute_test(
            "collection_operations",
            tester.test_collection_operations,
            test_config
        )
        test_results.append(result)
        
        # Test 2: Vector Operations
        result = await tester.execute_test(
            "vector_operations", 
            tester.test_vector_operations,
            test_config
        )
        test_results.append(result)
        
        # Test 3: Performance Benchmarks
        result = await tester.execute_test(
            "performance_benchmarks",
            tester.test_performance_benchmarks,
            test_config
        )
        test_results.append(result)
        
        # Test 4: Concurrent Operations
        result = await tester.execute_test(
            "concurrent_operations",
            tester.test_concurrent_operations,
            test_config
        )
        test_results.append(result)
        
        # Generate comprehensive report
        report_path = tester.save_session_report(
            Path(__file__).parent.parent / "results" / "reports"
        )
        
        print(f"\n📊 Database Integration Test Report saved: {report_path}")
        
        # Print summary
        successful_tests = sum(1 for r in test_results if r.success)
        print(f"\n🎯 Database Tests Summary:")
        print(f"   Total Tests: {len(test_results)}")
        print(f"   Successful: {successful_tests}")
        print(f"   Failed: {len(test_results) - successful_tests}")
        print(f"   Success Rate: {successful_tests / len(test_results) * 100:.1f}%")
        
        return test_results
        
    finally:
        # Always cleanup
        await tester.cleanup_test_resources()


if __name__ == "__main__":
    # Run the tests
    asyncio.run(run_database_integration_tests())