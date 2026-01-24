"use client";

import React from 'react';
import { Clock, CheckCircle, Circle, PlayCircle } from 'lucide-react';

interface SessionCardProps {
  title: string;
  topic: string;
  durationMins: number;
  status: 'completed' | 'upcoming' | 'missed';
  date: string;
}

export default function SessionCard({ title, topic, durationMins, status, date }: SessionCardProps) {
  return (
    <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-3">
        <div>
          <h4 className="font-semibold text-gray-900 dark:text-white line-clamp-1">{title}</h4>
          <span className="text-xs text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 px-2 py-0.5 rounded-full">
            {topic}
          </span>
        </div>
        <div className="text-right">
          <span className={`text-xs font-bold px-2 py-1 rounded uppercase ${
            status === 'completed' ? 'text-green-600 bg-green-50 dark:bg-green-900/20 dark:text-green-400' :
            status === 'upcoming' ? 'text-gray-600 bg-gray-100 dark:bg-gray-700 dark:text-gray-300' :
            'text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-400'
          }`}>
            {status}
          </span>
        </div>
      </div>
      
      <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400 mb-4">
        <div className="flex items-center gap-1">
          <Clock className="w-3 h-3" />
          <span>{durationMins}m</span>
        </div>
        <span>{date}</span>
      </div>

      <button 
        disabled={status === 'completed'}
        className={`w-full py-2 rounded-md text-sm font-medium flex items-center justify-center gap-2 transition ${
          status === 'completed' 
            ? 'bg-gray-100 text-gray-400 cursor-not-allowed dark:bg-gray-700 dark:text-gray-500' 
            : 'bg-blue-600 text-white hover:bg-blue-700'
        }`}
      >
        {status === 'completed' ? (
          <>
            <CheckCircle className="w-4 h-4" /> Completed
          </>
        ) : (
          <>
            <PlayCircle className="w-4 h-4" /> Start Session
          </>
        )}
      </button>
    </div>
  );
}
