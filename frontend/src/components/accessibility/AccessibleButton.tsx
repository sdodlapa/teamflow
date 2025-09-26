/**
 * AccessibleButton - WCAG 2.1 AA Compliant Button Component
 * Day 21 Implementation - Accessibility Compliance
 */

import React, { forwardRef, ReactNode } from 'react';
import { ARIA_ROLES, KEYBOARD_KEYS } from '../../utils/accessibility';

export interface AccessibleButtonProps {
  children: ReactNode;
  onClick?: (event: React.MouseEvent<HTMLButtonElement> | React.KeyboardEvent<HTMLButtonElement>) => void;
  type?: 'button' | 'submit' | 'reset';
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  loading?: boolean;
  'aria-label'?: string;
  'aria-describedby'?: string;
  'aria-expanded'?: boolean;
  'aria-haspopup'?: boolean | 'menu' | 'listbox' | 'tree' | 'grid' | 'dialog';
  'aria-controls'?: string;
  'aria-pressed'?: boolean;
  className?: string;
  id?: string;
  tabIndex?: number;
  autoFocus?: boolean;
  tooltip?: string;
}

const AccessibleButton = forwardRef<HTMLButtonElement, AccessibleButtonProps>(({
  children,
  onClick,
  type = 'button',
  variant = 'primary',
  size = 'medium',
  disabled = false,
  loading = false,
  'aria-label': ariaLabel,
  'aria-describedby': ariaDescribedBy,
  'aria-expanded': ariaExpanded,
  'aria-haspopup': ariaHasPopup,
  'aria-controls': ariaControls,
  'aria-pressed': ariaPressed,
  className = '',
  id,
  tabIndex,
  autoFocus = false,
  tooltip,
  ...props
}, ref) => {
  // Base button classes with proper contrast ratios
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
  
  // Variant classes - all meet WCAG 2.1 AA contrast requirements
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500 active:bg-blue-800',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500 active:bg-gray-400',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500 active:bg-red-800',
    ghost: 'bg-transparent text-gray-700 hover:bg-gray-100 focus:ring-gray-500 active:bg-gray-200 border border-gray-300'
  };

  // Size classes
  const sizeClasses = {
    small: 'px-3 py-1.5 text-sm',
    medium: 'px-4 py-2 text-base',
    large: 'px-6 py-3 text-lg'
  };

  const buttonClasses = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`;

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    if (disabled || loading) {
      event.preventDefault();
      return;
    }
    onClick?.(event);
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLButtonElement>) => {
    // Enhanced keyboard support
    if (event.key === KEYBOARD_KEYS.ENTER || event.key === KEYBOARD_KEYS.SPACE) {
      if (disabled || loading) {
        event.preventDefault();
        return;
      }
      onClick?.(event);
    }
  };

  const ariaAttributes = {
    role: ARIA_ROLES.button,
    'aria-disabled': disabled || loading,
    ...(ariaLabel && { 'aria-label': ariaLabel }),
    ...(ariaDescribedBy && { 'aria-describedby': ariaDescribedBy }),
    ...(ariaExpanded !== undefined && { 'aria-expanded': ariaExpanded }),
    ...(ariaHasPopup && { 'aria-haspopup': ariaHasPopup }),
    ...(ariaControls && { 'aria-controls': ariaControls }),
    ...(ariaPressed !== undefined && { 'aria-pressed': ariaPressed }),
    ...(tooltip && { 'aria-describedby': `${id}-tooltip` })
  };

  return (
    <>
      <button
        ref={ref}
        type={type}
        id={id}
        className={buttonClasses}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        disabled={disabled || loading}
        tabIndex={tabIndex}
        autoFocus={autoFocus}
        {...ariaAttributes}
        {...props}
      >
        {loading && (
          <svg 
            className="animate-spin -ml-1 mr-3 h-5 w-5 text-current" 
            xmlns="http://www.w3.org/2000/svg" 
            fill="none" 
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <circle 
              className="opacity-25" 
              cx="12" 
              cy="12" 
              r="10" 
              stroke="currentColor" 
              strokeWidth="4"
            />
            <path 
              className="opacity-75" 
              fill="currentColor" 
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        )}
        <span className={loading ? 'opacity-50' : ''}>
          {children}
        </span>
        {loading && (
          <span className="sr-only">Loading...</span>
        )}
      </button>
      
      {tooltip && (
        <div
          id={`${id}-tooltip`}
          role="tooltip"
          className="absolute z-50 px-2 py-1 text-sm text-white bg-gray-900 rounded opacity-0 pointer-events-none transition-opacity duration-200"
        >
          {tooltip}
        </div>
      )}
    </>
  );
});

AccessibleButton.displayName = 'AccessibleButton';

export default AccessibleButton;