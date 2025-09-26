/**
 * Accessibility Utilities - Day 21 Implementation
 * WCAG 2.1 AA compliance utilities and helpers
 */

// Accessibility constants
export const ARIA_ROLES = {
  button: 'button',
  link: 'link',
  navigation: 'navigation',
  main: 'main',
  banner: 'banner',
  contentinfo: 'contentinfo',
  search: 'search',
  form: 'form',
  dialog: 'dialog',
  alertdialog: 'alertdialog',
  alert: 'alert',
  status: 'status',
  progressbar: 'progressbar',
  tab: 'tab',
  tabpanel: 'tabpanel',
  tablist: 'tablist',
  menu: 'menu',
  menuitem: 'menuitem',
  menubar: 'menubar',
  listbox: 'listbox',
  option: 'option',
  combobox: 'combobox',
  tree: 'tree',
  treeitem: 'treeitem',
  grid: 'grid',
  gridcell: 'gridcell',
  row: 'row',
  columnheader: 'columnheader',
  rowheader: 'rowheader',
  tooltip: 'tooltip'
} as const;

export const ARIA_STATES = {
  expanded: 'aria-expanded',
  selected: 'aria-selected',
  checked: 'aria-checked',
  disabled: 'aria-disabled',
  hidden: 'aria-hidden',
  pressed: 'aria-pressed',
  current: 'aria-current',
  invalid: 'aria-invalid',
  required: 'aria-required',
  readonly: 'aria-readonly',
  live: 'aria-live',
  atomic: 'aria-atomic',
  busy: 'aria-busy',
  describedby: 'aria-describedby',
  labelledby: 'aria-labelledby',
  label: 'aria-label',
  controls: 'aria-controls',
  owns: 'aria-owns',
  activedescendant: 'aria-activedescendant',
  haspopup: 'aria-haspopup',
  level: 'aria-level',
  posinset: 'aria-posinset',
  setsize: 'aria-setsize',
  valuemin: 'aria-valuemin',
  valuemax: 'aria-valuemax',
  valuenow: 'aria-valuenow',
  valuetext: 'aria-valuetext'
} as const;

// Color contrast utility functions
export const COLOR_CONTRAST = {
  // WCAG 2.1 AA standards
  NORMAL_TEXT_MIN: 4.5,
  LARGE_TEXT_MIN: 3.0,
  
  // Convert hex to RGB
  hexToRgb: (hex: string): { r: number; g: number; b: number } | null => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null;
  },

  // Calculate relative luminance
  getRelativeLuminance: (r: number, g: number, b: number): number => {
    const [rs, gs, bs] = [r, g, b].map(c => {
      c = c / 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
  },

  // Calculate contrast ratio between two colors
  getContrastRatio: (color1: string, color2: string): number => {
    const rgb1 = COLOR_CONTRAST.hexToRgb(color1);
    const rgb2 = COLOR_CONTRAST.hexToRgb(color2);
    
    if (!rgb1 || !rgb2) return 0;
    
    const lum1 = COLOR_CONTRAST.getRelativeLuminance(rgb1.r, rgb1.g, rgb1.b);
    const lum2 = COLOR_CONTRAST.getRelativeLuminance(rgb2.r, rgb2.g, rgb2.b);
    
    const brightest = Math.max(lum1, lum2);
    const darkest = Math.min(lum1, lum2);
    
    return (brightest + 0.05) / (darkest + 0.05);
  },

  // Check if contrast ratio meets WCAG standards
  meetsWCAG: (foreground: string, background: string, isLargeText = false): boolean => {
    const ratio = COLOR_CONTRAST.getContrastRatio(foreground, background);
    const minimum = isLargeText ? COLOR_CONTRAST.LARGE_TEXT_MIN : COLOR_CONTRAST.NORMAL_TEXT_MIN;
    return ratio >= minimum;
  }
};

// Keyboard navigation utilities
export const KEYBOARD_KEYS = {
  ENTER: 'Enter',
  SPACE: ' ',
  ESCAPE: 'Escape',
  TAB: 'Tab',
  ARROW_UP: 'ArrowUp',
  ARROW_DOWN: 'ArrowDown',
  ARROW_LEFT: 'ArrowLeft',
  ARROW_RIGHT: 'ArrowRight',
  HOME: 'Home',
  END: 'End',
  PAGE_UP: 'PageUp',
  PAGE_DOWN: 'PageDown'
} as const;

export const keyboardNavigation = {
  // Handle roving tabindex for lists/grids
  setupRovingTabindex: (containerSelector: string, itemSelector: string): void => {
    const container = document.querySelector(containerSelector);
    if (!container) return;

    const items = container.querySelectorAll(itemSelector);
    if (items.length === 0) return;

    // Set first item as focusable
    items.forEach((item, index) => {
      (item as HTMLElement).tabIndex = index === 0 ? 0 : -1;
    });

    // Add keyboard event listeners
    const handleKeyDown = (e: Event) => {
      if (!(e instanceof KeyboardEvent)) return;
      
      const target = e.target as HTMLElement;
      const currentIndex = Array.from(items).indexOf(target);
      
      if (currentIndex === -1) return;

      let nextIndex = currentIndex;
      
      switch (e.key) {
        case KEYBOARD_KEYS.ARROW_DOWN:
        case KEYBOARD_KEYS.ARROW_RIGHT:
          e.preventDefault();
          nextIndex = Math.min(currentIndex + 1, items.length - 1);
          break;
        case KEYBOARD_KEYS.ARROW_UP:
        case KEYBOARD_KEYS.ARROW_LEFT:
          e.preventDefault();
          nextIndex = Math.max(currentIndex - 1, 0);
          break;
        case KEYBOARD_KEYS.HOME:
          e.preventDefault();
          nextIndex = 0;
          break;
        case KEYBOARD_KEYS.END:
          e.preventDefault();
          nextIndex = items.length - 1;
          break;
        default:
          return;
      }

      // Update tabindex and focus
      items.forEach((item, index) => {
        (item as HTMLElement).tabIndex = index === nextIndex ? 0 : -1;
      });
      
      (items[nextIndex] as HTMLElement).focus();
    };

    container.addEventListener('keydown', handleKeyDown);
  },

  // Handle modal focus trapping
  trapFocus: (modalElement: HTMLElement): (() => void) => {
    const focusableElements = modalElement.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstFocusable = focusableElements[0] as HTMLElement;
    const lastFocusable = focusableElements[focusableElements.length - 1] as HTMLElement;

    const handleKeydown = (e: KeyboardEvent) => {
      if (e.key !== KEYBOARD_KEYS.TAB) return;

      if (e.shiftKey) {
        if (document.activeElement === firstFocusable) {
          e.preventDefault();
          lastFocusable.focus();
        }
      } else {
        if (document.activeElement === lastFocusable) {
          e.preventDefault();
          firstFocusable.focus();
        }
      }
    };

    modalElement.addEventListener('keydown', handleKeydown);
    
    // Focus first element
    if (firstFocusable) {
      firstFocusable.focus();
    }

    // Return cleanup function
    return () => {
      modalElement.removeEventListener('keydown', handleKeydown);
    };
  }
};

// Screen reader utilities
export const screenReader = {
  // Announce messages to screen readers
  announce: (message: string, priority: 'polite' | 'assertive' = 'polite'): void => {
    const announcer = document.createElement('div');
    announcer.setAttribute('aria-live', priority);
    announcer.setAttribute('aria-atomic', 'true');
    announcer.style.position = 'absolute';
    announcer.style.left = '-10000px';
    announcer.style.width = '1px';
    announcer.style.height = '1px';
    announcer.style.overflow = 'hidden';
    
    document.body.appendChild(announcer);
    announcer.textContent = message;
    
    // Remove after announcement
    setTimeout(() => {
      document.body.removeChild(announcer);
    }, 1000);
  },

  // Create visually hidden but screen reader accessible text
  createSROnlyText: (text: string): HTMLSpanElement => {
    const span = document.createElement('span');
    span.textContent = text;
    span.className = 'sr-only';
    span.style.position = 'absolute';
    span.style.width = '1px';
    span.style.height = '1px';
    span.style.padding = '0';
    span.style.margin = '-1px';
    span.style.overflow = 'hidden';
    span.style.clip = 'rect(0, 0, 0, 0)';
    span.style.whiteSpace = 'nowrap';
    span.style.border = '0';
    return span;
  }
};

// Focus management utilities
export const focusManagement = {
  // Store and restore focus
  focusStore: null as HTMLElement | null,
  
  storeFocus: (): void => {
    focusManagement.focusStore = document.activeElement as HTMLElement;
  },
  
  restoreFocus: (): void => {
    if (focusManagement.focusStore && typeof focusManagement.focusStore.focus === 'function') {
      focusManagement.focusStore.focus();
      focusManagement.focusStore = null;
    }
  },

  // Get next focusable element
  getNextFocusable: (currentElement: HTMLElement): HTMLElement | null => {
    const focusableElements = Array.from(document.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )) as HTMLElement[];
    
    const currentIndex = focusableElements.indexOf(currentElement);
    return focusableElements[currentIndex + 1] || null;
  },

  // Get previous focusable element
  getPreviousFocusable: (currentElement: HTMLElement): HTMLElement | null => {
    const focusableElements = Array.from(document.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )) as HTMLElement[];
    
    const currentIndex = focusableElements.indexOf(currentElement);
    return focusableElements[currentIndex - 1] || null;
  }
};

// Form accessibility utilities
export const formAccessibility = {
  // Associate labels with form controls
  associateLabel: (input: HTMLElement, labelText: string): void => {
    const existingLabel = document.querySelector(`label[for="${input.id}"]`);
    
    if (!existingLabel) {
      const label = document.createElement('label');
      label.textContent = labelText;
      label.setAttribute('for', input.id);
      input.parentNode?.insertBefore(label, input);
    }
  },

  // Add error messages with proper ARIA
  addErrorMessage: (input: HTMLElement, errorMessage: string): void => {
    const errorId = `${input.id}-error`;
    let errorElement = document.getElementById(errorId);
    
    if (!errorElement) {
      errorElement = document.createElement('div');
      errorElement.id = errorId;
      errorElement.className = 'error-message';
      errorElement.setAttribute('role', 'alert');
      errorElement.setAttribute('aria-live', 'polite');
      input.parentNode?.insertBefore(errorElement, input.nextSibling);
    }
    
    errorElement.textContent = errorMessage;
    input.setAttribute('aria-invalid', 'true');
    input.setAttribute('aria-describedby', errorId);
  },

  // Clear error messages
  clearErrorMessage: (input: HTMLElement): void => {
    const errorId = `${input.id}-error`;
    const errorElement = document.getElementById(errorId);
    
    if (errorElement) {
      errorElement.remove();
    }
    
    input.removeAttribute('aria-invalid');
    input.removeAttribute('aria-describedby');
  }
};

// Skip link utility
export const skipLinks = {
  create: (): HTMLElement => {
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.textContent = 'Skip to main content';
    skipLink.className = 'skip-link';
    skipLink.style.position = 'absolute';
    skipLink.style.top = '-40px';
    skipLink.style.left = '6px';
    skipLink.style.background = '#000';
    skipLink.style.color = '#fff';
    skipLink.style.padding = '8px';
    skipLink.style.zIndex = '1000';
    skipLink.style.textDecoration = 'none';
    skipLink.style.borderRadius = '4px';
    
    // Show on focus
    skipLink.addEventListener('focus', () => {
      skipLink.style.top = '6px';
    });
    
    skipLink.addEventListener('blur', () => {
      skipLink.style.top = '-40px';
    });
    
    return skipLink;
  }
};

export default {
  ARIA_ROLES,
  ARIA_STATES,
  COLOR_CONTRAST,
  KEYBOARD_KEYS,
  keyboardNavigation,
  screenReader,
  focusManagement,
  formAccessibility,
  skipLinks
};