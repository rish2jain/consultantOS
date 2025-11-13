import type { Template } from '@/types/templates';

export const starterTemplates: Template[] = [
  {
    id: 'tmpl_porter_saas_enterprise',
    template_id: 'tmpl_porter_saas_enterprise',
    name: 'Enterprise SaaS Moat (Porter Five Forces)',
    description:
      'Pressure-test an ARR-heavy cloud platform, focusing on procurement dynamics, AI copilots, and hyperscaler alliances.',
    category: 'strategic',
    framework_type: 'porter',
    frameworks: ['porter'],
    visibility: 'public',
    industry: 'B2B SaaS / Cloud Infrastructure',
    region: 'Global',
    depth: 'board-ready',
    custom_focus: ['Switching costs', 'Buyer consolidation', 'AI-assisted workflows'],
    tags: ['SaaS', 'Enterprise', 'Porter'],
    prompt_template: `You are advising the CEO of {{company}}, a {{industry}} vendor with enterprise focus in {{region}}.
Apply Porter's Five Forces to quantify each competitive pressure.
Highlight:
- Procurement blockers and pricing power drivers
- Role of hyperscaler marketplaces and ISV alliances
- Impact of AI copilots on differentiation
Deliver a board-ready summary with recommendations ranked by impact vs. effort.`,
    created_by: 'consultantos-studio',
    created_at: '2025-10-15T12:00:00Z',
    fork_count: 18,
    usage_count: 64,
  },
  {
    id: 'tmpl_swot_fintech_growth',
    template_id: 'tmpl_swot_fintech_growth',
    name: 'Consumer Fintech GTM SWOT',
    description:
      'Balanced SWOT for venture-backed consumer banking apps – tuned for CAC compression, compliance drag, and ecosystem partners.',
    category: 'market',
    framework_type: 'swot',
    frameworks: ['swot'],
    visibility: 'public',
    industry: 'Consumer Fintech / Neobanking',
    region: 'North America',
    depth: 'growth-playbook',
    custom_focus: ['Unit economics', 'Trust & compliance', 'Partner distribution'],
    tags: ['Fintech', 'Growth', 'SWOT'],
    prompt_template: `Run a SWOT assessment for {{company}} targeting Gen-Z mass affluent users in {{region}}.
Emphasize:
- CAC vs. LTV trajectory and cost of capital
- Compliance, fraud, and data-privacy constraints
- Ecosystem leverage: payroll, card networks, brand partners
Finish with three GTM moves and two risk mitigations.`,
    created_by: 'consultantos-studio',
    created_at: '2025-09-28T09:30:00Z',
    fork_count: 12,
    usage_count: 47,
  },
  {
    id: 'tmpl_pestel_ev_supply_chain',
    template_id: 'tmpl_pestel_ev_supply_chain',
    name: 'APAC EV Supply-Chain PESTEL',
    description:
      'Regulatory and geopolitical scan for electric-vehicle OEMs balancing battery localization and grid incentives across APAC.',
    category: 'risk',
    framework_type: 'pestel',
    frameworks: ['pestel'],
    visibility: 'public',
    industry: 'Electric Vehicles / Battery Supply Chain',
    region: 'APAC',
    depth: 'regulatory-mapping',
    custom_focus: ['Battery minerals policy', 'Trade corridors', 'Grid constraints'],
    tags: ['EV', 'Supply Chain', 'Policy'],
    prompt_template: `Provide a PESTEL breakdown for {{company}} expanding EV production across {{region}}.
Call out:
- Policy shifts (tariffs, subsidies, export controls)
- Environmental and grid-readiness bottlenecks
- Labor, IP, and community risks tied to gigafactories
Close with confidence-weighted scenario triggers for 2025-2027.`,
    created_by: 'consultantos-studio',
    created_at: '2025-10-02T16:45:00Z',
    fork_count: 9,
    usage_count: 33,
  },
  {
    id: 'tmpl_blue_ocean_digital_health',
    template_id: 'tmpl_blue_ocean_digital_health',
    name: 'Digital Health Blue Ocean Canvas',
    description:
      'Identify whitespace moves for virtual-first care platforms, blending payer partnerships, employer channels, and AI triage.',
    category: 'strategic',
    framework_type: 'blue_ocean',
    frameworks: ['blue_ocean', 'swot'],
    visibility: 'public',
    industry: 'Digital Health / Virtual Care',
    region: 'United States',
    depth: 'innovation-lab',
    custom_focus: ['Experience curves', 'Payer contracting', 'AI triage'],
    tags: ['Healthcare', 'Blue Ocean', 'Innovation'],
    prompt_template: `Using the Blue Ocean Strategy canvas, craft a differentiation play for {{company}} in {{region}}.
Cover:
- Factors to eliminate/reduce (e.g., clinic footprint, reactive care)
- Elements to raise/create (AI care teams, employer bundles, outcomes guarantees)
- Two disruptive pricing or packaging ideas
Summarize the new value curve plus the first 90-day experiments.`,
    created_by: 'consultantos-studio',
    created_at: '2025-10-05T14:10:00Z',
    fork_count: 15,
    usage_count: 41,
  },
];
