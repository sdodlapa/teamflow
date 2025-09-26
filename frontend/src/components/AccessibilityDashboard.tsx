/**
 * AccessibilityDashboard - WCAG 2.1 AA Compliance Dashboard
 * Day 21 Implementation - Accessibility Compliance
 */

import React, { useState } from 'react';
import { accessibilityTester, AccessibilityTestResult, AccessibilityIssue } from '../utils/accessibilityTesting';
import AccessibleButton from './accessibility/AccessibleButton';
import AccessibleModal, { useModal } from './accessibility/AccessibleModal';

interface AccessibilityDashboardProps {
  className?: string;
}

const AccessibilityDashboard: React.FC<AccessibilityDashboardProps> = ({
  className = ''
}) => {
  const [testResults, setTestResults] = useState<AccessibilityTestResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedIssue, setSelectedIssue] = useState<AccessibilityIssue | null>(null);
  const { isOpen: isIssueModalOpen, openModal: openIssueModal, closeModal: closeIssueModal } = useModal();

  const runAccessibilityTest = async () => {
    setLoading(true);
    try {
      const results = await accessibilityTester.runAllTests();
      setTestResults(results);
    } catch (error) {
      console.error('Accessibility test failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleIssueClick = (issue: AccessibilityIssue) => {
    setSelectedIssue(issue);
    // Scroll to element if possible
    if (issue.element && issue.element.scrollIntoView) {
      issue.element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      // Highlight element temporarily
      const originalOutline = (issue.element as HTMLElement).style.outline;
      (issue.element as HTMLElement).style.outline = '3px solid #ef4444';
      setTimeout(() => {
        (issue.element as HTMLElement).style.outline = originalOutline;
      }, 3000);
    }
    openIssueModal();
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 90) return 'bg-green-100 border-green-200';
    if (score >= 70) return 'bg-yellow-100 border-yellow-200';
    return 'bg-red-100 border-red-200';
  };

  const getSeverityColor = (type: string) => {
    switch (type) {
      case 'error': return 'text-red-600 bg-red-50 border-red-200';
      case 'warning': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      default: return 'text-blue-600 bg-blue-50 border-blue-200';
    }
  };

  const getSeverityIcon = (type: string) => {
    switch (type) {
      case 'error':
        return (
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        );
      case 'warning':
        return (
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        );
      default:
        return (
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
        );
    }
  };

  const groupIssuesByRule = (issues: AccessibilityIssue[]) => {
    const grouped: Record<string, AccessibilityIssue[]> = {};
    issues.forEach(issue => {
      if (!grouped[issue.rule]) {
        grouped[issue.rule] = [];
      }
      grouped[issue.rule].push(issue);
    });
    return grouped;
  };

  return (
    <div className={`p-6 bg-white rounded-lg shadow-lg ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            Accessibility Compliance Dashboard
          </h2>
          <p className="text-gray-600">
            WCAG 2.1 AA compliance testing and monitoring
          </p>
        </div>
        <AccessibleButton
          onClick={runAccessibilityTest}
          loading={loading}
          disabled={loading}
          aria-label="Run accessibility test"
        >
          {loading ? 'Testing...' : 'Run Test'}
        </AccessibleButton>
      </div>

      {/* Results Summary */}
      {testResults && (
        <div className="mb-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            {/* Overall Score */}
            <div className={`p-4 rounded-lg border-2 ${getScoreBgColor(testResults.score)}`}>
              <div className="text-center">
                <div className={`text-3xl font-bold ${getScoreColor(testResults.score)}`}>
                  {testResults.score}
                </div>
                <div className="text-sm font-medium text-gray-600">
                  Accessibility Score
                </div>
              </div>
            </div>

            {/* Errors */}
            <div className="p-4 bg-red-50 rounded-lg border-2 border-red-200">
              <div className="flex items-center">
                <svg className="w-8 h-8 text-red-600 mr-3" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <div>
                  <div className="text-2xl font-bold text-red-600">
                    {testResults.summary.errors}
                  </div>
                  <div className="text-sm font-medium text-gray-600">
                    Errors
                  </div>
                </div>
              </div>
            </div>

            {/* Warnings */}
            <div className="p-4 bg-yellow-50 rounded-lg border-2 border-yellow-200">
              <div className="flex items-center">
                <svg className="w-8 h-8 text-yellow-600 mr-3" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <div>
                  <div className="text-2xl font-bold text-yellow-600">
                    {testResults.summary.warnings}
                  </div>
                  <div className="text-sm font-medium text-gray-600">
                    Warnings
                  </div>
                </div>
              </div>
            </div>

            {/* Status */}
            <div className={`p-4 rounded-lg border-2 ${testResults.passed ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
              <div className="flex items-center">
                {testResults.passed ? (
                  <svg className="w-8 h-8 text-green-600 mr-3" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg className="w-8 h-8 text-red-600 mr-3" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                )}
                <div>
                  <div className={`text-lg font-bold ${testResults.passed ? 'text-green-600' : 'text-red-600'}`}>
                    {testResults.passed ? 'Passed' : 'Failed'}
                  </div>
                  <div className="text-sm font-medium text-gray-600">
                    Status
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Issues List */}
          {testResults.issues.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Issues Found ({testResults.issues.length})
              </h3>
              
              <div className="space-y-4">
                {Object.entries(groupIssuesByRule(testResults.issues)).map(([rule, issues]) => (
                  <div key={rule} className="border rounded-lg overflow-hidden">
                    <div className="bg-gray-50 px-4 py-3 border-b">
                      <div className="flex items-center justify-between">
                        <h4 className="font-medium text-gray-900">
                          {rule.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </h4>
                        <span className="text-sm text-gray-500">
                          {issues.length} issue{issues.length !== 1 ? 's' : ''}
                        </span>
                      </div>
                    </div>
                    
                    <div className="divide-y">
                      {issues.slice(0, 3).map((issue, index) => (
                        <div
                          key={index}
                          className="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                          onClick={() => handleIssueClick(issue)}
                          role="button"
                          tabIndex={0}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter' || e.key === ' ') {
                              e.preventDefault();
                              handleIssueClick(issue);
                            }
                          }}
                        >
                          <div className="flex items-start">
                            <span className={`flex-shrink-0 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getSeverityColor(issue.type)}`}>
                              {getSeverityIcon(issue.type)}
                              <span className="ml-1 capitalize">{issue.type}</span>
                            </span>
                            <div className="ml-3 flex-1">
                              <p className="text-sm text-gray-900 font-medium">
                                {issue.message}
                              </p>
                              {issue.wcagReference && (
                                <p className="text-xs text-gray-500 mt-1">
                                  {issue.wcagReference}
                                </p>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                      
                      {issues.length > 3 && (
                        <div className="p-4 text-center border-t bg-gray-50">
                          <span className="text-sm text-gray-500">
                            And {issues.length - 3} more issues...
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {testResults.issues.length === 0 && (
            <div className="text-center py-12">
              <svg className="w-16 h-16 text-green-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No Accessibility Issues Found!
              </h3>
              <p className="text-gray-600">
                Your application meets WCAG 2.1 AA compliance standards.
              </p>
            </div>
          )}
        </div>
      )}

      {/* No Results State */}
      {!testResults && !loading && (
        <div className="text-center py-12">
          <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Ready for Accessibility Testing
          </h3>
          <p className="text-gray-600 mb-4">
            Run an accessibility audit to check WCAG 2.1 AA compliance.
          </p>
          <AccessibleButton
            onClick={runAccessibilityTest}
            variant="primary"
          >
            Run Accessibility Test
          </AccessibleButton>
        </div>
      )}

      {/* Issue Detail Modal */}
      {selectedIssue && (
        <AccessibleModal
          isOpen={isIssueModalOpen}
          onClose={closeIssueModal}
          title="Accessibility Issue Details"
          size="large"
        >
          <div className="space-y-4">
            <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getSeverityColor(selectedIssue.type)}`}>
              {getSeverityIcon(selectedIssue.type)}
              <span className="ml-2 capitalize">{selectedIssue.type}</span>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Message</h4>
              <p className="text-gray-700">{selectedIssue.message}</p>
            </div>

            <div>
              <h4 className="font-medium text-gray-900 mb-2">Rule</h4>
              <p className="text-gray-700 font-mono text-sm bg-gray-100 px-3 py-2 rounded">
                {selectedIssue.rule}
              </p>
            </div>

            {selectedIssue.wcagReference && (
              <div>
                <h4 className="font-medium text-gray-900 mb-2">WCAG Reference</h4>
                <p className="text-gray-700">{selectedIssue.wcagReference}</p>
              </div>
            )}

            <div>
              <h4 className="font-medium text-gray-900 mb-2">Element</h4>
              <p className="text-gray-700 font-mono text-sm bg-gray-100 px-3 py-2 rounded break-all">
                {selectedIssue.element.tagName.toLowerCase()}
                {selectedIssue.element.id && `#${selectedIssue.element.id}`}
                {selectedIssue.element.className && `.${selectedIssue.element.className.replace(/\s+/g, '.')}`}
              </p>
            </div>

            <div className="flex justify-end pt-4 border-t">
              <AccessibleButton
                onClick={closeIssueModal}
                variant="secondary"
              >
                Close
              </AccessibleButton>
            </div>
          </div>
        </AccessibleModal>
      )}
    </div>
  );
};

export default AccessibilityDashboard;