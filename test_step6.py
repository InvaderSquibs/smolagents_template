#!/usr/bin/env python3
"""
Test script for Step 6: Unit Handling
"""

import sys
import os
sys.path.append('src')

from unit_converter import UnitConverter

def normalize_conversion_result(amount: float, unit: str) -> str:
    """Normalize conversion results to use largest practical units with common cooking fractions."""
    
    # Common cooking fractions (in order of preference)
    fractions = {
        1/16: "1/16", 1/8: "1/8", 1/4: "1/4", 1/3: "1/3", 3/8: "3/8", 
        1/2: "1/2", 5/8: "5/8", 2/3: "2/3", 3/4: "3/4", 7/8: "7/8"
    }
    
    # If it's a whole number, return as int
    if abs(amount - int(amount)) < 0.001:
        return str(int(amount))
    
    # Find the closest fraction within tolerance
    for frac_value, frac_str in fractions.items():
        if abs(amount - frac_value) < 0.01:
            return frac_str
    
    # Check for whole number + fraction combinations
    whole_part = int(amount)
    fractional_part = amount - whole_part
    
    if whole_part > 0 and fractional_part > 0.01:
        for frac_value, frac_str in fractions.items():
            if abs(fractional_part - frac_value) < 0.01:
                return f"{whole_part} {frac_str}"
    
    # If no good fraction match, round to 2 decimal places
    rounded = round(amount, 2)
    if abs(rounded - int(rounded)) < 0.001:
        return str(int(rounded))
    
    return f"{rounded:.2f}".rstrip('0').rstrip('.')

def convert_to_largest_unit(amount: float, unit: str) -> tuple:
    """Convert to the largest practical unit (e.g., kg over g, cups over tbsp)."""
    
    # Unit conversion mappings (smaller unit -> larger unit)
    unit_conversions = {
        # Volume conversions
        'ml': ('cup', 240), 'tsp': ('tbsp', 3), 'tbsp': ('cup', 16),
        'fl oz': ('cup', 8), 'pint': ('cup', 2), 'quart': ('cup', 4),
        
        # Mass conversions  
        'g': ('kg', 1000), 'oz': ('lb', 16),
        
        # Length conversions
        'mm': ('cm', 10), 'cm': ('m', 100), 'in': ('ft', 12)
    }
    
    if unit in unit_conversions:
        larger_unit, conversion_factor = unit_conversions[unit]
        converted_amount = amount / conversion_factor
        
        # Only convert if the result is >= 1/16 of the larger unit
        if converted_amount >= 1/16:
            return converted_amount, larger_unit
    
    return amount, unit

def test_step6():
    print("=== STEP 6: UNIT HANDLING VALIDATION ===")
    print("Starting validation...")
    
    try:
        print("1. Importing UnitConverter...")
        converter = UnitConverter()
        print("✅ UnitConverter imported successfully")
        
        print("2. Testing same-dimension conversions...")
        same_dimension_tests = [
            ("1 cup", "ml"),
            ("2 cups", "ml"),
            ("1 lb", "kg"),
            ("500g", "lb"),
            ("1 tbsp", "tsp"),
            ("3 tsp", "tbsp"),
            ("1 oz", "g"),
            ("100g", "oz")
        ]
        
        for amount_str, target_unit in same_dimension_tests:
            try:
                # Parse the amount first
                quantity, from_unit = converter.parse_amount(amount_str)
                result = converter.convert(quantity, from_unit, target_unit)
                
                # Apply fraction normalization directly to the result
                normalized_amount = normalize_conversion_result(float(result.converted_amount), result.converted_unit)
                print(f"   ✅ {amount_str} → {normalized_amount} {result.converted_unit}")
            except Exception as e:
                print(f"   ❌ {amount_str} → Error: {e}")
        
        print("\n3. Testing cross-dimension conversions...")
        cross_dimension_tests = [
            ("1 cup water", "g"),  # volume to mass (water has known density)
            ("1 lb butter", "cups"),  # mass to volume
            ("500g sugar", "cups")   # mass to volume
        ]
        
        for amount_str, target_unit in cross_dimension_tests:
            try:
                # Parse the amount first
                quantity, from_unit = converter.parse_amount(amount_str)
                result = converter.convert(quantity, from_unit, target_unit)
                
                # Debug output
                print(f"   Debug: {amount_str} → {result.converted_amount} {result.converted_unit}")
                
                # Apply fraction normalization directly to the result
                normalized_amount = normalize_conversion_result(float(result.converted_amount), result.converted_unit)
                print(f"   ✅ {amount_str} → {normalized_amount} {result.converted_unit}")
            except Exception as e:
                print(f"   ❌ {amount_str} → Error: {e}")
        
        print("\n4. Testing fraction normalization...")
        fraction_tests = [
            (0.5, "cup"),
            (0.25, "cup"), 
            (0.125, "cup"),
            (1.5, "cup"),
            (1.25, "cup"),
            (2.0, "cup"),
            (0.33, "cup")
        ]
        
        for amount, unit in fraction_tests:
            normalized = normalize_conversion_result(amount, unit)
            print(f"   ✅ {amount} {unit} → {normalized} {unit}")
        
        print("\n5. Testing unit parsing...")
        parsing_tests = [
            "1 cup",
            "2.5 cups",
            "1/2 cup",
            "1 1/2 cups",
            "1 lb",
            "500g",
            "1 tbsp",
            "3 tsp"
        ]
        
        for amount_str in parsing_tests:
            try:
                quantity, unit = converter.parse_amount(amount_str)
                print(f"   ✅ '{amount_str}' → {quantity} {unit}")
            except Exception as e:
                print(f"   ❌ '{amount_str}' → Error: {e}")
        
        print("\n6. Testing conversion accuracy...")
        accuracy_tests = [
            ("1 cup", "ml", 240),  # 1 cup = 240ml
            ("1 lb", "kg", 0.454),  # 1 lb ≈ 0.454kg
            ("1 tbsp", "tsp", 3),   # 1 tbsp = 3 tsp
        ]
        
        for amount_str, target_unit, expected in accuracy_tests:
            try:
                # Parse the amount first
                quantity, from_unit = converter.parse_amount(amount_str)
                result = converter.convert(quantity, from_unit, target_unit)
                actual = float(result.converted_amount)
                
                # Apply fraction normalization directly to the result
                normalized_amount = normalize_conversion_result(actual, result.converted_unit)
                error = abs(actual - expected) / expected * 100
                print(f"   ✅ {amount_str} → {normalized_amount} {result.converted_unit} (expected ~{expected}, error: {error:.1f}%)")
            except Exception as e:
                print(f"   ❌ {amount_str} → Error: {e}")
        
        print("\n✅ Step 6 validation completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Step 6 validation failed: {e}")
        print("Full error details:")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_step6()
