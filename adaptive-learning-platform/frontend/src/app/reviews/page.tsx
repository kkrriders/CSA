"use client";

import React from 'react';
import { useRouter } from 'next/navigation';
import { Repeat, Calendar, BarChart } from 'lucide-react';
import ReviewQueue from '@/components/reviews/ReviewQueue';
import ReviewCalendar from '@/components/reviews/ReviewCalendar';

export default function ReviewsPage() {
  const router = useRouter();

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
            <Repeat className="w-8 h-8 text-blue-600" />
            Spaced Repetition
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Review cards at the optimal time to maximize retention.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Review Queue */}
        <div className="lg:col-span-2 space-y-8">
          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Due for Review</h2>
            <ReviewQueue />
          </div>

          <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl p-6 text-white shadow-lg">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-2xl font-bold mb-2">Daily Streak: 12 Days! 🔥</h3>
                <p className="text-indigo-100 max-w-md">
                  Consistency is key. You've reviewed 85% of your scheduled cards this week.
                </p>
              </div>
              <div className="text-4xl font-black opacity-20">12</div>
            </div>
          </div>
        </div>

        {/* Sidebar: Calendar & Stats */}
        <div className="space-y-8">
          <ReviewCalendar />
          
          <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm">
            <h3 className="font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <BarChart className="w-5 h-5 text-gray-400" />
              Retention Stats
            </h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600 dark:text-gray-400">Total Cards</span>
                <span className="font-bold text-gray-900 dark:text-white">1,240</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600 dark:text-gray-400">Mature Cards (>21 days)</span>
                <span className="font-bold text-green-600 dark:text-green-400">850 (68%)</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600 dark:text-gray-400">Young Cards</span>
                <span className="font-bold text-blue-600 dark:text-blue-400">390 (32%)</span>
              </div>
              <div className="h-px bg-gray-100 dark:bg-gray-700 my-2"></div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600 dark:text-gray-400">Accuracy (Last 7d)</span>
                <span className="font-bold text-gray-900 dark:text-white">94.2%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
