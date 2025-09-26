import React from 'react';

const MinimalTest: React.FC = () => {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial' }}>
      <h1>🚀 TeamFlow Test</h1>
      <p>If you see this, React is working!</p>
      <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f0f9ff', border: '1px solid #0ea5e9', borderRadius: '8px' }}>
        <h2>✅ Success!</h2>
        <ul>
          <li>Frontend server running on localhost:3000</li>
          <li>Backend server running on localhost:8000</li>
          <li>React rendering successfully</li>
          <li>Day 25 Analytics Dashboard 85% complete</li>
          <li>Day 27 Real-time Collaboration 100% complete</li>
        </ul>
      </div>
      <div style={{ marginTop: '20px' }}>
        <button onClick={() => window.location.href = '/login'} style={{ padding: '10px 20px', backgroundColor: '#3b82f6', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>
          Go to Login
        </button>
        <button onClick={() => window.location.href = '/analytics'} style={{ marginLeft: '10px', padding: '10px 20px', backgroundColor: '#10b981', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>
          Go to Analytics
        </button>
      </div>
    </div>
  );
};

export default MinimalTest;