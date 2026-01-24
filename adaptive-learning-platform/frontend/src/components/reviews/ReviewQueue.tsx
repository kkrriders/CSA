"use client";

import React from 'react';
import { Play, Clock, Layers } from 'lucide-react';

interface ReviewDeck {
  id: string;
  name: string;
  dueCount: number;
  estimatedTime: number; // minutes
  nextReview: string;
}

export default function ReviewQueue() {
  // Mock data
  const decks: ReviewDeck[] = [
    { id: '1', name: 'Computer Vision Basics', dueCount: 15, estimatedTime: 10, nextReview: 'Now' },
    { id: '2', name: 'Transformer Architectures', dueCount: 8, estimatedTime: 5, nextReview: 'Now' },
    { id: '3', name: 'Reinforcement Learning', dueCount: 42, estimatedTime: 25, nextReview: '2 hours' },
  ];

  return (
    <div className="space-y-4">
      {decks.map((deck) => (
        <div key={deck.id} className="bg-white dark:bg-gray-800 p-4 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm flex items-center justify-between hover:shadow-md transition">
          <div className="flex items-center gap-4">
            <div className="bg-blue-100 dark:bg-blue-900/30 p-3 rounded-lg text-blue-600 dark:text-blue-400">
              <Layers className="w-6 h-6" />
            </div>
            <div>
              <h4 className="font-bold text-gray-900 dark:text-white">{deck.name}</h4>
              <div className="flex gap-4 text-xs text-gray-500 dark:text-gray-400 mt-1">
                <span className="flex items-center gap-1">
                  <span className="font-bold text-red-500">{deck.dueCount}</span> due
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3" /> {deck.estimatedTime}m
                </span>
              </div>
            </div>
          </div>
          
          <button className="bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700 transition shadow-lg hover:shadow-blue-500/25">
            <Play className="w-5 h-5 fill-current" />
          </button>
        </div>
      ))}
      
      {decks.length === 0 && (
        <div className="text-center py-12 text-gray-500 dark:text-gray-400">
          <p>No reviews due right now. Great job!</p>
        </div>
      )}
    </div>
  );
}
