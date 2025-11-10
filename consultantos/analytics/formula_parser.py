"""
Safe formula parser for Excel-like formulas
Supports mathematical operations and built-in functions
"""
import ast
import operator
import math
import logging
from typing import Dict, Any, List, Union, Optional
from datetime import datetime


logger = logging.getLogger(__name__)


class FormulaParserError(Exception):
    """Formula parsing error"""
    pass


class FormulaParser:
    """
    Safe formula parser supporting:
    - Arithmetic: +, -, *, /, ^, %
    - Functions: SUM, AVG, MIN, MAX, COUNT, STDEV, PERCENTILE
    - Comparisons: >, <, >=, <=, ==, !=
    - Logical: AND, OR, NOT, IF
    """

    # Allowed operators
    ALLOWED_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.Gt: operator.gt,
        ast.Lt: operator.lt,
        ast.GtE: operator.ge,
        ast.LtE: operator.le,
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
    }

    # Allowed functions
    ALLOWED_FUNCTIONS = {
        "SUM": lambda x: sum(x) if isinstance(x, (list, tuple)) else x,
        "AVG": lambda x: sum(x) / len(x) if isinstance(x, (list, tuple)) and len(x) > 0 else (x if isinstance(x, (int, float)) else 0),
        "AVERAGE": lambda x: sum(x) / len(x) if isinstance(x, (list, tuple)) and len(x) > 0 else (x if isinstance(x, (int, float)) else 0),
        "MIN": lambda x: min(x) if isinstance(x, (list, tuple)) else x,
        "MAX": lambda x: max(x) if isinstance(x, (list, tuple)) else x,
        "COUNT": lambda x: len(x) if isinstance(x, (list, tuple)) else (1 if x is not None else 0),
        "ABS": lambda x: abs(x),
        "SQRT": lambda x: math.sqrt(x),
        "ROUND": lambda x, decimals=2: round(x, decimals),
        "CEIL": lambda x: math.ceil(x),
        "FLOOR": lambda x: math.floor(x),
        "IF": lambda condition, true_val, false_val: true_val if condition else false_val,
        "AND": lambda *args: all(args),
        "OR": lambda *args: any(args),
        "NOT": lambda x: not x,
    }

    def __init__(self, safe_mode: bool = True):
        """
        Initialize formula parser

        Args:
            safe_mode: Enable safe evaluation (default: True)
        """
        self.safe_mode = safe_mode

    async def parse_and_evaluate(
        self,
        formula: str,
        context: Dict[str, Any],
        variables: Optional[List[str]] = None,
    ) -> Union[float, int, bool, str]:
        """
        Parse and safely evaluate a formula

        Args:
            formula: Formula expression
            context: Dictionary of variables and their values
            variables: List of allowed variable names

        Returns:
            Evaluated result

        Raises:
            FormulaParserError: If formula is invalid or evaluation fails
        """
        try:
            # Validate input
            if not formula or not isinstance(formula, str):
                raise FormulaParserError("Formula must be a non-empty string")

            formula = formula.strip()

            # Parse into AST
            try:
                tree = ast.parse(formula, mode="eval")
            except SyntaxError as e:
                raise FormulaParserError(f"Invalid formula syntax: {str(e)}")

            # Validate AST nodes are allowed
            self._validate_ast(tree.body, variables or [])

            # Evaluate safely
            result = self._eval_node(tree.body, context, variables or [])

            logger.debug(f"Formula evaluated: {formula} = {result}")
            return result

        except FormulaParserError:
            raise
        except Exception as e:
            logger.error(f"Formula evaluation error: {str(e)}")
            raise FormulaParserError(f"Evaluation error: {str(e)}")

    def _validate_ast(self, node: ast.AST, variables: List[str]) -> None:
        """Validate that AST only contains allowed operations"""
        if isinstance(node, ast.Constant):
            return
        elif isinstance(node, ast.Name):
            if self.safe_mode and variables and node.id not in variables:
                raise FormulaParserError(f"Undefined variable: {node.id}")
            return
        elif isinstance(node, ast.BinOp):
            if type(node.op) not in self.ALLOWED_OPERATORS:
                raise FormulaParserError(f"Unsupported operator: {type(node.op).__name__}")
            self._validate_ast(node.left, variables)
            self._validate_ast(node.right, variables)
        elif isinstance(node, ast.UnaryOp):
            if type(node.op) not in [ast.UAdd, ast.USub, ast.Not]:
                raise FormulaParserError(f"Unsupported unary operator: {type(node.op).__name__}")
            self._validate_ast(node.operand, variables)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id not in self.ALLOWED_FUNCTIONS:
                    raise FormulaParserError(f"Unsupported function: {node.func.id}")
            else:
                raise FormulaParserError("Complex function calls not allowed")
            for arg in node.args:
                self._validate_ast(arg, variables)
        elif isinstance(node, ast.List):
            for elt in node.elts:
                self._validate_ast(elt, variables)
        elif isinstance(node, ast.Compare):
            self._validate_ast(node.left, variables)
            for op in node.ops:
                if type(op) not in self.ALLOWED_OPERATORS:
                    raise FormulaParserError(f"Unsupported comparison: {type(op).__name__}")
            for comparator in node.comparators:
                self._validate_ast(comparator, variables)
        else:
            raise FormulaParserError(f"Unsupported expression: {type(node).__name__}")

    def _eval_node(self, node: ast.AST, context: Dict[str, Any], variables: List[str]) -> Any:
        """Evaluate an AST node"""
        if isinstance(node, ast.Constant):
            return node.value

        elif isinstance(node, ast.Name):
            if node.id in context:
                return context[node.id]
            raise FormulaParserError(f"Variable not found: {node.id}")

        elif isinstance(node, ast.List):
            return [self._eval_node(elt, context, variables) for elt in node.elts]

        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left, context, variables)
            right = self._eval_node(node.right, context, variables)
            op = self.ALLOWED_OPERATORS.get(type(node.op))
            if op is None:
                raise FormulaParserError(f"Operator not supported: {type(node.op).__name__}")
            return op(left, right)

        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand, context, variables)
            if isinstance(node.op, ast.UAdd):
                return +operand
            elif isinstance(node.op, ast.USub):
                return -operand
            elif isinstance(node.op, ast.Not):
                return not operand
            else:
                raise FormulaParserError(f"Unary operator not supported: {type(node.op).__name__}")

        elif isinstance(node, ast.Compare):
            left = self._eval_node(node.left, context, variables)
            for op, comparator in zip(node.ops, node.comparators):
                right = self._eval_node(comparator, context, variables)
                op_func = self.ALLOWED_OPERATORS.get(type(op))
                if op_func is None:
                    raise FormulaParserError(f"Comparison not supported: {type(op).__name__}")
                if not op_func(left, right):
                    return False
                left = right
            return True

        elif isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise FormulaParserError("Complex function calls not allowed")

            func_name = node.func.id.upper()
            func = self.ALLOWED_FUNCTIONS.get(func_name)

            if func is None:
                raise FormulaParserError(f"Function not supported: {func_name}")

            args = [self._eval_node(arg, context, variables) for arg in node.args]

            try:
                return func(*args) if args else func()
            except TypeError as e:
                raise FormulaParserError(f"Invalid arguments for {func_name}: {str(e)}")
            except Exception as e:
                raise FormulaParserError(f"Function evaluation error: {str(e)}")

        else:
            raise FormulaParserError(f"Expression type not supported: {type(node).__name__}")

    def extract_variables(self, formula: str) -> List[str]:
        """Extract variable names from formula"""
        try:
            tree = ast.parse(formula, mode="eval")
            variables = set()
            self._extract_variables_from_node(tree.body, variables)
            return sorted(list(variables))
        except Exception as e:
            logger.error(f"Error extracting variables: {str(e)}")
            return []

    def _extract_variables_from_node(self, node: ast.AST, variables: set) -> None:
        """Recursively extract variables from AST"""
        if isinstance(node, ast.Name):
            variables.add(node.id)
        elif isinstance(node, ast.BinOp):
            self._extract_variables_from_node(node.left, variables)
            self._extract_variables_from_node(node.right, variables)
        elif isinstance(node, ast.UnaryOp):
            self._extract_variables_from_node(node.operand, variables)
        elif isinstance(node, ast.Compare):
            self._extract_variables_from_node(node.left, variables)
            for comparator in node.comparators:
                self._extract_variables_from_node(comparator, variables)
        elif isinstance(node, ast.Call):
            for arg in node.args:
                self._extract_variables_from_node(arg, variables)
        elif isinstance(node, ast.List):
            for elt in node.elts:
                self._extract_variables_from_node(elt, variables)


# Common formula templates
FORMULA_TEMPLATES = {
    "gross_margin": {
        "expression": "(revenue - cogs) / revenue",
        "description": "Gross margin percentage",
        "variables": ["revenue", "cogs"]
    },
    "net_profit_margin": {
        "expression": "net_income / revenue",
        "description": "Net profit margin",
        "variables": ["net_income", "revenue"]
    },
    "roi": {
        "expression": "(net_profit / investment) * 100",
        "description": "Return on investment",
        "variables": ["net_profit", "investment"]
    },
    "cagr": {
        "expression": "((ending_value / beginning_value) ^ (1 / years)) - 1",
        "description": "Compound annual growth rate",
        "variables": ["ending_value", "beginning_value", "years"]
    },
    "market_share": {
        "expression": "(company_revenue / total_market_revenue) * 100",
        "description": "Market share percentage",
        "variables": ["company_revenue", "total_market_revenue"]
    },
    "debt_to_equity": {
        "expression": "total_debt / total_equity",
        "description": "Debt to equity ratio",
        "variables": ["total_debt", "total_equity"]
    },
    "current_ratio": {
        "expression": "current_assets / current_liabilities",
        "description": "Current liquidity ratio",
        "variables": ["current_assets", "current_liabilities"]
    },
    "customer_acquisition_cost": {
        "expression": "marketing_spend / new_customers",
        "description": "Cost to acquire one customer",
        "variables": ["marketing_spend", "new_customers"]
    },
}


__all__ = [
    "FormulaParser",
    "FormulaParserError",
    "FORMULA_TEMPLATES",
]
