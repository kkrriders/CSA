// User types
export interface User {
  _id: string;
  email: string;
  name: string;
  created_at: string;
  last_login?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Document types
export type FileType = 'pdf' | 'markdown';
export type ProcessingStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface Section {
  title: string;
  content: string;
  level: number;
  start_index: number;
  end_index: number;
  topics: string[];
}

export interface DocumentMetadata {
  total_pages?: number;
  word_count: number;
  language: string;
  detected_topics: string[];
}

export interface Document {
  _id: string;
  title: string;
  original_file_name: string;
  file_type: FileType;
  file_size: number;
  sections: Section[];
  metadata: DocumentMetadata;
  processing_status: ProcessingStatus;
  processing_error?: string;
  uploaded_at: string;
}

export interface DocumentListItem {
  _id: string;
  title: string;
  file_type: FileType;
  processing_status: ProcessingStatus;
  uploaded_at: string;
  sections_count: number;
  word_count: number;
}

// Question types
export type QuestionType = 'mcq' | 'short_answer' | 'conceptual';
export type DifficultyLevel = 'easy' | 'medium' | 'hard' | 'tricky';

export interface MCQOption {
  text: string;
  is_correct?: boolean;
}

export interface Question {
  _id: string;
  question_text: string;
  question_type: QuestionType;
  difficulty: DifficultyLevel;
  topic: string;
  section_title?: string;
  options?: MCQOption[];
}

export interface QuestionWithAnswer extends Question {
  correct_answer: string;
  explanation: string;
  options?: MCQOption[];
}

export interface GenerateQuestionsRequest {
  document_id: string;
  num_questions: number;
  difficulty_distribution?: Record<DifficultyLevel, number>;
  topics?: string[];
  question_types: QuestionType[];
}

// Test session types
export type TestStatus = 'in_progress' | 'completed' | 'abandoned';
export type AnswerStatus = 'correct' | 'wrong' | 'skipped' | 'not_attempted';

export interface QuestionAnswer {
  question_id: string;
  user_answer?: string;
  is_correct?: boolean;
  time_taken: number;
  status: AnswerStatus;
  marked_tricky: boolean;
  marked_review: boolean;
  answered_at?: string;
}

export interface TestConfig {
  total_questions: number;
  time_per_question: number;
  topics?: string[];
  difficulty_levels?: string[];
  question_types?: QuestionType[];
}

export interface TestSession {
  _id: string;
  document_id: string;
  config: TestConfig;
  current_question_index: number;
  total_questions: number;
  status: TestStatus;
  started_at: string;
  completed_at?: string;
}

export interface SubmitAnswerResponse {
  is_correct: boolean;
  correct_answer: string;
  explanation: string;
  next_question_index: number;
  is_test_complete: boolean;
}

export interface TestScore {
  total_questions: number;
  correct: number;
  wrong: number;
  skipped: number;
  not_attempted: number;
  percentage: number;
  time_spent: number;
  marked_tricky_count: number;
  marked_review_count: number;
}

export interface TestResult {
  session_id: string;
  score: TestScore;
  answers: QuestionAnswer[];
  tricky_questions: string[];
  wrong_questions: string[];
  completed_at: string;
}

// Analytics types
export interface TopicMastery {
  topic: string;
  total_attempts: number;
  correct_attempts: number;
  wrong_attempts: number;
  mastery_percentage: number;
  avg_time_taken: number;
  difficulty_breakdown: Record<string, Record<string, number>>;
}

export interface WeaknessAnalysis {
  topic: string;
  mastery_percentage: number;
  failure_patterns: string[];
  question_ids: string[];
  priority_score: number;
  recommendation: string;
}

export interface WeaknessMapResponse {
  user_id: string;
  document_id: string;
  weakness_areas: WeaknessAnalysis[];
  high_priority_topics: string[];
  recommended_focus: string[];
}

export interface AdaptiveTargeting {
  weak_topics: string[];
  recommended_difficulty: string[];
  focus_question_types: string[];
  estimated_questions_needed: number;
}

export interface AIExplanation {
  question_id: string;
  user_answer: string;
  correct_answer: string;
  // Grounding - NO HALLUCINATION
  source_paragraph: string;  // Exact quote from document
  section_reference: string;  // Section citation
  // Explanation WITH behavioral context
  why_wrong: string;
  concept_explanation: string;
  common_mistake: string;
  behavioral_insight: string;  // What time/hesitation suggests
}

// ============================================================
// WORLD-CLASS FEATURES
// ============================================================

// 1. Learning Velocity
export interface LearningVelocity {
  topic: string;
  sessions_analyzed: number;
  mastery_trajectory: number[];  // [0.3, 0.5, 0.7, 0.8]
  velocity: number;  // Mastery gain per session
  acceleration: number;  // Is velocity increasing?
  sessions_to_mastery: number | null;  // Predicted sessions to 90%
  comparative_rank: string | null;  // "3× faster than Transformers"
}

// 2. Forgetting Curve
export interface ForgettingCurveData {
  topic: string;
  peak_mastery: number;
  peak_date: string;
  current_mastery: number;
  days_since_peak: number;
  decay_rate: number;  // Per day
  half_life_days: number | null;  // Days until mastery halves
  needs_review: boolean;
}

// 3. Exam Readiness Score
export interface ExamReadinessScore {
  overall_score: number;  // 0-100: "You are 72% ready"

  // Components (weighted)
  mastery_score: number;  // 40% weight
  consistency_score: number;  // 25% weight
  confidence_score: number;  // 20% weight
  coverage_score: number;  // 15% weight

  // Breakdown
  strong_topics: string[];  // Mastery > 80%
  weak_topics: string[];  // Mastery < 50%
  inconsistent_topics: string[];  // High variance

  // Actionable
  estimated_study_hours: number;  // To reach 90%
  priority_actions: string[];  // Specific recommendations
  readiness_level: string;  // "Ready", "Almost Ready", "Needs Work"
}

// 4. Behavior Fingerprint
export interface BehaviorFingerprint {
  user_id: string;

  // Core traits (0-1 scale)
  risk_taking: number;  // Answers fast even when uncertain
  perfectionism: number;  // Slow, changes answers, marks tricky
  skimming: number;  // Fast, skips hard questions
  grinding: number;  // Slow but thorough, high accuracy

  // Detailed metrics
  confidence_calibration: number;  // Confident when correct?
  speed_accuracy_tradeoff: number;  // -1 (slow accurate) to +1 (fast sloppy)
  difficulty_seeking: number;  // Avoid or embrace hard questions?
  consistency: number;  // Stable performance?

  // Personality
  primary_trait: string;  // "Risk-taker", "Perfectionist", "Skimmer", "Grinder"
  secondary_trait: string | null;

  // Coaching
  strengths: string[];
  growth_areas: string[];
  optimal_study_strategy: string;
}
