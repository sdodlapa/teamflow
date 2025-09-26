/**
 * User Onboarding Page - Day 20 Implementation
 * Complete onboarding system integration
 */

import React, { useState, useEffect } from 'react';
import {
  Users,
  BookOpen,
  HelpCircle,
  Lightbulb,
  CheckCircle,
  Play,
  ArrowRight,
  Star,
  Clock
} from 'lucide-react';
import OnboardingFlow from '../components/OnboardingFlow';
import { HelpCenter, HelpTooltip } from '../components/HelpCenter';
import { InteractiveTutorial, TutorialList, Tutorial } from '../components/InteractiveTutorial';

const UserOnboardingPage: React.FC = () => {
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [showHelpCenter, setShowHelpCenter] = useState(false);
  const [showTutorial, setShowTutorial] = useState(false);
  const [activeTutorial, setActiveTutorial] = useState<Tutorial | null>(null);
  const [onboardingComplete, setOnboardingComplete] = useState(false);
  const [userProfile] = useState({
    name: 'Demo User',
    email: 'demo@teamflow.com',
    role: 'Project Manager'
  });

  // Check if user has completed onboarding before
  useEffect(() => {
    const completed = localStorage.getItem('onboarding_completed');
    if (completed) {
      setOnboardingComplete(true);
    }
  }, []);

  const handleStartOnboarding = () => {
    setShowOnboarding(true);
  };

  const handleOnboardingComplete = () => {
    setOnboardingComplete(true);
    setShowOnboarding(false);
    localStorage.setItem('onboarding_completed', 'true');
  };

  const handleStartTutorial = (tutorial: Tutorial) => {
    setActiveTutorial(tutorial);
    setShowTutorial(true);
  };

  const handleTutorialComplete = () => {
    setShowTutorial(false);
    setActiveTutorial(null);
  };

  const quickStartActions = [
    {
      id: 'create-task',
      title: 'Create Your First Task',
      description: 'Get started by creating a simple task',
      icon: <CheckCircle className="h-6 w-6 text-green-600" />,
      action: () => alert('Navigate to task creation'),
      estimated: '1 min'
    },
    {
      id: 'create-project',
      title: 'Set Up a Project',
      description: 'Organize your work with a project',
      icon: <Users className="h-6 w-6 text-blue-600" />,
      action: () => alert('Navigate to project creation'),
      estimated: '3 min'
    },
    {
      id: 'explore-templates',
      title: 'Browse Templates',
      description: 'Speed up your workflow with templates',
      icon: <BookOpen className="h-6 w-6 text-purple-600" />,
      action: () => alert('Navigate to templates'),
      estimated: '2 min'
    },
    {
      id: 'invite-team',
      title: 'Invite Team Members',
      description: 'Collaborate with your team',
      icon: <Users className="h-6 w-6 text-orange-600" />,
      action: () => alert('Navigate to team settings'),
      estimated: '2 min'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center">
            <h1 className="text-4xl font-bold mb-4">
              Welcome to TeamFlow! 🎉
            </h1>
            <p className="text-xl mb-8 text-blue-100">
              The complete task management platform for high-performing teams
            </p>
            
            {!onboardingComplete ? (
              <div className="space-y-4">
                <button
                  onClick={handleStartOnboarding}
                  className="px-8 py-3 bg-white text-blue-600 font-semibold rounded-lg hover:bg-blue-50 transition-colors"
                >
                  <Play className="h-5 w-5 inline mr-2" />
                  Start Welcome Tour
                </button>
                <p className="text-sm text-blue-200">
                  Take a 5-minute guided tour to learn the basics
                </p>
              </div>
            ) : (
              <div className="bg-green-500 bg-opacity-20 border border-green-300 rounded-lg p-4 max-w-md mx-auto">
                <div className="flex items-center justify-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-200" />
                  <span className="text-green-100">Welcome tour completed!</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Quick Start Section */}
        <div className="mb-12">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Quick Start Actions</h2>
            <p className="text-gray-600">Get productive in minutes with these essential tasks</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {quickStartActions.map((action) => (
              <div key={action.id} className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    {action.icon}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 mb-2">{action.title}</h3>
                    <p className="text-sm text-gray-600 mb-4">{action.description}</p>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-500 flex items-center">
                        <Clock className="h-3 w-3 mr-1" />
                        {action.estimated}
                      </span>
                      <button
                        onClick={action.action}
                        className="text-blue-600 hover:text-blue-800 text-sm font-medium flex items-center"
                      >
                        Start
                        <ArrowRight className="h-4 w-4 ml-1" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Help Resources Section */}
        <div className="grid md:grid-cols-2 gap-8 mb-12">
          {/* Interactive Tutorials */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <Play className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Interactive Tutorials</h2>
                <p className="text-gray-600">Step-by-step guided learning</p>
              </div>
            </div>
            
            <div className="space-y-3 mb-4">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <h4 className="font-medium">Getting Started</h4>
                  <p className="text-sm text-gray-600">Learn the basics</p>
                </div>
                <button
                  onClick={() => handleStartTutorial({
                    id: 'getting-started',
                    title: 'Getting Started with TeamFlow',
                    description: 'Learn the basics',
                    duration: '5 min',
                    difficulty: 'beginner',
                    category: 'Basics',
                    steps: []
                  })}
                  className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                >
                  Start
                </button>
              </div>
              
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <h4 className="font-medium">Task Management</h4>
                  <p className="text-sm text-gray-600">Create and organize tasks</p>
                </div>
                <button className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700">
                  Start
                </button>
              </div>
            </div>
            
            <button
              onClick={() => setShowTutorial(true)}
              className="w-full text-blue-600 hover:text-blue-800 text-sm font-medium"
            >
              View All Tutorials →
            </button>
          </div>

          {/* Help Center */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <HelpCircle className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Help & Support</h2>
                <p className="text-gray-600">Get answers and assistance</p>
              </div>
            </div>
            
            <div className="space-y-3 mb-4">
              <div className="p-3 bg-gray-50 rounded-lg">
                <h4 className="font-medium mb-1">Frequently Asked Questions</h4>
                <p className="text-sm text-gray-600">Quick answers to common questions</p>
              </div>
              
              <div className="p-3 bg-gray-50 rounded-lg">
                <h4 className="font-medium mb-1">Live Chat Support</h4>
                <p className="text-sm text-gray-600">
                  Talk to our support team
                  <span className="ml-2 inline-block w-2 h-2 bg-green-400 rounded-full"></span>
                  <span className="text-xs text-green-600 ml-1">Online</span>
                </p>
              </div>
            </div>
            
            <button
              onClick={() => setShowHelpCenter(true)}
              className="w-full text-green-600 hover:text-green-800 text-sm font-medium"
            >
              Open Help Center →
            </button>
          </div>
        </div>

        {/* Feature Highlights */}
        <div className="bg-white rounded-lg shadow p-8">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Why Teams Love TeamFlow</h2>
            <p className="text-gray-600">Discover the features that make us different</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Star className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Smart Templates</h3>
              <p className="text-gray-600">
                Pre-built workflows and templates that adapt to your industry and use case.
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Users className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Team Collaboration</h3>
              <p className="text-gray-600">
                Real-time collaboration tools that keep everyone in sync and productive.
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Lightbulb className="h-8 w-8 text-purple-600" />
              </div>
              <h3 className="text-lg font-semibold mb-2">AI-Powered Insights</h3>
              <p className="text-gray-600">
                Intelligent recommendations and analytics to optimize your workflow.
              </p>
            </div>
          </div>
        </div>

        {/* Help Tooltips Demo */}
        <div className="mt-12 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Contextual Help Example</h2>
          <p className="text-gray-600 mb-6">
            Throughout TeamFlow, you'll find helpful tooltips and contextual guidance. Try hovering over the elements below:
          </p>
          
          <div className="flex items-center space-x-4">
            <HelpTooltip
              content="This is an example of contextual help that appears when you hover over elements with help icons."
              title="Contextual Help"
              position="top"
            >
              <div className="flex items-center space-x-2 p-3 bg-blue-50 rounded-lg cursor-help">
                <HelpCircle className="h-5 w-5 text-blue-600" />
                <span className="text-blue-800">Hover for help</span>
              </div>
            </HelpTooltip>
            
            <HelpTooltip
              content={
                <div>
                  <p className="mb-2">You can also click for help tooltips:</p>
                  <ul className="text-sm space-y-1">
                    <li>• Detailed explanations</li>
                    <li>• Step-by-step instructions</li>
                    <li>• Links to more resources</li>
                  </ul>
                </div>
              }
              title="Click Help"
              trigger="click"
              position="right"
            >
              <button className="flex items-center space-x-2 p-3 bg-green-50 rounded-lg hover:bg-green-100">
                <Lightbulb className="h-5 w-5 text-green-600" />
                <span className="text-green-800">Click for help</span>
              </button>
            </HelpTooltip>
          </div>
        </div>
      </div>

      {/* Onboarding Flow Modal */}
      <OnboardingFlow
        isOpen={showOnboarding}
        onClose={() => setShowOnboarding(false)}
        onComplete={handleOnboardingComplete}
        userProfile={userProfile}
      />

      {/* Help Center Modal */}
      <HelpCenter
        isOpen={showHelpCenter}
        onClose={() => setShowHelpCenter(false)}
      />

      {/* Tutorial System */}
      {showTutorial && !activeTutorial && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20">
            <div className="fixed inset-0 bg-black opacity-50" onClick={() => setShowTutorial(false)} />
            <div className="relative bg-white rounded-lg shadow-xl w-full max-w-4xl p-6">
              <TutorialList onStartTutorial={handleStartTutorial} />
              <div className="mt-6 text-center">
                <button
                  onClick={() => setShowTutorial(false)}
                  className="px-4 py-2 text-gray-500 hover:text-gray-700"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <InteractiveTutorial
        tutorial={activeTutorial}
        isActive={showTutorial && !!activeTutorial}
        onClose={() => setShowTutorial(false)}
        onComplete={handleTutorialComplete}
      />
    </div>
  );
};

export default UserOnboardingPage;