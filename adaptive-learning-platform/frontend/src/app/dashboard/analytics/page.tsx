"use client";

import React, { useEffect, useState } from 'react';
import LearningVelocityChart from '@/components/analytics/LearningVelocityChart';
import ForgettingCurveChart from '@/components/analytics/ForgettingCurveChart';
import ExamReadinessRadar from '@/components/analytics/ExamReadinessRadar';
import BehaviorFingerprintWheel from '@/components/analytics/BehaviorFingerprintWheel';
import TopicMasteryHeatmap from '@/components/analytics/TopicMasteryHeatmap';
import SessionComparisonChart from '@/components/analytics/SessionComparisonChart';
import DifficultyBreakdown from '@/components/analytics/DifficultyBreakdown';
import { api } from '@/lib/api';
import type { LearningVelocity, BehaviorFingerprint } from '@/types';

export default function AnalyticsDashboard() {
  const [velocityData, setVelocityData] = useState<any[] | undefined>(undefined);
  const [fingerprintData, setFingerprintData] = useState<any[] | undefined>(undefined);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [velocityRes, fingerprintRes] = await Promise.all([
          api.getLearningVelocity().catch(() => ({ velocities: [] })),
          api.getAggregateBehaviorFingerprint().catch(() => null)
        ]);

        // Process Velocity Data
        if (velocityRes.velocities.length > 0) {
          // Take the first topic for now, or aggregate
          const trajectory = velocityRes.velocities[0].mastery_trajectory;
          const chartData = trajectory.map((val, idx) => ({
            name: `Session ${idx + 1}`,
            velocity: Math.round(val * 100)
          }));
          setVelocityData(chartData);
        }

        // Process Fingerprint Data
        if (fingerprintRes) {
          const fp = fingerprintRes as BehaviorFingerprint;
          const chartData = [
            { trait: 'Risk Taking', val: Math.round(fp.risk_taking * 100), fullMark: 100 },
            { trait: 'Perfectionism', val: Math.round(fp.perfectionism * 100), fullMark: 100 },
            { trait: 'Skimming', val: Math.round(fp.skimming * 100), fullMark: 100 },
            { trait: 'Grinding', val: Math.round(fp.grinding * 100), fullMark: 100 },
            { trait: 'Confidence', val: Math.round(fp.confidence_calibration * 100), fullMark: 100 },
            { trait: 'Consistency', val: Math.round(fp.consistency * 100), fullMark: 100 },
          ];
          setFingerprintData(chartData);
        }

      } catch (error) {
        console.error("Failed to load analytics data", error);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6 md:p-8 transition-colors duration-200">
      <div className="max-w-7xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Analytics Dashboard</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-2">Deep insights into your learning progress and habits.</p>
        </div>

        {/* Key Metrics Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
           <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700">
             <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Study Time</h3>
             <p className="text-2xl font-bold text-gray-900 dark:text-white mt-2">12h 45m</p>
             <span className="text-xs text-green-500 font-medium">+15% vs last week</span>
           </div>
           <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700">
             <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Avg. Accuracy</h3>
             <p className="text-2xl font-bold text-gray-900 dark:text-white mt-2">78%</p>
             <span className="text-xs text-green-500 font-medium">+2% vs last week</span>
           </div>
           <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700">
             <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Questions Answered</h3>
             <p className="text-2xl font-bold text-gray-900 dark:text-white mt-2">1,245</p>
             <span className="text-xs text-blue-500 font-medium">Keep it up!</span>
           </div>
           <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700">
             <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Current Streak</h3>
             <p className="text-2xl font-bold text-gray-900 dark:text-white mt-2">5 Days</p>
             <span className="text-xs text-orange-500 font-medium">Best: 12 Days</span>
           </div>
        </div>

        {/* Main Charts Area */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <LearningVelocityChart data={velocityData} />
          <ForgettingCurveChart />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <ExamReadinessRadar />
          <BehaviorFingerprintWheel data={fingerprintData} />
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
