"use client";

import React from 'react';
import { BookOpen, CheckCircle, Clock } from 'lucide-react';

export default function ActivityFeed() {
  const activities = [
    { id: 1, type: 'quiz', title: 'Deep Learning Quiz', score: '85%', date: '2 hours ago' },
    { id: 2, type: 'study', title: 'Read: Convolutional Networks', duration: '45m', date: 'Yesterday' },
    { id: 3, type: 'quiz', title: 'Linear Algebra Review', score: '92%', date: '2 days ago' },
  ];

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm">
      <h3 className="font-bold text-gray-900 dark:text-white mb-4">Recent Activity</h3>
      <div className="space-y-4">
        {activities.map((item) => (
          <div key={item.id} className="flex items-start gap-3 pb-3 border-b border-gray-50 dark:border-gray-700 last:border-0 last:pb-0">
            <div className={`mt-1 p-2 rounded-full ${item.type === 'quiz' ? 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400' : 'bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400'}`}>
              {item.type === 'quiz' ? <CheckCircle className="w-4 h-4" /> : <BookOpen className="w-4 h-4" />}
            </div>
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white text-sm">{item.title}</h4>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 flex items-center gap-2">
                <span>{item.date}</span>
                <span>•</span>
                <span className="font-medium text-gray-700 dark:text-gray-300">
                  {item.type === 'quiz' ? `Score: ${item.score}` : item.duration}
                </span>
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
