"use client";

import React from 'react';
import { ArrowRight, PlayCircle } from 'lucide-react';

export default function RecommendedActions() {
  return (
    <div className="bg-blue-600 dark:bg-blue-700 p-6 rounded-xl shadow-lg text-white">
      <h3 className="font-bold text-lg mb-2">Recommended for You</h3>
      <p className="text-blue-100 text-sm mb-6">
        Based on your recent mistakes in <strong>Gradient Descent</strong>, we've prepared a focused review session.
      </p>
      
      <button className="w-full bg-white text-blue-600 py-3 rounded-lg font-bold hover:bg-blue-50 transition flex items-center justify-center gap-2">
        <PlayCircle className="w-5 h-5" /> Start Review Session
      </button>
      
      <div className="mt-4 pt-4 border-t border-blue-500 flex justify-between items-center text-sm text-blue-100">
        <span>Est. time: 15 mins</span>
        <button className="hover:text-white flex items-center gap-1">
          Skip <ArrowRight className="w-3 h-3" />
        </button>
      </div>
    </div>
  );
}
