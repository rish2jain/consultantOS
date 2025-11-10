"""
Tests for formula parser
"""
import pytest
import math
from consultantos.analytics.formula_parser import FormulaParser, FormulaParserError


@pytest.fixture
def parser():
    """Create formula parser fixture"""
    return FormulaParser(safe_mode=True)


class TestFormulaParserBasics:
    """Test basic formula parsing and evaluation"""

    @pytest.mark.asyncio
    async def test_simple_arithmetic(self, parser):
        """Test simple arithmetic operations"""
        result = await parser.parse_and_evaluate("2 + 3", {})
        assert result == 5

        result = await parser.parse_and_evaluate("10 - 4", {})
        assert result == 6

        result = await parser.parse_and_evaluate("3 * 4", {})
        assert result == 12

        result = await parser.parse_and_evaluate("20 / 4", {})
        assert result == 5

    @pytest.mark.asyncio
    async def test_complex_arithmetic(self, parser):
        """Test complex arithmetic with operator precedence"""
        result = await parser.parse_and_evaluate("2 + 3 * 4", {})
        assert result == 14

        result = await parser.parse_and_evaluate("(2 + 3) * 4", {})
        assert result == 20

    @pytest.mark.asyncio
    async def test_power_operator(self, parser):
        """Test power operator"""
        result = await parser.parse_and_evaluate("2 ** 3", {})
        assert result == 8

        result = await parser.parse_and_evaluate("5 ** 2", {})
        assert result == 25

    @pytest.mark.asyncio
    async def test_modulo_operator(self, parser):
        """Test modulo operator"""
        result = await parser.parse_and_evaluate("10 % 3", {})
        assert result == 1

        result = await parser.parse_and_evaluate("20 % 7", {})
        assert result == 6


class TestVariables:
    """Test variable substitution"""

    @pytest.mark.asyncio
    async def test_simple_variable(self, parser):
        """Test simple variable substitution"""
        context = {"x": 10}
        result = await parser.parse_and_evaluate("x + 5", context, ["x"])
        assert result == 15

    @pytest.mark.asyncio
    async def test_multiple_variables(self, parser):
        """Test multiple variable substitution"""
        context = {"revenue": 1000, "cogs": 600}
        result = await parser.parse_and_evaluate(
            "(revenue - cogs) / revenue",
            context,
            ["revenue", "cogs"]
        )
        assert result == 0.4

    @pytest.mark.asyncio
    async def test_variable_extraction(self, parser):
        """Test variable extraction"""
        variables = parser.extract_variables("(revenue - cogs) / revenue")
        assert set(variables) == {"revenue", "cogs"}

        variables = parser.extract_variables("SUM(values) / COUNT(items)")
        assert set(variables) == {"values", "items"}

    @pytest.mark.asyncio
    async def test_undefined_variable_safe_mode(self, parser):
        """Test undefined variable in safe mode"""
        context = {"x": 10}
        with pytest.raises(FormulaParserError):
            await parser.parse_and_evaluate("x + undefined", context, ["x"])


class TestFunctions:
    """Test built-in functions"""

    @pytest.mark.asyncio
    async def test_sum_function(self, parser):
        """Test SUM function"""
        context = {"values": [1, 2, 3, 4, 5]}
        result = await parser.parse_and_evaluate("SUM(values)", context, ["values"])
        assert result == 15

    @pytest.mark.asyncio
    async def test_avg_function(self, parser):
        """Test AVG function"""
        context = {"values": [1, 2, 3, 4, 5]}
        result = await parser.parse_and_evaluate("AVG(values)", context, ["values"])
        assert result == 3

    @pytest.mark.asyncio
    async def test_min_max_functions(self, parser):
        """Test MIN and MAX functions"""
        context = {"values": [1, 5, 3, 2, 4]}

        result = await parser.parse_and_evaluate("MIN(values)", context, ["values"])
        assert result == 1

        result = await parser.parse_and_evaluate("MAX(values)", context, ["values"])
        assert result == 5

    @pytest.mark.asyncio
    async def test_count_function(self, parser):
        """Test COUNT function"""
        context = {"values": [1, 2, 3, 4, 5]}
        result = await parser.parse_and_evaluate("COUNT(values)", context, ["values"])
        assert result == 5

    @pytest.mark.asyncio
    async def test_abs_function(self, parser):
        """Test ABS function"""
        result = await parser.parse_and_evaluate("ABS(-10)", {})
        assert result == 10

    @pytest.mark.asyncio
    async def test_sqrt_function(self, parser):
        """Test SQRT function"""
        result = await parser.parse_and_evaluate("SQRT(16)", {})
        assert result == 4

    @pytest.mark.asyncio
    async def test_round_function(self, parser):
        """Test ROUND function"""
        result = await parser.parse_and_evaluate("ROUND(3.14159, 2)", {})
        assert result == 3.14


class TestComparisons:
    """Test comparison operators"""

    @pytest.mark.asyncio
    async def test_greater_than(self, parser):
        """Test > operator"""
        result = await parser.parse_and_evaluate("10 > 5", {})
        assert result is True

        result = await parser.parse_and_evaluate("5 > 10", {})
        assert result is False

    @pytest.mark.asyncio
    async def test_less_than(self, parser):
        """Test < operator"""
        result = await parser.parse_and_evaluate("5 < 10", {})
        assert result is True

        result = await parser.parse_and_evaluate("10 < 5", {})
        assert result is False

    @pytest.mark.asyncio
    async def test_equal_not_equal(self, parser):
        """Test == and != operators"""
        result = await parser.parse_and_evaluate("5 == 5", {})
        assert result is True

        result = await parser.parse_and_evaluate("5 != 5", {})
        assert result is False


class TestLogicalOperators:
    """Test logical operators"""

    @pytest.mark.asyncio
    async def test_and_operator(self, parser):
        """Test AND operator"""
        result = await parser.parse_and_evaluate("True and True", {})
        assert result is True

        result = await parser.parse_and_evaluate("True and False", {})
        assert result is False

    @pytest.mark.asyncio
    async def test_or_operator(self, parser):
        """Test OR operator"""
        result = await parser.parse_and_evaluate("True or False", {})
        assert result is True

        result = await parser.parse_and_evaluate("False or False", {})
        assert result is False

    @pytest.mark.asyncio
    async def test_not_operator(self, parser):
        """Test NOT operator"""
        result = await parser.parse_and_evaluate("not True", {})
        assert result is False

        result = await parser.parse_and_evaluate("not False", {})
        assert result is True


class TestBusinessFormulas:
    """Test business-specific formulas"""

    @pytest.mark.asyncio
    async def test_gross_margin(self, parser):
        """Test gross margin calculation"""
        context = {"revenue": 1000, "cogs": 600}
        result = await parser.parse_and_evaluate(
            "(revenue - cogs) / revenue",
            context,
            ["revenue", "cogs"]
        )
        assert result == 0.4

    @pytest.mark.asyncio
    async def test_roi_calculation(self, parser):
        """Test ROI calculation"""
        context = {"net_profit": 100, "investment": 500}
        result = await parser.parse_and_evaluate(
            "(net_profit / investment) * 100",
            context,
            ["net_profit", "investment"]
        )
        assert result == 20

    @pytest.mark.asyncio
    async def test_market_share(self, parser):
        """Test market share calculation"""
        context = {"company_revenue": 150, "total_market_revenue": 1000}
        result = await parser.parse_and_evaluate(
            "(company_revenue / total_market_revenue) * 100",
            context,
            ["company_revenue", "total_market_revenue"]
        )
        assert result == 15

    @pytest.mark.asyncio
    async def test_debt_to_equity(self, parser):
        """Test debt to equity ratio"""
        context = {"total_debt": 500, "total_equity": 1000}
        result = await parser.parse_and_evaluate(
            "total_debt / total_equity",
            context,
            ["total_debt", "total_equity"]
        )
        assert result == 0.5


class TestErrorHandling:
    """Test error handling"""

    @pytest.mark.asyncio
    async def test_empty_formula(self, parser):
        """Test empty formula"""
        with pytest.raises(FormulaParserError):
            await parser.parse_and_evaluate("", {})

    @pytest.mark.asyncio
    async def test_invalid_syntax(self, parser):
        """Test invalid syntax"""
        with pytest.raises(FormulaParserError):
            await parser.parse_and_evaluate("2 + + 3", {})

    @pytest.mark.asyncio
    async def test_undefined_function(self, parser):
        """Test undefined function"""
        with pytest.raises(FormulaParserError):
            await parser.parse_and_evaluate("UNDEFINED_FUNC(10)", {})

    @pytest.mark.asyncio
    async def test_invalid_import_attempt(self, parser):
        """Test that import statements are blocked"""
        with pytest.raises(FormulaParserError):
            await parser.parse_and_evaluate("__import__('os')", {})
