/**
 * AccessibilityPage - Comprehensive WCAG 2.1 AA Compliance Showcase
 * Day 21 Implementation - Accessibility Compliance
 */

import React, { useState } from 'react';
import AccessibilityDashboard from '../components/AccessibilityDashboard';
import {
  AccessibleButton,
  AccessibleForm,
  FormField,
  AccessibleInput,
  AccessibleTextarea,
  AccessibleSelect,
  AccessibleCheckbox,
  AccessibleRadioGroup,
  AccessibleNavigation,
  BreadcrumbNavigation,
  TabNavigation,
  SkipNavigation,
  useModal,
  ConfirmationModal
} from '../components/accessibility';

interface AccessibilityPageProps {
  className?: string;
}

const AccessibilityPage: React.FC<AccessibilityPageProps> = ({ className = '' }) => {
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: '',
    newsletter: false,
    priority: '',
    category: ''
  });

  // Modal state
  const { isOpen: isConfirmModalOpen, openModal: openConfirmModal, closeModal: closeConfirmModal } = useModal();

  // Tab state
  const [activeTab, setActiveTab] = useState('overview');

  // Navigation items
  const navigationItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      href: '/dashboard',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
        </svg>
      ),
      current: false
    },
    {
      id: 'accessibility',
      label: 'Accessibility',
      href: '/accessibility',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
        </svg>
      ),
      current: true
    },
    {
      id: 'settings',
      label: 'Settings',
      href: '/settings',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      ),
      current: false
    }
  ];

  // Breadcrumb items
  const breadcrumbItems = [
    { id: 'home', label: 'Home', href: '/' },
    { id: 'dashboard', label: 'Dashboard', href: '/dashboard' },
    { id: 'accessibility', label: 'Accessibility' }
  ];

  // Tab items
  const tabItems = [
    {
      id: 'overview',
      label: 'Overview',
      content: (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Accessibility Overview</h3>
          <p className="text-gray-600">
            This page demonstrates comprehensive WCAG 2.1 AA compliance features including:
          </p>
          <ul className="list-disc list-inside space-y-2 text-gray-600">
            <li>Proper heading structure and semantic HTML</li>
            <li>Keyboard navigation support</li>
            <li>Screen reader compatibility</li>
            <li>Color contrast compliance</li>
            <li>Focus management</li>
            <li>ARIA labels and roles</li>
          </ul>
        </div>
      )
    },
    {
      id: 'testing',
      label: 'Testing Dashboard',
      content: <AccessibilityDashboard />
    },
    {
      id: 'components',
      label: 'Components',
      badge: '8',
      content: (
        <div className="space-y-6">
          <h3 className="text-lg font-semibold">Accessible Components</h3>
          
          {/* Button Examples */}
          <div className="space-y-4">
            <h4 className="font-medium text-gray-900">Buttons</h4>
            <div className="flex flex-wrap gap-3">
              <AccessibleButton variant="primary">Primary Button</AccessibleButton>
              <AccessibleButton variant="secondary">Secondary Button</AccessibleButton>
              <AccessibleButton variant="danger">Danger Button</AccessibleButton>
              <AccessibleButton variant="ghost">Ghost Button</AccessibleButton>
              <AccessibleButton disabled>Disabled Button</AccessibleButton>
              <AccessibleButton loading>Loading Button</AccessibleButton>
            </div>
          </div>

          {/* Form Example */}
          <div className="space-y-4">
            <h4 className="font-medium text-gray-900">Form Components</h4>
            <AccessibleForm
              title="Contact Form"
              description="Please fill out this form to get in touch with us."
              className="max-w-2xl"
              onSubmit={(e) => {
                e.preventDefault();
                openConfirmModal();
              }}
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FormField
                  label="Full Name"
                  required
                  helpText="Enter your first and last name"
                >
                  <AccessibleInput
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="John Doe"
                    required
                  />
                </FormField>

                <FormField
                  label="Email Address"
                  required
                  helpText="We'll use this to respond to your message"
                >
                  <AccessibleInput
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    placeholder="john@example.com"
                    required
                  />
                </FormField>
              </div>

              <FormField
                label="Category"
                required
              >
                <AccessibleSelect
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  placeholder="Select a category"
                  required
                >
                  <option value="general">General Inquiry</option>
                  <option value="support">Technical Support</option>
                  <option value="billing">Billing Question</option>
                  <option value="feature">Feature Request</option>
                </AccessibleSelect>
              </FormField>

              <FormField
                label="Priority"
                helpText="How urgent is your request?"
              >
                <AccessibleRadioGroup
                  name="priority"
                  value={formData.priority}
                  onChange={(value) => setFormData({ ...formData, priority: value })}
                  options={[
                    { value: 'low', label: 'Low Priority' },
                    { value: 'medium', label: 'Medium Priority' },
                    { value: 'high', label: 'High Priority' },
                    { value: 'urgent', label: 'Urgent' }
                  ]}
                  orientation="horizontal"
                />
              </FormField>

              <FormField
                label="Message"
                required
                helpText="Please provide details about your inquiry"
              >
                <AccessibleTextarea
                  value={formData.message}
                  onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                  placeholder="Tell us how we can help you..."
                  required
                />
              </FormField>

              <AccessibleCheckbox
                label="Subscribe to our newsletter for updates and tips"
                checked={formData.newsletter}
                onChange={(e) => setFormData({ ...formData, newsletter: e.target.checked })}
              />

              <div className="flex justify-end space-x-3">
                <AccessibleButton type="button" variant="secondary">
                  Cancel
                </AccessibleButton>
                <AccessibleButton type="submit" variant="primary">
                  Send Message
                </AccessibleButton>
              </div>
            </AccessibleForm>
          </div>
        </div>
      )
    }
  ];

  return (
    <div className={`min-h-screen bg-gray-50 ${className}`}>
      {/* Skip Navigation */}
      <SkipNavigation />

      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Accessibility Compliance
              </h1>
              <p className="mt-1 text-sm text-gray-600">
                WCAG 2.1 AA compliant components and testing dashboard
              </p>
            </div>
            
            {/* Navigation */}
            <AccessibleNavigation
              items={navigationItems}
              variant="primary"
              orientation="horizontal"
              className="hidden md:block"
            />
          </div>

          {/* Breadcrumbs */}
          <div className="pb-4">
            <BreadcrumbNavigation items={breadcrumbItems} />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main id="main-content" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <TabNavigation
          tabs={tabItems}
          activeTab={activeTab}
          onChange={setActiveTab}
          className="mb-8"
        />

        {/* Confirmation Modal */}
        <ConfirmationModal
          isOpen={isConfirmModalOpen}
          onClose={closeConfirmModal}
          onConfirm={() => {
            console.log('Form submitted:', formData);
            closeConfirmModal();
          }}
          title="Confirm Submission"
          message="Are you sure you want to submit this form? We'll get back to you within 24 hours."
          confirmText="Submit"
          cancelText="Cancel"
          variant="info"
        />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <p className="text-sm text-gray-600">
              © 2024 TeamFlow. Built with accessibility in mind.
            </p>
            <p className="text-xs text-gray-500 mt-2">
              This application meets WCAG 2.1 AA compliance standards.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default AccessibilityPage;