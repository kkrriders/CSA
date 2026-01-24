"use client";

import React from 'react';
import { Sparkles, ArrowRight } from 'lucide-react';

interface RecommendedSessionProps {
  topic: string;
  reason: string;
  duration: number;
  difficulty: string;
  onStart: () => void;
}

export default function RecommendedSession({ topic, reason, duration, difficulty, onStart }: RecommendedSessionProps) {
  return (
    <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl p-6 text-white shadow-lg relative overflow-hidden">
      <div className="absolute top-0 right-0 p-4 opacity-10">
        <Sparkles className="w-32 h-32" />
      </div>
      
      <div className="relative z-10">
        <div className="flex items-center gap-2 mb-2 text-blue-100 text-sm font-medium uppercase tracking-wide">
          <Sparkles className="w-4 h-4" />
          AI Recommended
        </div>
        
        <h3 className="text-2xl font-bold mb-1">Review: {topic}</h3>
        <p className="text-blue-100 mb-6 text-sm max-w-md">{reason}</p>
        
        <div className="flex flex-wrap gap-4 mb-6">
          <div className="bg-white/20 px-3 py-1 rounded-full text-sm backdrop-blur-sm">
            ⏱ {duration} mins
          </div>
          <div className="bg-white/20 px-3 py-1 rounded-full text-sm backdrop-blur-sm capitalize">
            📊 {difficulty}
          </div>
        </div>
        
        <button 
          onClick={onStart}
          className="bg-white text-blue-600 px-6 py-2 rounded-lg font-bold hover:bg-blue-50 transition flex items-center gap-2"
        >
          Start Session <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
