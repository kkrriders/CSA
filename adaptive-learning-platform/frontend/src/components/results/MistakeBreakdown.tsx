"use client";

import React from 'react';
import { AlertCircle, Zap, Brain, HelpCircle } from 'lucide-react';

export default function MistakeBreakdown() {
  const mistakes = [
    { type: 'Knowledge Gap', count: 3, icon: Brain, color: 'text-purple-600', bg: 'bg-purple-100 dark:bg-purple-900/30' },
    { type: 'Silly Mistake', count: 1, icon: Zap, color: 'text-yellow-600', bg: 'bg-yellow-100 dark:bg-yellow-900/30' },
    { type: 'Misread Question', count: 2, icon: HelpCircle, color: 'text-blue-600', bg: 'bg-blue-100 dark:bg-blue-900/30' },
  ];

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm">
      <h3 className="font-bold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
        <AlertCircle className="w-5 h-5 text-red-500" />
        Mistake Analysis
      </h3>

      <div className="space-y-4">
        {mistakes.map((m) => (
          <div key={m.type} className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg ${m.bg} ${m.color}`}>
                <m.icon className="w-5 h-5" />
              </div>
              <span className="font-medium text-gray-700 dark:text-gray-200">{m.type}</span>
            </div>
            <span className="font-bold text-gray-900 dark:text-white bg-gray-100 dark:bg-gray-700 px-3 py-1 rounded-full text-sm">
              {m.count}
            </span>
          </div>
        ))}
      </div>
      
      <div className="mt-6 pt-4 border-t border-gray-100 dark:border-gray-700">
        <p className="text-xs text-center text-gray-500 dark:text-gray-400">
          * Categorized based on time taken & answer patterns
        </p>
      </div>
    </div>
  );
}
