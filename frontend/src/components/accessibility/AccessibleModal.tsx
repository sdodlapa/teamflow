/**
 * AccessibleModal - WCAG 2.1 AA Compliant Modal Component
 * Day 21 Implementation - Accessibility Compliance
 */

import React, { ReactNode, useEffect, useRef, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { KEYBOARD_KEYS, keyboardNavigation } from '../../utils/accessibility';
import AccessibleButton from './AccessibleButton';

export interface AccessibleModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  size?: 'small' | 'medium' | 'large' | 'full';
  closeOnOverlayClick?: boolean;
  closeOnEscape?: boolean;
  preventScroll?: boolean;
  initialFocus?: React.RefObject<HTMLElement>;
  returnFocus?: React.RefObject<HTMLElement>;
  className?: string;
  overlayClassName?: string;
  contentClassName?: string;
  'aria-describedby'?: string;
  role?: 'dialog' | 'alertdialog';
}

const AccessibleModal: React.FC<AccessibleModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'medium',
  closeOnOverlayClick = true,
  closeOnEscape = true,
  preventScroll = true,
  initialFocus,
  returnFocus,
  className = '',
  overlayClassName = '',
  contentClassName = '',
  'aria-describedby': ariaDescribedBy,
  role = 'dialog'
}) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const titleId = `modal-title-${Math.random().toString(36).substr(2, 9)}`;
  const previousActiveElement = useRef<HTMLElement | null>(null);
  const trapFocusCleanup = useRef<(() => void) | null>(null);

  // Size classes
  const sizeClasses = {
    small: 'max-w-md',
    medium: 'max-w-lg',
    large: 'max-w-2xl',
    full: 'max-w-7xl mx-4'
  };

  // Store focus when modal opens
  useEffect(() => {
    if (isOpen) {
      previousActiveElement.current = document.activeElement as HTMLElement;
      
      // Prevent body scroll
      if (preventScroll) {
        document.body.style.overflow = 'hidden';
      }
    }

    return () => {
      // Restore scroll
      if (preventScroll) {
        document.body.style.overflow = '';
      }
    };
  }, [isOpen, preventScroll]);

  // Focus management
  useEffect(() => {
    if (isOpen && modalRef.current) {
      // Set up focus trap
      trapFocusCleanup.current = keyboardNavigation.trapFocus(modalRef.current);
      
      // Set initial focus
      const focusTarget = initialFocus?.current || 
                         modalRef.current.querySelector('[autofocus]') as HTMLElement ||
                         modalRef.current.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])') as HTMLElement;
      
      if (focusTarget) {
        // Small delay to ensure modal is fully rendered
        setTimeout(() => {
          focusTarget.focus();
        }, 100);
      }
    }

    return () => {
      if (trapFocusCleanup.current) {
        trapFocusCleanup.current();
        trapFocusCleanup.current = null;
      }
    };
  }, [isOpen, initialFocus]);

  // Handle close and restore focus
  const handleClose = useCallback(() => {
    onClose();
    
    // Restore focus to the element that opened the modal
    setTimeout(() => {
      const focusTarget = returnFocus?.current || previousActiveElement.current;
      if (focusTarget && typeof focusTarget.focus === 'function') {
        focusTarget.focus();
      }
    }, 100);
  }, [onClose, returnFocus]);

  // Keyboard event handlers
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (!isOpen) return;

    if (event.key === KEYBOARD_KEYS.ESCAPE && closeOnEscape) {
      event.preventDefault();
      handleClose();
    }
  }, [isOpen, closeOnEscape, handleClose]);

  // Set up global keyboard listeners
  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      return () => {
        document.removeEventListener('keydown', handleKeyDown);
      };
    }
  }, [isOpen, handleKeyDown]);

  const handleOverlayClick = (event: React.MouseEvent<HTMLDivElement>) => {
    if (event.target === event.currentTarget && closeOnOverlayClick) {
      handleClose();
    }
  };

  if (!isOpen) {
    return null;
  }

  const modalContent = (
    <div 
      className={`fixed inset-0 z-50 overflow-y-auto ${overlayClassName}`}
      aria-hidden="false"
    >
      {/* Overlay */}
      <div 
        className="flex min-h-full items-center justify-center p-4 text-center sm:items-center sm:p-0"
        onClick={handleOverlayClick}
      >
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
          aria-hidden="true"
        />
        
        {/* Modal panel */}
        <div
          ref={modalRef}
          className={`relative w-full ${sizeClasses[size]} transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:p-6 ${contentClassName} ${className}`}
          role={role}
          aria-modal="true"
          aria-labelledby={titleId}
          aria-describedby={ariaDescribedBy}
        >
          {/* Close button */}
          <div className="absolute right-0 top-0 pr-4 pt-4">
            <AccessibleButton
              variant="ghost"
              size="small"
              onClick={handleClose}
              aria-label="Close modal"
              className="rounded-md text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <span className="sr-only">Close</span>
              <svg
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth="1.5"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </AccessibleButton>
          </div>

          {/* Title */}
          <div className="mb-4">
            <h3 
              id={titleId}
              className="text-lg font-medium leading-6 text-gray-900 pr-8"
            >
              {title}
            </h3>
          </div>

          {/* Content */}
          <div className="mt-2">
            {children}
          </div>
        </div>
      </div>
    </div>
  );

  // Render modal in portal
  return createPortal(modalContent, document.body);
};

// Hook for managing modal state
export const useModal = (initialOpen = false) => {
  const [isOpen, setIsOpen] = React.useState(initialOpen);

  const openModal = useCallback(() => {
    setIsOpen(true);
  }, []);

  const closeModal = useCallback(() => {
    setIsOpen(false);
  }, []);

  const toggleModal = useCallback(() => {
    setIsOpen(prev => !prev);
  }, []);

  return {
    isOpen,
    openModal,
    closeModal,
    toggleModal
  };
};

// Modal context for nested components
interface ModalContextValue {
  closeModal: () => void;
}

const ModalContext = React.createContext<ModalContextValue | null>(null);

export const useModalContext = () => {
  const context = React.useContext(ModalContext);
  if (!context) {
    throw new Error('useModalContext must be used within a Modal');
  }
  return context;
};

// Enhanced Modal with context
export const AccessibleModalWithContext: React.FC<AccessibleModalProps> = (props) => {
  const contextValue: ModalContextValue = {
    closeModal: props.onClose
  };

  return (
    <ModalContext.Provider value={contextValue}>
      <AccessibleModal {...props} />
    </ModalContext.Provider>
  );
};

// Confirmation Modal variant
export interface ConfirmationModalProps extends Omit<AccessibleModalProps, 'children' | 'role'> {
  message: string;
  confirmText?: string;
  cancelText?: string;
  onConfirm: () => void;
  variant?: 'danger' | 'warning' | 'info';
  loading?: boolean;
}

export const ConfirmationModal: React.FC<ConfirmationModalProps> = ({
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  onConfirm,
  variant = 'info',
  loading = false,
  onClose,
  ...modalProps
}) => {
  const handleConfirm = () => {
    onConfirm();
    if (!loading) {
      onClose();
    }
  };

  const variantStyles = {
    danger: 'text-red-600',
    warning: 'text-yellow-600',
    info: 'text-blue-600'
  };

  const buttonVariant = variant === 'danger' ? 'danger' : 'primary';

  return (
    <AccessibleModal
      role="alertdialog"
      size="small"
      onClose={onClose}
      {...modalProps}
    >
      <div className="mt-3 text-center sm:mt-0 sm:text-left">
        <div className={`mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10 ${variant === 'danger' ? 'bg-red-100' : variant === 'warning' ? 'bg-yellow-100' : 'bg-blue-100'}`}>
          <svg
            className={`h-6 w-6 ${variantStyles[variant]}`}
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth="1.5"
            stroke="currentColor"
            aria-hidden="true"
          >
            {variant === 'danger' && (
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
            )}
            {variant === 'warning' && (
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
            )}
            {variant === 'info' && (
              <path strokeLinecap="round" strokeLinejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
            )}
          </svg>
        </div>
        <div className="mt-3 sm:mt-0 sm:ml-4">
          <p className="text-sm text-gray-500">
            {message}
          </p>
        </div>
      </div>
      <div className="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse space-y-2 sm:space-y-0 sm:space-x-2 sm:space-x-reverse">
        <AccessibleButton
          variant={buttonVariant}
          onClick={handleConfirm}
          disabled={loading}
          loading={loading}
          className="w-full sm:w-auto"
        >
          {confirmText}
        </AccessibleButton>
        <AccessibleButton
          variant="secondary"
          onClick={onClose}
          disabled={loading}
          className="w-full sm:w-auto"
        >
          {cancelText}
        </AccessibleButton>
      </div>
    </AccessibleModal>
  );
};

export default AccessibleModal;