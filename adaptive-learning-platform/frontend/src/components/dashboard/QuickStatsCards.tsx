"use client";

import React from 'react';
import { Target, Clock, Award, TrendingUp } from 'lucide-react';

export interface DashboardStats {
  avg_mastery: string;
  study_time: string;
  total_questions: number;
  streak: string;
}

export default function QuickStatsCards({ stats }: { stats?: DashboardStats }) {
  const cards = [
    { label: 'Avg Mastery', value: stats?.avg_mastery || '-', icon: Target, color: 'text-blue-600', bg: 'bg-blue-100 dark:bg-blue-900/30' },
    { label: 'Study Time', value: stats?.study_time || '-', icon: Clock, color: 'text-purple-600', bg: 'bg-purple-100 dark:bg-purple-900/30' },
    { label: 'Questions', value: stats?.total_questions?.toLocaleString() || '-', icon: Award, color: 'text-yellow-600', bg: 'bg-yellow-100 dark:bg-yellow-900/30' },
    { label: 'Current Streak', value: stats?.streak || '-', icon: TrendingUp, color: 'text-green-600', bg: 'bg-green-100 dark:bg-green-900/30' },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {cards.map((stat) => (
        <div key={stat.label} className="bg-white dark:bg-gray-800 p-4 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm flex flex-col items-center text-center">
          <div className={`p-3 rounded-full mb-3 ${stat.bg} ${stat.color}`}>
            <stat.icon className="w-5 h-5" />
          </div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white mb-1">{stat.value}</div>
          <div className="text-xs text-gray-500 dark:text-gray-400 uppercase font-bold tracking-wider">{stat.label}</div>
        </div>
      ))}
    </div>
  );
}
