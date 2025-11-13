export type TemplateCategory =
  | 'strategic'
  | 'financial'
  | 'operational'
  | 'market'
  | 'risk'
  | 'porter'
  | 'swot'
  | 'pestel'
  | 'blue_ocean'
  | 'custom'
  | 'industry_specific';

export type FrameworkType = 'porter' | 'swot' | 'pestel' | 'blue_ocean';

export type TemplateVisibility = 'public' | 'private' | 'shared';

export interface Template {
  id?: string;
  template_id?: string;
  name: string;
  description: string;
  category: TemplateCategory | string;
  framework_type: FrameworkType | string;
  visibility: TemplateVisibility;
  industry?: string;
  region?: string;
  prompt_template: string;
  created_by: string;
  created_at: string;
  updated_at?: string;
  fork_count?: number;
  usage_count?: number;
  frameworks?: string[];
  depth?: string;
  custom_focus?: string[];
  tags?: string[];
}
