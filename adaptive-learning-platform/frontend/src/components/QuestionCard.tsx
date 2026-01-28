import { Question } from '@/types';
import { Flag, HelpCircle } from 'lucide-react';
import ConfidenceSlider from './ConfidenceSlider';
import SanitizedContent from './SanitizedContent';

interface QuestionCardProps {
  question: Question;
  userAnswer?: string;
  onAnswerChange: (answer: string) => void;
  onMarkReview: () => void;
  isMarkedReview: boolean;
  questionNumber: number;
  confidence?: number;
  onConfidenceChange?: (value: number) => void;
  flagReason?: string;
  onFlagReasonChange?: (reason: string) => void;
}

export default function QuestionCard({
  question,
  userAnswer,
  onAnswerChange,
  onMarkReview,
  isMarkedReview,
  questionNumber,
  confidence = 50,
  onConfidenceChange,
  flagReason,
  onFlagReasonChange
}: QuestionCardProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 transition-colors duration-200">
      <div className="flex justify-between items-start mb-6">
        <div className="w-full">
          <span className="text-sm font-medium text-blue-600 dark:text-blue-400 mb-1 block">
            Question {questionNumber}
          </span>
          <SanitizedContent 
            tagName="h2"
            content={question.question_text}
            className="text-xl font-bold text-gray-900 dark:text-white leading-relaxed"
          />
        </div>
        <div className="flex flex-col items-end gap-2 ml-4 flex-shrink-0">
          <button
            onClick={onMarkReview}
            className={`p-2 rounded-lg transition focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500 ${
              isMarkedReview
                ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
                : 'text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 dark:text-gray-500'
            }`}
            title={isMarkedReview ? "Unmark for review" : "Mark for review"}
            aria-label={isMarkedReview ? "Unmark for review" : "Mark for review"}
            aria-pressed={isMarkedReview}
          >
            <Flag className="w-5 h-5" />
          </button>
          
          {isMarkedReview && onFlagReasonChange && (
            <select
              value={flagReason || 'Needs Review'}
              onChange={(e) => onFlagReasonChange(e.target.value)}
              className="text-xs p-1 rounded border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-300 focus:ring-1 focus:ring-blue-500"
              aria-label="Flag reason"
            >
              <option value="Needs Review">Needs Review</option>
              <option value="Unclear">Unclear</option>
              <option value="Tricky">Tricky</option>
            </select>
          )}
        </div>
      </div>

      <div className="space-y-4">
        {question.question_type === 'mcq' && question.options ? (
          <div 
            role="radiogroup" 
            aria-labelledby="question-text" 
            className="space-y-3"
          >
            {question.options.map((option, idx) => (
              <label
                key={idx}
                className={`
                  flex items-center p-4 rounded-lg border-2 cursor-pointer transition relative
                  hover:border-blue-300 dark:hover:border-blue-700
                  ${
                    userAnswer === option.text
                      ? 'border-blue-600 bg-blue-50 dark:bg-blue-900/20 dark:border-blue-500'
                      : 'border-gray-200 dark:border-gray-700'
                  }
                `}
              >
                <input
                  type="radio"
                  name={`question-${questionNumber}`}
                  value={option.text}
                  checked={userAnswer === option.text}
                  onChange={(e) => onAnswerChange(e.target.value)}
                  className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500 dark:focus:ring-offset-gray-800"
                />
                <span className="ml-3 text-gray-700 dark:text-gray-200 font-medium">
                  <SanitizedContent content={option.text} tagName="span" />
                </span>
              </label>
            ))}
          </div>
        ) : (
          <textarea
            value={userAnswer || ''}
            onChange={(e) => onAnswerChange(e.target.value)}
            placeholder="Type your answer here..."
            aria-label="Your answer"
            className="w-full h-32 p-4 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400"
          />
        )}
      </div>
      
      {onConfidenceChange && (
        <ConfidenceSlider value={confidence} onChange={onConfidenceChange} />
      )}

      <div className="mt-6 pt-6 border-t border-gray-100 dark:border-gray-700 flex justify-between text-sm text-gray-500 dark:text-gray-400">
        <span className="capitalize">Topic: {question.topic}</span>
        <span className="capitalize">Difficulty: {question.difficulty}</span>
      </div>
    </div>
  );
}
