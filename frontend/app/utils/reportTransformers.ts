/**
 * Utility functions for transforming API response data to UI format
 */

export interface ReportData {
  id: string;
  company: string;
  industry: string;
  created_at: string;
  frameworks: string[];
  depth: 'standard' | 'deep';
  confidence_score: number;
  status: 'completed' | 'processing' | 'failed';
  pdf_url?: string;
  analysis?: {
    porter?: {
      competitive_rivalry: string;
      supplier_power: string;
      buyer_power: string;
      threat_of_substitution: string;
      threat_of_new_entry: string;
      overall_assessment: string;
    };
    swot?: {
      strengths: string[];
      weaknesses: string[];
      opportunities: string[];
      threats: string[];
    };
    pestel?: {
      political: string;
      economic: string;
      social: string;
      technological: string;
      environmental: string;
      legal: string;
    };
    blue_ocean?: {
      eliminate: string[];
      reduce: string[];
      raise: string[];
      create: string[];
    };
  };
}

interface FrameworkAnalysis {
  porters_five_forces?: {
    competitive_rivalry?: string;
    supplier_power?: string;
    buyer_power?: string;
    threat_of_substitution?: string;
    threat_of_new_entry?: string;
    overall_assessment?: string;
  };
  porter_five_forces?: {
    competitive_rivalry?: string;
    supplier_power?: string;
    buyer_power?: string;
    threat_of_substitution?: string;
    threat_of_new_entry?: string;
    overall_assessment?: string;
  };
  swot_analysis?: {
    strengths?: string[];
    weaknesses?: string[];
    opportunities?: string[];
    threats?: string[];
  };
  pestel_analysis?: {
    political?: string;
    economic?: string;
    social?: string;
    technological?: string;
    environmental?: string;
    legal?: string;
  };
  blue_ocean_strategy?: {
    eliminate?: string[];
    reduce?: string[];
    raise?: string[];
    create?: string[];
  };
}

interface ApiReportData {
  report_id?: string;
  id?: string;
  company?: string;
  industry?: string;
  created_at?: string;
  frameworks?: string[];
  depth?: 'standard' | 'deep';
  confidence_score?: number;
  status?: 'completed' | 'processing' | 'failed';
  report_url?: string;
  pdf_url?: string;
  framework_analysis?: FrameworkAnalysis;
}

/**
 * Transform framework analysis from API format to UI format
 */
function transformFrameworkAnalysis(
  framework_analysis?: FrameworkAnalysis
): ReportData['analysis'] {
  if (!framework_analysis) {
    return undefined;
  }

  const porterData =
    framework_analysis.porters_five_forces ||
    framework_analysis.porter_five_forces;

  return {
    porter: porterData
      ? {
          competitive_rivalry: porterData.competitive_rivalry || '',
          supplier_power: porterData.supplier_power || '',
          buyer_power: porterData.buyer_power || '',
          threat_of_substitution: porterData.threat_of_substitution || '',
          threat_of_new_entry: porterData.threat_of_new_entry || '',
          overall_assessment: porterData.overall_assessment || '',
        }
      : undefined,
    swot: framework_analysis.swot_analysis
      ? {
          strengths: framework_analysis.swot_analysis.strengths || [],
          weaknesses: framework_analysis.swot_analysis.weaknesses || [],
          opportunities: framework_analysis.swot_analysis.opportunities || [],
          threats: framework_analysis.swot_analysis.threats || [],
        }
      : undefined,
    pestel: framework_analysis.pestel_analysis
      ? {
          political: framework_analysis.pestel_analysis.political || '',
          economic: framework_analysis.pestel_analysis.economic || '',
          social: framework_analysis.pestel_analysis.social || '',
          technological:
            framework_analysis.pestel_analysis.technological || '',
          environmental:
            framework_analysis.pestel_analysis.environmental || '',
          legal: framework_analysis.pestel_analysis.legal || '',
        }
      : undefined,
    blue_ocean: framework_analysis.blue_ocean_strategy
      ? {
          eliminate: framework_analysis.blue_ocean_strategy.eliminate || [],
          reduce: framework_analysis.blue_ocean_strategy.reduce || [],
          raise: framework_analysis.blue_ocean_strategy.raise || [],
          create: framework_analysis.blue_ocean_strategy.create || [],
        }
      : undefined,
  };
}

/**
 * Transform API report data to UI format
 */
export function transformReportData(
  apiData: ApiReportData,
  reportId: string
): ReportData {
  return {
    id: apiData.report_id || apiData.id || reportId,
    company: apiData.company || '',
    industry: apiData.industry || '',
    created_at: apiData.created_at || new Date().toISOString(),
    frameworks: apiData.frameworks || [],
    depth: apiData.depth || 'standard',
    confidence_score: apiData.confidence_score || 0,
    status: apiData.status || 'completed',
    pdf_url: apiData.report_url || apiData.pdf_url,
    analysis: transformFrameworkAnalysis(apiData.framework_analysis),
  };
}
