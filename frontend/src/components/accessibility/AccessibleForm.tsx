/**
 * AccessibleForm - WCAG 2.1 AA Compliant Form Components
 * Day 21 Implementation - Accessibility Compliance
 */

import React, { ReactNode, useId } from 'react';

// Form Field Interface
export interface FormFieldProps {
  label: string;
  children: ReactNode;
  error?: string;
  required?: boolean;
  helpText?: string;
  id?: string;
  className?: string;
}

// Form Field Component
export const FormField: React.FC<FormFieldProps> = ({
  label,
  children,
  error,
  required = false,
  helpText,
  id: providedId,
  className = ''
}) => {
  const generatedId = useId();
  const fieldId = providedId || generatedId;
  const errorId = `${fieldId}-error`;
  const helpId = `${fieldId}-help`;

  // Clone children to add necessary props
  const enhancedChildren = React.Children.map(children, (child) => {
    if (React.isValidElement(child)) {
      return React.cloneElement(child as React.ReactElement<any>, {
        id: fieldId,
        'aria-describedby': [
          error ? errorId : null,
          helpText ? helpId : null
        ].filter(Boolean).join(' ') || undefined,
        'aria-invalid': error ? 'true' : 'false',
        'aria-required': required
      });
    }
    return child;
  });

  return (
    <div className={`space-y-2 ${className}`}>
      <label 
        htmlFor={fieldId}
        className="block text-sm font-medium text-gray-700"
      >
        {label}
        {required && (
          <span 
            className="text-red-500 ml-1" 
            aria-label="required"
            title="This field is required"
          >
            *
          </span>
        )}
      </label>
      
      {enhancedChildren}
      
      {helpText && (
        <p 
          id={helpId}
          className="text-sm text-gray-500"
        >
          {helpText}
        </p>
      )}
      
      {error && (
        <div 
          id={errorId}
          role="alert"
          aria-live="polite"
          className="text-sm text-red-600 flex items-center"
        >
          <svg
            className="w-4 h-4 mr-1 flex-shrink-0"
            fill="currentColor"
            viewBox="0 0 20 20"
            aria-hidden="true"
          >
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
          {error}
        </div>
      )}
    </div>
  );
};

// Text Input Component
export interface AccessibleInputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'> {
  error?: string;
  size?: 'small' | 'medium' | 'large';
}

export const AccessibleInput: React.FC<AccessibleInputProps> = ({
  error,
  size = 'medium',
  className = '',
  ...props
}) => {
  const baseClasses = 'block w-full rounded-md border-gray-300 shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50 disabled:text-gray-500';
  
  const sizeClasses = {
    small: 'px-3 py-1.5 text-sm',
    medium: 'px-3 py-2 text-base',
    large: 'px-4 py-3 text-lg'
  };

  const errorClasses = error ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : '';
  
  const inputClasses = `${baseClasses} ${sizeClasses[size]} ${errorClasses} ${className}`;

  return (
    <input
      className={inputClasses}
      {...props}
    />
  );
};

// Textarea Component
export interface AccessibleTextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: string;
  resize?: boolean;
}

export const AccessibleTextarea: React.FC<AccessibleTextareaProps> = ({
  error,
  resize = true,
  className = '',
  ...props
}) => {
  const baseClasses = 'block w-full rounded-md border-gray-300 shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50 disabled:text-gray-500';
  const errorClasses = error ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : '';
  const resizeClasses = resize ? 'resize-y' : 'resize-none';
  
  const textareaClasses = `${baseClasses} ${errorClasses} ${resizeClasses} ${className}`;

  return (
    <textarea
      className={textareaClasses}
      rows={4}
      {...props}
    />
  );
};

// Select Component
export interface AccessibleSelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  error?: string;
  placeholder?: string;
}

export const AccessibleSelect: React.FC<AccessibleSelectProps> = ({
  error,
  placeholder,
  children,
  className = '',
  ...props
}) => {
  const baseClasses = 'block w-full rounded-md border-gray-300 shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50 disabled:text-gray-500 bg-white';
  const errorClasses = error ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : '';
  
  const selectClasses = `${baseClasses} ${errorClasses} ${className}`;

  return (
    <select
      className={selectClasses}
      {...props}
    >
      {placeholder && (
        <option value="" disabled>
          {placeholder}
        </option>
      )}
      {children}
    </select>
  );
};

// Checkbox Component
export interface AccessibleCheckboxProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label: string;
  error?: string;
}

export const AccessibleCheckbox: React.FC<AccessibleCheckboxProps> = ({
  label,
  error,
  id: providedId,
  className = '',
  ...props
}) => {
  const generatedId = useId();
  const checkboxId = providedId || generatedId;
  const errorId = `${checkboxId}-error`;

  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex items-start">
        <input
          type="checkbox"
          id={checkboxId}
          className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
          aria-describedby={error ? errorId : undefined}
          aria-invalid={error ? 'true' : 'false'}
          {...props}
        />
        <label
          htmlFor={checkboxId}
          className="ml-2 text-sm text-gray-700 cursor-pointer"
        >
          {label}
        </label>
      </div>
      
      {error && (
        <div 
          id={errorId}
          role="alert"
          aria-live="polite"
          className="text-sm text-red-600 flex items-center"
        >
          <svg
            className="w-4 h-4 mr-1 flex-shrink-0"
            fill="currentColor"
            viewBox="0 0 20 20"
            aria-hidden="true"
          >
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
          {error}
        </div>
      )}
    </div>
  );
};

// Radio Group Component
export interface RadioOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface AccessibleRadioGroupProps {
  name: string;
  options: RadioOption[];
  value?: string;
  onChange?: (value: string) => void;
  error?: string;
  className?: string;
  orientation?: 'horizontal' | 'vertical';
}

export const AccessibleRadioGroup: React.FC<AccessibleRadioGroupProps> = ({
  name,
  options,
  value,
  onChange,
  error,
  className = '',
  orientation = 'vertical'
}) => {
  const groupId = useId();
  const errorId = `${groupId}-error`;
  
  const containerClasses = orientation === 'horizontal' 
    ? 'flex space-x-4' 
    : 'space-y-2';

  const handleChange = (optionValue: string) => {
    onChange?.(optionValue);
  };

  return (
    <div className={`space-y-2 ${className}`}>
      <fieldset 
        role="radiogroup"
        aria-describedby={error ? errorId : undefined}
        aria-invalid={error ? 'true' : 'false'}
      >
        <div className={containerClasses}>
          {options.map((option) => {
            const optionId = `${groupId}-${option.value}`;
            
            return (
              <div key={option.value} className="flex items-center">
                <input
                  type="radio"
                  id={optionId}
                  name={name}
                  value={option.value}
                  checked={value === option.value}
                  onChange={() => handleChange(option.value)}
                  disabled={option.disabled}
                  className="h-4 w-4 text-blue-600 border-gray-300 focus:ring-2 focus:ring-blue-500"
                />
                <label
                  htmlFor={optionId}
                  className="ml-2 text-sm text-gray-700 cursor-pointer"
                >
                  {option.label}
                </label>
              </div>
            );
          })}
        </div>
      </fieldset>
      
      {error && (
        <div 
          id={errorId}
          role="alert"
          aria-live="polite"
          className="text-sm text-red-600 flex items-center"
        >
          <svg
            className="w-4 h-4 mr-1 flex-shrink-0"
            fill="currentColor"
            viewBox="0 0 20 20"
            aria-hidden="true"
          >
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
          {error}
        </div>
      )}
    </div>
  );
};

// Main Form Component
export interface AccessibleFormProps extends React.FormHTMLAttributes<HTMLFormElement> {
  children: ReactNode;
  onSubmit?: (event: React.FormEvent<HTMLFormElement>) => void;
  title?: string;
  description?: string;
}

export const AccessibleForm: React.FC<AccessibleFormProps> = ({
  children,
  onSubmit,
  title,
  description,
  className = '',
  ...props
}) => {
  const formId = useId();
  const titleId = `${formId}-title`;
  const descriptionId = `${formId}-description`;
  
  return (
    <form
      className={`space-y-6 ${className}`}
      onSubmit={onSubmit}
      aria-labelledby={title ? titleId : undefined}
      aria-describedby={description ? descriptionId : undefined}
      noValidate
      {...props}
    >
      {title && (
        <h2 id={titleId} className="text-lg font-medium text-gray-900">
          {title}
        </h2>
      )}
      
      {description && (
        <p id={descriptionId} className="text-sm text-gray-600">
          {description}
        </p>
      )}
      
      {children}
    </form>
  );
};

export default {
  AccessibleForm,
  FormField,
  AccessibleInput,
  AccessibleTextarea,
  AccessibleSelect,
  AccessibleCheckbox,
  AccessibleRadioGroup
};