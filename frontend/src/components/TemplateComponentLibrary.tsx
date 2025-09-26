/**
 * Template Component Library - Day 17 Implementation
 * Reusable template components for the drag-and-drop builder
 */

import React from 'react';
import { ComponentType } from './TemplateBuilder';

// Enhanced component rendering utilities
export const renderTemplateComponent = (component: any): React.ReactNode => {
  switch (component.type as ComponentType) {
    case 'heading':
      return renderHeading(component);
    case 'text':
      return renderText(component);
    case 'button':
      return renderButton(component);
    case 'input':
      return renderInput(component);
    case 'textarea':
      return renderTextarea(component);
    case 'select':
      return renderSelect(component);
    case 'checkbox':
      return renderCheckbox(component);
    case 'date':
      return renderDatePicker(component);
    case 'image':
      return renderImage(component);
    case 'card':
      return renderCard(component);
    case 'section':
      return renderSection(component);
    case 'grid':
      return renderGrid(component);
    case 'list':
      return renderList(component);
    case 'table':
      return renderTable(component);
    default:
      return renderDefault(component);
  }
};

// Individual component renderers
const renderHeading = (component: any) => {
  const HeadingTag = `h${component.props.level || 1}` as keyof JSX.IntrinsicElements;
  const sizeClasses = {
    1: 'text-3xl font-bold',
    2: 'text-2xl font-semibold',
    3: 'text-xl font-semibold',
    4: 'text-lg font-medium',
    5: 'text-base font-medium',
    6: 'text-sm font-medium'
  };
  
  return (
    <HeadingTag className={`${sizeClasses[component.props.level as keyof typeof sizeClasses]} text-gray-900 ${component.props.className || ''}`}>
      {component.props.text || 'Heading'}
    </HeadingTag>
  );
};

const renderText = (component: any) => (
  <p className={`text-gray-700 leading-relaxed ${component.props.className || ''}`}>
    {component.props.content || 'Text content'}
  </p>
);

const renderButton = (component: any) => {
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'bg-gray-600 text-white hover:bg-gray-700',
    outline: 'border border-gray-300 text-gray-700 hover:bg-gray-50',
    success: 'bg-green-600 text-white hover:bg-green-700',
    danger: 'bg-red-600 text-white hover:bg-red-700',
  };

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  return (
    <button
      className={`
        rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
        ${variantClasses[component.props.variant as keyof typeof variantClasses] || variantClasses.primary}
        ${sizeClasses[component.props.size as keyof typeof sizeClasses] || sizeClasses.md}
        ${component.props.className || ''}
      `}
      disabled={component.props.disabled}
    >
      {component.props.text || 'Button'}
    </button>
  );
};

const renderInput = (component: any) => (
  <div className={component.props.containerClassName || ''}>
    {component.props.label && (
      <label className="block text-sm font-medium text-gray-700 mb-2">
        {component.props.label}
        {component.props.required && <span className="text-red-500 ml-1">*</span>}
      </label>
    )}
    <input
      type={component.props.inputType || 'text'}
      placeholder={component.props.placeholder}
      value={component.props.value || ''}
      required={component.props.required}
      disabled={component.props.disabled}
      className={`
        w-full px-3 py-2 border border-gray-300 rounded-lg
        focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
        disabled:bg-gray-50 disabled:text-gray-500
        ${component.props.error ? 'border-red-500 focus:ring-red-500' : ''}
        ${component.props.className || ''}
      `}
    />
    {component.props.helperText && (
      <p className="mt-1 text-sm text-gray-500">{component.props.helperText}</p>
    )}
    {component.props.error && (
      <p className="mt-1 text-sm text-red-600">{component.props.error}</p>
    )}
  </div>
);

const renderTextarea = (component: any) => (
  <div className={component.props.containerClassName || ''}>
    {component.props.label && (
      <label className="block text-sm font-medium text-gray-700 mb-2">
        {component.props.label}
        {component.props.required && <span className="text-red-500 ml-1">*</span>}
      </label>
    )}
    <textarea
      placeholder={component.props.placeholder}
      value={component.props.value || ''}
      rows={component.props.rows || 3}
      required={component.props.required}
      disabled={component.props.disabled}
      className={`
        w-full px-3 py-2 border border-gray-300 rounded-lg
        focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
        disabled:bg-gray-50 disabled:text-gray-500 resize-vertical
        ${component.props.error ? 'border-red-500 focus:ring-red-500' : ''}
        ${component.props.className || ''}
      `}
    />
    {component.props.helperText && (
      <p className="mt-1 text-sm text-gray-500">{component.props.helperText}</p>
    )}
  </div>
);

const renderSelect = (component: any) => (
  <div className={component.props.containerClassName || ''}>
    {component.props.label && (
      <label className="block text-sm font-medium text-gray-700 mb-2">
        {component.props.label}
        {component.props.required && <span className="text-red-500 ml-1">*</span>}
      </label>
    )}
    <select
      value={component.props.value || ''}
      required={component.props.required}
      disabled={component.props.disabled}
      className={`
        w-full px-3 py-2 border border-gray-300 rounded-lg
        focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
        disabled:bg-gray-50 disabled:text-gray-500
        ${component.props.className || ''}
      `}
    >
      {component.props.placeholder && (
        <option value="" disabled>
          {component.props.placeholder}
        </option>
      )}
      {(component.props.options || []).map((option: any, index: number) => (
        <option key={index} value={typeof option === 'string' ? option : option.value}>
          {typeof option === 'string' ? option : option.label}
        </option>
      ))}
    </select>
  </div>
);

const renderCheckbox = (component: any) => (
  <div className={`flex items-center ${component.props.containerClassName || ''}`}>
    <input
      type="checkbox"
      checked={component.props.checked || false}
      disabled={component.props.disabled}
      className={`
        h-4 w-4 text-blue-600 border-gray-300 rounded
        focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
        ${component.props.className || ''}
      `}
    />
    {component.props.label && (
      <label className="ml-2 block text-sm text-gray-700">
        {component.props.label}
      </label>
    )}
  </div>
);

const renderDatePicker = (component: any) => (
  <div className={component.props.containerClassName || ''}>
    {component.props.label && (
      <label className="block text-sm font-medium text-gray-700 mb-2">
        {component.props.label}
        {component.props.required && <span className="text-red-500 ml-1">*</span>}
      </label>
    )}
    <input
      type="date"
      value={component.props.value || ''}
      min={component.props.min}
      max={component.props.max}
      required={component.props.required}
      disabled={component.props.disabled}
      className={`
        w-full px-3 py-2 border border-gray-300 rounded-lg
        focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
        disabled:bg-gray-50 disabled:text-gray-500
        ${component.props.className || ''}
      `}
    />
  </div>
);

const renderImage = (component: any) => (
  <div className={`relative ${component.props.containerClassName || ''}`}>
    <img
      src={component.props.src || '/api/placeholder/300/200'}
      alt={component.props.alt || 'Image'}
      className={`
        max-w-full h-auto rounded-lg
        ${component.props.className || ''}
      `}
      style={{
        width: component.props.width,
        height: component.props.height,
        objectFit: component.props.objectFit || 'cover'
      }}
    />
    {component.props.caption && (
      <p className="mt-2 text-sm text-gray-600 text-center">{component.props.caption}</p>
    )}
  </div>
);

const renderCard = (component: any) => (
  <div className={`bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden ${component.props.className || ''}`}>
    {component.props.image && (
      <img
        src={component.props.image}
        alt={component.props.imageAlt || ''}
        className="w-full h-48 object-cover"
      />
    )}
    <div className="p-6">
      {component.props.title && (
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          {component.props.title}
        </h3>
      )}
      {component.props.content && (
        <p className="text-gray-600 mb-4">
          {component.props.content}
        </p>
      )}
      {component.props.actions && (
        <div className="flex space-x-3">
          {component.props.actions.map((action: any, index: number) => (
            <button
              key={index}
              className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                action.variant === 'primary'
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'text-gray-700 hover:text-gray-900'
              }`}
            >
              {action.label}
            </button>
          ))}
        </div>
      )}
    </div>
  </div>
);

const renderSection = (component: any) => (
  <section className={`bg-white rounded-lg border border-gray-200 ${component.props.className || ''}`}>
    {component.props.title && (
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900">
          {component.props.title}
        </h2>
        {component.props.subtitle && (
          <p className="text-gray-600 mt-1">{component.props.subtitle}</p>
        )}
      </div>
    )}
    <div className="p-6">
      {component.props.content && (
        <div className="prose max-w-none">{component.props.content}</div>
      )}
    </div>
  </section>
);

const renderGrid = (component: any) => {
  const columns = component.props.columns || 2;
  const gap = component.props.gap || 6;
  
  return (
    <div 
      className={`grid gap-${gap} ${component.props.className || ''}`}
      style={{ gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))` }}
    >
      {(component.props.items || []).map((item: any, index: number) => (
        <div key={index} className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          {typeof item === 'string' ? item : item.content || `Grid Item ${index + 1}`}
        </div>
      ))}
    </div>
  );
};

const renderList = (component: any) => {
  const ListTag = component.props.ordered ? 'ol' : 'ul';
  
  return (
    <div className={component.props.containerClassName || ''}>
      {component.props.title && (
        <h3 className="text-lg font-medium text-gray-900 mb-3">
          {component.props.title}
        </h3>
      )}
      <ListTag className={`
        space-y-2 ${component.props.ordered ? 'list-decimal' : 'list-disc'} list-inside
        ${component.props.className || ''}
      `}>
        {(component.props.items || []).map((item: any, index: number) => (
          <li key={index} className="text-gray-700">
            {typeof item === 'string' ? item : item.text || `Item ${index + 1}`}
          </li>
        ))}
      </ListTag>
    </div>
  );
};

const renderTable = (component: any) => (
  <div className={`overflow-hidden border border-gray-200 rounded-lg ${component.props.containerClassName || ''}`}>
    {component.props.title && (
      <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">{component.props.title}</h3>
      </div>
    )}
    <table className={`min-w-full divide-y divide-gray-200 ${component.props.className || ''}`}>
      <thead className="bg-gray-50">
        <tr>
          {(component.props.headers || []).map((header: string, index: number) => (
            <th
              key={index}
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              {header}
            </th>
          ))}
        </tr>
      </thead>
      <tbody className="bg-white divide-y divide-gray-200">
        {(component.props.rows || []).map((row: any[], rowIndex: number) => (
          <tr key={rowIndex} className={rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
            {row.map((cell: any, cellIndex: number) => (
              <td
                key={cellIndex}
                className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
              >
                {cell}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

const renderDefault = (component: any) => (
  <div className={`p-4 bg-gray-100 border border-gray-300 rounded-lg ${component.props.className || ''}`}>
    <p className="text-sm text-gray-600">
      {component.type} component
    </p>
    {component.props.content && (
      <p className="text-xs text-gray-500 mt-1">{component.props.content}</p>
    )}
  </div>
);

export default renderTemplateComponent;