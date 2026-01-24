'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { ChevronRight, Flag, Loader2, Keyboard } from 'lucide-react';
import toast from 'react-hot-toast';
import { api } from '@/lib/api';
import type { Question, QuestionAnswer } from '@/types';
import Timer from '@/components/Timer';
import QuestionCard from '@/components/QuestionCard';

// Since we don't have a specific ReviewSession type exported yet, we'll infer it or use any
interface ReviewSession {
  _id: string;
  total_reviews: number;
  completed_reviews: number;
  reviews: any[]; // Full review objects with embedded questions
}

export default function ReviewSessionPage({ params }: { params: { sessionId: string } }) {
  const router = useRouter();
  const { sessionId } = params;

  const [session, setSession] = useState<ReviewSession | null>(null);
  const [currentReviewIndex, setCurrentReviewIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  
  // State for the current question
  const [currentAnswer, setCurrentAnswer] = useState<string>('');
  const [markedReview, setMarkedReview] = useState(false);
  const [confidence, setConfidence] = useState<number>(50);
  const [startTime, setStartTime] = useState<number>(Date.now());
  const [timeRemaining, setTimeRemaining] = useState<number>(120); // 2 mins per review default

  // Load session
  useEffect(() => {
    loadSession();
  }, [sessionId]);

  const loadSession = async () => {
    try {
      setLoading(true);
      const sess = await api.getReviewSession(sessionId);
      setSession(sess);
      
      // Find first uncompleted review if needed, or just start from 0/completed count
      // For now, let's assume we serve them in order of the array
      // But we need to track local progress index if the API returns all reviews
      setCurrentReviewIndex(sess.completed_reviews || 0);
      setStartTime(Date.now());
    } catch (error) {
      toast.error('Failed to load review session');
      router.push('/reviews');
    } finally {
      setLoading(false);
    }
  };

  const currentReview = session?.reviews[currentReviewIndex];
  const currentQuestion: Question | null = currentReview ? currentReview.question : null;

  const handleSubmitAnswer = useCallback(async () => {
    if (!currentQuestion || !session || submitting) return;

    setSubmitting(true);
    const timeTaken = Math.floor((Date.now() - startTime) / 1000);

    try {
      // Review submission uses 'quality' (0-5) usually, but our API might expect just answer/correctness
      // The API definition: submitReviewResponse(sessionId, reviewId, quality, timeTaken)
      // We need to determine quality. Simple heuristic:
      // Correct + Fast = 5
      // Correct + Slow = 4
      // Wrong = 1
      // For now, we need to check correctness client-side if we want to send quality immediately, 
      // OR the backend handles it.
      // Wait, the API `submitReviewResponse` takes `quality`. 
      // Standard SRS apps ask user "How easy was this?". 
      // Our `QuestionCard` has a confidence slider. We can use that + correctness.
      // But we first need to know if it's correct. 
      // If it's MCQ, we can check against `currentQuestion.options`.
      // If it's subjective, we might need self-grading.
      
      // Let's assume the backend will grade it if we send the answer? 
      // Actually `submitReviewResponse` in `api.ts` takes `quality`.
      // This implies we should show the answer, let user grade themselves, THEN submit.
      // Or we change the flow: Submit Answer -> Backend Grades -> Show Result -> User confirms quality -> Next.
      
      // For this implementation, let's simplify:
      // We will map Confidence directly to Quality for now, assuming the user is 'grading' their confidence.
      // A better flow would be: Submit -> Show Correct Answer -> User rates difficulty -> Next.
      // Let's stick to the current API signature. We'll map confidence 0-100 to 0-5.
      
      const derivedQuality = Math.round((confidence / 100) * 5);

      await api.submitReviewResponse(
        sessionId,
        currentReview._id, // This is the REVIEW ID, not question ID
        derivedQuality,
        timeTaken
      );

      // Move to next
      const nextIndex = currentReviewIndex + 1;
      if (nextIndex >= session.reviews.length) {
        // Finish
        await api.completeReviewSession(sessionId);
        toast.success("Review session completed!");
        router.push('/reviews');
      } else {
        setCurrentReviewIndex(nextIndex);
        setCurrentAnswer('');
        setMarkedReview(false);
        setConfidence(50);
        setStartTime(Date.now());
      }

    } catch (error) {
      console.error(error);
      toast.error('Failed to submit review');
    } finally {
      setSubmitting(false);
    }
  }, [currentQuestion, session, currentReviewIndex, submitting, startTime, sessionId, currentReview, confidence, router]);

  const handleTimeUp = useCallback(() => {
    toast('Time is up!', { icon: '⏰' });
    // Optional: Auto-submit or just warn
  }, []);

  // Keyboard Shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (submitting || !currentQuestion) return;

      if (currentQuestion.question_type === 'mcq' && currentQuestion.options) {
        if (['1', '2', '3', '4'].includes(e.key)) {
          const index = parseInt(e.key) - 1;
          if (index < currentQuestion.options.length) {
            setCurrentAnswer(currentQuestion.options[index].text);
          }
        }
      }

      if (e.key === 'Enter' && !e.shiftKey) {
        handleSubmitAnswer();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentQuestion, submitting, handleSubmitAnswer]);

  if (loading || !session) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 transition-colors">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-600 dark:text-blue-400 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading review session...</p>
        </div>
      </div>
    );
  }

  if (!currentQuestion) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 transition-colors">
        <div className="text-center">
          <p className="text-gray-600 dark:text-gray-400">No questions found in this review.</p>
          <button onClick={() => router.push('/reviews')} className="mt-4 text-blue-600 hover:underline">Return to Dashboard</button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      <header className="bg-white dark:bg-gray-800 border-b dark:border-gray-700 sticky top-0 z-10 transition-colors duration-200">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <h1 className="font-bold text-xl dark:text-white">Review Session</h1>
            <span className="px-3 py-1 bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300 rounded-full text-sm font-medium">
              Card {currentReviewIndex + 1} of {session.reviews.length}
            </span>
          </div>
          <Timer seconds={timeRemaining} onTimeUp={handleTimeUp} />
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <QuestionCard
          question={currentQuestion}
          userAnswer={currentAnswer}
          onAnswerChange={setCurrentAnswer}
          onMarkReview={() => setMarkedReview(!markedReview)}
          isMarkedReview={markedReview}
          questionNumber={currentReviewIndex + 1}
          confidence={confidence}
          onConfidenceChange={setConfidence}
        />

        <div className="mt-8 flex justify-between items-center">
          <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
            <Keyboard className="w-4 h-4" />
            <span className="hidden sm:inline">Shortcuts enabled</span>
          </div>
          <button
            onClick={handleSubmitAnswer}
            disabled={submitting}
            className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition flex items-center gap-2 disabled:opacity-50"
          >
            {submitting ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              'Submit Review'
            )}
            {!submitting && <ChevronRight className="w-5 h-5" />}
          </button>
        </div>
      </div>
    </div>
  );
}
