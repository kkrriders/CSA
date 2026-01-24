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
  const [config, setConfig] = useState({
    num_questions: 10,
    time_per_question: 90,
    topics: [] as string[],
    difficulty_levels: [] as DifficultyLevel[],
    question_types: ['mcq', 'short_answer'] as QuestionType[],
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
      const doc = await api.getDocument(documentId!);
      setDocument(doc);
    } catch (error) {
      toast.error('Failed to load document');
      router.push('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const handleStartTest = async () => {
    setLoading(true);
    const loadingToast = toast.loading('Generating questions...');

    try {
      // Generate questions
      await api.generateQuestions({
        document_id: documentId!,
        num_questions: config.num_questions,
        question_types: config.question_types,
      });

      // Wait for questions to be generated (poll every 3 seconds, max 60 seconds)
      let questionsReady = false;
      let attempts = 0;
      const maxAttempts = 20;

      // Initial wait to let generation start
      await new Promise(resolve => setTimeout(resolve, 3000));

      while (!questionsReady && attempts < maxAttempts) {
        try {
          const questions = await api.getQuestionsForDocument(documentId!);
          console.log(`Polling: ${questions.length}/${config.num_questions} questions ready`);

          if (questions.length >= config.num_questions) {
            questionsReady = true;
            toast.success('Questions generated!', { id: loadingToast });
          } else {
            toast.loading(`Generating questions... ${questions.length}/${config.num_questions}`, { id: loadingToast });
            await new Promise(resolve => setTimeout(resolve, 3000)); // Wait 3 seconds before next check
          }
        } catch (error) {
          console.error('Error checking questions:', error);
          await new Promise(resolve => setTimeout(resolve, 3000));
        }

        attempts++;
      }

      if (!questionsReady) {
        toast.error('Question generation timed out. Please refresh and try again.', { id: loadingToast });
        setLoading(false);
        return;
      }

      // Start test session
      toast.loading('Starting test...', { id: loadingToast });
      const session = await api.startTest(documentId!, {
        total_questions: config.num_questions,
        time_per_question: config.time_per_question,
        topics: config.topics.length > 0 ? config.topics : undefined,
        difficulty_levels: config.difficulty_levels.length > 0 ? config.difficulty_levels : undefined,
      });

      toast.success('Test started!', { id: loadingToast });
      router.push(`/test/${session._id}`);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to start test', { id: loadingToast });
    } finally {
      setLoading(false);
    }
  };

  if (loading || !document) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-2">
            <Brain className="w-8 h-8 text-blue-600" />
            <span className="text-2xl font-bold">Configure Test</span>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-2xl">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <div className="mb-6">
            <h1 className="text-2xl font-bold mb-2">{document.title}</h1>
            <p className="text-gray-600">{document.sections.length} sections, {document.metadata.word_count} words</p>
          </div>

          {/* Number of Questions */}
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">Number of Questions</label>
            <input
              type="number"
              min="5"
              max="100"
              value={config.num_questions}
              onChange={(e) => setConfig({ ...config, num_questions: parseInt(e.target.value) })}
              className="w-full px-4 py-2 border rounded-lg"
            />
          </div>

          {/* Time per Question */}
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">Time per Question (seconds)</label>
            <input
              type="number"
              min="30"
              max="300"
              value={config.time_per_question}
              onChange={(e) => setConfig({ ...config, time_per_question: parseInt(e.target.value) })}
              className="w-full px-4 py-2 border rounded-lg"
            />
          </div>

          {/* Topics (optional) */}
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">Topics (Optional)</label>
            <div className="flex flex-wrap gap-2">
              {document.metadata.detected_topics.slice(0, 10).map((topic) => (
                <button
                  key={topic}
                  onClick={() => {
                    if (config.topics.includes(topic)) {
                      setConfig({ ...config, topics: config.topics.filter(t => t !== topic) });
                    } else {
                      setConfig({ ...config, topics: [...config.topics, topic] });
                    }
                  }}
                  className={`px-3 py-1 rounded-full text-sm ${
                    config.topics.includes(topic)
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  {topic}
                </button>
              ))}
            </div>
          </div>

          {/* Start Button */}
          <button
            onClick={handleStartTest}
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition disabled:opacity-50"
          >
            {loading ? 'Starting Test...' : 'Start Test'}
          </button>
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