"use client";

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Plus, BookOpen, Calendar as CalendarIcon, Loader2 } from 'lucide-react';
import RecommendedSession from '@/components/study-plan/RecommendedSession';
import SessionCard from '@/components/study-plan/SessionCard';
import GoalProgress from '@/components/study-plan/GoalProgress';
import StudyCalendar from '@/components/study-plan/StudyCalendar';
import { api } from '@/lib/api';

export default function StudyPlanPage() {
  const router = useRouter();
  const [activePlan, setActivePlan] = useState<any>(null);
  const [nextSession, setNextSession] = useState<any>(null);
  const [progress, setProgress] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadPlanData() {
      try {
        const plansData = await api.getStudyPlans();
        if (plansData.plans && plansData.plans.length > 0) {
          const plan = plansData.plans[0];
          setActivePlan(plan);

          const [nextSess, prog] = await Promise.all([
            api.getNextStudySession(plan._id).catch(() => null),
            api.getStudyPlanProgress(plan._id).catch(() => null)
          ]);
          setNextSession(nextSess);
          setProgress(prog);
        }
      } catch (error) {
        console.error("Failed to load study plan", error);
      } finally {
        setLoading(false);
      }
    }
    loadPlanData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (!activePlan) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">My Study Plan</h1>
        <div className="bg-white dark:bg-gray-800 p-12 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
          <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">No Active Plan</h2>
          <p className="text-gray-500 dark:text-gray-400 mb-8">Create a personalized study plan to stay on track.</p>
          <button
            onClick={() => router.push('/study-plan/create')}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition flex items-center gap-2 mx-auto shadow-lg"
          >
            <Plus className="w-5 h-5" />
            Create New Plan
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">My Study Plan</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">{activePlan.name}</p>
        </div>
        <button
          onClick={() => router.push('/study-plan/create')}
          className="bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700 px-4 py-2 rounded-lg font-semibold hover:bg-gray-50 dark:hover:bg-gray-700 transition flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          New Plan
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
        {/* Left Column: Recommendations & Today's Tasks */}
        <div className="lg:col-span-2 space-y-8">
          {nextSession && (
            <RecommendedSession 
              topic={nextSession.topic || "General Review"}
              reason={nextSession.reason || "Scheduled session"}
              duration={nextSession.duration || 30}
              difficulty={nextSession.difficulty || "medium"}
              onStart={() => router.push('/test/configure')}
            />
          )}

          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-blue-600" />
              Today's Sessions
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Mock fallback if no schedule data yet */}
              <SessionCard 
                title="Chapter 4: CNN Architectures"
                topic="Computer Vision"
                durationMins={45}
                status="upcoming"
                date="Today, 2:00 PM"
              />
            </div>
          </div>
        </div>

        {/* Right Column: Calendar & Goals */}
        <div className="space-y-8">
          <StudyCalendar sessions={[]} /> {/* Pass real sessions when available */}
          
          <div>
            <h3 className="font-bold text-gray-900 dark:text-white mb-4">Active Goals</h3>
            <div className="space-y-4">
              <GoalProgress 
                goalName="Plan Completion"
                current={progress?.completed_sessions || 0}
                target={activePlan.total_sessions || 20}
                unit="sessions"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
