import { Question } from '@/types';
import { Flag, HelpCircle } from 'lucide-react';

interface QuestionCardProps {
  question: Question;
  userAnswer?: string;
  onAnswerChange: (answer: string) => void;
  onMarkReview: () => void;
  isMarkedReview: boolean;
  questionNumber: number;
}

export default function QuestionCard({
  question,
  userAnswer,
  onAnswerChange,
  onMarkReview,
  isMarkedReview,
  questionNumber,
}: QuestionCardProps) {
  return (
    <div className="bg-white rounded-xl shadow-lg p-8">
      <div className="flex justify-between items-start mb-6">
        <div>
          <span className="text-sm font-medium text-blue-600 mb-1 block">
            Question {questionNumber}
          </span>
          <h2 className="text-xl font-bold text-gray-900">{question.question_text}</h2>
        </div>
        <div className="flex gap-2">
          <button
            onClick={onMarkReview}
            className={`p-2 rounded-lg transition ${
              isMarkedReview
                ? 'bg-yellow-100 text-yellow-700'
                : 'text-gray-400 hover:bg-gray-100'
            }`}
            title="Mark for Review"
          >
            <Flag className="w-5 h-5" />
          </button>
        </div>
      </div>

      <div className="space-y-4">
        {question.question_type === 'mcq' && question.options ? (
          <div className="space-y-3">
            {question.options.map((option, idx) => (
              <label
                key={idx}
                className={`
                  flex items-center p-4 rounded-lg border-2 cursor-pointer transition
                  ${
                    userAnswer === option.text
                      ? 'border-blue-600 bg-blue-50'
                      : 'border-gray-200 hover:border-blue-300'
                  }
                `}
              >
                <input
                  type="radio"
                  name="answer"
                  value={option.text}
                  checked={userAnswer === option.text}
                  onChange={(e) => onAnswerChange(e.target.value)}
                  className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                />
                <span className="ml-3 text-gray-700">{option.text}</span>
              </label>
            ))}
          </div>
        ) : (
          <textarea
            value={userAnswer || ''}
            onChange={(e) => onAnswerChange(e.target.value)}
            placeholder="Type your answer here..."
            className="w-full h-32 p-4 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
          />
        )}
      </div>

      <div className="mt-6 pt-6 border-t flex justify-between text-sm text-gray-500">
        <span className="capitalize">Topic: {question.topic}</span>
        <span className="capitalize">Difficulty: {question.difficulty}</span>
      </div>
    </div>
  );
}
