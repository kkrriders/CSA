"use client";

import React from 'react';

interface TopicData {
  name: string;
  mastery: number;
}

const defaultTopics: TopicData[] = [
  { name: 'Algebra', mastery: 85 },
  { name: 'Geometry', mastery: 60 },
  { name: 'Calculus', mastery: 40 },
  { name: 'Statistics', mastery: 90 },
  { name: 'Trigonometry', mastery: 75 },
  { name: 'Linear Algebra', mastery: 55 },
  { name: 'Probability', mastery: 95 },
  { name: 'Number Theory', mastery: 30 },
];

const getColor = (mastery: number) => {
  if (mastery >= 80) return 'bg-green-500';
  if (mastery >= 60) return 'bg-yellow-400';
  if (mastery >= 40) return 'bg-orange-400';
  return 'bg-red-500';
};

const TopicMasteryHeatmap = ({ data }: { data?: TopicData[] }) => {
  const topics = data || defaultTopics;

  return (
    <div className="w-full h-80 bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700 flex flex-col">
      <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">Topic Mastery Heatmap</h3>
      <div className="flex-1 grid grid-cols-2 gap-2 overflow-y-auto">
        {topics.map((topic) => (
          <div key={topic.name} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-900 rounded-md">
             <span className="text-sm font-medium text-gray-700 dark:text-gray-300 truncate mr-2" title={topic.name}>{topic.name}</span>
             <div className="flex items-center gap-2 flex-shrink-0">
               <div className={`w-3 h-3 rounded-full ${getColor(topic.mastery)}`}></div>
               <span className="text-xs text-gray-500 dark:text-gray-400 w-8 text-right">{topic.mastery.toFixed(0)}%</span>
             </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TopicMasteryHeatmap;
