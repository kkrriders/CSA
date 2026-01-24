"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Check, Calendar, Clock, Target, Book } from 'lucide-react';

export default function CreateStudyPlanPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);

  // Mock form state
  const [formData, setFormData] = useState({
    name: '',
    examDate: '',
    hoursPerWeek: 10,
    focusTopics: [] as string[],
    difficulty: 'balanced'
  });

  const handleCreate = async () => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      setLoading(false);
      router.push('/study-plan');
    }, 1500);
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-3xl">
      <button 
        onClick={() => router.back()}
        className="flex items-center gap-2 text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white mb-6 transition"
      >
        <ArrowLeft className="w-4 h-4" /> Back
      </button>

      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden border border-gray-100 dark:border-gray-700">
        {/* Progress Bar */}
        <div className="bg-gray-100 dark:bg-gray-700 h-2">
          <div 
            className="bg-blue-600 h-full transition-all duration-500" 
            style={{ width: `${(step / 3) * 100}%` }}
          ></div>
        </div>

        <div className="p-8">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Create New Study Plan</h1>
          <p className="text-gray-500 dark:text-gray-400 mb-8">Let AI design a personalized schedule for you.</p>

          {step === 1 && (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-8 duration-300">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Plan Name</label>
                <input 
                  type="text" 
                  className="w-full p-3 border rounded-lg bg-gray-50 dark:bg-gray-900 border-gray-200 dark:border-gray-700 focus:ring-2 focus:ring-blue-500 outline-none transition"
                  placeholder="e.g. Midterm Prep"
                  value={formData.name}
                  onChange={e => setFormData({...formData, name: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Exam Date (Optional)</label>
                <input 
                  type="date" 
                  className="w-full p-3 border rounded-lg bg-gray-50 dark:bg-gray-900 border-gray-200 dark:border-gray-700 focus:ring-2 focus:ring-blue-500 outline-none transition dark:text-white"
                  value={formData.examDate}
                  onChange={e => setFormData({...formData, examDate: e.target.value})}
                />
              </div>
              <button 
                onClick={() => setStep(2)}
                className="w-full bg-blue-600 text-white py-3 rounded-lg font-bold hover:bg-blue-700 transition"
              >
                Next: Set Goals
              </button>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-8 duration-300">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Weekly Commitment: {formData.hoursPerWeek} hours
                </label>
                <input 
                  type="range" 
                  min="2" max="40" step="1"
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                  value={formData.hoursPerWeek}
                  onChange={e => setFormData({...formData, hoursPerWeek: parseInt(e.target.value)})}
                />
                <div className="flex justify-between text-xs text-gray-400 mt-1">
                  <span>Casual (2h)</span>
                  <span>Intense (40h)</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Pacing Preference</label>
                <div className="grid grid-cols-3 gap-4">
                  {['Relaxed', 'Balanced', 'Intensive'].map((opt) => (
                    <button
                      key={opt}
                      onClick={() => setFormData({...formData, difficulty: opt.toLowerCase()})}
                      className={`p-4 rounded-lg border text-center transition ${
                        formData.difficulty === opt.toLowerCase()
                          ? 'border-blue-600 bg-blue-50 dark:bg-blue-900/20 text-blue-600 font-bold'
                          : 'border-gray-200 dark:border-gray-700 hover:border-blue-300 text-gray-600 dark:text-gray-400'
                      }`}
                    >
                      {opt}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex gap-4">
                <button 
                  onClick={() => setStep(1)}
                  className="w-1/3 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 py-3 rounded-lg font-bold hover:bg-gray-200 dark:hover:bg-gray-600 transition"
                >
                  Back
                </button>
                <button 
                  onClick={() => setStep(3)}
                  className="w-2/3 bg-blue-600 text-white py-3 rounded-lg font-bold hover:bg-blue-700 transition"
                >
                  Next: Topics
                </button>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-8 duration-300">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-4">Select Focus Areas</label>
                <div className="grid grid-cols-2 gap-3">
                  {['Computer Vision', 'NLP', 'Reinforcement Learning', 'Optimization', 'Ethics', 'Robotics'].map((topic) => (
                    <label 
                      key={topic}
                      className={`flex items-center p-3 rounded-lg border cursor-pointer transition ${
                        formData.focusTopics.includes(topic)
                          ? 'border-blue-600 bg-blue-50 dark:bg-blue-900/20'
                          : 'border-gray-200 dark:border-gray-700 hover:border-blue-300'
                      }`}
                    >
                      <input 
                        type="checkbox"
                        className="rounded text-blue-600 focus:ring-blue-500"
                        checked={formData.focusTopics.includes(topic)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setFormData(prev => ({...prev, focusTopics: [...prev.focusTopics, topic]}));
                          } else {
                            setFormData(prev => ({...prev, focusTopics: prev.focusTopics.filter(t => t !== topic)}));
                          }
                        }}
                      />
                      <span className="ml-2 text-gray-700 dark:text-gray-300">{topic}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-100 dark:border-yellow-900/40 p-4 rounded-lg">
                <h4 className="font-bold text-yellow-800 dark:text-yellow-200 text-sm mb-1 flex items-center gap-2">
                  <Target className="w-4 h-4" /> AI Projection
                </h4>
                <p className="text-xs text-yellow-700 dark:text-yellow-300">
                  Based on your pace, you should achieve mastery in selected topics by <strong>March 15th, 2026</strong>.
                </p>
              </div>

              <div className="flex gap-4">
                <button 
                  onClick={() => setStep(2)}
                  className="w-1/3 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 py-3 rounded-lg font-bold hover:bg-gray-200 dark:hover:bg-gray-600 transition"
                >
                  Back
                </button>
                <button 
                  onClick={handleCreate}
                  disabled={loading}
                  className="w-2/3 bg-green-600 text-white py-3 rounded-lg font-bold hover:bg-green-700 transition flex items-center justify-center gap-2"
                >
                  {loading ? 'Generating...' : 'Create Plan'}
                  {!loading && <Check className="w-5 h-5" />}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
