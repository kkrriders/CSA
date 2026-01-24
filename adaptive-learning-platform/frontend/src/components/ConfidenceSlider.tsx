"use client";

import React from 'react';

interface ConfidenceSliderProps {
  value: number;
  onChange: (value: number) => void;
}

export default function ConfidenceSlider({ value, onChange }: ConfidenceSliderProps) {
  return (
    <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-100 dark:border-gray-700">
      <div className="flex justify-between items-center mb-2">
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
          How confident are you?
        </label>
        <span className={`text-sm font-bold ${
          value < 50 ? 'text-red-500' : value < 80 ? 'text-yellow-500' : 'text-green-500'
        }`}>
          {value}%
        </span>
      </div>
      <input
        type="range"
        min="0"
        max="100"
        step="10"
        value={value}
        onChange={(e) => onChange(parseInt(e.target.value))}
        className="w-full h-2 bg-gray-200 dark:bg-gray-600 rounded-lg appearance-none cursor-pointer accent-blue-600"
      />
      <div className="flex justify-between text-xs text-gray-400 mt-1">
        <span>Guessing</span>
        <span>Sure</span>
      </div>
    </div>
  );
}
