'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Upload, FileText, Loader, Trash2, PlayCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import { api } from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import type { DocumentListItem, TestSession } from '@/types';
import StreakCounter from '@/components/dashboard/StreakCounter';
import QuickStatsCards, { DashboardStats } from '@/components/dashboard/QuickStatsCards';
import ActivityFeed from '@/components/dashboard/ActivityFeed';
import TopicOverview, { TopicStats } from '@/components/dashboard/TopicOverview';
import RecommendedActions from '@/components/dashboard/RecommendedActions';

export default function DashboardPage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const [documents, setDocuments] = useState<DocumentListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [stats, setStats] = useState<DashboardStats | undefined>(undefined);
  const [topics, setTopics] = useState<TopicStats[]>([]);
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);
  const [inProgressTests, setInProgressTests] = useState<TestSession[]>([]);

  useEffect(() => {
    if (!user) {
      router.push('/auth/login');
      return;
    }
    
    async function loadDashboardData() {
      try {
        const [docs, dashboardStats, velocity, inProgress] = await Promise.all([
          api.getDocuments(),
          api.getUserDashboardStats().catch(() => null),
          api.getLearningVelocity().catch(() => ({ velocities: [] })),
          api.getInProgressTests().catch(() => [])
        ]);
        
        setDocuments(docs);
        setInProgressTests(inProgress);

        if (dashboardStats) {
          setStats(dashboardStats);
        }

        if (velocity && velocity.velocities) {
          const topicStats = velocity.velocities.map((v: any) => ({
            name: v.topic,
            mastery: Math.round((v.mastery_trajectory[v.mastery_trajectory.length - 1] || 0) * 100),
            count: v.sessions_analyzed // Proxy for count, or just show sessions
          }));
          setTopics(topicStats);
        }

      } catch (error) {
        toast.error('Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    }

    loadDashboardData();
  }, [user]);

  // Poll for processing documents
  useEffect(() => {
    const hasProcessingDocs = documents.some(doc => doc.processing_status === 'processing' || doc.processing_status === 'pending');

    if (hasProcessingDocs) {
      // Poll every 3 seconds
      const interval = setInterval(async () => {
        try {
          const docs = await api.getDocuments();
          setDocuments(docs);

          // Stop polling if no more processing docs
          const stillProcessing = docs.some(doc => doc.processing_status === 'processing' || doc.processing_status === 'pending');
          if (!stillProcessing) {
            clearInterval(interval);
            setPollingInterval(null);
            toast.success('Document processing completed!');
          }
        } catch (error) {
          console.error('Error polling documents:', error);
        }
      }, 3000);

      setPollingInterval(interval);

      return () => {
        clearInterval(interval);
      };
    }
  }, [documents]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.pdf') && !file.name.endsWith('.md')) {
      toast.error('Only PDF and Markdown files are supported');
      return;
    }

    setUploading(true);
    try {
      await api.uploadDocument(file);
      toast.success('Document uploaded! Processing...');
      // Reload documents
      const docs = await api.getDocuments();
      setDocuments(docs);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return;

    try {
      await api.deleteDocument(id);
      toast.success('Document deleted');
      const docs = await api.getDocuments();
      setDocuments(docs);
    } catch (error) {
      toast.error('Failed to delete document');
    }
  };

  const handleStartTest = (documentId: string) => {
    // Check if there's an in-progress test for this document
    const inProgressTest = inProgressTests.find(t => t.document_id === documentId);

    if (inProgressTest) {
      // Resume existing test
      router.push(`/test/${inProgressTest._id}`);
    } else {
      // Configure new test
      router.push(`/test/configure?documentId=${documentId}`);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header Row */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2 dark:text-white">Welcome back, {user?.name}!</h1>
          <p className="text-gray-600 dark:text-gray-400">Ready to continue your learning journey?</p>
        </div>
        <div className="w-full md:w-auto">
        </div>
      </div>

      {/* Stats Row */}
      <div className="mb-8">
        <QuickStatsCards stats={stats} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content Column (Left) */}
        <div className="lg:col-span-2 space-y-8">
          <RecommendedActions />

          {/* Upload Section */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-bold mb-4 dark:text-white">Upload Document</h2>
            <div className="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-lg p-8 text-center hover:border-blue-500 dark:hover:border-blue-500 transition">
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <label className="cursor-pointer">
                <span className="text-blue-600 hover:text-blue-700 font-semibold">
                  {uploading ? 'Uploading...' : 'Click to upload'}
                </span>
                <span className="text-gray-600 dark:text-gray-400"> or drag and drop</span>
                <input
                  type="file"
                  accept=".pdf,.md"
                  onChange={handleFileUpload}
                  disabled={uploading}
                  className="hidden"
                />
              </label>
              <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">PDF or Markdown files (Max 50MB)</p>
            </div>
          </div>

          {/* Documents List */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-bold mb-6 dark:text-white">Your Documents</h2>

            {loading ? (
              <div className="text-center py-12">
                <Loader className="w-8 h-8 animate-spin text-blue-600 mx-auto" />
                <p className="text-gray-600 dark:text-gray-400 mt-4">Loading documents...</p>
              </div>
            ) : documents.length === 0 ? (
              <div className="text-center py-12">
                <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-600 dark:text-gray-400">No documents yet. Upload one to get started!</p>
              </div>
            ) : (
              <div className="grid gap-4">
                {documents.map((doc) => (
                  <div
                    key={doc._id}
                    className="border dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition dark:bg-gray-800"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg dark:text-white">{doc.title}</h3>
                        <div className="flex gap-4 text-sm text-gray-600 dark:text-gray-400 mt-1">
                          <span>{doc.sections_count} sections</span>
                          <span>{doc.word_count} words</span>
                          <span className={`px-2 py-1 rounded ${
                            doc.processing_status === 'completed' ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300' :
                            doc.processing_status === 'processing' ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300' :
                            doc.processing_status === 'failed' ? 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300' :
                            'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
                          }`}>
                            {doc.processing_status}
                          </span>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        {doc.processing_status === 'completed' && (
                          <>
                            {inProgressTests.find(t => t.document_id === doc._id) ? (
                              <button
                                onClick={() => handleStartTest(doc._id)}
                                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition flex items-center gap-2"
                              >
                                <PlayCircle className="w-4 h-4" />
                                Resume Test
                              </button>
                            ) : (
                              <button
                                onClick={() => handleStartTest(doc._id)}
                                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center gap-2"
                              >
                                <PlayCircle className="w-4 h-4" />
                                Start Test
                              </button>
                            )}
                          </>
                        )}
                        <button
                          onClick={() => handleDelete(doc._id)}
                          className="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition"
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Sidebar Column (Right) */}
        <div className="space-y-8">
          <StreakCounter streak={stats?.streak} />
          <TopicOverview topics={topics} />
          <ActivityFeed items={[]} />
        </div>
      </div>
    </div>
  );
}
