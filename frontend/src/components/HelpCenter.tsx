/**
 * Contextual Help System - Day 20 Implementation
 * Tooltips, help overlays, and contextual guidance
 */

import React, { useState, useRef, useEffect } from 'react';
import {
  HelpCircle,
  X,
  Lightbulb,
  MessageCircle,
  ExternalLink,
  ChevronDown
} from 'lucide-react';

export interface HelpTooltipProps {
  content: string | React.ReactNode;
  title?: string;
  position?: 'top' | 'bottom' | 'left' | 'right';
  trigger?: 'hover' | 'click';
  children: React.ReactNode;
  className?: string;
}

export const HelpTooltip: React.FC<HelpTooltipProps> = ({
  content,
  title,
  position = 'top',
  trigger = 'hover',
  children,
  className = ''
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (tooltipRef.current && !tooltipRef.current.contains(event.target as Node) &&
          triggerRef.current && !triggerRef.current.contains(event.target as Node)) {
        setIsVisible(false);
      }
    };

    if (trigger === 'click' && isVisible) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isVisible, trigger]);

  const handleTrigger = () => {
    if (trigger === 'click') {
      setIsVisible(!isVisible);
    }
  };

  const handleMouseEnter = () => {
    if (trigger === 'hover') {
      setIsVisible(true);
    }
  };

  const handleMouseLeave = () => {
    if (trigger === 'hover') {
      setIsVisible(false);
    }
  };

  const getPositionClasses = () => {
    switch (position) {
      case 'top':
        return 'bottom-full left-1/2 transform -translate-x-1/2 mb-2';
      case 'bottom':
        return 'top-full left-1/2 transform -translate-x-1/2 mt-2';
      case 'left':
        return 'right-full top-1/2 transform -translate-y-1/2 mr-2';
      case 'right':
        return 'left-full top-1/2 transform -translate-y-1/2 ml-2';
      default:
        return 'bottom-full left-1/2 transform -translate-x-1/2 mb-2';
    }
  };

  return (
    <div className={`relative inline-block ${className}`}>
      <div
        ref={triggerRef}
        onClick={handleTrigger}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        className="cursor-help"
      >
        {children}
      </div>
      
      {isVisible && (
        <div
          ref={tooltipRef}
          className={`
            absolute z-50 w-64 bg-gray-900 text-white text-sm rounded-lg shadow-lg p-3
            ${getPositionClasses()}
          `}
        >
          {title && (
            <div className="font-medium mb-1">{title}</div>
          )}
          <div className="text-gray-200">
            {typeof content === 'string' ? content : content}
          </div>
          
          {/* Arrow */}
          <div className={`
            absolute w-2 h-2 bg-gray-900 transform rotate-45
            ${position === 'top' ? 'top-full left-1/2 -translate-x-1/2 -mt-1' : ''}
            ${position === 'bottom' ? 'bottom-full left-1/2 -translate-x-1/2 -mb-1' : ''}
            ${position === 'left' ? 'left-full top-1/2 -translate-y-1/2 -ml-1' : ''}
            ${position === 'right' ? 'right-full top-1/2 -translate-y-1/2 -mr-1' : ''}
          `} />
        </div>
      )}
    </div>
  );
};

export interface HelpCenterProps {
  isOpen: boolean;
  onClose: () => void;
}

export const HelpCenter: React.FC<HelpCenterProps> = ({ isOpen, onClose }) => {
  const [activeSection, setActiveSection] = useState<string>('faq');
  const [searchTerm, setSearchTerm] = useState('');

  const faqData = [
    {
      id: 1,
      question: "How do I create a new project?",
      answer: "Click the 'New Project' button in the dashboard, fill in the project details, and click 'Create'. You can also use project templates to speed up the process."
    },
    {
      id: 2,
      question: "How do I assign tasks to team members?",
      answer: "When creating or editing a task, use the 'Assignee' dropdown to select team members. You can assign multiple people to a single task."
    },
    {
      id: 3,
      question: "Can I use keyboard shortcuts?",
      answer: "Yes! Press 'Ctrl+N' to create new tasks, 'Ctrl+/' to open command palette, 'F1' for help, and 'Ctrl+K' for quick search."
    },
    {
      id: 4,
      question: "How do I set up recurring tasks?",
      answer: "In the task creation form, enable 'Recurring' and set your desired frequency (daily, weekly, monthly). The system will automatically create new instances."
    },
    {
      id: 5,
      question: "How do I export my data?",
      answer: "Go to Settings > Data Export. You can export projects, tasks, and reports in various formats including CSV, PDF, and JSON."
    }
  ];

  const filteredFaqs = faqData.filter(faq =>
    faq.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
    faq.answer.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20">
        <div className="fixed inset-0 bg-black opacity-50 transition-opacity" onClick={onClose} />
        
        <div className="relative bg-white rounded-lg shadow-xl transform transition-all w-full max-w-4xl max-h-screen">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <HelpCircle className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Help Center</h1>
                <p className="text-sm text-gray-600">Get help and learn how to use TeamFlow</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          <div className="flex h-96">
            {/* Sidebar */}
            <div className="w-64 border-r border-gray-200 p-4">
              <nav className="space-y-2">
                <button
                  onClick={() => setActiveSection('faq')}
                  className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeSection === 'faq'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    <Lightbulb className="h-4 w-4" />
                    <span>FAQ</span>
                  </div>
                </button>
                
                <button
                  onClick={() => setActiveSection('tutorials')}
                  className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeSection === 'tutorials'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    <ExternalLink className="h-4 w-4" />
                    <span>Video Tutorials</span>
                  </div>
                </button>
                
                <button
                  onClick={() => setActiveSection('contact')}
                  className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeSection === 'contact'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    <MessageCircle className="h-4 w-4" />
                    <span>Contact Support</span>
                  </div>
                </button>
              </nav>
            </div>

            {/* Content */}
            <div className="flex-1 p-6 overflow-y-auto">
              {activeSection === 'faq' && (
                <div>
                  <div className="mb-6">
                    <h2 className="text-lg font-semibold mb-4">Frequently Asked Questions</h2>
                    <input
                      type="text"
                      placeholder="Search FAQ..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  
                  <div className="space-y-4">
                    {filteredFaqs.map((faq) => (
                      <details key={faq.id} className="border border-gray-200 rounded-lg">
                        <summary className="px-4 py-3 font-medium cursor-pointer hover:bg-gray-50 flex items-center justify-between">
                          {faq.question}
                          <ChevronDown className="h-4 w-4 text-gray-400" />
                        </summary>
                        <div className="px-4 pb-3 text-gray-600 text-sm">
                          {faq.answer}
                        </div>
                      </details>
                    ))}
                    
                    {filteredFaqs.length === 0 && (
                      <div className="text-center py-8 text-gray-500">
                        <p>No FAQ items match your search.</p>
                        <p className="text-sm mt-1">Try different keywords or contact support.</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {activeSection === 'tutorials' && (
                <div>
                  <h2 className="text-lg font-semibold mb-6">Video Tutorials</h2>
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="w-full h-32 bg-gray-200 rounded-lg mb-3 flex items-center justify-center">
                        🎥 Getting Started
                      </div>
                      <h3 className="font-medium mb-2">TeamFlow Basics (5 min)</h3>
                      <p className="text-sm text-gray-600">Learn the fundamentals of using TeamFlow</p>
                    </div>
                    
                    <div className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="w-full h-32 bg-gray-200 rounded-lg mb-3 flex items-center justify-center">
                        🎥 Project Management
                      </div>
                      <h3 className="font-medium mb-2">Managing Projects (8 min)</h3>
                      <p className="text-sm text-gray-600">Advanced project management techniques</p>
                    </div>
                    
                    <div className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="w-full h-32 bg-gray-200 rounded-lg mb-3 flex items-center justify-center">
                        🎥 Templates
                      </div>
                      <h3 className="font-medium mb-2">Using Templates (6 min)</h3>
                      <p className="text-sm text-gray-600">Boost productivity with templates</p>
                    </div>
                    
                    <div className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="w-full h-32 bg-gray-200 rounded-lg mb-3 flex items-center justify-center">
                        🎥 Team Collaboration
                      </div>
                      <h3 className="font-medium mb-2">Team Features (10 min)</h3>
                      <p className="text-sm text-gray-600">Collaborate effectively with your team</p>
                    </div>
                  </div>
                </div>
              )}

              {activeSection === 'contact' && (
                <div>
                  <h2 className="text-lg font-semibold mb-6">Contact Support</h2>
                  
                  <div className="space-y-6">
                    <div className="border rounded-lg p-4">
                      <div className="flex items-start space-x-3">
                        <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                          <MessageCircle className="h-5 w-5 text-green-600" />
                        </div>
                        <div className="flex-1">
                          <h3 className="font-medium mb-1">Live Chat</h3>
                          <p className="text-sm text-gray-600 mb-3">Get instant help from our support team</p>
                          <button className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 text-sm">
                            Start Chat
                          </button>
                        </div>
                        <div className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded">
                          Online
                        </div>
                      </div>
                    </div>
                    
                    <div className="border rounded-lg p-4">
                      <div className="flex items-start space-x-3">
                        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                          <MessageCircle className="h-5 w-5 text-blue-600" />
                        </div>
                        <div className="flex-1">
                          <h3 className="font-medium mb-1">Email Support</h3>
                          <p className="text-sm text-gray-600 mb-3">Send us a detailed message</p>
                          <div className="text-sm text-gray-500">
                            support@teamflow.com
                          </div>
                        </div>
                        <div className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                          24h response
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <h3 className="font-medium text-blue-900 mb-2">Before contacting support:</h3>
                      <ul className="text-sm text-blue-800 space-y-1">
                        <li>• Check the FAQ section above</li>
                        <li>• Try the search function in the app</li>
                        <li>• Include screenshots when reporting bugs</li>
                        <li>• Mention your browser and operating system</li>
                      </ul>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HelpCenter;