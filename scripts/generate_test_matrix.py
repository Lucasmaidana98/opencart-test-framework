#!/usr/bin/env python3
"""
Test Matrix Generator
Generates dynamic test execution matrix for GitHub Actions
Author: Lucas Maidana
"""

import json
import argparse
import os
from typing import List, Dict, Any


class TestMatrixGenerator:
    """Generates optimized test execution matrix for CI/CD pipeline"""
    
    def __init__(self):
        self.test_groups = {
            'frontend': {
                'tests': [
                    'test_user_registration',
                    'test_user_authentication', 
                    'test_product_catalog',
                    'test_shopping_cart',
                    'test_checkout_process'
                ],
                'parallel_capacity': 4,
                'execution_time': 8  # minutes
            },
            'backend': {
                'tests': [
                    'test_admin_authentication',
                    'test_product_management',
                    'test_order_management',
                    'test_customer_management'
                ],
                'parallel_capacity': 3,
                'execution_time': 6  # minutes
            },
            'integration': {
                'tests': [
                    'test_end_to_end_purchase',
                    'test_cross_browser_compatibility',
                    'test_email_notifications'
                ],
                'parallel_capacity': 2,
                'execution_time': 12  # minutes
            },
            'performance': {
                'tests': [
                    'test_page_load_performance',
                    'test_cart_performance',
                    'test_search_performance'
                ],
                'parallel_capacity': 2,
                'execution_time': 10  # minutes
            },
            'security': {
                'tests': [
                    'test_sql_injection_protection',
                    'test_xss_protection',
                    'test_authentication_security'
                ],
                'parallel_capacity': 2,
                'execution_time': 8  # minutes
            },
            'smoke': {
                'tests': [
                    'test_basic_functionality',
                    'test_critical_paths'
                ],
                'parallel_capacity': 1,
                'execution_time': 3  # minutes
            }
        }
        
        self.browsers = ['chrome', 'firefox', 'edge']
    
    def generate_matrix(self, 
                       test_suite: str = 'all',
                       browser: str = 'chrome', 
                       max_parallel: int = 20) -> Dict[str, Any]:
        """
        Generate test execution matrix
        
        Args:
            test_suite: Test suite to run (all, frontend, backend, etc.)
            browser: Browser to test (chrome, firefox, edge, all)
            max_parallel: Maximum parallel jobs
            
        Returns:
            Dict containing the test matrix
        """
        matrix_entries = []
        
        # Determine test groups to include
        if test_suite == 'all':
            selected_groups = list(self.test_groups.keys())
        else:
            selected_groups = [test_suite] if test_suite in self.test_groups else []
        
        # Determine browsers to include
        if browser == 'all':
            selected_browsers = self.browsers
        else:
            selected_browsers = [browser] if browser in self.browsers else ['chrome']
        
        # Generate matrix entries
        for group_name in selected_groups:
            group_config = self.test_groups[group_name]
            
            for browser_name in selected_browsers:
                # Determine chunking strategy based on test count and parallel capacity
                tests = group_config['tests']
                parallel_capacity = group_config['parallel_capacity']
                
                if len(tests) <= parallel_capacity:
                    # Run all tests in single chunk
                    matrix_entries.append({
                        'test-group': group_name,
                        'browser': browser_name,
                        'chunk': 'all',
                        'tests': tests,
                        'estimated-time': group_config['execution_time']
                    })
                else:
                    # Split into multiple chunks
                    chunk_size = max(1, len(tests) // parallel_capacity)
                    for i in range(0, len(tests), chunk_size):
                        chunk_tests = tests[i:i + chunk_size]
                        chunk_num = (i // chunk_size) + 1
                        
                        matrix_entries.append({
                            'test-group': group_name,
                            'browser': browser_name,
                            'chunk': f'chunk-{chunk_num}',
                            'tests': chunk_tests,
                            'estimated-time': group_config['execution_time'] // parallel_capacity
                        })
        
        # Optimize matrix to fit within max_parallel constraint
        optimized_matrix = self._optimize_matrix(matrix_entries, max_parallel)
        
        return {
            'include': optimized_matrix,
            'total_jobs': len(optimized_matrix),
            'estimated_total_time': self._calculate_total_time(optimized_matrix, max_parallel)
        }
    
    def _optimize_matrix(self, matrix_entries: List[Dict], max_parallel: int) -> List[Dict]:
        """
        Optimize matrix to respect parallel job limits
        
        Args:
            matrix_entries: List of matrix entries
            max_parallel: Maximum parallel jobs
            
        Returns:
            Optimized matrix entries
        """
        if len(matrix_entries) <= max_parallel:
            return matrix_entries
        
        # Sort by estimated execution time (longest first)
        sorted_entries = sorted(matrix_entries, 
                              key=lambda x: x['estimated-time'], 
                              reverse=True)
        
        # If we have too many jobs, we need to combine some
        if len(sorted_entries) > max_parallel:
            # For now, just take the first max_parallel entries
            # In a more sophisticated implementation, we could combine test chunks
            optimized = sorted_entries[:max_parallel]
            
            # Log what was excluded
            excluded = sorted_entries[max_parallel:]
            print(f"Warning: Excluded {len(excluded)} jobs due to parallel limit")
            for job in excluded:
                print(f"  - {job['test-group']} | {job['browser']} | {job['chunk']}")
            
            return optimized
        
        return sorted_entries
    
    def _calculate_total_time(self, matrix_entries: List[Dict], max_parallel: int) -> int:
        """
        Calculate estimated total execution time
        
        Args:
            matrix_entries: Matrix entries
            max_parallel: Maximum parallel jobs
            
        Returns:
            Estimated total time in minutes
        """
        if not matrix_entries:
            return 0
        
        # Sort by execution time
        times = sorted([entry['estimated-time'] for entry in matrix_entries], reverse=True)
        
        # Calculate time with parallel execution
        total_time = 0
        job_batches = [times[i:i + max_parallel] for i in range(0, len(times), max_parallel)]
        
        for batch in job_batches:
            # Each batch runs in parallel, so time is the longest job in the batch
            batch_time = max(batch) if batch else 0
            total_time += batch_time
        
        return total_time
    
    def generate_smoke_matrix(self) -> Dict[str, Any]:
        """Generate matrix for smoke tests only"""
        return self.generate_matrix(test_suite='smoke', browser='chrome', max_parallel=5)
    
    def generate_cross_browser_matrix(self) -> Dict[str, Any]:
        """Generate matrix for cross-browser testing"""
        return self.generate_matrix(test_suite='frontend', browser='all', max_parallel=15)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Generate test execution matrix')
    parser.add_argument('--test-suite', default='all', 
                       choices=['all', 'frontend', 'backend', 'integration', 'performance', 'security', 'smoke'],
                       help='Test suite to run')
    parser.add_argument('--browser', default='chrome',
                       choices=['chrome', 'firefox', 'edge', 'all'],
                       help='Browser to test')
    parser.add_argument('--max-parallel', type=int, default=20,
                       help='Maximum parallel jobs')
    parser.add_argument('--output-file', default='test_matrix.json',
                       help='Output file for matrix JSON')
    parser.add_argument('--pretty', action='store_true',
                       help='Pretty print JSON output')
    
    args = parser.parse_args()
    
    # Generate matrix
    generator = TestMatrixGenerator()
    matrix = generator.generate_matrix(
        test_suite=args.test_suite,
        browser=args.browser,
        max_parallel=args.max_parallel
    )
    
    # Output matrix
    indent = 2 if args.pretty else None
    matrix_json = json.dumps(matrix, indent=indent)
    
    # Write to file
    with open(args.output_file, 'w') as f:
        f.write(matrix_json)
    
    # Print summary
    print(f"Generated test matrix: {args.output_file}")
    print(f"Total jobs: {matrix['total_jobs']}")
    print(f"Estimated execution time: {matrix['estimated_total_time']} minutes")
    print(f"Max parallel jobs: {args.max_parallel}")
    
    # Print matrix for debugging
    if args.pretty:
        print("\nGenerated Matrix:")
        for entry in matrix['include']:
            print(f"  - {entry['test-group']} | {entry['browser']} | {entry['chunk']} "
                  f"({entry['estimated-time']}min)")


if __name__ == '__main__':
    main()