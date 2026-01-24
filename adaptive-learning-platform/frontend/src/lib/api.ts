import axios, { AxiosInstance } from 'axios';
import type {
  AuthResponse,
  User,
  Document,
  DocumentListItem,
  Question,
  QuestionWithAnswer,
  GenerateQuestionsRequest,
  TestSession,
  TestConfig,
  SubmitAnswerResponse,
  TestResult,
  WeaknessMapResponse,
  AdaptiveTargeting,
  AIExplanation,
  TopicMastery,
  LearningVelocity,
  ForgettingCurveData,
  ExamReadinessScore,
  BehaviorFingerprint,
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth token to requests
    this.client.interceptors.request.use((config) => {
      if (typeof window !== 'undefined') {
        const token = localStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      }
      return config;
    });
  }

  // Auth APIs
  async register(email: string, password: string, name: string): Promise<AuthResponse> {
    const { data } = await this.client.post('/auth/register', { email, password, name });
    return data;
  }

  async login(email: string, password: string): Promise<AuthResponse> {
    const { data } = await this.client.post('/auth/login', { email, password });
    return data;
  }

  async getMe(): Promise<User> {
    const { data } = await this.client.get('/auth/me');
    return data;
  }

  // Document APIs
  async uploadDocument(file: File): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);
    const { data } = await this.client.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  }

  async getDocuments(): Promise<DocumentListItem[]> {
    const { data } = await this.client.get('/documents/');
    return data;
  }

  async getDocument(id: string): Promise<Document> {
    const { data } = await this.client.get(`/documents/${id}`);
    return data;
  }

  async deleteDocument(id: string): Promise<void> {
    await this.client.delete(`/documents/${id}`);
  }

  // Question APIs
  async generateQuestions(request: GenerateQuestionsRequest): Promise<void> {
    await this.client.post('/questions/generate', request);
  }

  async getQuestionsForDocument(documentId: string): Promise<Question[]> {
    const { data } = await this.client.get(`/questions/document/${documentId}`);
    return data;
  }

  // Test APIs
  async startTest(documentId: string, config: TestConfig): Promise<TestSession> {
    const { data } = await this.client.post('/tests/start', { document_id: documentId, config });
    return data;
  }

  async getTestSession(sessionId: string): Promise<TestSession> {
    const { data } = await this.client.get(`/tests/${sessionId}`);
    return data;
  }

  async getCurrentQuestion(sessionId: string): Promise<Question> {
    const { data } = await this.client.get(`/tests/${sessionId}/current-question`);
    return data;
  }

  async submitAnswer(
    sessionId: string,
    questionId: string,
    userAnswer: string,
    timeTaken: number
  ): Promise<SubmitAnswerResponse> {
    const { data } = await this.client.post(`/tests/${sessionId}/submit-answer`, {
      question_id: questionId,
      user_answer: userAnswer,
      time_taken: timeTaken,
    });
    return data;
  }

  async markQuestion(
    sessionId: string,
    questionId: string,
    markedTricky: boolean = false,
    markedReview: boolean = false
  ): Promise<void> {
    await this.client.post(`/tests/${sessionId}/mark-question`, {
      question_id: questionId,
      marked_tricky: markedTricky,
      marked_review: markedReview,
    });
  }

  async finishTestEarly(sessionId: string): Promise<void> {
    await this.client.post(`/tests/${sessionId}/finish-early`);
  }

  async getTestResults(sessionId: string): Promise<TestResult> {
    const { data } = await this.client.get(`/tests/${sessionId}/results`);
    return data;
  }

  async getReviewQuestions(sessionId: string): Promise<QuestionWithAnswer[]> {
    const { data } = await this.client.get(`/tests/${sessionId}/review-questions`);
    return data;
  }

  // Analytics APIs
  async getPatterns(sessionId: string): Promise<any> {
    const { data } = await this.client.get(`/analytics/session/${sessionId}/patterns`);
    return data;
  }

  async getTopicMastery(sessionId: string): Promise<{ topic_mastery: TopicMastery[] }> {
    const { data } = await this.client.get(`/analytics/session/${sessionId}/topic-mastery`);
    return data;
  }

  async getWeaknessMap(sessionId: string): Promise<WeaknessMapResponse> {
    const { data } = await this.client.get(`/analytics/session/${sessionId}/weakness-map`);
    return data;
  }

  async getAdaptiveTargeting(sessionId: string): Promise<AdaptiveTargeting> {
    const { data } = await this.client.get(`/analytics/session/${sessionId}/adaptive-targeting`);
    return data;
  }

  async explainWrongAnswer(sessionId: string, questionId: string): Promise<AIExplanation> {
    const { data } = await this.client.post('/analytics/explain-wrong-answer', {
      session_id: sessionId,
      question_id: questionId,
    });
    return data;
  }

  // Study Plan APIs
  async createStudyPlan(request: any): Promise<any> {
    const { data } = await this.client.post('/study-plans/generate', request);
    return data;
  }

  async getStudyPlans(): Promise<any> {
    const { data } = await this.client.get('/study-plans/');
    return data;
  }

  async getStudyPlan(planId: string): Promise<any> {
    const { data } = await this.client.get(`/study-plans/${planId}`);
    return data;
  }

  async getNextStudySession(planId: string): Promise<any> {
    const { data } = await this.client.get(`/study-plans/${planId}/next-session`);
    return data;
  }

  async completeStudySession(planId: string, sessionNumber: number): Promise<any> {
    const { data } = await this.client.post(`/study-plans/${planId}/complete-session/${sessionNumber}`);
    return data;
  }

  async getStudyPlanProgress(planId: string): Promise<any> {
    const { data } = await this.client.get(`/study-plans/${planId}/progress`);
    return data;
  }

  // Reviews APIs
  async getReviewQueue(documentId?: string): Promise<any> {
    const { data } = await this.client.get('/reviews/queue', { params: { document_id: documentId } });
    return data;
  }

  async createReviewSession(documentId?: string, maxReviews: number = 20): Promise<any> {
    const { data } = await this.client.post('/reviews/sessions', null, { params: { document_id: documentId, max_reviews: maxReviews } });
    return data;
  }

  async getReviewSession(sessionId: string): Promise<any> {
    const { data } = await this.client.get(`/reviews/sessions/${sessionId}`);
    return data;
  }

  async submitReviewResponse(sessionId: string, reviewId: string, quality: number, timeTaken: number): Promise<any> {
    const { data } = await this.client.post(`/reviews/sessions/${sessionId}/reviews/${reviewId}`, {
      quality,
      time_taken: timeTaken
    });
    return data;
  }

  async completeReviewSession(sessionId: string): Promise<any> {
    const { data } = await this.client.post(`/reviews/sessions/${sessionId}/complete`);
    return data;
  }

  async getReviewSchedule(): Promise<any> {
    const { data } = await this.client.get('/reviews/schedule');
    return data;
  }

  // Notification APIs
  async getNotificationPreferences(): Promise<any> {
    const { data } = await this.client.get('/notifications/preferences');
    return data;
  }

  async updateNotificationPreferences(preferences: any): Promise<any> {
    const { data } = await this.client.put('/notifications/preferences', preferences);
    return data;
  }

  async getNotificationHistory(limit: number = 50): Promise<any> {
    const { data } = await this.client.get('/notifications/history', { params: { limit } });
    return data;
  }

  // Extended Analytics APIs
  async getLearningVelocity(): Promise<{ velocities: LearningVelocity[] }> {
    const { data } = await this.client.get('/analytics/user/learning-velocity');
    return data;
  }

  async getForgettingCurve(topic: string): Promise<ForgettingCurveData> {
    const { data } = await this.client.get(`/analytics/user/topic/${topic}/forgetting-curve`);
    return data;
  }

  async getExamReadiness(documentId: string): Promise<ExamReadinessScore> {
    const { data } = await this.client.get(`/analytics/document/${documentId}/exam-readiness`);
    return data;
  }

  async getBehaviorFingerprint(sessionId: string): Promise<BehaviorFingerprint> {
    const { data } = await this.client.get(`/analytics/session/${sessionId}/behavior-fingerprint`);
    return data;
  }

  async getAggregateBehaviorFingerprint(): Promise<BehaviorFingerprint> {
    const { data } = await this.client.get('/analytics/user/behavior-fingerprint-aggregate');
    return data;
  }

  async getOverallPerformance(documentId: string): Promise<any> {
    const { data } = await this.client.get(`/analytics/document/${documentId}/overall-performance`);
    return data;
  }

  async getUserDashboardStats(): Promise<any> {
    const { data } = await this.client.get('/analytics/user/dashboard-stats');
    return data;
  }
}

export const api = new APIClient();
