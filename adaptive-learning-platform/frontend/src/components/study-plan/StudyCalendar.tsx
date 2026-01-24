"use client";

import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

export default function StudyCalendar() {
  const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  // Mock data for a month view
  const currentMonth = "February 2026";
  const calendarDays = Array.from({ length: 28 }, (_, i) => ({
    day: i + 1,
    hasSession: [2, 5, 8, 12, 14, 15, 19, 22].includes(i + 1),
    isToday: i + 1 === 24
  }));

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
      <div className="flex justify-between items-center mb-6">
        <h3 className="font-bold text-gray-900 dark:text-white">{currentMonth}</h3>
        <div className="flex gap-2">
          <button className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"><ChevronLeft className="w-4 h-4 text-gray-500" /></button>
          <button className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"><ChevronRight className="w-4 h-4 text-gray-500" /></button>
        </div>
      </div>

      <div className="grid grid-cols-7 gap-1 text-center mb-2">
        {days.map(d => (
          <div key={d} className="text-xs font-medium text-gray-400 uppercase py-1">{d}</div>
        ))}
      </div>

      <div className="grid grid-cols-7 gap-1">
        {calendarDays.map((date) => (
          <div 
            key={date.day} 
            className={`
              aspect-square rounded-lg flex flex-col items-center justify-center text-sm relative cursor-pointer transition
              hover:bg-gray-50 dark:hover:bg-gray-700
              ${date.isToday ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 font-bold border border-blue-200 dark:border-blue-800' : 'text-gray-700 dark:text-gray-300'}
            `}
          >
            {date.day}
            {date.hasSession && (
              <div className="w-1.5 h-1.5 bg-green-500 rounded-full mt-1"></div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
