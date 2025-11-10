/**
 * Formula Builder Component
 * Visual editor for creating and managing analytics formulas
 */
import React, { useState, useCallback } from 'react';

interface FormulaTemplate {
  name: string;
  expression: string;
  description: string;
  variables: string[];
}

interface FormulaBuilderProps {
  onFormulaCreate?: (formula: any) => void;
  templates?: Record<string, FormulaTemplate>;
}

export const FormulaBuilder: React.FC<FormulaBuilderProps> = ({
  onFormulaCreate,
  templates = {},
}) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [expression, setExpression] = useState('');
  const [category, setCategory] = useState('custom');
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');

  const handleTemplateSelect = useCallback((templateKey: string) => {
    if (templates[templateKey]) {
      const template = templates[templateKey];
      setName(template.name);
      setExpression(template.expression);
      setDescription(template.description);
      setSelectedTemplate(templateKey);
    }
  }, [templates]);

  const handleCreateFormula = useCallback(async () => {
    if (!name.trim()) {
      setError('Formula name is required');
      return;
    }

    if (!expression.trim()) {
      setError('Expression is required');
      return;
    }

    try {
      const formulaData = {
        name: name.trim(),
        description: description.trim(),
        expression: expression.trim(),
        category,
      };

      if (onFormulaCreate) {
        await onFormulaCreate(formulaData);
        setSuccess('Formula created successfully!');
        // Reset form
        setName('');
        setDescription('');
        setExpression('');
        setSelectedTemplate('');
        setError('');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create formula');
    }
  }, [name, expression, description, category, onFormulaCreate]);

  return (
    <div className="formula-builder p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6">Formula Builder</h2>

      {/* Templates Section */}
      {Object.keys(templates).length > 0 && (
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Quick Templates
          </label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {Object.entries(templates).map(([key, template]) => (
              <button
                key={key}
                onClick={() => handleTemplateSelect(key)}
                className={`p-2 text-sm border rounded transition ${
                  selectedTemplate === key
                    ? 'bg-blue-500 text-white border-blue-500'
                    : 'bg-white text-gray-700 border-gray-300 hover:border-blue-500'
                }`}
              >
                {template.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Name Input */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Formula Name
        </label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g., Gross Margin"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Expression Input */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Expression
        </label>
        <textarea
          value={expression}
          onChange={(e) => setExpression(e.target.value)}
          placeholder="e.g., (revenue - cogs) / revenue"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono"
          rows={4}
        />
        <p className="mt-2 text-sm text-gray-600">
          Supported: +, -, *, /, ^, %, >, <, >=, <=, ==, !=, SUM, AVG, MIN, MAX, COUNT, ABS, SQRT, ROUND
        </p>
      </div>

      {/* Description Input */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Description
        </label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Brief description of what this formula calculates"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          rows={2}
        />
      </div>

      {/* Category Selection */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Category
        </label>
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="custom">Custom</option>
          <option value="financial">Financial</option>
          <option value="marketing">Marketing</option>
          <option value="sales">Sales</option>
          <option value="operations">Operations</option>
        </select>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {/* Success Message */}
      {success && (
        <div className="mb-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded">
          {success}
        </div>
      )}

      {/* Create Button */}
      <button
        onClick={handleCreateFormula}
        className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded transition"
      >
        Create Formula
      </button>
    </div>
  );
};

export default FormulaBuilder;
