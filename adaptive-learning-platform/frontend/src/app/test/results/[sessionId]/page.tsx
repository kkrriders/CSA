'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { 
  CheckCircle, XCircle, Clock, AlertTriangle, 
  ArrowLeft, Brain, Target, BookOpen, Loader2,
  ChevronDown, ChevronUp
} from 'lucide-react';
import { api } from '@/lib/api';
import type { 
  TestResult, TopicMastery, WeaknessAnalysis, 
  AdaptiveTargeting, AIExplanation 
} from '@/types';
import toast from 'react-hot-toast';

export default function TestResultsPage({ params }: { params: { sessionId: string } }) {
  const router = useRouter();
  const { sessionId } = params;
  
  const [results, setResults] = useState<TestResult | null>(null);
  const [mastery, setMastery] = useState<TopicMastery[]>([]);
  const [weakness, setWeakness] = useState<WeaknessAnalysis[]>([]);
  const [adaptive, setAdaptive] = useState<AdaptiveTargeting | null>(null);
  const [loading, setLoading] = useState(true);
  
  const [explanations, setExplanations] = useState<Record<string, AIExplanation>>({});
  const [explainingId, setExplainingId] = useState<string | null>(null);
  const [expandedQuestion, setExpandedQuestion] = useState<string | null>(null);

  useEffect(() => {
    const loadResults = async () => {
      try {
        const [resData, masteryData, weaknessData, adaptiveData] = await Promise.all([
          api.getTestResults(sessionId),
          api.getTopicMastery(sessionId),
          api.getWeaknessMap(sessionId),
          api.getAdaptiveTargeting(sessionId).catch(() => null)
        ]);
        
        setResults(resData);
        setMastery(masteryData.topic_mastery);
        setWeakness(weaknessData.weakness_areas);
        setAdaptive(adaptiveData);
      } catch (error) {
        toast.error('Failed to load results');
      } finally {
        setLoading(false);
      }
    };

    loadResults();
  }, [sessionId]);

  const handleExplain = async (questionId: string) => {
    if (explanations[questionId]) {
      setExpandedQuestion(expandedQuestion === questionId ? null : questionId);
      return;
    }

    setExplainingId(questionId);
    try {
      const explanation = await api.explainWrongAnswer(sessionId, questionId);
      setExplanations(prev => ({ ...prev, [questionId]: explanation }));
      setExpandedQuestion(questionId);
    } catch (error) {
      toast.error('Failed to get AI explanation');
    } finally {
      setExplainingId(null);
    }
  };

  if (loading || !results) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Analyzing your performance...</p>
        </div>
      </div>
    );
  }

  const { score } = results;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-5xl">
        <div className="mb-8 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => router.push('/dashboard')}
              className="p-2 hover:bg-white rounded-full transition shadow-sm"
            >
              <ArrowLeft className="w-6 h-6 text-gray-600" />
            </button>
            <h1 className="text-3xl font-bold text-gray-900">Performance Report</h1>
          </div>
          <button
            onClick={() => router.push('/dashboard')}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 transition"
          >
            Back to Dashboard
          </button>
        </div>

        {/* Score Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8 border border-gray-100">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div className="p-4 rounded-xl bg-blue-50 border border-blue-100">
              <div className="text-4xl font-black text-blue-600 mb-2">{score.percentage.toFixed(0)}%</div>
              <div className="text-sm font-medium text-blue-800 uppercase tracking-wider">Score</div>
            </div>
            <div className="p-4 rounded-xl bg-green-50 border border-green-100">
              <div className="text-4xl font-black text-green-600 mb-2">{score.correct}/{score.total_questions}</div>
              <div className="text-sm font-medium text-green-800 uppercase tracking-wider">Correct</div>
            </div>
            <div className="p-4 rounded-xl bg-red-50 border border-red-100">
              <div className="text-4xl font-black text-red-600 mb-2">{score.wrong}</div>
              <div className="text-sm font-medium text-red-800 uppercase tracking-wider">Wrong</div>
            </div>
            <div className="p-4 rounded-xl bg-gray-50 border border-gray-100">
              <div className="text-4xl font-black text-gray-600 mb-2">{Math.floor(score.time_spent / 60)}m</div>
              <div className="text-sm font-medium text-gray-800 uppercase tracking-wider">Duration</div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          {/* Topic Mastery */}
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <div className="flex items-center gap-2 mb-6">
              <Brain className="w-6 h-6 text-purple-600" />
              <h2 className="text-xl font-bold">Cognitive Profile</h2>
            </div>
            <div className="space-y-6">
              {mastery.map((topic) => (
                <div key={topic.topic}>
                  <div className="flex justify-between mb-2">
                    <span className="font-semibold text-gray-700">{topic.topic}</span>
                    <span className="text-sm font-bold text-gray-500">{topic.mastery_percentage.toFixed(0)}%</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-3">
                    <div 
                      className={`h-3 rounded-full transition-all duration-1000 ${
                        topic.mastery_percentage > 75 ? 'bg-green-500' : 
                        topic.mastery_percentage > 45 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${topic.mastery_percentage}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Adaptive Targeting */}
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <div className="flex items-center gap-2 mb-6">
              <Target className="w-6 h-6 text-red-600" />
              <h2 className="text-xl font-bold">Next Steps</h2>
            </div>
            {adaptive ? (
              <div className="space-y-4">
                <div className="p-4 bg-blue-50 rounded-xl border border-blue-100">
                  <h3 className="font-bold text-blue-900 mb-2 flex items-center gap-2">
                    <BookOpen className="w-4 h-4" />
                    Recommended Focus
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {adaptive.weak_topics.map(topic => (
                      <span key={topic} className="bg-white px-3 py-1 rounded-full text-sm font-medium text-blue-700 border border-blue-200">
                        {topic}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-gray-50 rounded-lg text-center">
                    <div className="text-xs text-gray-500 uppercase font-bold mb-1">Target Difficulty</div>
                    <div className="font-bold text-gray-800 capitalize">{adaptive.recommended_difficulty[0]}</div>
                  </div>
                  <div className="p-3 bg-gray-50 rounded-lg text-center">
                    <div className="text-xs text-gray-500 uppercase font-bold mb-1">Est. Questions</div>
                    <div className="font-bold text-gray-800">{adaptive.estimated_questions_needed}</div>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-gray-500 italic">Complete more tests to unlock adaptive recommendations.</p>
            )}
          </div>
        </div>

        {/* Question Review */}
        <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
          <h2 className="text-2xl font-bold mb-8">Detailed Review</h2>
          <div className="space-y-6">
            {results.answers.map((answer, idx) => (
              <div key={idx} className={`rounded-xl overflow-hidden border ${
                answer.status === 'correct' ? 'border-green-100' : 'border-red-100'
              }`}>
                <div 
                  className={`p-4 flex justify-between items-center cursor-pointer transition ${
                    answer.status === 'correct' ? 'bg-green-50' : 'bg-red-50'
                  }`}
                  onClick={() => answer.status !== 'correct' && handleExplain(answer.question_id)}
                >
                  <div className="flex items-center gap-4">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                      answer.status === 'correct' ? 'bg-green-200 text-green-700' : 'bg-red-200 text-red-700'
                    }`}>
                      {idx + 1}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        {answer.status === 'correct' ? (
                          <CheckCircle className="w-4 h-4 text-green-600" />
                        ) : (
                          <XCircle className="w-4 h-4 text-red-600" />
                        )}
                        <span className="font-bold text-gray-800">
                          {answer.status === 'correct' ? 'Correct' : 'Incorrect'}
                        </span>
                        {answer.marked_review && (
                          <span className="bg-yellow-200 text-yellow-800 text-[10px] px-2 py-0.5 rounded uppercase font-bold">
                            Marked
                          </span>
                        )}
                      </div>
                      <div className="text-sm text-gray-500">
                        Response time: {answer.time_taken.toFixed(1)}s
                      </div>
                    </div>
                  </div>
                  
                  {answer.status !== 'correct' && (
                    <div className="flex items-center gap-2 text-blue-600 font-semibold text-sm">
                      {explainingId === answer.question_id ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <>
                          {expandedQuestion === answer.question_id ? 'Hide Explanation' : 'Ask AI Why'}
                          {expandedQuestion === answer.question_id ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                        </>
                      )}
                    </div>
                  )}
                </div>

                {expandedQuestion === answer.question_id && explanations[answer.question_id] && (
                  <div className="p-6 bg-white border-t border-red-50">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-4">
                        <div>
                          <h4 className="text-xs font-bold text-gray-400 uppercase mb-1">Your Answer</h4>
                          <div className="p-3 bg-red-50 text-red-700 rounded-lg font-medium border border-red-100">
                            {answer.user_answer || 'Skipped'}
                          </div>
                        </div>
                        <div>
                          <h4 className="text-xs font-bold text-gray-400 uppercase mb-1">Correct Answer</h4>
                          <div className="p-3 bg-green-50 text-green-700 rounded-lg font-medium border border-green-100">
                            {explanations[answer.question_id].correct_answer}
                          </div>
                        </div>
                      </div>
                      <div className="space-y-4">
                        <div className="p-4 bg-blue-50 rounded-xl border border-blue-100">
                          <h4 className="font-bold text-blue-900 mb-2 flex items-center gap-2">
                            <Brain className="w-4 h-4" />
                            AI Insight
                          </h4>
                          <p className="text-sm text-blue-800 leading-relaxed">
                            {explanations[answer.question_id].why_wrong}
                          </p>
                          <div className="mt-3 pt-3 border-t border-blue-200">
                            <h5 className="text-xs font-bold text-blue-900 mb-1">Concept Guide:</h5>
                            <p className="text-xs text-blue-700 italic">
                              {explanations[answer.question_id].concept_explanation}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}