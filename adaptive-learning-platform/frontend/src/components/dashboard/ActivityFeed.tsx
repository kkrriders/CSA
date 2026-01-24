"use client";

import React from 'react';
import { BookOpen, CheckCircle, Clock } from 'lucide-react';

export interface ActivityItem {
  id: number | string;
  type: 'quiz' | 'study';
  title: string;
  score?: string;
  duration?: string;
  date: string;
}

export default function ActivityFeed({ items }: { items?: ActivityItem[] }) {
  if (!items || items.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm">
        <h3 className="font-bold text-gray-900 dark:text-white mb-4">Recent Activity</h3>
        <p className="text-gray-500 dark:text-gray-400 text-sm">No recent activity.</p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm">
      <h3 className="font-bold text-gray-900 dark:text-white mb-4">Recent Activity</h3>
      <div className="space-y-4">
        {items.map((item) => (
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
