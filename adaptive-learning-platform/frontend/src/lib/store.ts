import { create } from 'zustand';
import type { User, Question, QuestionWithAnswer } from '@/types';

interface AuthStore {
  user: User | null;
  token: string | null;
  setAuth: (token: string, user: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: typeof window !== 'undefined' && localStorage.getItem('user')
    ? JSON.parse(localStorage.getItem('user')!)
    : null,
  token: typeof window !== 'undefined' ? localStorage.getItem('token') : null,
  setAuth: (token, user) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
    }
    set({ token, user });
  },
  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
    set({ token: null, user: null });
  },
}));

interface TestStore {
  currentQuestion: Question | null;
  timeRemaining: number;
  reviewQuestions: QuestionWithAnswer[];
  markedQuestions: string[];
  wrongQuestions: string[];
  setCurrentQuestion: (question: Question | null) => void;
  setTimeRemaining: (time: number) => void;
  setReviewQuestions: (questions: QuestionWithAnswer[]) => void;
  addMarkedQuestion: (questionId: string) => void;
  addWrongQuestion: (questionId: string) => void;
  reset: () => void;
}

export const useTestStore = create<TestStore>((set) => ({
  currentQuestion: null,
  timeRemaining: 90,
  reviewQuestions: [],
  markedQuestions: [],
  wrongQuestions: [],
  setCurrentQuestion: (question) => set({ currentQuestion: question }),
  setTimeRemaining: (time) => set({ timeRemaining: time }),
  setReviewQuestions: (questions) => set({ reviewQuestions: questions }),
  addMarkedQuestion: (questionId) =>
    set((state) => ({
      markedQuestions: [...state.markedQuestions, questionId],
    })),
  addWrongQuestion: (questionId) =>
    set((state) => ({
      wrongQuestions: [...state.wrongQuestions, questionId],
    })),
  reset: () =>
    set({
      currentQuestion: null,
      timeRemaining: 90,
      reviewQuestions: [],
      markedQuestions: [],
      wrongQuestions: [],
    }),
}));
