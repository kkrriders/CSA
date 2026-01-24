"use client";

import React from 'react';
import { CheckCircle, XCircle, MinusCircle, Clock } from 'lucide-react';

interface TimelineItem {
  id: number;
  status: 'correct' | 'wrong' | 'skipped';
  timeTaken: number;
}

export default function QuestionTimeline({ items }: { items: TimelineItem[] }) {
  const maxTime = Math.max(...items.map(i => i.timeTaken));

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm overflow-x-auto">
      <h3 className="font-bold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
        <Clock className="w-5 h-5 text-blue-500" />
        Time & Accuracy Timeline
      </h3>
      
      <div className="flex items-end gap-2 h-40 min-w-[600px] pb-6 px-2">
        {items.map((item, idx) => {
          const heightPct = Math.max(10, (item.timeTaken / maxTime) * 100);
          return (
            <div key={idx} className="flex-1 flex flex-col items-center gap-2 group relative">
              {/* Tooltip */}
              <div className="absolute bottom-full mb-2 opacity-0 group-hover:opacity-100 transition-opacity bg-gray-900 text-white text-xs px-2 py-1 rounded whitespace-nowrap z-10">
                Q{idx + 1}: {item.timeTaken}s ({item.status})
              </div>
              
              <div 
                className={`
                  w-full rounded-t-md transition-all hover:brightness-110
                  ${item.status === 'correct' ? 'bg-green-400 dark:bg-green-500' : 
                    item.status === 'wrong' ? 'bg-red-400 dark:bg-red-500' : 'bg-gray-300 dark:bg-gray-600'}
                `}
                style={{ height: `${heightPct}%` }}
              ></div>
              <div className="text-[10px] font-medium text-gray-500 dark:text-gray-400">
                {idx + 1}
              </div>
            </div>
          );
        })}
      </div>
      
      <div className="flex justify-center gap-6 text-xs text-gray-500 dark:text-gray-400">
        <div className="flex items-center gap-1"><div className="w-3 h-3 bg-green-400 rounded"></div> Correct</div>
        <div className="flex items-center gap-1"><div className="w-3 h-3 bg-red-400 rounded"></div> Incorrect</div>
        <div className="flex items-center gap-1"><div className="w-3 h-3 bg-gray-300 rounded"></div> Skipped</div>
        <div className="flex items-center gap-1 ml-4 text-gray-400">Bar height = Time taken</div>
      </div>
    </div>
  );
}
