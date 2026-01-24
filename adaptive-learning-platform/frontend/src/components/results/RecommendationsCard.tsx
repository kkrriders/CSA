"use client";

import React from 'react';
import { ArrowRight, BookOpen, Video } from 'lucide-react';

export default function RecommendationsCard() {
  return (
    <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-xl p-6 text-white shadow-lg">
      <h3 className="font-bold text-lg mb-2">Recommended Next Steps</h3>
      <p className="text-blue-100 text-sm mb-6">Based on your performance, we recommend focusing on <strong>Neural Network Architectures</strong>.</p>

      <div className="space-y-3">
        <button className="w-full bg-white/10 hover:bg-white/20 p-3 rounded-lg text-left flex items-center justify-between transition backdrop-blur-sm border border-white/10">
          <div className="flex items-center gap-3">
            <div className="bg-white/20 p-2 rounded-full"><BookOpen className="w-4 h-4" /></div>
            <span className="text-sm font-medium">Read: Section 4.2 - CNNs</span>
          </div>
          <ArrowRight className="w-4 h-4 opacity-70" />
        </button>

        <button className="w-full bg-white/10 hover:bg-white/20 p-3 rounded-lg text-left flex items-center justify-between transition backdrop-blur-sm border border-white/10">
          <div className="flex items-center gap-3">
            <div className="bg-white/20 p-2 rounded-full"><Video className="w-4 h-4" /></div>
            <span className="text-sm font-medium">Watch: Backprop Explained</span>
          </div>
          <ArrowRight className="w-4 h-4 opacity-70" />
        </button>
      </div>
    </div>
  );
}
