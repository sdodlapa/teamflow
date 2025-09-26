/**
 * AccessibleNavigation - WCAG 2.1 AA Compliant Navigation Component
 * Day 21 Implementation - Accessibility Compliance
 */

import React, { ReactNode, useState, useRef, useEffect } from 'react';
import { KEYBOARD_KEYS, keyboardNavigation } from '../../utils/accessibility';

export interface NavigationItem {
  id: string;
  label: string;
  href?: string;
  onClick?: () => void;
  children?: NavigationItem[];
  icon?: ReactNode;
  badge?: string | number;
  disabled?: boolean;
  current?: boolean;
}

export interface AccessibleNavigationProps {
  items: NavigationItem[];
  orientation?: 'horizontal' | 'vertical';
  variant?: 'primary' | 'secondary' | 'sidebar';
  label?: string;
  className?: string;
  onItemSelect?: (item: NavigationItem) => void;
}

const AccessibleNavigation: React.FC<AccessibleNavigationProps> = ({
  items,
  orientation = 'horizontal',
  variant = 'primary',
  label = 'Main navigation',
  className = '',
  onItemSelect
}) => {
  const navRef = useRef<HTMLElement>(null);
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());
  
  // Set up keyboard navigation for menu items
  useEffect(() => {
    if (navRef.current) {
      keyboardNavigation.setupRovingTabindex('nav', '[role="menuitem"]');
    }
  }, [items]);

  const toggleExpanded = (itemId: string) => {
    setExpandedItems(prev => {
      const newSet = new Set(prev);
      if (newSet.has(itemId)) {
        newSet.delete(itemId);
      } else {
        newSet.add(itemId);
      }
      return newSet;
    });
  };

  const handleItemClick = (item: NavigationItem, event: React.MouseEvent | React.KeyboardEvent) => {
    if (item.disabled) {
      event.preventDefault();
      return;
    }

    if (item.children && item.children.length > 0) {
      event.preventDefault();
      toggleExpanded(item.id);
    } else {
      onItemSelect?.(item);
      if (item.onClick) {
        item.onClick();
      }
    }
  };

  const handleItemKeyDown = (item: NavigationItem, event: React.KeyboardEvent) => {
    switch (event.key) {
      case KEYBOARD_KEYS.ENTER:
      case KEYBOARD_KEYS.SPACE:
        event.preventDefault();
        handleItemClick(item, event);
        break;
      case KEYBOARD_KEYS.ARROW_RIGHT:
        if (item.children && orientation === 'horizontal') {
          event.preventDefault();
          if (!expandedItems.has(item.id)) {
            toggleExpanded(item.id);
          }
        }
        break;
      case KEYBOARD_KEYS.ARROW_LEFT:
        if (item.children && orientation === 'horizontal' && expandedItems.has(item.id)) {
          event.preventDefault();
          toggleExpanded(item.id);
        }
        break;
      case KEYBOARD_KEYS.ARROW_DOWN:
        if (item.children && orientation === 'vertical') {
          event.preventDefault();
          if (!expandedItems.has(item.id)) {
            toggleExpanded(item.id);
          }
        }
        break;
      case KEYBOARD_KEYS.ARROW_UP:
        if (item.children && orientation === 'vertical' && expandedItems.has(item.id)) {
          event.preventDefault();
          toggleExpanded(item.id);
        }
        break;
    }
  };

  const renderNavigationItem = (item: NavigationItem, level = 0) => {
    const isExpanded = expandedItems.has(item.id);
    const hasChildren = item.children && item.children.length > 0;
    
    const baseClasses = 'flex items-center w-full text-left rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500';
    
    const variantClasses = {
      primary: item.current 
        ? 'bg-blue-100 text-blue-700' 
        : 'text-gray-700 hover:bg-gray-100',
      secondary: item.current 
        ? 'bg-gray-100 text-gray-900' 
        : 'text-gray-600 hover:bg-gray-50',
      sidebar: item.current 
        ? 'bg-blue-600 text-white' 
        : 'text-gray-300 hover:bg-gray-700 hover:text-white'
    };

    const sizeClasses = variant === 'sidebar' 
      ? 'px-3 py-2 text-sm' 
      : 'px-3 py-2 text-base';

    const itemClasses = `${baseClasses} ${variantClasses[variant]} ${sizeClasses} ${
      item.disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
    }`;

    const itemContent = (
      <>
        {item.icon && (
          <span className="mr-2 flex-shrink-0" aria-hidden="true">
            {item.icon}
          </span>
        )}
        <span className="flex-1">
          {item.label}
        </span>
        {item.badge && (
          <span 
            className="ml-2 inline-flex items-center rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-800"
            aria-label={`${item.badge} notifications`}
          >
            {item.badge}
          </span>
        )}
        {hasChildren && (
          <svg
            className={`ml-2 h-4 w-4 transition-transform ${
              isExpanded ? 'rotate-90' : ''
            }`}
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth="1.5"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
          </svg>
        )}
      </>
    );

    return (
      <li key={item.id} role="none">
        {item.href && !hasChildren ? (
          <a
            href={item.href}
            className={itemClasses}
            role="menuitem"
            aria-current={item.current ? 'page' : undefined}
            aria-disabled={item.disabled}
            onClick={(e) => handleItemClick(item, e)}
            onKeyDown={(e) => handleItemKeyDown(item, e)}
            style={{ paddingLeft: `${level * 1.5 + 0.75}rem` }}
          >
            {itemContent}
          </a>
        ) : (
          <button
            className={itemClasses}
            role="menuitem"
            aria-expanded={hasChildren ? isExpanded : undefined}
            aria-haspopup={hasChildren ? 'menu' : undefined}
            aria-current={item.current ? 'page' : undefined}
            aria-disabled={item.disabled}
            disabled={item.disabled}
            onClick={(e) => handleItemClick(item, e)}
            onKeyDown={(e) => handleItemKeyDown(item, e)}
            style={{ paddingLeft: `${level * 1.5 + 0.75}rem` }}
          >
            {itemContent}
          </button>
        )}
        
        {hasChildren && isExpanded && (
          <ul
            role="menu"
            aria-label={`${item.label} submenu`}
            className="mt-1 space-y-1"
          >
            {item.children!.map((child) => renderNavigationItem(child, level + 1))}
          </ul>
        )}
      </li>
    );
  };

  const containerClasses = {
    horizontal: 'flex space-x-1',
    vertical: 'space-y-1'
  };

  return (
    <nav
      ref={navRef}
      className={`${className}`}
      role="menubar"
      aria-label={label}
      aria-orientation={orientation}
    >
      <ul 
        role="menu" 
        className={containerClasses[orientation]}
      >
        {items.map((item) => renderNavigationItem(item))}
      </ul>
    </nav>
  );
};

// Breadcrumb Navigation Component
export interface BreadcrumbItem {
  id: string;
  label: string;
  href?: string;
  onClick?: () => void;
}

export interface BreadcrumbNavigationProps {
  items: BreadcrumbItem[];
  separator?: ReactNode;
  className?: string;
  onItemClick?: (item: BreadcrumbItem) => void;
}

export const BreadcrumbNavigation: React.FC<BreadcrumbNavigationProps> = ({
  items,
  separator,
  className = '',
  onItemClick
}) => {
  const handleItemClick = (item: BreadcrumbItem, event: React.MouseEvent) => {
    if (item.onClick) {
      event.preventDefault();
      item.onClick();
    }
    onItemClick?.(item);
  };

  const defaultSeparator = (
    <svg
      className="h-4 w-4 text-gray-400"
      fill="none"
      viewBox="0 0 24 24"
      strokeWidth="1.5"
      stroke="currentColor"
      aria-hidden="true"
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
    </svg>
  );

  return (
    <nav 
      className={`flex ${className}`} 
      role="navigation"
      aria-label="Breadcrumb"
    >
      <ol className="flex items-center space-x-2">
        {items.map((item, index) => {
          const isLast = index === items.length - 1;
          
          return (
            <li key={item.id} className="flex items-center">
              {item.href && !isLast ? (
                <a
                  href={item.href}
                  className="text-blue-600 hover:text-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded"
                  onClick={(e) => handleItemClick(item, e)}
                >
                  {item.label}
                </a>
              ) : (
                <span 
                  className={isLast ? 'text-gray-900 font-medium' : 'text-gray-600'}
                  aria-current={isLast ? 'page' : undefined}
                >
                  {item.label}
                </span>
              )}
              
              {!isLast && (
                <span className="ml-2" aria-hidden="true">
                  {separator || defaultSeparator}
                </span>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
};

// Tab Navigation Component
export interface TabItem {
  id: string;
  label: string;
  content?: ReactNode;
  disabled?: boolean;
  badge?: string | number;
}

export interface TabNavigationProps {
  tabs: TabItem[];
  activeTab: string;
  onChange: (tabId: string) => void;
  orientation?: 'horizontal' | 'vertical';
  variant?: 'pills' | 'underline';
  className?: string;
}

export const TabNavigation: React.FC<TabNavigationProps> = ({
  tabs,
  activeTab,
  onChange,
  orientation = 'horizontal',
  variant = 'underline',
  className = ''
}) => {
  const tabListRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (tabListRef.current) {
      keyboardNavigation.setupRovingTabindex('[role="tablist"]', '[role="tab"]');
    }
  }, [tabs]);

  const handleTabClick = (tabId: string) => {
    const tab = tabs.find(t => t.id === tabId);
    if (tab && !tab.disabled) {
      onChange(tabId);
    }
  };

  const handleTabKeyDown = (tabId: string, event: React.KeyboardEvent) => {
    switch (event.key) {
      case KEYBOARD_KEYS.ENTER:
      case KEYBOARD_KEYS.SPACE:
        event.preventDefault();
        handleTabClick(tabId);
        break;
    }
  };

  const getTabClasses = (tab: TabItem) => {
    const isActive = tab.id === activeTab;
    const baseClasses = 'px-4 py-2 text-sm font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors';
    
    if (variant === 'pills') {
      return `${baseClasses} ${
        isActive 
          ? 'bg-blue-600 text-white' 
          : tab.disabled
            ? 'text-gray-400 cursor-not-allowed'
            : 'text-gray-700 hover:text-blue-600 hover:bg-blue-50'
      }`;
    } else {
      return `${baseClasses} border-b-2 ${
        isActive 
          ? 'border-blue-600 text-blue-600' 
          : tab.disabled
            ? 'border-transparent text-gray-400 cursor-not-allowed'
            : 'border-transparent text-gray-700 hover:text-blue-600 hover:border-blue-300'
      }`;
    }
  };

  const containerClasses = orientation === 'horizontal' 
    ? 'flex space-x-1' 
    : 'flex flex-col space-y-1';

  return (
    <div className={className}>
      <div
        ref={tabListRef}
        className={containerClasses}
        role="tablist"
        aria-orientation={orientation}
      >
        {tabs.map((tab) => (
          <button
            key={tab.id}
            role="tab"
            aria-selected={tab.id === activeTab}
            aria-controls={`tabpanel-${tab.id}`}
            aria-disabled={tab.disabled}
            disabled={tab.disabled}
            className={getTabClasses(tab)}
            onClick={() => handleTabClick(tab.id)}
            onKeyDown={(e) => handleTabKeyDown(tab.id, e)}
            tabIndex={tab.id === activeTab ? 0 : -1}
          >
            <span>{tab.label}</span>
            {tab.badge && (
              <span 
                className="ml-2 inline-flex items-center rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-800"
                aria-label={`${tab.badge} items`}
              >
                {tab.badge}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Tab panels */}
      <div className="mt-4">
        {tabs.map((tab) => (
          <div
            key={tab.id}
            id={`tabpanel-${tab.id}`}
            role="tabpanel"
            aria-labelledby={tab.id}
            hidden={tab.id !== activeTab}
            className={tab.id === activeTab ? 'block' : 'hidden'}
          >
            {tab.content}
          </div>
        ))}
      </div>
    </div>
  );
};

// Skip Navigation Component
export const SkipNavigation: React.FC = () => {
  return (
    <a
      href="#main-content"
      className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 bg-white text-blue-600 px-4 py-2 rounded-md shadow-lg z-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
    >
      Skip to main content
    </a>
  );
};

export default AccessibleNavigation;