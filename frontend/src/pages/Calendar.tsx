/**
 * Calendar Page Component
 * Calendar and scheduling interface (placeholder for future implementation)
 */

import React from 'react';
import Layout from '../components/Layout';
import { Calendar as CalendarIcon, Plus, ChevronLeft, ChevronRight } from 'lucide-react';

const Calendar: React.FC = () => {
  const today = new Date();
  const currentMonth = today.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center">
              <CalendarIcon className="mr-3 text-blue-600" size={32} />
              Calendar
            </h1>
            <p className="text-gray-600 mt-1">
              Schedule and track your team's events and milestones
            </p>
          </div>
          
          <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2">
            <Plus size={20} />
            New Event
          </button>
        </div>

        {/* Calendar Controls */}
        <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-900">{currentMonth}</h2>
            <div className="flex items-center space-x-2">
              <button className="p-2 hover:bg-gray-100 rounded-md transition-colors">
                <ChevronLeft size={20} />
              </button>
              <button className="px-4 py-2 bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors">
                Today
              </button>
              <button className="p-2 hover:bg-gray-100 rounded-md transition-colors">
                <ChevronRight size={20} />
              </button>
            </div>
          </div>

          {/* Calendar Placeholder */}
          <div className="text-center py-16 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
            <CalendarIcon size={64} className="mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Calendar Coming Soon</h3>
            <p className="text-gray-600 mb-6 max-w-md mx-auto">
              Full calendar functionality with event scheduling, task deadlines, and team coordination will be available in a future update.
            </p>
            
            {/* Feature Preview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto mt-8">
              <div className="text-center">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  📅
                </div>
                <h4 className="font-medium text-gray-900 mb-2">Event Scheduling</h4>
                <p className="text-sm text-gray-600">Create and manage team events, meetings, and deadlines</p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  🔗
                </div>
                <h4 className="font-medium text-gray-900 mb-2">Task Integration</h4>
                <p className="text-sm text-gray-600">See task deadlines and project milestones on your calendar</p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  👥
                </div>
                <h4 className="font-medium text-gray-900 mb-2">Team Coordination</h4>
                <p className="text-sm text-gray-600">Coordinate schedules and plan collaborative work sessions</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Calendar;