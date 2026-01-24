"use client";

import React from 'react';

export default function ReviewCalendar() {
  // Mock data: Review load for next 7 days
  const days = [
    { day: 'Mon', load: 'low', count: 12 },
    { day: 'Tue', load: 'medium', count: 45 },
    { day: 'Wed', load: 'high', count: 120 },
    { day: 'Thu', load: 'medium', count: 50 },
    { day: 'Fri', load: 'low', count: 20 },
    { day: 'Sat', load: 'none', count: 0 },
    { day: 'Sun', load: 'high', count: 85 },
  ];

  const getBarHeight = (count: number) => {
    return Math.min(100, Math.max(10, (count / 150) * 100)); // normalize to 100px max
  };

  const getColor = (load: string) => {
    switch(load) {
      case 'high': return 'bg-red-400 dark:bg-red-500';
      case 'medium': return 'bg-yellow-400 dark:bg-yellow-500';
      case 'low': return 'bg-green-400 dark:bg-green-500';
      default: return 'bg-gray-200 dark:bg-gray-700';
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm">
      <h3 className="font-bold text-gray-900 dark:text-white mb-6">Upcoming Review Load</h3>
      
      <div className="flex items-end justify-between gap-2 h-32 mb-2">
        {days.map((d) => (
          <div key={d.day} className="flex-1 flex flex-col items-center gap-2 group">
            <span className="text-xs font-bold text-gray-500 dark:text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity absolute -mt-6">
              {d.count}
            </span>
            <div 
              className={`w-full rounded-t-lg transition-all hover:opacity-80 ${getColor(d.load)}`}
              style={{ height: `${getBarHeight(d.count)}%` }}
            ></div>
          </div>
        ))}
      </div>
      
      <div className="flex justify-between text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
        {days.map((d) => (
          <div key={d.day} className="flex-1 text-center">{d.day}</div>
        ))}
      </div>
    </div>
  );
}
