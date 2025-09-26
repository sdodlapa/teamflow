/**
 * Interactive Tutorial System - Day 20 Implementation
 * Step-by-step interactive tutorials for features
 */

import React, { useState, useEffect } from 'react';
import {
  Play,
  X,
  CheckCircle,
  ArrowRight,
  MousePointer,
  Keyboard,
  Eye
} from 'lucide-react';

export interface TutorialStep {
  id: string;
  title: string;
  description: string;
  target?: string; // CSS selector for element to highlight
  action?: 'click' | 'type' | 'hover' | 'observe';
  content: React.ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
}

export interface Tutorial {
  id: string;
  title: string;
  description: string;
  duration: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  category: string;
  steps: TutorialStep[];
}

export interface InteractiveTutorialProps {
  tutorial: Tutorial | null;
  isActive: boolean;
  onClose: () => void;
  onComplete: () => void;
}

export const InteractiveTutorial: React.FC<InteractiveTutorialProps> = ({
  tutorial,
  isActive,
  onClose,
  onComplete
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (!tutorial || !isActive) return;

    const step = tutorial.steps[currentStep];
    if (step?.target) {
      const element = document.querySelector(step.target) as HTMLElement;
      if (element) {
        highlightElement(element);
      }
    }

    return () => {
      removeHighlight();
    };
  }, [currentStep, tutorial, isActive]);

  const highlightElement = (element: HTMLElement) => {
    // Add highlight overlay
    const rect = element.getBoundingClientRect();
    const overlay = document.createElement('div');
    overlay.id = 'tutorial-highlight';
    overlay.style.position = 'fixed';
    overlay.style.top = `${rect.top - 4}px`;
    overlay.style.left = `${rect.left - 4}px`;
    overlay.style.width = `${rect.width + 8}px`;
    overlay.style.height = `${rect.height + 8}px`;
    overlay.style.border = '3px solid #3B82F6';
    overlay.style.borderRadius = '8px';
    overlay.style.background = 'rgba(59, 130, 246, 0.1)';
    overlay.style.pointerEvents = 'none';
    overlay.style.zIndex = '9999';
    overlay.style.animation = 'pulse 2s infinite';
    
    // Add pulse animation
    const style = document.createElement('style');
    style.textContent = `
      @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
      }
    `;
    document.head.appendChild(style);
    document.body.appendChild(overlay);
  };

  const removeHighlight = () => {
    const existing = document.getElementById('tutorial-highlight');
    if (existing) {
      existing.remove();
    }
  };

  const handleNext = () => {
    if (!tutorial) return;

    const currentStepData = tutorial.steps[currentStep];
    setCompletedSteps(prev => new Set([...prev, currentStepData.id]));

    if (currentStep < tutorial.steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
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

  const getActionIcon = (action?: string) => {
    switch (action) {
      case 'click':
        return <MousePointer className="h-4 w-4 text-blue-500" />;
      case 'type':
        return <Keyboard className="h-4 w-4 text-green-500" />;
      case 'hover':
        return <MousePointer className="h-4 w-4 text-yellow-500" />;
      case 'observe':
        return <Eye className="h-4 w-4 text-purple-500" />;
      default:
        return <ArrowRight className="h-4 w-4 text-gray-500" />;
    }
  };

  if (!tutorial || !isActive) return null;

  const currentStepData = tutorial.steps[currentStep];
  const progress = ((currentStep + 1) / tutorial.steps.length) * 100;

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black bg-opacity-50 z-40" />
      
      {/* Tutorial Panel */}
      <div className="fixed bottom-4 right-4 w-96 bg-white rounded-lg shadow-xl z-50 border">
        {/* Header */}
        <div className="p-4 border-b">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-lg font-semibold text-gray-900">{tutorial.title}</h2>
            <button
              onClick={onClose}
              className="p-1 text-gray-400 hover:text-gray-600"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
          
          <div className="flex items-center justify-between text-sm text-gray-500">
            <span>Step {currentStep + 1} of {tutorial.steps.length}</span>
            <span>{tutorial.duration}</span>
          </div>
          
          {/* Progress Bar */}
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Step Content */}
        <div className="p-4">
          <div className="flex items-start space-x-3 mb-4">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              {getActionIcon(currentStepData.action)}
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900 mb-1">
                {currentStepData.title}
              </h3>
              <p className="text-sm text-gray-600 mb-3">
                {currentStepData.description}
              </p>
            </div>
          </div>

          <div className="mb-4">
            {currentStepData.content}
          </div>

          {currentStepData.action && (
            <div className="mb-4 p-3 bg-blue-50 rounded-lg">
              <div className="flex items-center space-x-2 text-sm text-blue-800">
                {getActionIcon(currentStepData.action)}
                <span className="font-medium">
                  {currentStepData.action === 'click' && 'Click on the highlighted element'}
                  {currentStepData.action === 'type' && 'Type in the highlighted field'}
                  {currentStepData.action === 'hover' && 'Hover over the highlighted element'}
                  {currentStepData.action === 'observe' && 'Observe the highlighted area'}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Controls */}
        <div className="p-4 border-t bg-gray-50 flex items-center justify-between">
          <button
            onClick={handleSkip}
            className="text-sm text-gray-500 hover:text-gray-700"
          >
            Skip Tutorial
          </button>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={handlePrevious}
              disabled={currentStep === 0}
              className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            
            <button
              onClick={handleNext}
              className="flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
            >
              {currentStep === tutorial.steps.length - 1 ? (
                <>
                  <CheckCircle className="h-4 w-4 mr-1" />
                  Complete
                </>
              ) : (
                <>
                  Next
                  <ArrowRight className="h-4 w-4 ml-1" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export interface TutorialListProps {
  onStartTutorial: (tutorial: Tutorial) => void;
}

export const TutorialList: React.FC<TutorialListProps> = ({ onStartTutorial }) => {
  const tutorials: Tutorial[] = [
    {
      id: 'getting-started',
      title: 'Getting Started with TeamFlow',
      description: 'Learn the basics of navigating and using TeamFlow',
      duration: '5 min',
      difficulty: 'beginner',
      category: 'Basics',
      steps: [
        {
          id: 'welcome',
          title: 'Welcome to TeamFlow',
          description: 'Let\'s explore your new dashboard',
          content: (
            <div className="text-sm text-gray-600">
              <p>This is your main dashboard where you can see all your tasks, projects, and recent activity.</p>
            </div>
          )
        },
        {
          id: 'navigation',
          title: 'Navigation Menu',
          description: 'Learn about the main navigation',
          target: '.sidebar-nav',
          action: 'observe',
          content: (
            <div className="text-sm text-gray-600">
              <p>The navigation menu gives you quick access to all major features like Tasks, Projects, Templates, and Settings.</p>
            </div>
          )
        },
        {
          id: 'quick-actions',
          title: 'Quick Actions',
          description: 'Create tasks and projects instantly',
          target: '.quick-actions',
          action: 'observe',
          content: (
            <div className="text-sm text-gray-600">
              <p>Use the quick action buttons to create new tasks, projects, or access templates without navigating away from your current view.</p>
            </div>
          )
        }
      ]
    },
    {
      id: 'task-management',
      title: 'Task Management Basics',
      description: 'Create, edit, and organize your tasks',
      duration: '8 min',
      difficulty: 'beginner',
      category: 'Tasks',
      steps: [
        {
          id: 'create-task',
          title: 'Creating a New Task',
          description: 'Learn how to create your first task',
          target: '.new-task-btn',
          action: 'click',
          content: (
            <div className="text-sm text-gray-600">
              <p>Click the "New Task" button to open the task creation form. Fill in the title and description to get started.</p>
            </div>
          )
        },
        {
          id: 'task-details',
          title: 'Adding Task Details',
          description: 'Set due dates, assignees, and priorities',
          target: '.task-form',
          action: 'type',
          content: (
            <div className="text-sm text-gray-600">
              <p>Add important details like due dates, assignees, priority level, and any relevant tags to help organize your tasks.</p>
            </div>
          )
        },
        {
          id: 'task-status',
          title: 'Managing Task Status',
          description: 'Update task progress and completion',
          content: (
            <div className="text-sm text-gray-600">
              <p>Use the status dropdown to move tasks through different stages: To Do, In Progress, Review, and Done.</p>
            </div>
          )
        }
      ]
    },
    {
      id: 'project-setup',
      title: 'Setting Up Your First Project',
      description: 'Create and configure a new project',
      duration: '10 min',
      difficulty: 'intermediate',
      category: 'Projects',
      steps: [
        {
          id: 'project-creation',
          title: 'Creating a Project',
          description: 'Start a new project from scratch',
          target: '.new-project-btn',
          action: 'click',
          content: (
            <div className="text-sm text-gray-600">
              <p>Projects help you organize related tasks and collaborate with your team. Click "New Project" to get started.</p>
            </div>
          )
        },
        {
          id: 'project-settings',
          title: 'Project Configuration',
          description: 'Set up project details and permissions',
          content: (
            <div className="text-sm text-gray-600">
              <p>Configure your project settings, add team members, and set up the project structure that works best for your workflow.</p>
            </div>
          )
        }
      ]
    }
  ];

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner':
        return 'bg-green-100 text-green-800';
      case 'intermediate':
        return 'bg-yellow-100 text-yellow-800';
      case 'advanced':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-4">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Interactive Tutorials</h2>
        <p className="text-gray-600">Step-by-step guides to help you master TeamFlow</p>
      </div>

      <div className="grid gap-4">
        {tutorials.map((tutorial) => (
          <div key={tutorial.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <h3 className="font-semibold text-gray-900">{tutorial.title}</h3>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getDifficultyColor(tutorial.difficulty)}`}>
                    {tutorial.difficulty}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-2">{tutorial.description}</p>
                <div className="flex items-center space-x-4 text-xs text-gray-500">
                  <span>⏱️ {tutorial.duration}</span>
                  <span>📂 {tutorial.category}</span>
                  <span>📝 {tutorial.steps.length} steps</span>
                </div>
              </div>
              
              <button
                onClick={() => onStartTutorial(tutorial)}
                className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm font-medium"
              >
                <Play className="h-4 w-4 mr-1" />
                Start
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default InteractiveTutorial;