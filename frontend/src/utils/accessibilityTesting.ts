/**
 * AccessibilityTesting - WCAG 2.1 AA Compliance Testing Utilities
 * Day 21 Implementation - Accessibility Compliance
 */

import { COLOR_CONTRAST } from '../utils/accessibility';

export interface AccessibilityIssue {
  type: 'error' | 'warning' | 'info';
  rule: string;
  element: Element;
  message: string;
  wcagReference?: string;
}

export interface AccessibilityTestResult {
  passed: boolean;
  issues: AccessibilityIssue[];
  score: number;
  summary: {
    errors: number;
    warnings: number;
    passed: number;
  };
}

class AccessibilityTester {
  private issues: AccessibilityIssue[] = [];

  // Test all accessibility rules
  public async runAllTests(container?: Element): Promise<AccessibilityTestResult> {
    this.issues = [];
    const root = container || document.body;

    // Run all tests
    this.testHeadingStructure(root);
    this.testImageAltText(root);
    this.testFormLabels(root);
    this.testKeyboardNavigation(root);
    this.testColorContrast(root);
    this.testAriaLabels(root);
    this.testFocusManagement(root);
    this.testSemanticStructure(root);
    this.testLandmarkRoles(root);
    this.testTabIndex(root);

    return this.generateReport();
  }

  // Test heading structure (H1-H6 hierarchy)
  private testHeadingStructure(container: Element): void {
    const headings = container.querySelectorAll('h1, h2, h3, h4, h5, h6');
    let previousLevel = 0;

    // Check for H1
    const h1Elements = container.querySelectorAll('h1');
    if (h1Elements.length === 0) {
      this.addIssue({
        type: 'error',
        rule: 'heading-hierarchy',
        element: container,
        message: 'Page should have exactly one H1 element',
        wcagReference: 'WCAG 2.1 SC 2.4.6'
      });
    } else if (h1Elements.length > 1) {
      this.addIssue({
        type: 'warning',
        rule: 'heading-hierarchy',
        element: h1Elements[1],
        message: 'Multiple H1 elements found. Consider using only one H1 per page',
        wcagReference: 'WCAG 2.1 SC 2.4.6'
      });
    }

    // Check heading hierarchy
    headings.forEach((heading) => {
      const level = parseInt(heading.tagName.substring(1));
      
      if (level > previousLevel + 1) {
        this.addIssue({
          type: 'error',
          rule: 'heading-hierarchy',
          element: heading,
          message: `Heading level ${level} skips intermediate levels. Previous was ${previousLevel}`,
          wcagReference: 'WCAG 2.1 SC 2.4.6'
        });
      }

      // Check if heading has content
      if (!heading.textContent?.trim()) {
        this.addIssue({
          type: 'error',
          rule: 'heading-content',
          element: heading,
          message: 'Heading element is empty or contains only whitespace',
          wcagReference: 'WCAG 2.1 SC 2.4.6'
        });
      }

      previousLevel = level;
    });
  }

  // Test image alt text
  private testImageAltText(container: Element): void {
    const images = container.querySelectorAll('img');
    
    images.forEach((img) => {
      const alt = img.getAttribute('alt');
      const role = img.getAttribute('role');
      const ariaHidden = img.getAttribute('aria-hidden');

      // Skip decorative images
      if (role === 'presentation' || ariaHidden === 'true' || alt === '') {
        return;
      }

      if (alt === null) {
        this.addIssue({
          type: 'error',
          rule: 'img-alt',
          element: img,
          message: 'Image missing alt attribute',
          wcagReference: 'WCAG 2.1 SC 1.1.1'
        });
      } else if (alt.trim().length === 0) {
        this.addIssue({
          type: 'info',
          rule: 'img-alt',
          element: img,
          message: 'Image has empty alt attribute (decorative image)',
          wcagReference: 'WCAG 2.1 SC 1.1.1'
        });
      } else if (alt.length > 100) {
        this.addIssue({
          type: 'warning',
          rule: 'img-alt',
          element: img,
          message: 'Alt text is very long. Consider shorter, more concise description',
          wcagReference: 'WCAG 2.1 SC 1.1.1'
        });
      }
    });
  }

  // Test form labels
  private testFormLabels(container: Element): void {
    const inputs = container.querySelectorAll('input:not([type="hidden"]), textarea, select');
    
    inputs.forEach((input) => {
      const id = input.getAttribute('id');
      const ariaLabel = input.getAttribute('aria-label');
      const ariaLabelledBy = input.getAttribute('aria-labelledby');
      
      // Check for associated label
      let hasLabel = false;
      
      if (id) {
        const label = container.querySelector(`label[for="${id}"]`);
        if (label) {
          hasLabel = true;
        }
      }

      if (ariaLabel && ariaLabel.trim()) {
        hasLabel = true;
      }

      if (ariaLabelledBy) {
        const labelElement = document.getElementById(ariaLabelledBy);
        if (labelElement && labelElement.textContent?.trim()) {
          hasLabel = true;
        }
      }

      // Check if input is wrapped in a label
      const parentLabel = input.closest('label');
      if (parentLabel) {
        hasLabel = true;
      }

      if (!hasLabel) {
        this.addIssue({
          type: 'error',
          rule: 'form-label',
          element: input,
          message: 'Form control missing accessible label',
          wcagReference: 'WCAG 2.1 SC 3.3.2'
        });
      }

      // Check required fields
      if (input.hasAttribute('required') && !input.hasAttribute('aria-required')) {
        this.addIssue({
          type: 'warning',
          rule: 'form-required',
          element: input,
          message: 'Required field should have aria-required="true"',
          wcagReference: 'WCAG 2.1 SC 3.3.2'
        });
      }
    });
  }

  // Test keyboard navigation
  private testKeyboardNavigation(container: Element): void {
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    focusableElements.forEach((element) => {
      const tabIndex = element.getAttribute('tabindex');
      
      // Check for positive tabindex (anti-pattern)
      if (tabIndex && parseInt(tabIndex) > 0) {
        this.addIssue({
          type: 'warning',
          rule: 'tabindex-positive',
          element: element,
          message: 'Avoid positive tabindex values. Use 0 or -1 instead',
          wcagReference: 'WCAG 2.1 SC 2.1.1'
        });
      }

      // Check if element is visible but not focusable
      const style = window.getComputedStyle(element);
      if (style.display !== 'none' && style.visibility !== 'hidden') {
        if (tabIndex === '-1' && !element.hasAttribute('aria-hidden')) {
          this.addIssue({
            type: 'warning',
            rule: 'keyboard-access',
            element: element,
            message: 'Interactive element may not be keyboard accessible',
            wcagReference: 'WCAG 2.1 SC 2.1.1'
          });
        }
      }
    });

    // Check for click handlers on non-interactive elements
    const clickableElements = container.querySelectorAll('*[onclick]');
    clickableElements.forEach((element) => {
      const tagName = element.tagName.toLowerCase();
      const role = element.getAttribute('role');
      
      if (!['button', 'a', 'input', 'select', 'textarea'].includes(tagName) && 
          !['button', 'link', 'menuitem'].includes(role || '')) {
        this.addIssue({
          type: 'error',
          rule: 'click-events',
          element: element,
          message: 'Click event on non-interactive element. Add role="button" and keyboard support',
          wcagReference: 'WCAG 2.1 SC 2.1.1'
        });
      }
    });
  }

  // Test color contrast
  private testColorContrast(container: Element): void {
    const textElements = container.querySelectorAll('*:not(script):not(style)');
    
    textElements.forEach((element) => {
      const style = window.getComputedStyle(element);
      const hasText = element.textContent?.trim();
      
      if (hasText && style.color && style.backgroundColor) {
        try {
          const textColor = this.rgbToHex(style.color);
          const bgColor = this.rgbToHex(style.backgroundColor);
          
          if (textColor && bgColor && textColor !== bgColor) {
            const fontSize = parseFloat(style.fontSize);
            const isLargeText = fontSize >= 18 || (fontSize >= 14 && style.fontWeight >= '700');
            
            if (!COLOR_CONTRAST.meetsWCAG(textColor, bgColor, isLargeText)) {
              const ratio = COLOR_CONTRAST.getContrastRatio(textColor, bgColor);
              const required = isLargeText ? COLOR_CONTRAST.LARGE_TEXT_MIN : COLOR_CONTRAST.NORMAL_TEXT_MIN;
              
              this.addIssue({
                type: 'error',
                rule: 'color-contrast',
                element: element,
                message: `Insufficient color contrast: ${ratio.toFixed(2)}:1 (required: ${required}:1)`,
                wcagReference: 'WCAG 2.1 SC 1.4.3'
              });
            }
          }
        } catch (error) {
          // Skip if color parsing fails
        }
      }
    });
  }

  // Test ARIA labels and roles
  private testAriaLabels(container: Element): void {
    const elementsWithAria = container.querySelectorAll('[aria-labelledby], [aria-describedby]');
    
    elementsWithAria.forEach((element) => {
      const labelledBy = element.getAttribute('aria-labelledby');
      const describedBy = element.getAttribute('aria-describedby');
      
      if (labelledBy) {
        const labelIds = labelledBy.split(/\s+/);
        labelIds.forEach((id) => {
          const labelElement = document.getElementById(id);
          if (!labelElement) {
            this.addIssue({
              type: 'error',
              rule: 'aria-labelledby',
              element: element,
              message: `aria-labelledby references non-existent element: ${id}`,
              wcagReference: 'WCAG 2.1 SC 4.1.2'
            });
          }
        });
      }

      if (describedBy) {
        const descIds = describedBy.split(/\s+/);
        descIds.forEach((id) => {
          const descElement = document.getElementById(id);
          if (!descElement) {
            this.addIssue({
              type: 'error',
              rule: 'aria-describedby',
              element: element,
              message: `aria-describedby references non-existent element: ${id}`,
              wcagReference: 'WCAG 2.1 SC 4.1.2'
            });
          }
        });
      }
    });

    // Check for invalid ARIA roles
    const elementsWithRoles = container.querySelectorAll('[role]');
    const validRoles = [
      'alert', 'alertdialog', 'application', 'article', 'banner', 'button', 'cell', 'checkbox',
      'columnheader', 'combobox', 'complementary', 'contentinfo', 'definition', 'dialog',
      'directory', 'document', 'feed', 'figure', 'form', 'grid', 'gridcell', 'group',
      'heading', 'img', 'link', 'list', 'listbox', 'listitem', 'log', 'main', 'marquee',
      'math', 'menu', 'menubar', 'menuitem', 'menuitemcheckbox', 'menuitemradio', 'navigation',
      'none', 'note', 'option', 'presentation', 'progressbar', 'radio', 'radiogroup',
      'region', 'row', 'rowgroup', 'rowheader', 'scrollbar', 'search', 'searchbox',
      'separator', 'slider', 'spinbutton', 'status', 'switch', 'tab', 'table', 'tablist',
      'tabpanel', 'term', 'textbox', 'timer', 'toolbar', 'tooltip', 'tree', 'treegrid',
      'treeitem'
    ];

    elementsWithRoles.forEach((element) => {
      const role = element.getAttribute('role');
      if (role && !validRoles.includes(role)) {
        this.addIssue({
          type: 'error',
          rule: 'aria-role',
          element: element,
          message: `Invalid ARIA role: ${role}`,
          wcagReference: 'WCAG 2.1 SC 4.1.2'
        });
      }
    });
  }

  // Test focus management
  private testFocusManagement(container: Element): void {
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    focusableElements.forEach((element) => {
      const style = window.getComputedStyle(element);
      
      // Check for focus indicators
      if (style.outline === 'none' && 
          !style.boxShadow.includes('inset') && 
          !element.classList.toString().includes('focus:')) {
        this.addIssue({
          type: 'warning',
          rule: 'focus-indicator',
          element: element,
          message: 'Interactive element may lack visible focus indicator',
          wcagReference: 'WCAG 2.1 SC 2.4.7'
        });
      }
    });
  }

  // Test semantic structure
  private testSemanticStructure(container: Element): void {
    // Check for proper list structure
    const listItems = container.querySelectorAll('li');
    listItems.forEach((li) => {
      const parent = li.parentElement;
      if (parent && !['ul', 'ol', 'menu'].includes(parent.tagName.toLowerCase())) {
        this.addIssue({
          type: 'error',
          rule: 'list-structure',
          element: li,
          message: 'List item not contained within ul, ol, or menu element',
          wcagReference: 'WCAG 2.1 SC 1.3.1'
        });
      }
    });

    // Check for table headers
    const tables = container.querySelectorAll('table');
    tables.forEach((table) => {
      const hasHeaders = table.querySelector('th');
      if (!hasHeaders) {
        this.addIssue({
          type: 'warning',
          rule: 'table-headers',
          element: table,
          message: 'Data table should have header cells (th elements)',
          wcagReference: 'WCAG 2.1 SC 1.3.1'
        });
      }
    });
  }

  // Test landmark roles
  private testLandmarkRoles(container: Element): void {
    const landmarks = ['main', 'navigation', 'banner', 'contentinfo', 'complementary'];
    const foundLandmarks = new Set<string>();

    // Check for landmark elements
    landmarks.forEach((landmark) => {
      const elements = container.querySelectorAll(`[role="${landmark}"], ${landmark}`);
      if (elements.length > 0) {
        foundLandmarks.add(landmark);
      }
      
      if (elements.length > 1 && landmark === 'main') {
        this.addIssue({
          type: 'error',
          rule: 'landmark-unique',
          element: elements[1],
          message: 'Page should have only one main landmark',
          wcagReference: 'WCAG 2.1 SC 1.3.6'
        });
      }
    });

    // Check for main landmark
    if (!foundLandmarks.has('main')) {
      this.addIssue({
        type: 'error',
        rule: 'landmark-main',
        element: container,
        message: 'Page should have a main landmark',
        wcagReference: 'WCAG 2.1 SC 1.3.6'
      });
    }
  }

  // Test tabindex usage
  private testTabIndex(container: Element): void {
    const elementsWithTabIndex = container.querySelectorAll('[tabindex]');
    
    elementsWithTabIndex.forEach((element) => {
      const tabIndex = element.getAttribute('tabindex');
      const numericTabIndex = parseInt(tabIndex || '0');
      
      if (numericTabIndex > 0) {
        this.addIssue({
          type: 'warning',
          rule: 'tabindex-positive',
          element: element,
          message: 'Positive tabindex can disrupt natural tab order',
          wcagReference: 'WCAG 2.1 SC 2.4.3'
        });
      }
    });
  }

  // Helper methods
  private addIssue(issue: AccessibilityIssue): void {
    this.issues.push(issue);
  }

  private generateReport(): AccessibilityTestResult {
    const errors = this.issues.filter(i => i.type === 'error').length;
    const warnings = this.issues.filter(i => i.type === 'warning').length;
    const total = this.issues.length;
    const passed = Math.max(0, 100 - total);
    
    // Calculate score (0-100)
    const score = Math.max(0, 100 - (errors * 10 + warnings * 5));

    return {
      passed: errors === 0,
      issues: this.issues,
      score,
      summary: {
        errors,
        warnings,
        passed
      }
    };
  }

  private rgbToHex(rgb: string): string | null {
    const rgbMatch = rgb.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
    if (!rgbMatch) return null;
    
    const [, r, g, b] = rgbMatch;
    return '#' + [r, g, b].map(c => parseInt(c).toString(16).padStart(2, '0')).join('');
  }
}

// Export singleton instance
export const accessibilityTester = new AccessibilityTester();

// Hook for React components
export const useAccessibilityTesting = () => {
  const runTest = async (element?: Element) => {
    return await accessibilityTester.runAllTests(element);
  };

  return { runTest };
};

export default AccessibilityTester;