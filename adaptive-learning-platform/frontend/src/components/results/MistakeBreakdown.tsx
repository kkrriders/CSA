"use client";

import React from 'react';
import { AlertCircle, Clock, Target, XCircle, Info } from 'lucide-react';
import type { WeaknessAnalysis } from '@/types';

interface MistakeBreakdownProps {
  weaknesses: WeaknessAnalysis[];
  totalWrong: number;
}

export default function MistakeBreakdown({ weaknesses, totalWrong }: MistakeBreakdownProps) {
  if (totalWrong === 0 || weaknesses.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm">
        <h3 className="font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-green-500" />
          Mistake Analysis
        </h3>
        <div className="flex items-start gap-3 text-sm text-gray-600 dark:text-gray-400">
          <Info className="w-5 h-5 flex-shrink-0 mt-0.5 text-green-500" />
          <p>Great job! No mistakes to analyze yet.</p>
        </div>
      </div>
    );
  }

  // Group weaknesses by type
  const weaknessCounts: Record<string, number> = {};
  weaknesses.forEach(w => {
    const patterns = w.failure_patterns || [];
    patterns.forEach(pattern => {
      weaknessCounts[pattern] = (weaknessCounts[pattern] || 0) + 1;
    });
  });

  // Map failure patterns to display info
  const mistakeTypeMap: Record<string, { icon: any; color: string; bg: string; label: string }> = {
    'fast_wrong': { icon: Clock, color: 'text-yellow-600', bg: 'bg-yellow-100 dark:bg-yellow-900/30', label: 'Rushed Answers' },
    'slow_wrong': { icon: Target, color: 'text-blue-600', bg: 'bg-blue-100 dark:bg-blue-900/30', label: 'Struggled Topics' },
    'easy_wrong': { icon: AlertCircle, color: 'text-red-600', bg: 'bg-red-100 dark:bg-red-900/30', label: 'Knowledge Gaps' },
    'tricky_wrong': { icon: AlertCircle, color: 'text-purple-600', bg: 'bg-purple-100 dark:bg-purple-900/30', label: 'Tricky Questions' },
    'repeated_topic': { icon: Target, color: 'text-orange-600', bg: 'bg-orange-100 dark:bg-orange-900/30', label: 'Recurring Issues' },
  };

  const mistakes = Object.entries(weaknessCounts).map(([type, count]) => ({
    type: mistakeTypeMap[type]?.label || type,
    count,
    icon: mistakeTypeMap[type]?.icon || XCircle,
    color: mistakeTypeMap[type]?.color || 'text-gray-600',
    bg: mistakeTypeMap[type]?.bg || 'bg-gray-100 dark:bg-gray-700',
  }));

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm">
      <h3 className="font-bold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
        <AlertCircle className="w-5 h-5 text-red-500" />
        Mistake Analysis
      </h3>

      <div className="space-y-4">
        {mistakes.length > 0 ? (
          mistakes.map((m) => (
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
          ))
        ) : (
          <div className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
            Answer more questions to see detailed mistake analysis
          </div>
        )}
      </div>

      <div className="mt-6 pt-4 border-t border-gray-100 dark:border-gray-700">
        <p className="text-xs text-center text-gray-500 dark:text-gray-400">
          * Categorized based on time taken & answer patterns
        </p>
      </div>
    </div>
  );
}
