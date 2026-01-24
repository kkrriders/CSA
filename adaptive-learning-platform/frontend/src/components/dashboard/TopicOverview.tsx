"use client";

import React from 'react';

export interface TopicStats {
  name: string;
  mastery: number;
  count: number;
}

export default function TopicOverview({ topics }: { topics?: TopicStats[] }) {
  if (!topics || topics.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm">
        <h3 className="font-bold text-gray-900 dark:text-white mb-4">Topic Performance</h3>
        <p className="text-gray-500 dark:text-gray-400 text-sm">No topic data available.</p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm">
      <h3 className="font-bold text-gray-900 dark:text-white mb-4">Topic Performance</h3>
      <div className="space-y-4">
        {topics.map((t) => (
          <div key={t.name}>
            <div className="flex justify-between text-sm mb-1">
              <span className="font-medium text-gray-700 dark:text-gray-300">{t.name}</span>
              <span className={`font-bold ${
                t.mastery >= 80 ? 'text-green-600 dark:text-green-400' :
                t.mastery >= 60 ? 'text-yellow-600 dark:text-yellow-400' : 'text-red-600 dark:text-red-400'
              }`}>{t.mastery}%</span>
            </div>
            <div className="w-full bg-gray-100 dark:bg-gray-700 rounded-full h-2">
              <div 
                className={`h-2 rounded-full ${
                  t.mastery >= 80 ? 'bg-green-500' :
                  t.mastery >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${t.mastery}%` }}
              ></div>
            </div>
            <div className="text-xs text-gray-400 mt-1 text-right">{t.count} questions</div>
          </div>
        ))}
      </div>
    </div>
  );
}
