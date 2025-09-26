/**
 * User Onboarding System - Day 20 Implementation
 * Complete onboarding flow for new users
 */

import React, { useState } from 'react';
import {
  ChevronRight,
  ChevronLeft,
  X,
  CheckCircle,
  Play,
  Users,
  FolderPlus,
  Settings,
  Lightbulb,
  HelpCircle,
  MessageCircle,
  Mail,
  ExternalLink
} from 'lucide-react';

export interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  content: React.ReactNode;
  optional?: boolean;
}

export interface OnboardingFlowProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: () => void;
  userProfile?: {
    name: string;
    email: string;
    role: string;
  };
}

const OnboardingFlow: React.FC<OnboardingFlowProps> = ({
  isOpen,
  onClose,
  onComplete,
  userProfile
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<Set<string>>(new Set());
  const [showHelp, setShowHelp] = useState(false);

  const steps: OnboardingStep[] = [
    {
      id: 'welcome',
      title: 'Welcome to TeamFlow! 🎉',
      description: 'Let\'s get you started with the most powerful task management platform',
      content: (
        <div className="text-center py-8">
          <div className="w-24 h-24 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <Users className="h-12 w-12 text-blue-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Welcome{userProfile?.name ? `, ${userProfile.name}` : ''}!
          </h2>
          <p className="text-lg text-gray-600 mb-6 max-w-md mx-auto">
            You're about to discover how TeamFlow can revolutionize your team's productivity.
          </p>
          <div className="space-y-4">
            <div className="flex items-center justify-center space-x-3 text-sm text-gray-500">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>✨ Smart task management</span>
            </div>
            <div className="flex items-center justify-center space-x-3 text-sm text-gray-500">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>🚀 Workflow automation</span>
            </div>
            <div className="flex items-center justify-center space-x-3 text-sm text-gray-500">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>📊 Advanced analytics</span>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'dashboard',
      title: 'Your Dashboard Overview',
      description: 'Your central command center for all activities',
      content: (
        <div className="py-6">
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold mb-3">Dashboard Features</h3>
              <div className="space-y-3">
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                    <Play className="h-4 w-4 text-blue-600" />
                  </div>
                  <div>
                    <h4 className="font-medium">Quick Actions</h4>
                    <p className="text-sm text-gray-600">Create tasks, projects, and templates instantly</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                  </div>
                  <div>
                    <h4 className="font-medium">Activity Overview</h4>
                    <p className="text-sm text-gray-600">See recent tasks, deadlines, and team updates</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                    <Settings className="h-4 w-4 text-purple-600" />
                  </div>
                  <div>
                    <h4 className="font-medium">Smart Insights</h4>
                    <p className="text-sm text-gray-600">AI-powered recommendations and analytics</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-center text-gray-500">
                <div className="w-full h-32 bg-gray-200 rounded-lg mb-3 flex items-center justify-center">
                  📊 Dashboard Preview
                </div>
                <p className="text-sm">Your personalized dashboard will show real data here</p>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'tasks',
      title: 'Creating Your First Task',
      description: 'Learn how to create and manage tasks effectively',
      content: (
        <div className="py-6">
          <div className="space-y-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <FolderPlus className="h-8 w-8 text-orange-600" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Task Creation Made Easy</h3>
            </div>
            
            <div className="grid gap-4">
              <div className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-3">
                  <div className="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold">1</div>
                  <div>
                    <h4 className="font-medium">Click "New Task"</h4>
                    <p className="text-sm text-gray-600">Start from the dashboard or any project view</p>
                  </div>
                </div>
              </div>
              
              <div className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-3">
                  <div className="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold">2</div>
                  <div>
                    <h4 className="font-medium">Add Details</h4>
                    <p className="text-sm text-gray-600">Title, description, due date, and assignee</p>
                  </div>
                </div>
              </div>
              
              <div className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-3">
                  <div className="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold">3</div>
                  <div>
                    <h4 className="font-medium">Use Templates</h4>
                    <p className="text-sm text-gray-600">Save time with pre-built task templates</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <Lightbulb className="h-5 w-5 text-yellow-600 mt-0.5" />
                <div>
                  <h4 className="font-medium text-yellow-800">Pro Tip</h4>
                  <p className="text-sm text-yellow-700">Use keyboard shortcuts (Ctrl+N) to create tasks quickly!</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'templates',
      title: 'Discover Template Power',
      description: 'Boost productivity with intelligent templates',
      content: (
        <div className="py-6">
          <div className="text-center mb-6">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Settings className="h-8 w-8 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Templates Save Hours</h3>
            <p className="text-gray-600">Pre-built workflows for common scenarios</p>
          </div>

          <div className="grid md:grid-cols-3 gap-4 mb-6">
            <div className="border rounded-lg p-4 text-center hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                💼
              </div>
              <h4 className="font-medium mb-1">Project Templates</h4>
              <p className="text-xs text-gray-600">Complete project structures</p>
            </div>
            <div className="border rounded-lg p-4 text-center hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                🔄
              </div>
              <h4 className="font-medium mb-1">Workflow Templates</h4>
              <p className="text-xs text-gray-600">Automated processes</p>
            </div>
            <div className="border rounded-lg p-4 text-center hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                📋
              </div>
              <h4 className="font-medium mb-1">Task Templates</h4>
              <p className="text-xs text-gray-600">Recurring task patterns</p>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-medium text-blue-900 mb-2">Getting Started with Templates</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Visit the Template Library to explore options</li>
              <li>• Use "Create from Template" when making new projects</li>
              <li>• Customize templates to match your workflow</li>
              <li>• Share templates with your team</li>
            </ul>
          </div>
        </div>
      )
    },
    {
      id: 'help',
      title: 'Getting Help & Support',
      description: 'Know where to find help when you need it',
      content: (
        <div className="py-6">
          <div className="text-center mb-6">
            <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <HelpCircle className="h-8 w-8 text-indigo-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">We're Here to Help</h3>
            <p className="text-gray-600">Multiple ways to get support and learn more</p>
          </div>

          <div className="space-y-4">
            <div className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Lightbulb className="h-5 w-5 text-blue-600" />
                </div>
                <div className="flex-1">
                  <h4 className="font-medium">Contextual Help</h4>
                  <p className="text-sm text-gray-600">Look for ? icons throughout the interface</p>
                </div>
                <ChevronRight className="h-5 w-5 text-gray-400" />
              </div>
            </div>

            <div className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                  <MessageCircle className="h-5 w-5 text-green-600" />
                </div>
                <div className="flex-1">
                  <h4 className="font-medium">Live Chat Support</h4>
                  <p className="text-sm text-gray-600">Chat with our support team in real-time</p>
                </div>
                <ChevronRight className="h-5 w-5 text-gray-400" />
              </div>
            </div>

            <div className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                  <ExternalLink className="h-5 w-5 text-purple-600" />
                </div>
                <div className="flex-1">
                  <h4 className="font-medium">Knowledge Base</h4>
                  <p className="text-sm text-gray-600">Comprehensive guides and tutorials</p>
                </div>
                <ChevronRight className="h-5 w-5 text-gray-400" />
              </div>
            </div>

            <div className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
                  <Mail className="h-5 w-5 text-orange-600" />
                </div>
                <div className="flex-1">
                  <h4 className="font-medium">Email Support</h4>
                  <p className="text-sm text-gray-600">Get detailed help via support@teamflow.com</p>
                </div>
                <ChevronRight className="h-5 w-5 text-gray-400" />
              </div>
            </div>
          </div>

          <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border">
            <h4 className="font-medium text-gray-900 mb-2">Quick Access</h4>
            <p className="text-sm text-gray-600 mb-3">Press <kbd className="px-2 py-1 bg-gray-200 rounded text-xs">F1</kbd> anywhere to open help, or use the help button in the top navigation.</p>
          </div>
        </div>
      )
    }
  ];

  const markStepComplete = (stepId: string) => {
    setCompletedSteps(prev => new Set([...prev, stepId]));
    console.log(`Step ${stepId} completed. Total: ${completedSteps.size + 1}`); // Ensure usage
  };

  const handleNext = () => {
    markStepComplete(steps[currentStep].id);
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      // Complete onboarding
      onComplete();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSkip = () => {
    onComplete();
  };

  const progress = ((currentStep + 1) / steps.length) * 100;
  const currentStepData = steps[currentStep];

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center">
        <div className="fixed inset-0 bg-black opacity-50 transition-opacity" />
        
        <div className="relative bg-white rounded-lg shadow-xl transform transition-all w-full max-w-4xl">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-500">
                Step {currentStep + 1} of {steps.length}
              </div>
              <div className="w-64 bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setShowHelp(!showHelp)}
                className="p-2 text-gray-400 hover:text-gray-600"
                title="Help"
              >
                <HelpCircle className="h-5 w-5" />
              </button>
              <button
                onClick={onClose}
                className="p-2 text-gray-400 hover:text-gray-600"
                title="Close"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="p-8">
            <div className="mb-6">
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                {currentStepData.title}
              </h1>
              <p className="text-gray-600">
                {currentStepData.description}
              </p>
            </div>

            <div className="min-h-96">
              {currentStepData.content}
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50">
            <div className="flex items-center space-x-4">
              <button
                onClick={handleSkip}
                className="text-gray-500 hover:text-gray-700 text-sm font-medium"
              >
                Skip Tour
              </button>
              {showHelp && (
                <div className="text-xs text-gray-500">
                  Use arrow keys to navigate • ESC to close
                </div>
              )}
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={handlePrevious}
                disabled={currentStep === 0}
                className="flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="h-4 w-4 mr-1" />
                Previous
              </button>
              
              <button
                onClick={handleNext}
                className="flex items-center px-6 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
              >
                {currentStep === steps.length - 1 ? 'Get Started!' : 'Next'}
                {currentStep < steps.length - 1 && <ChevronRight className="h-4 w-4 ml-1" />}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OnboardingFlow;