"use client";

import React from 'react';
import { TrendingUp, Users } from 'lucide-react';

export default function ComparisonView() {
  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm">
      <h3 className="font-bold text-gray-900 dark:text-white mb-6">Performance Context</h3>

      <div className="space-y-6">
        {/* Vs Previous */}
        <div>
          <div className="flex justify-between text-sm mb-2">
            <span className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
              <TrendingUp className="w-4 h-4" /> Vs. Last Session
            </span>
            <span className="font-bold text-green-500">+12%</span>
          </div>
          <div className="h-2 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden flex">
             <div className="w-[65%] bg-gray-300 dark:bg-gray-600 h-full"></div>
             <div className="w-[12%] bg-green-500 h-full"></div>
          </div>
          <p className="text-xs text-gray-500 mt-1 text-right">You scored 77% (prev: 65%)</p>
        </div>

        {/* Vs Peers */}
        <div>
          <div className="flex justify-between text-sm mb-2">
            <span className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
              <Users className="w-4 h-4" /> Vs. Class Average
            </span>
            <span className="font-bold text-blue-500">Top 15%</span>
          </div>
          <div className="relative pt-6 pb-2">
            <div className="h-2 bg-gray-100 dark:bg-gray-700 rounded-full w-full"></div>
            {/* Avg Marker */}
            <div className="absolute top-0 left-[60%] -translate-x-1/2 flex flex-col items-center">
              <span className="text-[10px] text-gray-400 mb-1">Avg</span>
              <div className="w-0.5 h-8 bg-gray-300 dark:bg-gray-500"></div>
            </div>
            {/* You Marker */}
            <div className="absolute top-0 left-[85%] -translate-x-1/2 flex flex-col items-center z-10">
               <span className="text-[10px] font-bold text-blue-600 dark:text-blue-400 mb-1">You</span>
               <div className="w-4 h-4 bg-blue-600 rounded-full border-2 border-white dark:border-gray-800 shadow-sm mt-2"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
