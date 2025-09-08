#!/usr/bin/env python3
"""
Step 9: Comprehensive Test Runner
Runs all 10 recipes against all diet combinations to generate robust error rate data.
"""

import sys
import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict

# Add src to path
sys.path.append('../src')

from test_recipes import get_test_recipes, get_diet_combinations, get_simple_diets, get_complex_diets
from recipe_transformer_cli import RecipeTransformer, RecipeInput

@dataclass
class TestResult:
    """Individual test result."""
    recipe_name: str
    recipe_category: str
    recipe_complexity: str
    diets: List[str]
    success: bool
    substitutions_made: int
    unchanged_ingredients: int
    warnings: List[str]
    error_message: str
    execution_time: float
    substitutions: List[Dict[str, Any]]

@dataclass
class TestSummary:
    """Overall test summary."""
    total_tests: int
    successful_tests: int
    failed_tests: int
    success_rate: float
    total_execution_time: float
    average_execution_time: float
    results_by_recipe: Dict[str, Dict[str, Any]]
    results_by_diet: Dict[str, Dict[str, Any]]
    results_by_complexity: Dict[str, Dict[str, Any]]

class ComprehensiveTestRunner:
    """Runs comprehensive tests across all recipes and diet combinations."""
    
    def __init__(self):
        self.transformer = RecipeTransformer()
        self.results: List[TestResult] = []
        self.start_time = None
        self.end_time = None
    
    def run_all_tests(self) -> TestSummary:
        """Run all tests and return comprehensive summary."""
        print("🧪 COMPREHENSIVE RECIPE TRANSFORMATION TESTING")
        print("=" * 60)
        
        self.start_time = time.time()
        recipes = get_test_recipes()
        diet_combinations = get_diet_combinations()
        
        total_tests = len(recipes) * len(diet_combinations)
        print(f"Running {total_tests} tests:")
        print(f"  • {len(recipes)} recipes")
        print(f"  • {len(diet_combinations)} diet combinations")
        print()
        
        test_count = 0
        for recipe in recipes:
            print(f"Testing {recipe.name} ({recipe.category}, {recipe.complexity})...")
            
            for diets in diet_combinations:
                test_count += 1
                result = self._run_single_test(recipe, diets)
                self.results.append(result)
                
                # Progress indicator
                if test_count % 10 == 0:
                    print(f"  Completed {test_count}/{total_tests} tests...")
        
        self.end_time = time.time()
        return self._generate_summary()
    
    def _run_single_test(self, recipe: Any, diets: List[str]) -> TestResult:
        """Run a single test case."""
        start_time = time.time()
        
        try:
            # Create RecipeInput
            recipe_input = RecipeInput(
                name=recipe.name,
                ingredients=recipe.ingredients,
                instructions=recipe.instructions,
                servings=recipe.servings
            )
            
            # Transform recipe
            result = self.transformer.transform_recipe(recipe_input, diets)
            
            execution_time = time.time() - start_time
            
            return TestResult(
                recipe_name=recipe.name,
                recipe_category=recipe.category,
                recipe_complexity=recipe.complexity,
                diets=diets,
                success=result.success,
                substitutions_made=len(result.substitutions),
                unchanged_ingredients=len(result.unchanged_ingredients),
                warnings=result.warnings,
                error_message="",
                execution_time=execution_time,
                substitutions=result.substitutions
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                recipe_name=recipe.name,
                recipe_category=recipe.category,
                recipe_complexity=recipe.complexity,
                diets=diets,
                success=False,
                substitutions_made=0,
                unchanged_ingredients=0,
                warnings=[],
                error_message=str(e),
                execution_time=execution_time,
                substitutions=[]
            )
    
    def _generate_summary(self) -> TestSummary:
        """Generate comprehensive test summary."""
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        total_execution_time = self.end_time - self.start_time if self.end_time and self.start_time else 0
        average_execution_time = sum(r.execution_time for r in self.results) / total_tests if total_tests > 0 else 0
        
        # Results by recipe
        results_by_recipe = {}
        for result in self.results:
            if result.recipe_name not in results_by_recipe:
                results_by_recipe[result.recipe_name] = {
                    "total_tests": 0,
                    "successful_tests": 0,
                    "failed_tests": 0,
                    "success_rate": 0,
                    "category": result.recipe_category,
                    "complexity": result.recipe_complexity
                }
            
            results_by_recipe[result.recipe_name]["total_tests"] += 1
            if result.success:
                results_by_recipe[result.recipe_name]["successful_tests"] += 1
            else:
                results_by_recipe[result.recipe_name]["failed_tests"] += 1
        
        # Calculate success rates
        for recipe_name, stats in results_by_recipe.items():
            stats["success_rate"] = (stats["successful_tests"] / stats["total_tests"]) * 100
        
        # Results by diet combination
        results_by_diet = {}
        for result in self.results:
            diet_key = ", ".join(result.diets)
            if diet_key not in results_by_diet:
                results_by_diet[diet_key] = {
                    "total_tests": 0,
                    "successful_tests": 0,
                    "failed_tests": 0,
                    "success_rate": 0
                }
            
            results_by_diet[diet_key]["total_tests"] += 1
            if result.success:
                results_by_diet[diet_key]["successful_tests"] += 1
            else:
                results_by_diet[diet_key]["failed_tests"] += 1
        
        # Calculate success rates
        for diet_key, stats in results_by_diet.items():
            stats["success_rate"] = (stats["successful_tests"] / stats["total_tests"]) * 100
        
        # Results by complexity
        results_by_complexity = {}
        for result in self.results:
            complexity = result.recipe_complexity
            if complexity not in results_by_complexity:
                results_by_complexity[complexity] = {
                    "total_tests": 0,
                    "successful_tests": 0,
                    "failed_tests": 0,
                    "success_rate": 0
                }
            
            results_by_complexity[complexity]["total_tests"] += 1
            if result.success:
                results_by_complexity[complexity]["successful_tests"] += 1
            else:
                results_by_complexity[complexity]["failed_tests"] += 1
        
        # Calculate success rates
        for complexity, stats in results_by_complexity.items():
            stats["success_rate"] = (stats["successful_tests"] / stats["total_tests"]) * 100
        
        return TestSummary(
            total_tests=total_tests,
            successful_tests=successful_tests,
            failed_tests=failed_tests,
            success_rate=success_rate,
            total_execution_time=total_execution_time,
            average_execution_time=average_execution_time,
            results_by_recipe=results_by_recipe,
            results_by_diet=results_by_diet,
            results_by_complexity=results_by_complexity
        )
    
    def print_summary(self, summary: TestSummary):
        """Print comprehensive test summary."""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 60)
        
        print(f"🎯 Overall Results:")
        print(f"   Total Tests: {summary.total_tests}")
        print(f"   Successful: {summary.successful_tests}")
        print(f"   Failed: {summary.failed_tests}")
        print(f"   Success Rate: {summary.success_rate:.1f}%")
        print(f"   Total Time: {summary.total_execution_time:.2f}s")
        print(f"   Average Time: {summary.average_execution_time:.3f}s per test")
        
        print(f"\n📈 Results by Recipe:")
        for recipe_name, stats in summary.results_by_recipe.items():
            print(f"   {recipe_name} ({stats['category']}, {stats['complexity']}): {stats['success_rate']:.1f}% ({stats['successful_tests']}/{stats['total_tests']})")
        
        print(f"\n🥗 Results by Diet Combination:")
        for diet_key, stats in summary.results_by_diet.items():
            print(f"   {diet_key}: {stats['success_rate']:.1f}% ({stats['successful_tests']}/{stats['total_tests']})")
        
        print(f"\n⚡ Results by Complexity:")
        for complexity, stats in summary.results_by_complexity.items():
            print(f"   {complexity}: {stats['success_rate']:.1f}% ({stats['successful_tests']}/{stats['total_tests']})")
        
        # Show failed tests
        failed_tests = [r for r in self.results if not r.success]
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for result in failed_tests[:10]:  # Show first 10 failures
                print(f"   {result.recipe_name} + {', '.join(result.diets)}: {result.error_message}")
            if len(failed_tests) > 10:
                print(f"   ... and {len(failed_tests) - 10} more")
    
    def save_results(self, summary: TestSummary, filename: str = None):
        """Save detailed results to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_results_{timestamp}.json"
        
        results_data = {
            "summary": asdict(summary),
            "detailed_results": [asdict(result) for result in self.results],
            "test_metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_recipes": len(get_test_recipes()),
                "total_diet_combinations": len(get_diet_combinations()),
                "simple_diets": get_simple_diets(),
                "complex_diets": get_complex_diets()
            }
        }
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        with open(filepath, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"\n💾 Results saved to: {filepath}")
        return filepath


def main():
    """Run comprehensive tests."""
    runner = ComprehensiveTestRunner()
    summary = runner.run_all_tests()
    runner.print_summary(summary)
    runner.save_results(summary)
    
    return summary


if __name__ == "__main__":
    main()
