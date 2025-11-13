'use client';

import React, { useState } from 'react';
import { Card, CardContent } from '@/app/components/Card';
import { Users, Brain, DollarSign, TrendingUp, BarChart } from 'lucide-react';

export type Persona = 'executive' | 'technical' | 'sales' | 'investor' | 'analyst';

interface PersonaSelectorProps {
  selectedPersona: Persona;
  onPersonaChange: (persona: Persona) => void;
  showDescription?: boolean;
  className?: string;
}

const personaConfig = {
  executive: {
    icon: Users,
    label: 'Executive',
    color: 'purple',
    description: 'C-suite focus on ROI, strategy, and competitive advantage',
    focus: ['Strategic impact', 'ROI', 'Competitive position'],
    detailLevel: 'High-level overview'
  },
  technical: {
    icon: Brain,
    label: 'Technical',
    color: 'blue',
    description: 'Engineers and data scientists wanting methodology and accuracy',
    focus: ['Technical details', 'Methodology', 'Data quality'],
    detailLevel: 'Detailed analysis'
  },
  sales: {
    icon: DollarSign,
    label: 'Sales',
    color: 'green',
    description: 'Sales teams needing customer value and competitive wins',
    focus: ['Customer benefits', 'Differentiation', 'Value proposition'],
    detailLevel: 'Moderate detail'
  },
  investor: {
    icon: TrendingUp,
    label: 'Investor',
    color: 'amber',
    description: 'VCs and investors focused on growth and financial metrics',
    focus: ['Financial performance', 'Growth trajectory', 'Market size'],
    detailLevel: 'Moderate detail'
  },
  analyst: {
    icon: BarChart,
    label: 'Analyst',
    color: 'gray',
    description: 'Business analysts wanting comprehensive framework analysis',
    focus: ['Comprehensive view', 'Frameworks', 'Industry trends'],
    detailLevel: 'Detailed analysis'
  }
};

export default function PersonaSelector({
  selectedPersona,
  onPersonaChange,
  showDescription = true,
  className = ''
}: PersonaSelectorProps) {
  const [hoveredPersona, setHoveredPersona] = useState<Persona | null>(null);

  const getColorClasses = (persona: Persona, isSelected: boolean) => {
    const { color } = personaConfig[persona];
    const colorMap: Record<string, { bg: string; border: string; text: string; hover: string }> = {
      purple: {
        bg: isSelected ? 'bg-purple-50' : 'bg-white',
        border: isSelected ? 'border-purple-500 border-2' : 'border-gray-200',
        text: 'text-purple-700',
        hover: 'hover:border-purple-300'
      },
      blue: {
        bg: isSelected ? 'bg-blue-50' : 'bg-white',
        border: isSelected ? 'border-blue-500 border-2' : 'border-gray-200',
        text: 'text-blue-700',
        hover: 'hover:border-blue-300'
      },
      green: {
        bg: isSelected ? 'bg-green-50' : 'bg-white',
        border: isSelected ? 'border-green-500 border-2' : 'border-gray-200',
        text: 'text-green-700',
        hover: 'hover:border-green-300'
      },
      amber: {
        bg: isSelected ? 'bg-amber-50' : 'bg-white',
        border: isSelected ? 'border-amber-500 border-2' : 'border-gray-200',
        text: 'text-amber-700',
        hover: 'hover:border-amber-300'
      },
      gray: {
        bg: isSelected ? 'bg-gray-50' : 'bg-white',
        border: isSelected ? 'border-gray-500 border-2' : 'border-gray-200',
        text: 'text-gray-700',
        hover: 'hover:border-gray-300'
      }
    };
    return colorMap[color];
  };

  return (
    <div className={`space-y-4 ${className}`}>
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {(Object.keys(personaConfig) as Persona[]).map((persona) => {
          const config = personaConfig[persona];
          const Icon = config.icon;
          const isSelected = selectedPersona === persona;
          const colors = getColorClasses(persona, isSelected);

          return (
            <button
              key={persona}
              onClick={() => onPersonaChange(persona)}
              onMouseEnter={() => setHoveredPersona(persona)}
              onMouseLeave={() => setHoveredPersona(null)}
              className={`
                p-4 rounded-lg border transition-all
                ${colors.bg} ${colors.border} ${colors.hover}
                ${isSelected ? 'shadow-md' : 'shadow-sm hover:shadow'}
              `}
            >
              <div className="flex flex-col items-center gap-2">
                <Icon className={`h-8 w-8 ${colors.text}`} />
                <span className={`font-medium ${colors.text}`}>
                  {config.label}
                </span>
              </div>
            </button>
          );
        })}
      </div>

      {showDescription && (
        <Card className="border-l-4 border-l-blue-500">
          <CardContent className="pt-6">
            <div className="space-y-3">
              <div>
                <h3 className="font-semibold text-gray-900 mb-1">
                  {personaConfig[selectedPersona].label} Perspective
                </h3>
                <p className="text-sm text-gray-600">
                  {personaConfig[selectedPersona].description}
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                <div>
                  <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">
                    Focus Areas
                  </h4>
                  <ul className="space-y-1">
                    {personaConfig[selectedPersona].focus.map((item, idx) => (
                      <li key={idx} className="text-sm text-gray-700 flex items-center gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-blue-500" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">
                    Detail Level
                  </h4>
                  <p className="text-sm text-gray-700">
                    {personaConfig[selectedPersona].detailLevel}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {hoveredPersona && !showDescription && (
        <div className="p-3 bg-gray-50 rounded-md border border-gray-200">
          <p className="text-sm text-gray-600">
            {personaConfig[hoveredPersona].description}
          </p>
        </div>
      )}
    </div>
  );
}
