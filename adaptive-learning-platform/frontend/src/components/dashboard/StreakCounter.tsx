"use client";

import React from 'react';
import { Flame } from 'lucide-react';

export default function StreakCounter() {
  const days = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];
  const activeDays = [true, true, true, true, false, true, true]; // Mock data

  return (
    <div className="bg-gradient-to-br from-orange-500 to-red-600 p-6 rounded-xl shadow-lg text-white">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-2xl font-bold flex items-center gap-2">
            <Flame className="w-6 h-6 animate-pulse" /> 12 Days
          </h3>
          <p className="text-orange-100 text-sm">You're on fire! Keep it up.</p>
        </div>
        <div className="bg-white/20 p-2 rounded-lg backdrop-blur-sm">
          <span className="text-xs font-bold uppercase tracking-wider">Streak</span>
        </div>
      </div>

      <div className="flex justify-between gap-1">
        {days.map((day, i) => (
          <div key={i} className="flex flex-col items-center gap-1">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
              activeDays[i] ? 'bg-white text-orange-600' : 'bg-white/20 text-white'
            }`}>
              {activeDays[i] ? '✓' : ''}
            </div>
            <span className="text-[10px] text-orange-100">{day}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
