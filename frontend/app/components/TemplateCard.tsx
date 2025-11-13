"use client";

import React from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from './Card';
import { Badge } from './Badge';
import { Button } from './Button';
import { Eye, Copy, FileText } from 'lucide-react';
import type { Template } from '@/types/templates';

export type { Template } from '@/types/templates';

export interface TemplateCardProps {
  /** Template data */
  template: Template;
  /** View template handler */
  onView?: (template: Template) => void;
  /** Use template handler */
  onUse?: (template: Template) => void;
  /** Fork template handler */
  onFork?: (template: Template) => void;
  /** Card is clickable */
  clickable?: boolean;
}

type BadgeVariant = 'primary' | 'success' | 'info' | 'warning' | 'danger' | 'default';

const categoryColors: Record<string, BadgeVariant> = {
  strategic: 'primary',
  financial: 'success',
  operational: 'info',
  market: 'warning',
  risk: 'danger',
  porter: 'primary',
  swot: 'warning',
  pestel: 'info',
  blue_ocean: 'success',
};

const getCategoryBadgeVariant = (category: string): BadgeVariant => {
  return categoryColors[category] || 'default';
};

const frameworkLabels: Record<Template['framework_type'], string> = {
  porter: "Porter's 5 Forces",
  swot: 'SWOT Analysis',
  pestel: 'PESTEL Analysis',
  blue_ocean: 'Blue Ocean Strategy',
};

export const TemplateCard: React.FC<TemplateCardProps> = ({
  template,
  onView,
  onUse,
  onFork,
  clickable = false,
}) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <Card
      variant="default"
      hoverable
      clickable={clickable}
      onClick={clickable ? () => onView?.(template) : undefined}
      className="h-full flex flex-col"
    >
      <CardHeader>
        <div className="flex items-start justify-between gap-2 mb-2">
          <Badge
            variant={getCategoryBadgeVariant(template.category)}
            size="sm"
          >
            {template.category}
          </Badge>
          <Badge
            variant="default"
            size="sm"
          >
            {frameworkLabels[template.framework_type]}
          </Badge>
        </div>
        <CardTitle className="line-clamp-2">
          {template.name}
        </CardTitle>
        <CardDescription className="line-clamp-3 mt-2">
          {template.description}
        </CardDescription>
      </CardHeader>

      <CardContent className="flex-1">
        <div className="space-y-2 text-sm text-gray-600">
          {template.industry && (
            <div className="flex items-center gap-2">
              <span className="font-medium">Industry:</span>
              <span>{template.industry}</span>
            </div>
          )}
          {template.region && (
            <div className="flex items-center gap-2">
              <span className="font-medium">Region:</span>
              <span>{template.region}</span>
            </div>
          )}
          <div className="flex items-center gap-2">
            <span className="font-medium">Visibility:</span>
            <Badge
              variant={template.visibility === 'public' ? 'success' : 'default'}
              size="sm"
            >
              {template.visibility}
            </Badge>
          </div>
        </div>
      </CardContent>

      <CardFooter>
        <div className="w-full space-y-3">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>Created {formatDate(template.created_at)}</span>
            <span className="flex items-center gap-1">
              <Copy className="w-3 h-3" aria-hidden="true" />
              {template.fork_count ?? 0} forks
            </span>
          </div>

          <div className="flex items-center gap-2">
            {onView && (
              <Button
                variant="outline"
                size="sm"
                leftIcon={<Eye className="w-4 h-4" />}
                onClick={(e) => {
                  e.stopPropagation();
                  onView(template);
                }}
                fullWidth
              >
                View
              </Button>
            )}
            {onUse && (
              <Button
                variant="primary"
                size="sm"
                leftIcon={<FileText className="w-4 h-4" />}
                onClick={(e) => {
                  e.stopPropagation();
                  onUse(template);
                }}
                fullWidth
              >
                Use
              </Button>
            )}
            {onFork && (
              <Button
                variant="ghost"
                size="sm"
                leftIcon={<Copy className="w-4 h-4" />}
                onClick={(e) => {
                  e.stopPropagation();
                  onFork(template);
                }}
                aria-label="Fork template"
              >
                Fork
              </Button>
            )}
          </div>
        </div>
      </CardFooter>
    </Card>
  );
};
