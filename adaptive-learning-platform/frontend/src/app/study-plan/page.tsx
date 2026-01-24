"use client";

import React from 'react';
import { useRouter } from 'next/navigation';
import { Plus, BookOpen, Calendar as CalendarIcon } from 'lucide-react';
import RecommendedSession from '@/components/study-plan/RecommendedSession';
import SessionCard from '@/components/study-plan/SessionCard';
import GoalProgress from '@/components/study-plan/GoalProgress';
import StudyCalendar from '@/components/study-plan/StudyCalendar';

export default function StudyPlanPage() {
  const router = useRouter();

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">My Study Plan</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Stay on track with your learning goals</p>
        </div>
        <button
          onClick={() => router.push('/study-plan/create')}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-blue-700 transition flex items-center gap-2 shadow-lg hover:shadow-xl"
        >
          <Plus className="w-5 h-5" />
          Create New Plan
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
        {/* Left Column: Recommendations & Today's Tasks */}
        <div className="lg:col-span-2 space-y-8">
          <RecommendedSession 
            topic="Neural Networks - Backpropagation"
            reason="You struggled with this topic in the last quiz. A quick review will boost your retention."
            duration={15}
            difficulty="medium"
            onStart={() => router.push('/test/configure')}
          />

          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-blue-600" />
              Today's Sessions
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <SessionCard 
                title="Chapter 4: CNN Architectures"
                topic="Computer Vision"
                durationMins={45}
                status="upcoming"
                date="Today, 2:00 PM"
              />
              <SessionCard 
                title="Review: Optimization Algorithms"
                topic="Deep Learning"
                durationMins={20}
                status="completed"
                date="Today, 10:00 AM"
              />
            </div>
          </div>

          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <CalendarIcon className="w-5 h-5 text-purple-600" />
              Upcoming This Week
            </h2>
            <div className="space-y-4">
              <SessionCard 
                title="Mock Exam: Midterm Prep"
                topic="General"
                durationMins={90}
                status="upcoming"
                date="Tomorrow, 4:00 PM"
              />
              <SessionCard 
                title="Reading: Transformers Paper"
                topic="NLP"
                durationMins={60}
                status="upcoming"
                date="Wed, Feb 26"
              />
            </div>
          </div>
        </div>

        {/* Right Column: Calendar & Goals */}
        <div className="space-y-8">
          <StudyCalendar />
          
          <div>
            <h3 className="font-bold text-gray-900 dark:text-white mb-4">Active Goals</h3>
            <div className="space-y-4">
              <GoalProgress 
                goalName="Master CNNs"
                current={12}
                target={20}
                unit="concepts"
              />
              <GoalProgress 
                goalName="Weekly Practice"
                current={350}
                target={500}
                unit="questions"
              />
              <GoalProgress 
                goalName="Study Hours"
                current={8.5}
                target={15}
                unit="hours"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
