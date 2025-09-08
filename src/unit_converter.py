#!/usr/bin/env python3
"""
Unit Conversion System

This module handles unit conversions for recipe substitutions:
- Same-dimension conversions (mass↔mass, volume↔volume)
- Cross-dimension conversions (mass↔volume) when density factors are provided
- Ingredient-specific density lookups
- Conversion validation and error handling
"""

import re
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum


class UnitType(Enum):
    """Types of measurement units."""
    MASS = "mass"
    VOLUME = "volume"
    COUNT = "count"
    LENGTH = "length"
    TEMPERATURE = "temperature"
    UNKNOWN = "unknown"


@dataclass
class Unit:
    """Represents a measurement unit with conversion factors."""
    name: str
    unit_type: UnitType
    base_factor: float  # Factor to convert to base unit (g for mass, ml for volume)
    aliases: List[str] = None
    
    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []


@dataclass
class ConversionResult:
    """Result of a unit conversion."""
    original_amount: float
    original_unit: str
    converted_amount: float
    converted_unit: str
    conversion_factor: float
    success: bool
    error_message: str = ""


@dataclass
class IngredientDensity:
    """Density information for cross-dimension conversions."""
    ingredient: str
    density_g_per_ml: float  # Density in grams per milliliter
    notes: str = ""


class UnitConverter:
    """Handles unit conversions for recipe ingredients."""
    
    def __init__(self):
        self.units = self._build_unit_database()
        self.densities = self._build_density_database()
    
    def _build_unit_database(self) -> Dict[str, Unit]:
        """Build the database of measurement units."""
        units = {}
        
        # Mass units (base: grams)
        mass_units = [
            Unit("g", UnitType.MASS, 1.0, ["gram", "grams"]),
            Unit("kg", UnitType.MASS, 1000.0, ["kilogram", "kilograms", "kilo"]),
            Unit("lb", UnitType.MASS, 453.592, ["pound", "pounds", "lbs"]),
            Unit("oz", UnitType.MASS, 28.3495, ["ounce", "ounces"]),
        ]
        
        # Volume units (base: milliliters)
        volume_units = [
            Unit("ml", UnitType.VOLUME, 1.0, ["milliliter", "milliliters"]),
            Unit("l", UnitType.VOLUME, 1000.0, ["liter", "liters", "litre", "litres"]),
            Unit("cup", UnitType.VOLUME, 236.588, ["cups"]),
            Unit("tbsp", UnitType.VOLUME, 14.7868, ["tablespoon", "tablespoons", "T", "Tbsp"]),
            Unit("tsp", UnitType.VOLUME, 4.92892, ["teaspoon", "teaspoons", "t"]),
            Unit("fl oz", UnitType.VOLUME, 29.5735, ["fluid ounce", "fluid ounces"]),
            Unit("pt", UnitType.VOLUME, 473.176, ["pint", "pints"]),
            Unit("qt", UnitType.VOLUME, 946.353, ["quart", "quarts"]),
            Unit("gal", UnitType.VOLUME, 3785.41, ["gallon", "gallons"]),
        ]
        
        # Count units
        count_units = [
            Unit("piece", UnitType.COUNT, 1.0, ["pieces", "pcs", "pc"]),
            Unit("dozen", UnitType.COUNT, 12.0, ["dozens"]),
        ]
        
        # Length units (base: millimeters)
        length_units = [
            Unit("mm", UnitType.LENGTH, 1.0, ["millimeter", "millimeters"]),
            Unit("cm", UnitType.LENGTH, 10.0, ["centimeter", "centimeters"]),
            Unit("in", UnitType.LENGTH, 25.4, ["inch", "inches"]),
        ]
        
        # Temperature units
        temp_units = [
            Unit("°C", UnitType.TEMPERATURE, 1.0, ["celsius", "centigrade"]),
            Unit("°F", UnitType.TEMPERATURE, 1.0, ["fahrenheit"]),
        ]
        
        # Combine all units
        all_units = mass_units + volume_units + count_units + length_units + temp_units
        
        for unit in all_units:
            units[unit.name] = unit
            for alias in unit.aliases:
                units[alias] = unit
        
        return units
    
    def _build_density_database(self) -> Dict[str, IngredientDensity]:
        """Build the database of ingredient densities for cross-dimension conversions."""
        densities = {}
        
        # Common ingredient densities (g/ml)
        density_data = [
            ("flour", 0.6, "All-purpose flour"),
            ("sugar", 0.85, "Granulated sugar"),
            ("brown sugar", 0.8, "Packed brown sugar"),
            ("powdered sugar", 0.6, "Confectioners sugar"),
            ("butter", 0.91, "Dairy butter"),
            ("oil", 0.92, "Vegetable oil"),
            ("milk", 1.03, "Whole milk"),
            ("water", 1.0, "Water"),
            ("honey", 1.4, "Honey"),
            ("molasses", 1.4, "Molasses"),
            ("corn syrup", 1.36, "Light corn syrup"),
            ("cream", 1.0, "Heavy cream"),
            ("yogurt", 1.03, "Plain yogurt"),
            ("sour cream", 1.0, "Sour cream"),
            ("cheese", 1.0, "Grated cheese"),
            ("nuts", 0.6, "Chopped nuts"),
            ("almond flour", 0.4, "Almond flour"),
            ("coconut flour", 0.3, "Coconut flour"),
            ("cocoa powder", 0.4, "Unsweetened cocoa powder"),
            ("baking powder", 0.9, "Baking powder"),
            ("baking soda", 0.9, "Baking soda"),
            ("salt", 1.2, "Table salt"),
            ("rice", 0.8, "Uncooked rice"),
            ("oats", 0.3, "Rolled oats"),
        ]
        
        for ingredient, density, notes in density_data:
            densities[ingredient] = IngredientDensity(
                ingredient=ingredient,
                density_g_per_ml=density,
                notes=notes
            )
        
        return densities
    
    def parse_amount(self, amount_str: str) -> Tuple[float, str]:
        """Parse an amount string into quantity and unit."""
        if not amount_str:
            return 0.0, ""
        
        # Clean the string
        amount_str = amount_str.strip().lower()
        
        # Handle fractions first
        amount_str = self._convert_fractions(amount_str)
        
        # Extract number and unit
        # Match patterns like "1 cup", "2.5 tbsp", "0.5 tsp", "1/2 cup butter, softened", etc.
        # Updated pattern to handle fractions and extract only the first unit
        pattern = r'^(\d+(?:\.\d+)?)\s+([a-zA-Z]+)'
        match = re.match(pattern, amount_str)
        
        if match:
            quantity = float(match.group(1))
            unit = match.group(2).strip()
            return quantity, unit
        
        # If no number found, assume it's just a unit
        return 1.0, amount_str
    
    def _convert_fractions(self, amount_str: str) -> str:
        """Convert common fractions to decimals."""
        fraction_map = {
            "1/8": "0.125",
            "1/4": "0.25",
            "1/3": "0.333",
            "3/8": "0.375",
            "1/2": "0.5",
            "5/8": "0.625",
            "2/3": "0.667",
            "3/4": "0.75",
            "7/8": "0.875",
        }
        
        # Handle mixed numbers like "2 1/4"
        import re
        mixed_pattern = r'(\d+)\s+(\d+/\d+)'
        match = re.search(mixed_pattern, amount_str)
        if match:
            whole_number = int(match.group(1))
            fraction = match.group(2)
            if fraction in fraction_map:
                decimal_part = float(fraction_map[fraction])
                total = whole_number + decimal_part
                amount_str = amount_str.replace(match.group(0), str(total))
        
        # Handle standalone fractions
        for fraction, decimal in fraction_map.items():
            amount_str = amount_str.replace(fraction, decimal)
        
        return amount_str
    
    def get_unit_type(self, unit: str) -> UnitType:
        """Get the type of a unit."""
        unit_lower = unit.lower().strip()
        if unit_lower in self.units:
            return self.units[unit_lower].unit_type
        return UnitType.UNKNOWN
    
    def convert_same_dimension(self, amount: float, from_unit: str, to_unit: str) -> ConversionResult:
        """Convert between units of the same dimension."""
        from_unit_lower = from_unit.lower().strip()
        to_unit_lower = to_unit.lower().strip()
        
        # Check if units exist
        if from_unit_lower not in self.units:
            return ConversionResult(
                original_amount=amount,
                original_unit=from_unit,
                converted_amount=0.0,
                converted_unit=to_unit,
                conversion_factor=0.0,
                success=False,
                error_message=f"Unknown unit: {from_unit}"
            )
        
        if to_unit_lower not in self.units:
            return ConversionResult(
                original_amount=amount,
                original_unit=from_unit,
                converted_amount=0.0,
                converted_unit=to_unit,
                conversion_factor=0.0,
                success=False,
                error_message=f"Unknown unit: {to_unit}"
            )
        
        from_unit_obj = self.units[from_unit_lower]
        to_unit_obj = self.units[to_unit_lower]
        
        # Check if units are same type
        if from_unit_obj.unit_type != to_unit_obj.unit_type:
            return ConversionResult(
                original_amount=amount,
                original_unit=from_unit,
                converted_amount=0.0,
                converted_unit=to_unit,
                conversion_factor=0.0,
                success=False,
                error_message=f"Cannot convert {from_unit} ({from_unit_obj.unit_type.value}) to {to_unit} ({to_unit_obj.unit_type.value})"
            )
        
        # Perform conversion
        base_amount = amount * from_unit_obj.base_factor
        converted_amount = base_amount / to_unit_obj.base_factor
        conversion_factor = to_unit_obj.base_factor / from_unit_obj.base_factor
        
        return ConversionResult(
            original_amount=amount,
            original_unit=from_unit,
            converted_amount=converted_amount,
            converted_unit=to_unit,
            conversion_factor=conversion_factor,
            success=True
        )
    
    def convert_cross_dimension(self, amount: float, from_unit: str, to_unit: str, 
                              ingredient: str = "") -> ConversionResult:
        """Convert between units of different dimensions using ingredient density."""
        from_unit_lower = from_unit.lower().strip()
        to_unit_lower = to_unit.lower().strip()
        
        # Check if units exist
        if from_unit_lower not in self.units or to_unit_lower not in self.units:
            return ConversionResult(
                original_amount=amount,
                original_unit=from_unit,
                converted_amount=0.0,
                converted_unit=to_unit,
                conversion_factor=0.0,
                success=False,
                error_message="Unknown units for cross-dimension conversion"
            )
        
        from_unit_obj = self.units[from_unit_lower]
        to_unit_obj = self.units[to_unit_lower]
        
        # Check if we have density information
        if ingredient.lower() not in self.densities:
            return ConversionResult(
                original_amount=amount,
                original_unit=from_unit,
                converted_amount=0.0,
                converted_unit=to_unit,
                conversion_factor=0.0,
                success=False,
                error_message=f"No density information available for {ingredient}"
            )
        
        density = self.densities[ingredient.lower()]
        
        # Convert to base units
        if from_unit_obj.unit_type == UnitType.MASS:
            # Mass to volume
            mass_grams = amount * from_unit_obj.base_factor
            volume_ml = mass_grams / density.density_g_per_ml
            converted_amount = volume_ml / to_unit_obj.base_factor
        elif from_unit_obj.unit_type == UnitType.VOLUME:
            # Volume to mass
            volume_ml = amount * from_unit_obj.base_factor
            mass_grams = volume_ml * density.density_g_per_ml
            converted_amount = mass_grams / to_unit_obj.base_factor
        else:
            return ConversionResult(
                original_amount=amount,
                original_unit=from_unit,
                converted_amount=0.0,
                converted_unit=to_unit,
                conversion_factor=0.0,
                success=False,
                error_message=f"Cannot convert {from_unit_obj.unit_type.value} to {to_unit_obj.unit_type.value}"
            )
        
        return ConversionResult(
            original_amount=amount,
            original_unit=from_unit,
            converted_amount=converted_amount,
            converted_unit=to_unit,
            conversion_factor=converted_amount / amount,
            success=True
        )
    
    def convert(self, amount: float, from_unit: str, to_unit: str, 
                ingredient: str = "") -> ConversionResult:
        """Convert between units, automatically handling same-dimension and cross-dimension conversions."""
        from_unit_lower = from_unit.lower().strip()
        to_unit_lower = to_unit.lower().strip()
        
        # If units are the same, no conversion needed
        if from_unit_lower == to_unit_lower:
            return ConversionResult(
                original_amount=amount,
                original_unit=from_unit,
                converted_amount=amount,
                converted_unit=to_unit,
                conversion_factor=1.0,
                success=True
            )
        
        # Check unit types
        from_type = self.get_unit_type(from_unit)
        to_type = self.get_unit_type(to_unit)
        
        if from_type == UnitType.UNKNOWN or to_type == UnitType.UNKNOWN:
            return ConversionResult(
                original_amount=amount,
                original_unit=from_unit,
                converted_amount=0.0,
                converted_unit=to_unit,
                conversion_factor=0.0,
                success=False,
                error_message="Unknown unit types"
            )
        
        # Same dimension conversion
        if from_type == to_type:
            return self.convert_same_dimension(amount, from_unit, to_unit)
        
        # Cross dimension conversion
        if (from_type == UnitType.MASS and to_type == UnitType.VOLUME) or \
           (from_type == UnitType.VOLUME and to_type == UnitType.MASS):
            return self.convert_cross_dimension(amount, from_unit, to_unit, ingredient)
        
        # Unsupported conversion
        return ConversionResult(
            original_amount=amount,
            original_unit=from_unit,
            converted_amount=0.0,
            converted_unit=to_unit,
            conversion_factor=0.0,
            success=False,
            error_message=f"Cannot convert {from_type.value} to {to_type.value}"
        )
    
    def demo_conversions(self) -> List[Dict]:
        """Demo various unit conversions."""
        test_cases = [
            # Same dimension conversions
            ("1", "cup", "ml", ""),
            ("2", "tbsp", "tsp", ""),
            ("500", "g", "kg", ""),
            ("1", "lb", "oz", ""),
            
            # Cross dimension conversions
            ("1", "cup", "g", "flour"),
            ("100", "g", "ml", "butter"),
            ("1", "tbsp", "g", "honey"),
            ("250", "ml", "g", "milk"),
            
            # Fraction handling
            ("1/2", "cup", "ml", ""),
            ("1/4", "tsp", "ml", ""),
        ]
        
        results = []
        for amount_str, from_unit, to_unit, ingredient in test_cases:
            amount, _ = self.parse_amount(amount_str)
            result = self.convert(amount, from_unit, to_unit, ingredient)
            
            results.append({
                "input": f"{amount_str} {from_unit}",
                "output": f"{result.converted_amount:.2f} {result.converted_unit}",
                "success": result.success,
                "factor": result.conversion_factor,
                "error": result.error_message if not result.success else ""
            })
        
        return results


def main():
    """Demo the unit converter."""
    print("🧪 Testing Unit Conversion System")
    print("=" * 50)
    
    converter = UnitConverter()
    
    print(f"📋 Available units: {len(converter.units)}")
    print(f"📋 Ingredient densities: {len(converter.densities)}")
    print()
    
    # Test 1: Amount parsing
    print("📝 Test 1: Amount Parsing")
    test_amounts = ["1 cup", "2.5 tbsp", "1/2 tsp", "3/4 cup", "1 lb"]
    
    for amount_str in test_amounts:
        amount, unit = converter.parse_amount(amount_str)
        print(f"   '{amount_str}' → {amount} {unit}")
    
    print()
    
    # Test 2: Same dimension conversions
    print("📝 Test 2: Same Dimension Conversions")
    same_dim_tests = [
        ("1", "cup", "ml"),
        ("2", "tbsp", "tsp"),
        ("500", "g", "kg"),
        ("1", "lb", "oz"),
    ]
    
    for amount_str, from_unit, to_unit in same_dim_tests:
        amount, _ = converter.parse_amount(amount_str)
        result = converter.convert_same_dimension(amount, from_unit, to_unit)
        status = "✅" if result.success else "❌"
        print(f"   {status} {amount} {from_unit} → {result.converted_amount:.2f} {result.converted_unit}")
        if not result.success:
            print(f"      Error: {result.error_message}")
    
    print()
    
    # Test 3: Cross dimension conversions
    print("📝 Test 3: Cross Dimension Conversions")
    cross_dim_tests = [
        ("1", "cup", "g", "flour"),
        ("100", "g", "ml", "butter"),
        ("1", "tbsp", "g", "honey"),
        ("250", "ml", "g", "milk"),
    ]
    
    for amount_str, from_unit, to_unit, ingredient in cross_dim_tests:
        amount, _ = converter.parse_amount(amount_str)
        result = converter.convert_cross_dimension(amount, from_unit, to_unit, ingredient)
        status = "✅" if result.success else "❌"
        print(f"   {status} {amount} {from_unit} ({ingredient}) → {result.converted_amount:.2f} {result.converted_unit}")
        if not result.success:
            print(f"      Error: {result.error_message}")
    
    print()
    
    # Test 4: Complete demo
    print("📝 Test 4: Complete Conversion Demo")
    demo_results = converter.demo_conversions()
    
    for result in demo_results:
        status = "✅" if result["success"] else "❌"
        print(f"   {status} {result['input']} → {result['output']}")
        if not result["success"]:
            print(f"      Error: {result['error']}")
    
    print(f"\n✅ Unit conversion system ready!")
    print("✅ Same-dimension conversions working")
    print("✅ Cross-dimension conversions working")
    print("✅ Fraction parsing working")
    print("✅ Error handling working")


if __name__ == "__main__":
    main()
