'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Upload, FileText, Trash2, PlayCircle, Plus } from 'lucide-react';
import toast from 'react-hot-toast';
import { api } from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import type { DocumentListItem, TestSession } from '@/types';
import StreakCounter from '@/components/dashboard/StreakCounter';
import QuickStatsCards, { DashboardStats } from '@/components/dashboard/QuickStatsCards';
import ActivityFeed from '@/components/dashboard/ActivityFeed';
import TopicOverview, { TopicStats } from '@/components/dashboard/TopicOverview';
import RecommendedActions from '@/components/dashboard/RecommendedActions';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';

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
          api.getInProgressTests().catch(err => {
            console.error('Failed to load in-progress tests:', err);
            return [];
          })
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
            count: v.sessions_analyzed
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
      const interval = setInterval(async () => {
        try {
          const docs = await api.getDocuments();
          setDocuments(docs);

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
    const inProgressTest = inProgressTests.find(t => t.document_id === documentId);

    if (inProgressTest && inProgressTest._id) {
      router.push(`/test/${inProgressTest._id}`);
    } else {
      router.push(`/test/configure?documentId=${documentId}`);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back, {user?.name}! Ready to continue your learning journey?
          </p>
        </div>
      </div>

      <QuickStatsCards stats={stats} />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-8">
          <RecommendedActions />

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <div className="space-y-1">
                <CardTitle>Documents</CardTitle>
                <CardDescription>
                  Manage your study materials and start new tests.
                </CardDescription>
              </div>
              <div className="relative">
                 <input
                    type="file"
                    accept=".pdf,.md"
                    onChange={handleFileUpload}
                    disabled={uploading}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
                    id="file-upload"
                  />
                  <Button disabled={uploading} className="cursor-pointer">
                    {uploading ? (
                      <>Uploading...</>
                    ) : (
                      <>
                        <Plus className="mr-2 h-4 w-4" /> Upload New
                      </>
                    )}
                  </Button>
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="flex items-center space-x-4">
                      <Skeleton className="h-12 w-12 rounded-lg" />
                      <div className="space-y-2">
                        <Skeleton className="h-4 w-[250px]" />
                        <Skeleton className="h-4 w-[200px]" />
                      </div>
                    </div>
                  ))}
                </div>
              ) : documents.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-center border-2 border-dashed rounded-lg bg-muted/50">
                  <div className="bg-background p-4 rounded-full mb-4">
                    <Upload className="w-8 h-8 text-muted-foreground" />
                  </div>
                  <h3 className="text-lg font-semibold mb-1">No documents yet</h3>
                  <p className="text-muted-foreground max-w-sm mb-4">
                    Upload your first PDF or Markdown file to generate questions and start learning.
                  </p>
                  <div className="relative">
                    <input
                      type="file"
                      accept=".pdf,.md"
                      onChange={handleFileUpload}
                      disabled={uploading}
                      className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    />
                    <Button variant="outline">Select File</Button>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  {documents.map((doc) => (
                    <div
                      key={doc._id}
                      className="flex items-center justify-between p-4 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
                    >
                      <div className="flex items-center gap-4">
                        <div className="p-2 bg-primary/10 rounded-lg">
                          <FileText className="w-6 h-6 text-primary" />
                        </div>
                        <div>
                          <h4 className="font-semibold">{doc.title}</h4>
                          <div className="flex items-center gap-2 text-sm text-muted-foreground mt-1">
                            <span>{doc.sections_count} sections</span>
                            <span>•</span>
                            <span>{doc.word_count} words</span>
                            <Badge variant={
                              doc.processing_status === 'completed' ? 'default' :
                              doc.processing_status === 'failed' ? 'destructive' :
                              'secondary'
                            }>
                              {doc.processing_status}
                            </Badge>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {doc.processing_status === 'completed' && (
                          <Button
                            size="sm"
                            onClick={() => handleStartTest(doc._id)}
                            className="gap-2"
                          >
                            <PlayCircle className="w-4 h-4" />
                            {inProgressTests.find(t => t.document_id === doc._id) ? 'Resume' : 'Start'}
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleDelete(doc._id)}
                          className="text-destructive hover:text-destructive hover:bg-destructive/10"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-8">
          <StreakCounter streak={stats?.streak} />
          <TopicOverview topics={topics} />
          <ActivityFeed items={[]} />
        </div>
      </div>
    </div>
  );
}
