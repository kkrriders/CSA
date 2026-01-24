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

import TopicMasteryHeatmap from '@/components/analytics/TopicMasteryHeatmap';
import ExamReadinessRadar from '@/components/analytics/ExamReadinessRadar';
import QuestionTimeline from '@/components/results/QuestionTimeline';
import MistakeBreakdown from '@/components/results/MistakeBreakdown';
import ComparisonView from '@/components/results/ComparisonView';
import RecommendationsCard from '@/components/results/RecommendationsCard';

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
    const toastId = toast.loading('Asking AI...');
    try {
      const explanation = await api.explainWrongAnswer(sessionId, questionId);
      setExplanations(prev => ({ ...prev, [questionId]: explanation }));
      setExpandedQuestion(questionId);
      toast.dismiss(toastId);
    } catch (error) {
      toast.error('Failed to get AI explanation', { id: toastId });
    } finally {
      setExplainingId(null);
    }
  };

  if (loading || !results) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 transition-colors">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Analyzing your performance...</p>
        </div>
      </div>
    );
  }

  const { score } = results;

  // Prepare data for analytics charts
  const readinessData = [
    { subject: 'Knowledge', A: mastery.length > 0 ? mastery.reduce((acc, curr) => acc + curr.mastery_percentage, 0) / mastery.length * 1.5 : 0, fullMark: 150 },
    { subject: 'Speed', A: score.time_spent > 0 ? Math.min(150, (score.total_questions / score.time_spent) * 3000) : 0, fullMark: 150 },
    { subject: 'Accuracy', A: score.percentage * 1.5, fullMark: 150 },
    { subject: 'Consistency', A: 0, fullMark: 150 }, // Real metric requires history
    { subject: 'Endurance', A: score.total_questions > 5 ? 100 : 50, fullMark: 150 }, // Simple heuristic
    { subject: 'Recall', A: score.percentage * 1.2, fullMark: 150 },
  ];

  const heatmapData = mastery.map(t => ({ name: t.topic, mastery: t.mastery_percentage }));
  
  const timelineItems = results.answers.map((a, i) => ({
    id: i + 1,
    status: a.status,
    timeTaken: a.time_taken
  }));

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 transition-colors duration-200">
      <div className="container mx-auto px-4 max-w-5xl">
        <div className="mb-8 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => router.push('/dashboard')}
              className="p-2 hover:bg-white dark:hover:bg-gray-800 rounded-full transition shadow-sm text-gray-600 dark:text-gray-400"
            >
              <ArrowLeft className="w-6 h-6" />
            </button>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Performance Report</h1>
          </div>
          <button
            onClick={() => router.push('/dashboard')}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 transition shadow-lg hover:shadow-blue-500/25"
          >
            Back to Dashboard
          </button>
        </div>

        {/* Score Card */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 mb-8 border border-gray-100 dark:border-gray-700">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div className="p-4 rounded-xl bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-800">
              <div className="text-4xl font-black text-blue-600 dark:text-blue-400 mb-2">{score.percentage.toFixed(0)}%</div>
              <div className="text-sm font-medium text-blue-800 dark:text-blue-300 uppercase tracking-wider">Score</div>
            </div>
            <div className="p-4 rounded-xl bg-green-50 dark:bg-green-900/20 border border-green-100 dark:border-green-800">
              <div className="text-4xl font-black text-green-600 dark:text-green-400 mb-2">{score.correct}/{score.total_questions}</div>
              <div className="text-sm font-medium text-green-800 dark:text-green-300 uppercase tracking-wider">Correct</div>
            </div>
            <div className="p-4 rounded-xl bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-800">
              <div className="text-4xl font-black text-red-600 dark:text-red-400 mb-2">{score.wrong}</div>
              <div className="text-sm font-medium text-red-800 dark:text-red-300 uppercase tracking-wider">Wrong</div>
            </div>
            <div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-700/50 border border-gray-100 dark:border-gray-600">
              <div className="text-4xl font-black text-gray-600 dark:text-gray-300 mb-2">{Math.floor(score.time_spent / 60)}m</div>
              <div className="text-sm font-medium text-gray-800 dark:text-gray-400 uppercase tracking-wider">Duration</div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          {/* Topic Mastery */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-100 dark:border-gray-700">
            <div className="flex items-center gap-2 mb-6">
              <Brain className="w-6 h-6 text-purple-600 dark:text-purple-400" />
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">Cognitive Profile</h2>
            </div>
            <div className="space-y-6">
              {mastery.map((topic) => (
                <div key={topic.topic}>
                  <div className="flex justify-between mb-2">
                    <span className="font-semibold text-gray-700 dark:text-gray-300">{topic.topic}</span>
                    <span className="text-sm font-bold text-gray-500 dark:text-gray-400">{topic.mastery_percentage.toFixed(0)}%</span>
                  </div>
                  <div className="w-full bg-gray-100 dark:bg-gray-700 rounded-full h-3">
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
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-100 dark:border-gray-700">
            <div className="flex items-center gap-2 mb-6">
              <Target className="w-6 h-6 text-red-600 dark:text-red-400" />
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">Next Steps</h2>
            </div>
            {adaptive ? (
              <div className="space-y-4">
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-xl border border-blue-100 dark:border-blue-800">
                  <h3 className="font-bold text-blue-900 dark:text-blue-300 mb-2 flex items-center gap-2">
                    <BookOpen className="w-4 h-4" />
                    Recommended Focus
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {adaptive.weak_topics.map(topic => (
                      <span key={topic} className="bg-white dark:bg-gray-800 px-3 py-1 rounded-full text-sm font-medium text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-700">
                        {topic}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg text-center">
                    <div className="text-xs text-gray-500 dark:text-gray-400 uppercase font-bold mb-1">Target Difficulty</div>
                    <div className="font-bold text-gray-800 dark:text-gray-200 capitalize">{adaptive.recommended_difficulty[0]}</div>
                  </div>
                  <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg text-center">
                    <div className="text-xs text-gray-500 dark:text-gray-400 uppercase font-bold mb-1">Est. Questions</div>
                    <div className="font-bold text-gray-800 dark:text-gray-200">{adaptive.estimated_questions_needed}</div>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-gray-500 italic">Complete more tests to unlock adaptive recommendations.</p>
            )}
          </div>
        </div>

        {/* Analytics Deep Dive */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
           <ExamReadinessRadar data={readinessData} />
           <TopicMasteryHeatmap data={heatmapData} />
        </div>

        {/* Performance Deep Dive (New) */}
        <div className="space-y-8 mb-8">
          <QuestionTimeline items={timelineItems} />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <MistakeBreakdown />
            <ComparisonView />
            <RecommendationsCard />
          </div>
        </div>

        {/* Question Review */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8 border border-gray-100 dark:border-gray-700">
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
                        {/* Source Grounding - Anti-hallucination */}
                        <div className="p-4 bg-gray-50 rounded-xl border border-gray-200">
                          <h4 className="font-bold text-gray-900 mb-2 flex items-center gap-2">
                            <BookOpen className="w-4 h-4" />
                            Source: {explanations[answer.question_id].section_reference}
                          </h4>
                          <p className="text-xs text-gray-700 italic leading-relaxed border-l-4 border-gray-300 pl-3">
                            "{explanations[answer.question_id].source_paragraph}"
                          </p>
                        </div>

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
                          {explanations[answer.question_id].behavioral_insight && (
                            <div className="mt-3 pt-3 border-t border-blue-200">
                              <h5 className="text-xs font-bold text-blue-900 mb-1">Your Behavior Pattern:</h5>
                              <p className="text-xs text-blue-700">
                                {explanations[answer.question_id].behavioral_insight}
                              </p>
                            </div>
                          )}
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