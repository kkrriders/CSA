import { QuestionAnswer } from '@/types';

interface ReviewPanelProps {
  totalQuestions: number;
  currentQuestionIndex: number;
  answers: Map<string, QuestionAnswer>; // questionId -> answer
  onQuestionSelect: (index: number) => void;
  onSubmit: () => void;
}

export default function ReviewPanel({
  totalQuestions,
  currentQuestionIndex,
  answers,
  onQuestionSelect,
  onSubmit,
}: ReviewPanelProps) {
  
  const getStatusColor = (index: number) => {
    if (index === currentQuestionIndex) return 'ring-2 ring-blue-600 border-blue-600 bg-blue-50 text-blue-700';
    
    // In sequential mode, we don't necessarily have the ID of future questions
    // But we know which indices are past.
    if (index < currentQuestionIndex) return 'bg-green-100 border-green-500 text-green-700';
    
    return 'bg-white border-gray-200 text-gray-400';
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 h-fit sticky top-24 border border-gray-100">
      <h3 className="font-bold text-gray-900 mb-4 flex items-center justify-between">
        Test Progress
        <span className="text-xs font-medium text-gray-500">
          {Math.round((currentQuestionIndex / totalQuestions) * 100)}%
        </span>
      </h3>
      
      <div className="grid grid-cols-5 gap-2 mb-6">
        {Array.from({ length: totalQuestions }).map((_, idx) => (
          <button
            key={idx}
            onClick={() => onQuestionSelect(idx)}
            className={`
              aspect-square flex items-center justify-center rounded-lg border font-bold text-xs transition
              ${getStatusColor(idx)}
            `}
          >
            {idx + 1}
          </button>
        ))}
      </div>

      <div className="space-y-3 text-xs font-medium text-gray-600 mb-8">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 bg-green-100 border border-green-500 rounded" />
          <span>Completed</span>
        </div>
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 bg-blue-50 border border-blue-600 rounded" />
          <span>Current</span>
        </div>
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 bg-white border border-gray-200 rounded" />
          <span>Remaining</span>
        </div>
      </div>

      <div className="p-4 bg-yellow-50 rounded-xl border border-yellow-100 mb-6">
        <p className="text-[10px] text-yellow-800 leading-relaxed font-medium uppercase tracking-wider">
          Exam Rules:
        </p>
        <ul className="text-[10px] text-yellow-700 mt-1 space-y-1">
          <li>• Strict 90s per question</li>
          <li>• No backwards navigation</li>
          <li>• Answers lock after submission</li>
        </ul>
      </div>

      <button
        onClick={onSubmit}
        className="w-full bg-red-50 text-red-600 py-3 rounded-xl font-bold hover:bg-red-100 transition border border-red-100"
      >
        End Test Early
      </button>
    </div>
  );
}