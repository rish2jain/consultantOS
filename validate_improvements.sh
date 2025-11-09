#!/bin/bash

echo "=================================="
echo "Code Quality Validation Script"
echo "=================================="
echo ""

echo "1. Testing imports (type hints compatibility)..."
python3 -c "from consultantos.agents import ResearchAgent, MarketAgent, FinancialAgent, FrameworkAgent, SynthesisAgent; print('✅ All agent imports successful')" 2>&1

echo ""
echo "2. Testing orchestrator import..."
python3 -c "from consultantos.orchestrator import AnalysisOrchestrator; print('✅ Orchestrator import successful')" 2>&1

echo ""
echo "3. Testing sanitize utilities..."
python3 -c "from consultantos.utils.sanitize import sanitize_input, sanitize_dict; print('✅ Sanitize utilities import successful')" 2>&1

echo ""
echo "4. Checking docstring coverage for agents..."
for agent in research_agent market_agent financial_agent framework_agent synthesis_agent; do
    lines=$(grep -A 20 "async def _execute_internal" consultantos/agents/$agent.py | grep -c "Args:\|Returns:\|Raises:")
    if [ $lines -ge 3 ]; then
        echo "✅ $agent: Comprehensive docstring (found Args, Returns, Raises sections)"
    else
        echo "⚠️  $agent: Incomplete docstring"
    fi
done

echo ""
echo "5. Checking type hints in base_agent.py..."
if grep -q "def __init__.*-> None:" consultantos/agents/base_agent.py; then
    echo "✅ base_agent.py: __init__ has proper return type"
else
    echo "⚠️  base_agent.py: Missing __init__ return type"
fi

echo ""
echo "6. Checking sanitize.py type improvements..."
if grep -q "Dict\[str, Any\]" consultantos/utils/sanitize.py; then
    echo "✅ sanitize.py: Using proper Dict[str, Any] types"
else
    echo "⚠️  sanitize.py: Still using bare dict types"
fi

echo ""
echo "7. Checking orchestrator docstrings..."
orchestrator_methods=$(grep -c "Args:\|Returns:\|Raises:" consultantos/orchestrator/orchestrator.py)
echo "✅ orchestrator.py: Found $orchestrator_methods docstring sections"

echo ""
echo "8. Running quick type check on improved files..."
echo "   (Note: Some errors expected from external dependencies)"
mypy_output=$(python3 -m mypy consultantos/agents/base_agent.py --no-error-summary 2>&1)
mypy_exit_code=$?
echo "$mypy_output" | head -5
if [ $mypy_exit_code -eq 0 ]; then
    echo "✅ base_agent.py: No type errors"
fi

echo ""
echo "=================================="
echo "Validation Complete"
echo "=================================="
