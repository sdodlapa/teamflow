/**
 * Accessibility Components Index - Day 21 Implementation
 * WCAG 2.1 AA Compliant Components Export
 */

// Core Components
export { default as AccessibleButton } from './AccessibleButton';
export { default as AccessibleModal, useModal, ConfirmationModal } from './AccessibleModal';
export { default as AccessibleNavigation, BreadcrumbNavigation, TabNavigation, SkipNavigation } from './AccessibleNavigation';

// Form Components
export {
  AccessibleForm,
  FormField,
  AccessibleInput,
  AccessibleTextarea,
  AccessibleSelect,
  AccessibleCheckbox,
  AccessibleRadioGroup,
  default as FormComponents
} from './AccessibleForm';

// Export types
export type { AccessibleButtonProps } from './AccessibleButton';
export type { AccessibleModalProps, ConfirmationModalProps } from './AccessibleModal';
export type { 
  AccessibleNavigationProps, 
  NavigationItem, 
  BreadcrumbNavigationProps, 
  BreadcrumbItem,
  TabNavigationProps,
  TabItem
} from './AccessibleNavigation';

export type {
  AccessibleFormProps,
  FormFieldProps,
  AccessibleInputProps,
  AccessibleTextareaProps,
  AccessibleSelectProps,
  AccessibleCheckboxProps,
  AccessibleRadioGroupProps,
  RadioOption
} from './AccessibleForm';