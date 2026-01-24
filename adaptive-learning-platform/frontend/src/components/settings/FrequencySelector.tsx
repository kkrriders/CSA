"use client";

import React from 'react';

interface FrequencySelectorProps {
  value: string;
  onChange: (value: string) => void;
}

export default function FrequencySelector({ value, onChange }: FrequencySelectorProps) {
  const options = [
    { id: 'instant', label: 'Instant', desc: 'As soon as it happens' },
    { id: 'daily', label: 'Daily Digest', desc: 'Once a day at 9 AM' },
    { id: 'weekly', label: 'Weekly Summary', desc: 'Every Sunday' },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
      {options.map((opt) => (
        <button
          key={opt.id}
          onClick={() => onChange(opt.id)}
          className={`
            p-3 rounded-lg border text-left transition relative overflow-hidden
            ${value === opt.id 
              ? 'border-blue-600 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300' 
              : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 text-gray-900 dark:text-gray-300'}
          `}
        >
          <div className="font-semibold text-sm">{opt.label}</div>
          <div className="text-xs opacity-70 mt-1">{opt.desc}</div>
          {value === opt.id && (
            <div className="absolute top-2 right-2 w-2 h-2 rounded-full bg-blue-600"></div>
          )}
        </button>
      ))}
    </div>
  );
}
