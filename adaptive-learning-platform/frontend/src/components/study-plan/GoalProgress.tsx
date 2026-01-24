"use client";

import React from 'react';
import { Target, Trophy } from 'lucide-react';

interface GoalProgressProps {
  goalName: string;
  current: number;
  target: number;
  unit: string;
}

export default function GoalProgress({ goalName, current, target, unit }: GoalProgressProps) {
  const percentage = Math.min(100, Math.round((current / target) * 100));
  
  return (
    <div className="bg-white dark:bg-gray-800 p-5 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg text-purple-600 dark:text-purple-400">
            <Target className="w-5 h-5" />
          </div>
          <div>
            <h4 className="font-bold text-gray-900 dark:text-white text-sm">{goalName}</h4>
            <p className="text-xs text-gray-500 dark:text-gray-400">Target: {target} {unit}</p>
          </div>
        </div>
        {percentage >= 100 && (
          <Trophy className="w-5 h-5 text-yellow-500 animate-bounce" />
        )}
      </div>

      <div className="relative pt-1">
        <div className="flex mb-2 items-center justify-between">
          <div className="text-right">
            <span className="text-xs font-semibold inline-block text-purple-600 dark:text-purple-400">
              {percentage}%
            </span>
          </div>
          <div className="text-right">
            <span className="text-xs font-semibold inline-block text-gray-600 dark:text-gray-400">
              {current} / {target}
            </span>
          </div>
        </div>
        <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-purple-100 dark:bg-purple-900/20">
          <div 
            style={{ width: `${percentage}%` }} 
            className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-purple-500 transition-all duration-1000"
          ></div>
        </div>
      </div>
    </div>
  );
}
