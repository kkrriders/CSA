"use client";

import React from 'react';
import { Mail, Bell, CheckCircle } from 'lucide-react';

export interface NotificationHistoryItem {
  id: number | string;
  type: 'email' | 'push' | 'in_app';
  title: string;
  date: string;
  status: string;
}

interface NotificationHistoryProps {
  items?: NotificationHistoryItem[];
}

export default function NotificationHistory({ items: propItems }: NotificationHistoryProps) {
  const defaultHistory: NotificationHistoryItem[] = [
    { id: 1, type: 'email', title: 'Weekly Progress Report', date: '2 days ago', status: 'sent' },
    { id: 2, type: 'push', title: 'Study Reminder: CNNs', date: '3 days ago', status: 'sent' },
    { id: 3, type: 'email', title: 'New Course Recommendation', date: '5 days ago', status: 'opened' },
  ];

  const history = propItems || defaultHistory;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
        <h3 className="font-semibold text-gray-900 dark:text-white">Recent Activity</h3>
      </div>
      <div className="divide-y divide-gray-100 dark:divide-gray-700">
        {history.map((item) => (
          <div key={item.id} className="p-4 flex items-center gap-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition">
            <div className="bg-gray-100 dark:bg-gray-700 p-2 rounded-full text-gray-500 dark:text-gray-400">
              {item.type === 'email' ? <Mail className="w-4 h-4" /> : <Bell className="w-4 h-4" />}
            </div>
            <div className="flex-1">
              <div className="font-medium text-gray-900 dark:text-white text-sm">{item.title}</div>
              <div className="text-xs text-gray-500 dark:text-gray-400">{item.date}</div>
            </div>
            <div className="text-xs font-medium text-green-600 dark:text-green-400 flex items-center gap-1">
              <CheckCircle className="w-3 h-3" /> {item.status}
            </div>
          </div>
        ))}
      </div>
      <div className="p-3 text-center border-t border-gray-100 dark:border-gray-700">
        <button className="text-sm text-blue-600 dark:text-blue-400 font-medium hover:underline">View All History</button>
      </div>
    </div>
  );
}
