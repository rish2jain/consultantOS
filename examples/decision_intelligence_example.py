"""
Decision Intelligence Engine - Quick Start Example

This example demonstrates how to use the DecisionIntelligenceEngine to transform
framework analyses into actionable decision briefs with ROI models.
"""
import asyncio
from consultantos.agents import FrameworkAgent, DecisionIntelligenceEngine
from consultantos.models import FrameworkAnalysis


async def basic_usage():
    """Basic usage: Generate decisions from framework analysis"""

    print("="*60)
    print("DECISION INTELLIGENCE ENGINE - BASIC EXAMPLE")
    print("="*60)

    # Step 1: Create sample framework analysis (normally from FrameworkAgent)
    # In production, you would run:
    # framework_agent = FrameworkAgent()
    # framework_result = await framework_agent.execute({"company": "Tesla", ...})

    # For this example, we'll create a mock framework analysis
    from consultantos.models import (
        PortersFiveForces,
        SWOTAnalysis,
        BlueOceanStrategy
    )

    framework_analysis = FrameworkAnalysis(
        porter_five_forces=PortersFiveForces(
            supplier_power=4.2,  # High - will trigger decision
            buyer_power=3.8,     # High - will trigger decision
            competitive_rivalry=4.5,  # Very high - will trigger decision
            threat_of_substitutes=3.0,
            threat_of_new_entrants=2.5,
            overall_intensity="High",
            detailed_analysis={
                "supplier_power": "Battery suppliers have strong pricing power",
                "buyer_power": "Customers have many EV alternatives",
                "competitive_rivalry": "Intense competition from traditional and new EV makers"
            }
        ),
        swot_analysis=SWOTAnalysis(
            strengths=[
                "Industry-leading battery technology and range",
                "Strong brand recognition and customer loyalty",
                "Vertically integrated manufacturing capabilities"
            ],
            weaknesses=[
                "Production capacity constraints",
                "Quality control challenges at scale",
                "Limited service network compared to traditional automakers"
            ],
            opportunities=[
                "Growing global EV market demand",
                "Energy storage and solar integration",
                "Autonomous vehicle technology leadership"
            ],
            threats=[
                "Traditional automakers entering EV market aggressively",
                "Potential battery supply chain disruptions",
                "Regulatory changes affecting subsidies"
            ]
        ),
        blue_ocean_strategy=BlueOceanStrategy(
            eliminate=[
                "Dealer network overhead",
                "Traditional advertising spend"
            ],
            reduce=[
                "Physical service locations",
                "Marketing complexity"
            ],
            raise_factors=[
                "Over-the-air updates and continuous improvement",
                "Charging infrastructure coverage",
                "Autonomous driving capabilities"
            ],
            create=[
                "Direct-to-consumer digital sales model",
                "Supercharger network as competitive moat",
                "Software-defined vehicle experience"
            ]
        )
    )

    # Step 2: Initialize Decision Intelligence Engine
    decision_engine = DecisionIntelligenceEngine(timeout=120)

    # Step 3: Generate decision brief
    print("\nGenerating decision brief...")
    decision_result = await decision_engine.execute({
        "company": "Tesla",
        "industry": "Electric Vehicles",
        "framework_analysis": framework_analysis,
        "revenue": 81_000_000_000  # $81B annual revenue for ROI scaling
    })

    if not decision_result["success"]:
        print("❌ Decision generation failed")
        return

    decision_brief = decision_result["data"]

    # Step 4: Display results
    print("\n" + "="*60)
    print("DECISION BRIEF GENERATED")
    print("="*60)

    print(f"\nCompany: {decision_brief.company}")
    print(f"Generated at: {decision_brief.generated_at}")
    print(f"Confidence Score: {decision_brief.confidence_score:.1f}%")

    print(f"\n📊 DECISION SUMMARY:")
    print(f"  Total Decisions: {decision_brief.decision_count}")
    print(f"  Critical Decisions: {len(decision_brief.critical_decisions)}")
    print(f"  High Priority Decisions: {len(decision_brief.high_priority_decisions)}")

    print(f"\n🎯 STRATEGIC THEMES:")
    for theme in decision_brief.strategic_themes:
        print(f"  • {theme}")

    if decision_brief.resource_conflicts:
        print(f"\n⚠️  RESOURCE CONFLICTS:")
        for conflict in decision_brief.resource_conflicts:
            print(f"  • {conflict}")

    # Step 5: Show top decision in detail
    if decision_brief.top_decision:
        print("\n" + "="*60)
        print("TOP PRIORITY DECISION")
        print("="*60)

        decision = decision_brief.top_decision

        print(f"\n❓ QUESTION: {decision.decision_question}")
        print(f"📂 Category: {decision.decision_category.value}")
        print(f"⏰ Urgency: {decision.urgency.value}")
        print(f"\n📝 Context: {decision.context}")
        print(f"\n💰 Stakes: {decision.stakes}")

        if decision.porter_analysis:
            print(f"\n🔍 Framework Insight: {decision.porter_analysis}")

        print(f"\n🎯 OPTIONS ANALYSIS ({len(decision.options)} options):")
        print("-" * 60)

        for i, option in enumerate(decision.options, 1):
            print(f"\n{i}. {option.option_name}")
            print(f"   Description: {option.description}")
            print(f"\n   💵 Financial Model:")
            print(f"      Investment: ${option.investment_required:,.0f}")
            print(f"      Annual Return: ${option.expected_annual_return:,.0f}")
            print(f"      ROI Multiple: {option.roi_multiple:.2f}x")
            print(f"      Payback: {option.payback_period_months} months")

            print(f"\n   📅 Implementation:")
            print(f"      Timeline: {option.timeline_days} days")
            print(f"      Success Probability: {option.success_probability:.1f}%")
            print(f"      Risk Level: {option.risk_level}")
            print(f"      Strategic Fit: {option.strategic_fit:.1f}/100")

            print(f"\n   🎖️  Competitive Advantage:")
            print(f"      {option.competitive_advantage}")

            if option.risks:
                print(f"\n   ⚠️  Key Risks:")
                for risk in option.risks[:3]:  # Top 3 risks
                    print(f"      • {risk}")

            if option.mitigation_strategies:
                print(f"\n   🛡️  Mitigation Strategies:")
                for strategy in option.mitigation_strategies[:3]:
                    print(f"      • {strategy}")

            if option.implementation_steps:
                print(f"\n   📋 Implementation Steps:")
                for step in option.implementation_steps[:5]:
                    print(f"      {step}")

            # Highlight if this is the recommended option
            if option.option_id == decision.recommended_option:
                print(f"\n   ✅ RECOMMENDED OPTION")

        # Show success metrics and assumptions
        if decision.success_metrics:
            print(f"\n📊 SUCCESS METRICS:")
            for metric in decision.success_metrics:
                print(f"   • {metric}")

        if decision.key_assumptions:
            print(f"\n🔑 KEY ASSUMPTIONS:")
            for assumption in decision.key_assumptions:
                print(f"   • {assumption}")

    print("\n" + "="*60)
    print("END OF DECISION BRIEF")
    print("="*60)


async def portfolio_analysis():
    """Advanced usage: Portfolio-level ROI analysis"""

    print("\n\n" + "="*60)
    print("PORTFOLIO ROI ANALYSIS")
    print("="*60)

    # This would follow the same setup as basic_usage()
    # For brevity, assuming we have decision_brief already

    # Sample calculation
    print("\nCalculating portfolio-level metrics...")
    print("\nNote: Run basic_usage() first to generate actual decision brief")


def main():
    """Run examples"""
    print("\n🚀 Decision Intelligence Engine Examples\n")

    # Run basic usage example
    asyncio.run(basic_usage())

    # Additional examples can be added here
    # asyncio.run(portfolio_analysis())
    # asyncio.run(decision_comparison())


if __name__ == "__main__":
    main()
