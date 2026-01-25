"use client";

import React from 'react';
import { Target, BookOpen, Info } from 'lucide-react';
import type { AdaptiveTargeting } from '@/types';

interface RecommendationsCardProps {
  adaptive: AdaptiveTargeting | null;
}

export default function RecommendationsCard({ adaptive }: RecommendationsCardProps) {
  // If no adaptive data, show info message
  if (!adaptive || !adaptive.weak_topics || adaptive.weak_topics.length === 0) {
    return (
      <div className="bg-gradient-to-r from-gray-600 to-gray-700 rounded-xl p-6 text-white shadow-lg">
        <h3 className="font-bold text-lg mb-2">Recommended Next Steps</h3>
        <div className="flex items-start gap-3 text-sm text-gray-200">
          <Info className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <p>Complete more questions to get personalized recommendations.</p>
        </div>
      </div>
    );
  }

  const topWeakTopic = adaptive.weak_topics[0];
  const recommendedDifficulty = adaptive.recommended_difficulty[0] || 'medium';

  return (
    <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-xl p-6 text-white shadow-lg">
      <h3 className="font-bold text-lg mb-2">Recommended Next Steps</h3>
      <p className="text-blue-100 text-sm mb-4">
        Based on your performance, we recommend focusing on <strong>{topWeakTopic}</strong>.
      </p>

      <div className="space-y-3">
        <div className="bg-white/10 p-4 rounded-lg backdrop-blur-sm border border-white/10">
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-white/20 p-2 rounded-full">
              <Target className="w-4 h-4" />
            </div>
            <span className="text-sm font-bold">Your Focus Areas</span>
          </div>
          <div className="flex flex-wrap gap-2 mt-3">
            {adaptive.weak_topics.slice(0, 3).map((topic, idx) => (
              <span
                key={idx}
                className="bg-white/20 px-3 py-1 rounded-full text-xs font-medium"
              >
                {topic}
              </span>
            ))}
          </div>
        </div>

        <div className="bg-white/10 p-4 rounded-lg backdrop-blur-sm border border-white/10">
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-white/20 p-2 rounded-full">
              <BookOpen className="w-4 h-4" />
            </div>
            <span className="text-sm font-bold">Practice Recommendation</span>
          </div>
          <p className="text-xs text-blue-100 mt-2">
            Take {adaptive.estimated_questions_needed} more questions at <span className="font-semibold">{recommendedDifficulty}</span> difficulty on these topics.
          </p>
        </div>
      </div>
    </div>
  );
}
