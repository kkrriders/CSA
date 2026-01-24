"use client";

import React from 'react';
import LearningVelocityChart from '@/components/analytics/LearningVelocityChart';
import ForgettingCurveChart from '@/components/analytics/ForgettingCurveChart';
import ExamReadinessRadar from '@/components/analytics/ExamReadinessRadar';
import BehaviorFingerprintWheel from '@/components/analytics/BehaviorFingerprintWheel';
import TopicMasteryHeatmap from '@/components/analytics/TopicMasteryHeatmap';
import SessionComparisonChart from '@/components/analytics/SessionComparisonChart';
import DifficultyBreakdown from '@/components/analytics/DifficultyBreakdown';

export default function AnalyticsDashboard() {
  return (
    <div className="min-h-screen bg-gray-50 p-6 md:p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="text-gray-500 mt-2">Deep insights into your learning progress and habits.</p>
        </div>

        {/* Key Metrics Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
           <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
             <h3 className="text-sm font-medium text-gray-500">Total Study Time</h3>
             <p className="text-2xl font-bold text-gray-900 mt-2">12h 45m</p>
             <span className="text-xs text-green-500 font-medium">+15% vs last week</span>
           </div>
           <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
             <h3 className="text-sm font-medium text-gray-500">Avg. Accuracy</h3>
             <p className="text-2xl font-bold text-gray-900 mt-2">78%</p>
             <span className="text-xs text-green-500 font-medium">+2% vs last week</span>
           </div>
           <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
             <h3 className="text-sm font-medium text-gray-500">Questions Answered</h3>
             <p className="text-2xl font-bold text-gray-900 mt-2">1,245</p>
             <span className="text-xs text-blue-500 font-medium">Keep it up!</span>
           </div>
           <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
             <h3 className="text-sm font-medium text-gray-500">Current Streak</h3>
             <p className="text-2xl font-bold text-gray-900 mt-2">5 Days</p>
             <span className="text-xs text-orange-500 font-medium">Best: 12 Days</span>
           </div>
        </div>

        {/* Main Charts Area */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <LearningVelocityChart />
          <ForgettingCurveChart />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <ExamReadinessRadar />
          <BehaviorFingerprintWheel />
          <DifficultyBreakdown />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <SessionComparisonChart />
          <TopicMasteryHeatmap />
        </div>
      </div>
    </div>
  );
}
