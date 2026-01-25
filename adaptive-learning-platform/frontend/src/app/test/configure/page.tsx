'use client';

import { useEffect, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Brain, Settings } from 'lucide-react';
import toast from 'react-hot-toast';
import { api } from '@/lib/api';
import type { Document, QuestionType, DifficultyLevel } from '@/types';

function TestConfigureContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const documentId = searchParams.get('documentId');

  const [document, setDocument] = useState<Document | null>(null);
  const [loading, setLoading] = useState(true);
  const [poolStats, setPoolStats] = useState<any>(null);
  const [config, setConfig] = useState({
    num_questions: 10,
    time_per_question: 90,
    topics: [] as string[],
    difficulty_levels: [] as DifficultyLevel[],
    question_types: ['mcq'] as QuestionType[], // Default to MCQ only
  });

  useEffect(() => {
    if (!documentId) {
      router.push('/dashboard');
      return;
    }
    loadDocument();
  }, [documentId]);

  const loadDocument = async () => {
    try {
      const [doc, stats] = await Promise.all([
        api.getDocument(documentId!),
        api.getQuestionPoolStats(documentId!).catch(() => null)
      ]);
      setDocument(doc);
      setPoolStats(stats);
    } catch (error) {
      toast.error('Failed to load document');
      router.push('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const handleStartTest = async () => {
    // Check if enough questions are available
    if (poolStats && typeof poolStats === 'object' && poolStats.available !== undefined) {
      if (poolStats.available < config.num_questions) {
        const needed = config.num_questions - poolStats.available;
        toast.error(`Not enough questions available. You have ${poolStats.available}, need ${config.num_questions}. Generate ${needed} more questions first.`);
        return;
      }
    }

    setLoading(true);
    const loadingToast = toast.loading('Preparing your test...');

    try {
      // Start test session directly (using smart question selection)
      const session = await api.startTest(documentId!, {
        total_questions: config.num_questions,
        time_per_question: config.time_per_question,
        topics: config.topics.length > 0 ? config.topics : undefined,
        difficulty_levels: config.difficulty_levels.length > 0 ? config.difficulty_levels : undefined,
        question_types: config.question_types,
      });

      toast.success('Test started!', { id: loadingToast });
      router.push(`/test/${session._id}`);
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Failed to start test';
      toast.error(errorMsg, { id: loadingToast });

      // Refresh pool stats after error
      if (errorMsg.includes('Not enough questions')) {
        const stats = await api.getQuestionPoolStats(documentId!).catch(() => null);
        setPoolStats(stats);
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading || !document) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
      <header className="bg-white dark:bg-gray-800 border-b dark:border-gray-700">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-2">
            <Brain className="w-8 h-8 text-blue-600 dark:text-blue-400" />
            <span className="text-2xl font-bold dark:text-white">Configure Test</span>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-2xl">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8">
          <div className="mb-6">
            <h1 className="text-2xl font-bold mb-2 dark:text-white">{document.title}</h1>
            <p className="text-gray-600 dark:text-gray-400">{document.sections.length} sections, {document.metadata.word_count} words</p>

            {/* Question Pool Stats */}
            {poolStats && typeof poolStats === 'object' && poolStats.available !== undefined && (
              <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                <div className="flex items-start gap-3">
                  <Settings className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <p className="font-medium text-blue-900 dark:text-blue-200">
                      {poolStats.available || 0} questions available for testing
                    </p>
                    <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
                      {(poolStats.never_answered || 0) > 0 && `${poolStats.never_answered} fresh • `}
                      {(poolStats.needs_practice || 0) > 0 && `${poolStats.needs_practice} need practice • `}
                      {poolStats.mastered || 0} mastered
                    </p>
                    {(poolStats.available || 0) < 10 && (
                      <p className="text-sm text-orange-600 dark:text-orange-400 mt-2">
                        ⚠️ Low question pool. Consider generating more questions for variety.
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Number of Questions */}
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2 dark:text-gray-200">Number of Questions</label>
            <input
              type="number"
              min="5"
              max="100"
              value={config.num_questions}
              onChange={(e) => setConfig({ ...config, num_questions: parseInt(e.target.value) })}
              className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>

          {/* Time per Question */}
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2 dark:text-gray-200">Time per Question (seconds)</label>
            <input
              type="number"
              min="30"
              max="300"
              value={config.time_per_question}
              onChange={(e) => setConfig({ ...config, time_per_question: parseInt(e.target.value) })}
              className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>

          {/* Question Type Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2 dark:text-gray-200">Question Type</label>
            <div className="flex gap-4">
              <button
                type="button"
                onClick={() => setConfig({ ...config, question_types: ['mcq'] })}
                className={`flex-1 px-4 py-3 rounded-lg border-2 font-medium transition ${
                  config.question_types.includes('mcq') && config.question_types.length === 1
                    ? 'border-blue-600 bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300 dark:border-blue-500'
                    : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 dark:hover:border-gray-500'
                }`}
              >
                Multiple Choice (MCQ)
              </button>
              <button
                type="button"
                onClick={() => setConfig({ ...config, question_types: ['short_answer'] })}
                className={`flex-1 px-4 py-3 rounded-lg border-2 font-medium transition ${
                  config.question_types.includes('short_answer') && config.question_types.length === 1
                    ? 'border-blue-600 bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300 dark:border-blue-500'
                    : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 dark:hover:border-gray-500'
                }`}
              >
                Short Answer
              </button>
              <button
                type="button"
                onClick={() => setConfig({ ...config, question_types: ['mcq', 'short_answer'] })}
                className={`flex-1 px-4 py-3 rounded-lg border-2 font-medium transition ${
                  config.question_types.length === 2
                    ? 'border-blue-600 bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300 dark:border-blue-500'
                    : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 dark:hover:border-gray-500'
                }`}
              >
                Mixed
              </button>
            </div>
            <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
              Choose the type of questions you want to practice
            </p>
          </div>

          {/* Topics (optional) */}
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2 dark:text-gray-200">Topics (Optional)</label>
            <div className="flex flex-wrap gap-2">
              {document.metadata.detected_topics.slice(0, 10).map((topic) => (
                <button
                  key={topic}
                  type="button"
                  onClick={() => {
                    if (config.topics.includes(topic)) {
                      setConfig({ ...config, topics: config.topics.filter(t => t !== topic) });
                    } else {
                      setConfig({ ...config, topics: [...config.topics, topic] });
                    }
                  }}
                  className={`px-3 py-1 rounded-full text-sm transition ${
                    config.topics.includes(topic)
                      ? 'bg-blue-600 text-white dark:bg-blue-500'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
                  }`}
                >
                  {topic}
                </button>
              ))}
            </div>
            <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
              Select specific topics or leave empty for all topics
            </p>
          </div>

          {/* Start Button */}
          <button
            onClick={handleStartTest}
            disabled={loading || (poolStats && typeof poolStats === 'object' && poolStats.available !== undefined && poolStats.available < config.num_questions)}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed dark:bg-blue-500 dark:hover:bg-blue-600"
          >
            {loading ? 'Starting Test...' :
             poolStats && typeof poolStats === 'object' && poolStats.available !== undefined && poolStats.available < config.num_questions ?
             `Need ${config.num_questions - poolStats.available} More Questions` :
             'Start Test'}
          </button>

          {poolStats && typeof poolStats === 'object' && poolStats.available !== undefined && poolStats.available < config.num_questions && (
            <p className="mt-3 text-center text-sm text-orange-600 dark:text-orange-400">
              Generate more questions or reduce the number of questions to start the test
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export default function TestConfigurePage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
      <TestConfigureContent />
    </Suspense>
  );
}