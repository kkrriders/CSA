'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { ChevronRight, Flag, Loader2, Keyboard } from 'lucide-react';
import toast from 'react-hot-toast';
import { api } from '@/lib/api';
import type { TestSession, Question, QuestionAnswer } from '@/types';
import Timer from '@/components/Timer';
import ReviewPanel from '@/components/ReviewPanel';
import QuestionCard from '@/components/QuestionCard';

export default function TestSessionPage({ params }: { params: { sessionId: string } }) {
  const router = useRouter();
  const { sessionId } = params;

  const [session, setSession] = useState<TestSession | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  
  // State for the test
  const [answers, setAnswers] = useState<Map<string, QuestionAnswer>>(new Map());
  const [currentAnswer, setCurrentAnswer] = useState<string>('');
  const [markedReview, setMarkedReview] = useState<Set<string>>(new Set());
  const [startTime, setStartTime] = useState<number>(Date.now());
  const [timeRemaining, setTimeRemaining] = useState<number>(90);
  const [endingEarly, setEndingEarly] = useState(false);

  // Telemetry state
  const [hasChangedAnswer, setHasChangedAnswer] = useState(false);
  const [hesitationCount, setHesitationCount] = useState(0);

  // New UI states
  const [confidence, setConfidence] = useState<number>(50);
  const [flagReason, setFlagReason] = useState<string>('Needs Review');

  // Load session and initial question
  useEffect(() => {
    loadSession();
  }, [sessionId]);

  const loadSession = async () => {
    try {
      const sess = await api.getTestSession(sessionId);
      setSession(sess);
      
      if (sess.status === 'completed') {
        router.push(`/test/results/${sessionId}`);
        return;
      }

      await loadQuestion();
    } catch (error) {
      toast.error('Failed to load test session');
      router.push('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const loadQuestion = async () => {
    try {
      setLoading(true);
      const question = await api.getCurrentQuestion(sessionId);
      setCurrentQuestion(question);
      setCurrentAnswer('');
      setConfidence(50);
      setFlagReason('Needs Review');
      setHasChangedAnswer(false);
      setHesitationCount(0);
      setStartTime(Date.now());
      setTimeRemaining(session?.config.time_per_question || 90);
    } catch (error: any) {
      console.error('Failed to load question', error);

      // Check if it's a 400 error (bad test session)
      if (error?.response?.status === 400) {
        const errorMsg = error?.response?.data?.detail || 'Test session is invalid';
        toast.error(errorMsg);
        // If session is invalid, go back to dashboard
        setTimeout(() => router.push('/dashboard'), 1500);
        return;
      }

      // Otherwise try to go to results
      toast.error('Session might have ended');
      router.push(`/test/results/${sessionId}`);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (answer: string) => {
    if (currentAnswer && currentAnswer !== answer) {
      setHasChangedAnswer(true);
    }
    setCurrentAnswer(answer);
  };

  const handleHesitation = () => {
    setHesitationCount(prev => prev + 1);
  };

  const handleSubmitAnswer = useCallback(async () => {
    if (!currentQuestion || !session || submitting) return;

    setSubmitting(true);
    const timeTaken = Math.floor(Math.min(
      (Date.now() - startTime) / 1000,
      session.config.time_per_question
    ));

    try {
      const response = await api.submitAnswer(
        sessionId,
        currentQuestion._id,
        currentAnswer || 'SKIPPED_TIMEOUT',
        timeTaken,
        hasChangedAnswer,
        hesitationCount
      );

      // Update local state for Review Panel
      const newAnswers = new Map(answers);
      newAnswers.set(currentQuestion._id, {
        question_id: currentQuestion._id,
        user_answer: currentAnswer,
        status: response.is_correct ? 'correct' : 'wrong',
        time_taken: timeTaken,
        marked_tricky: flagReason === 'Tricky',
        marked_review: markedReview.has(currentQuestion._id)
      });
      setAnswers(newAnswers);

      if (response.is_test_complete) {
        router.push(`/test/results/${sessionId}`);
      } else {
        // Fetch next question
        const nextSess = await api.getTestSession(sessionId);
        setSession(nextSess);
        await loadQuestion();
      }
    } catch (error) {
      toast.error('Failed to submit answer');
    } finally {
      setSubmitting(false);
    }
  }, [currentQuestion, session, submitting, startTime, sessionId, currentAnswer, answers, markedReview, router, flagReason, confidence, hasChangedAnswer, hesitationCount]);

  const handleMarkReview = () => {
    if (!currentQuestion) return;
    const isCurrentlyMarked = markedReview.has(currentQuestion._id);
    const newMarked = new Set(markedReview);
    
    if (isCurrentlyMarked) {
      newMarked.delete(currentQuestion._id);
    } else {
      newMarked.add(currentQuestion._id);
    }
    setMarkedReview(newMarked);
    
    api.markQuestion(sessionId, currentQuestion._id, false, !isCurrentlyMarked);
  };

  const handleTimeUp = useCallback(async () => {
    if (!submitting) {
      toast('Time is up for this question!', { icon: '⏰' });
      handleSubmitAnswer();
    }
  }, [submitting, handleSubmitAnswer]);

  // Keyboard Shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (submitting || !currentQuestion) return;

      // Number keys 1-4 for MCQ options
      if (currentQuestion.question_type === 'mcq' && currentQuestion.options) {
        if (['1', '2', '3', '4'].includes(e.key)) {
          const index = parseInt(e.key) - 1;
          if (index < currentQuestion.options.length) {
            handleAnswerChange(currentQuestion.options[index].text);
          }
        }
      }

      // Enter to submit
      if (e.key === 'Enter' && !e.shiftKey) {
        handleSubmitAnswer();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentQuestion, submitting, handleSubmitAnswer, currentAnswer]);

  if (loading && !currentQuestion) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 transition-colors">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-600 dark:text-blue-400 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading question...</p>
        </div>
      </div>
    );
  }

  if (endingEarly) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 transition-colors">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-600 dark:text-blue-400 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Ending test and analyzing performance...</p>
        </div>
      </div>
    );
  }

  if (!session || !currentQuestion) return null;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      <header className="bg-white dark:bg-gray-800 border-b dark:border-gray-700 sticky top-0 z-10 transition-colors duration-200">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <h1 className="font-bold text-xl dark:text-white">Test in Progress</h1>
            <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 rounded-full text-sm font-medium">
              Q{session.current_question_index + 1} of {session.config.total_questions}
            </span>
          </div>
          <Timer key={currentQuestion?._id} seconds={timeRemaining} onTimeUp={handleTimeUp} />
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Main Question Area */}
          <div className="lg:col-span-3">
            <QuestionCard
              question={currentQuestion}
              userAnswer={currentAnswer}
              onAnswerChange={handleAnswerChange}
              onMarkReview={handleMarkReview}
              isMarkedReview={markedReview.has(currentQuestion._id)}
              questionNumber={session.current_question_index + 1}
              confidence={confidence}
              onConfidenceChange={setConfidence}
              flagReason={flagReason}
              onFlagReasonChange={setFlagReason}
              onOptionHover={handleHesitation}
            />

            <div className="mt-8 flex justify-between items-center">
              <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                <Keyboard className="w-4 h-4" />
                <span className="hidden sm:inline">Press <kbd className="font-mono bg-gray-100 dark:bg-gray-800 px-1 rounded">1</kbd>-<kbd className="font-mono bg-gray-100 dark:bg-gray-800 px-1 rounded">4</kbd> to select, <kbd className="font-mono bg-gray-100 dark:bg-gray-800 px-1 rounded">Enter</kbd> to submit</span>
              </div>
              <button
                onClick={handleSubmitAnswer}
                disabled={submitting}
                className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition flex items-center gap-2 disabled:opacity-50"
              >
                {submitting ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : session.current_question_index + 1 === session.config.total_questions ? (
                  'Finish Test'
                ) : (
                  'Next Question'
                )}
                {!submitting && <ChevronRight className="w-5 h-5" />}
              </button>
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <ReviewPanel
              totalQuestions={session.config.total_questions}
              currentQuestionIndex={session.current_question_index}
              answers={answers}
              onQuestionSelect={() => toast('Navigation is strictly one-way')}
              onSubmit={async () => {
                if (confirm('Finish test early? Remaining questions will be marked as skipped.')) {
                  setEndingEarly(true);
                  try {
                    await api.finishTestEarly(sessionId);
                    router.push(`/test/results/${sessionId}`);
                  } catch (error) {
                    toast.error('Failed to end test early');
                    setEndingEarly(false);
                  }
                }
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}