"use client";

import React from 'react';
import { TrendingUp, Info } from 'lucide-react';

interface ComparisonViewProps {
  currentScore: number;
  previousScore?: number;
}

export default function ComparisonView({ currentScore, previousScore }: ComparisonViewProps) {
  // If no previous score, show info message
  if (previousScore === undefined || previousScore === null) {
    return (
      <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm">
        <h3 className="font-bold text-gray-900 dark:text-white mb-4">Performance Context</h3>
        <div className="flex items-start gap-3 text-sm text-gray-600 dark:text-gray-400">
          <Info className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <p>Complete more tests on this document to see your progress over time.</p>
        </div>
      </div>
    );
  }

  // Calculate improvement
  const improvement = currentScore - previousScore;
  const improvementPercent = improvement.toFixed(1);
  const isImprovement = improvement > 0;
  const isDecline = improvement < 0;

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm">
      <h3 className="font-bold text-gray-900 dark:text-white mb-6">Performance Context</h3>

      <div className="space-y-6">
        {/* Vs Previous */}
        <div>
          <div className="flex justify-between text-sm mb-2">
            <span className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
              <TrendingUp className="w-4 h-4" /> Vs. Last Session
            </span>
            <span className={`font-bold ${
              isImprovement ? 'text-green-500' :
              isDecline ? 'text-red-500' :
              'text-gray-500'
            }`}>
              {isImprovement && '+'}{improvementPercent}%
            </span>
          </div>
          <div className="h-2 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden flex">
             <div
               className="bg-gray-300 dark:bg-gray-600 h-full"
               style={{ width: `${previousScore}%` }}
             ></div>
             {isImprovement && (
               <div
                 className="bg-green-500 h-full"
                 style={{ width: `${improvement}%` }}
               ></div>
             )}
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 text-right">
            You scored {currentScore.toFixed(0)}% (prev: {previousScore.toFixed(0)}%)
          </p>
        </div>
      </div>
    </div>
  );
}
