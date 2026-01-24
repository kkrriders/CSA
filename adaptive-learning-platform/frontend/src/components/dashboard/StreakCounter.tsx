"use client";

import React from 'react';
import { Flame } from 'lucide-react';

export default function StreakCounter({ streak }: { streak?: string }) {
  // If we had history data, we would visualize it. For now, showing the count is key.
  // We can show a generic placeholder or hide the dots. Let's hide them to avoid "fake" data visual.
  
  return (
    <div className="bg-gradient-to-br from-orange-500 to-red-600 p-6 rounded-xl shadow-lg text-white">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-2xl font-bold flex items-center gap-2">
            <Flame className="w-6 h-6 animate-pulse" /> {streak || "0 Days"}
          </h3>
          <p className="text-orange-100 text-sm">
            {streak && streak !== "0 Days" ? "Keep the momentum going!" : "Start your streak today!"}
          </p>
        </div>
        <div className="bg-white/20 p-2 rounded-lg backdrop-blur-sm">
          <span className="text-xs font-bold uppercase tracking-wider">Streak</span>
        </div>
      </div>
    </div>
  );
}
