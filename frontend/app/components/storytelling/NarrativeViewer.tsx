'use client';

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Lightbulb, Target, TrendingUp, CheckCircle } from 'lucide-react';

interface NarrativeSection {
  heading: string;
  content: string;
  supporting_data?: Record<string, any>;
  visualizations?: string[];
  key_points?: string[];
}

interface Narrative {
  title: string;
  subtitle?: string;
  sections: NarrativeSection[];
  key_insights: string[];
  recommendations: string[];
  tone: string;
  length_words: number;
  confidence_score: number;
  generated_for_persona: string;
}

interface NarrativeViewerProps {
  narrative: Narrative;
  onExport?: (format: string) => void;
  className?: string;
}

export default function NarrativeViewer({
  narrative,
  onExport,
  className = ''
}: NarrativeViewerProps) {
  const getPersonaBadgeColor = (persona: string) => {
    const colors: Record<string, string> = {
      executive: 'bg-purple-100 text-purple-800',
      technical: 'bg-blue-100 text-blue-800',
      sales: 'bg-green-100 text-green-800',
      investor: 'bg-amber-100 text-amber-800',
      analyst: 'bg-gray-100 text-gray-800'
    };
    return colors[persona] || 'bg-gray-100 text-gray-800';
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-amber-600';
    return 'text-red-600';
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="border-b pb-4">
        <div className="flex items-start justify-between mb-2">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {narrative.title}
            </h1>
            {narrative.subtitle && (
              <p className="text-lg text-gray-600">{narrative.subtitle}</p>
            )}
          </div>
          <div className="flex gap-2">
            <Badge className={getPersonaBadgeColor(narrative.generated_for_persona)}>
              {narrative.generated_for_persona}
            </Badge>
            <Badge variant="outline">
              {narrative.length_words} words
            </Badge>
          </div>
        </div>

        <div className="flex items-center gap-4 text-sm text-gray-500">
          <span>Tone: {narrative.tone}</span>
          <span className={getConfidenceColor(narrative.confidence_score)}>
            Confidence: {(narrative.confidence_score * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      {/* Key Insights */}
      {narrative.key_insights.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lightbulb className="h-5 w-5 text-yellow-500" />
              Key Insights
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {narrative.key_insights.map((insight, index) => (
                <li key={index} className="flex items-start gap-2">
                  <TrendingUp className="h-4 w-4 text-blue-500 mt-1 flex-shrink-0" />
                  <span className="text-gray-700">{insight}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Narrative Sections */}
      <div className="space-y-6">
        {narrative.sections.map((section, index) => (
          <Card key={index}>
            <CardHeader>
              <CardTitle className="text-xl">{section.heading}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Main content */}
              <div className="prose max-w-none">
                <p className="text-gray-700 whitespace-pre-line">
                  {section.content}
                </p>
              </div>

              {/* Key points */}
              {section.key_points && section.key_points.length > 0 && (
                <div className="mt-4 bg-blue-50 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-900 mb-2">Key Points:</h4>
                  <ul className="space-y-1">
                    {section.key_points.map((point, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <CheckCircle className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                        <span className="text-blue-800 text-sm">{point}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Visualizations */}
              {section.visualizations && section.visualizations.length > 0 && (
                <div className="mt-4">
                  <p className="text-sm text-gray-500">
                    Related charts: {section.visualizations.join(', ')}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Recommendations */}
      {narrative.recommendations.length > 0 && (
        <Card className="border-l-4 border-l-green-500">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5 text-green-500" />
              Recommendations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ol className="space-y-3">
              {narrative.recommendations.map((recommendation, index) => (
                <li key={index} className="flex items-start gap-3">
                  <span className="flex-shrink-0 flex items-center justify-center w-6 h-6 rounded-full bg-green-100 text-green-700 font-semibold text-sm">
                    {index + 1}
                  </span>
                  <span className="text-gray-700 pt-0.5">{recommendation}</span>
                </li>
              ))}
            </ol>
          </CardContent>
        </Card>
      )}

      {/* Export Options */}
      {onExport && (
        <div className="flex gap-2 justify-end pt-4 border-t">
          <button
            onClick={() => onExport('pdf')}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Export PDF
          </button>
          <button
            onClick={() => onExport('docx')}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Export Word
          </button>
          <button
            onClick={() => onExport('pptx')}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
          >
            Export Presentation
          </button>
        </div>
      )}
    </div>
  );
}
