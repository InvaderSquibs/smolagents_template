#!/usr/bin/env python3
"""
Calculator tool for SmolAgents that safely evaluates mathematical expressions.
Enhanced version of the original calculator with better safety and error handling.
"""

import ast
import operator
from smolagents import Tool

class CalculatorTool(Tool):
    name = "calculator"
    description = (
        "Safely evaluate simple Python arithmetic expressions. "
        "Supports basic math operations: +, -, *, /, **, parentheses, and common functions."
    )
    inputs = {
        "expression": {
            "type": "string", 
            "description": "Mathematical expression to evaluate (e.g., '2 + 2 * 10', 'sqrt(16)', 'pi * 5**2')"
        }
    }
    output_type = "string"

    def __init__(self):
        super().__init__()
        # Safe operations dictionary
        self.safe_operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }
        
        # Safe functions
        self.safe_functions = {
            'abs': abs,
            'round': round,
            'min': min,
            'max': max,
            'sum': sum,
            'pow': pow,
            'sqrt': lambda x: x ** 0.5,
            'pi': 3.141592653589793,
            'e': 2.718281828459045,
        }

    def _safe_eval(self, node):
        """Safely evaluate AST nodes with limited operations."""
        if isinstance(node, ast.Expression):
            return self._safe_eval(node.body)
        elif isinstance(node, ast.Constant):  # Python 3.8+
            return node.value
        elif isinstance(node, ast.Num):  # Python < 3.8
            return node.n
        elif isinstance(node, ast.BinOp):
            left = self._safe_eval(node.left)
            right = self._safe_eval(node.right)
            op = self.safe_operators.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsafe operation: {type(node.op).__name__}")
            return op(left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = self._safe_eval(node.operand)
            op = self.safe_operators.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsafe unary operation: {type(node.op).__name__}")
            return op(operand)
        elif isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Only simple function calls are allowed")
            func_name = node.func.id
            if func_name not in self.safe_functions:
                raise ValueError(f"Unsafe function: {func_name}")
            func = self.safe_functions[func_name]
            args = [self._safe_eval(arg) for arg in node.args]
            return func(*args)
        elif isinstance(node, ast.Name):
            if node.id in self.safe_functions:
                return self.safe_functions[node.id]
            raise ValueError(f"Unsafe variable: {node.id}")
        else:
            raise ValueError(f"Unsafe node type: {type(node).__name__}")

    def forward(self, expression: str) -> str:
        """
        Safely evaluate a mathematical expression.
        
        Args:
            expression: Mathematical expression to evaluate
            
        Returns:
            String result of the calculation or error message
        """
        try:
            # Parse the expression into an AST
            tree = ast.parse(expression, mode='eval')
            
            # Safely evaluate the AST
            result = self._safe_eval(tree)
            
            # Format the result nicely
            if isinstance(result, float):
                # Round to reasonable precision for display
                if result.is_integer():
                    return str(int(result))
                else:
                    return f"{result:.6f}".rstrip('0').rstrip('.')
            else:
                return str(result)
                
        except SyntaxError as e:
            return f"Syntax error: {e}"
        except ValueError as e:
            return f"Error: {e}"
        except ZeroDivisionError:
            return "Error: Division by zero"
        except OverflowError:
            return "Error: Result too large"
        except Exception as e:
            return f"Error: {e}"
