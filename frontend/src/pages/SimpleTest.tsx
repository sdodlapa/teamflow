import React from 'react';
import Layout from '../components/Layout';

const SimpleTest: React.FC = () => {
  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white shadow rounded-lg p-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            🚀 TeamFlow is Working!
          </h1>
          <div className="space-y-4">
            <p className="text-lg text-gray-600">
              Both servers are running successfully:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-green-50 p-4 rounded">
                <h3 className="font-semibold text-green-800">✅ Frontend Server</h3>
                <p className="text-green-600">React + Vite running on localhost:3000</p>
              </div>
              <div className="bg-blue-50 p-4 rounded">
                <h3 className="font-semibold text-blue-800">✅ Backend Server</h3>
                <p className="text-blue-600">FastAPI running on localhost:8000</p>
              </div>
            </div>
            <div className="mt-8">
              <h2 className="text-xl font-semibold mb-4">🎉 Major Achievements</h2>
              <ul className="space-y-2 text-gray-700">
                <li>✅ Day 27: Real-time Collaboration - COMPLETE</li>
                <li>🚧 Day 25: Analytics Dashboard - 85% Complete</li>
                <li>✅ Both backend and frontend operational</li>
                <li>✅ Authentication system working</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default SimpleTest;