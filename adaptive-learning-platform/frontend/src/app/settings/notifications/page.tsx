"use client";

import React, { useState, useEffect } from 'react';
import { Bell, Mail, ArrowLeft, Save } from 'lucide-react';
import { useRouter } from 'next/navigation';
import NotificationToggle from '@/components/settings/NotificationToggle';
import FrequencySelector from '@/components/settings/FrequencySelector';
import NotificationHistory, { NotificationHistoryItem } from '@/components/settings/NotificationHistory';
import toast from 'react-hot-toast';
import { api } from '@/lib/api';

export default function NotificationSettingsPage() {
  const router = useRouter();
  const [frequency, setFrequency] = useState('daily');
  const [settings, setSettings] = useState({
    studyReminders: true,
    weeklyProgress: true,
    newFeatures: false,
    communityUpdates: true,
    achievementAlerts: true,
  });
  const [history, setHistory] = useState<NotificationHistoryItem[]>([]);

  useEffect(() => {
    async function loadSettings() {
      try {
        const [prefs, hist] = await Promise.all([
          api.getNotificationPreferences(),
          api.getNotificationHistory()
        ]);

        if (prefs) {
          // Map backend response to local state if necessary
          // Assuming backend returns keys matching these or similar
          setSettings(prev => ({
            ...prev,
            ...prefs // Overlay backend values
          }));
          if (prefs.email_frequency) {
            setFrequency(prefs.email_frequency);
          }
        }

        if (hist && hist.history) {
          // Map history items
          setHistory(hist.history.map((h: any) => ({
            id: h._id || h.id,
            type: h.type || 'email',
            title: h.subject || h.title || 'Notification',
            date: new Date(h.sent_at).toLocaleDateString(),
            status: h.status || 'sent'
          })));
        }
      } catch (error) {
        console.error("Failed to load notification settings", error);
      }
    }
    loadSettings();
  }, []);

  const handleToggle = (key: keyof typeof settings) => {
    setSettings(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const handleSave = async () => {
    try {
      await api.updateNotificationPreferences({
        ...settings,
        email_frequency: frequency
      });
      toast.success('Notification preferences saved');
    } catch (error) {
      toast.error('Failed to save preferences');
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="flex items-center gap-4 mb-8">
        <button 
          onClick={() => router.back()}
          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition"
        >
          <ArrowLeft className="w-5 h-5 text-gray-500 dark:text-gray-400" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Notification Preferences</h1>
          <p className="text-gray-500 dark:text-gray-400">Manage how and when you want to be notified.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Settings Column */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* Email Frequency */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
            <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Mail className="w-5 h-5 text-blue-600" /> Email Frequency
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
              How often should we send you summaries and reports?
            </p>
            <FrequencySelector value={frequency} onChange={setFrequency} />
          </div>

          {/* Notification Types */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
            <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Bell className="w-5 h-5 text-purple-600" /> Alert Types
            </h2>
            <div className="divide-y divide-gray-100 dark:divide-gray-700">
              <NotificationToggle 
                label="Study Reminders" 
                description="Get notified when it's time for your scheduled session."
                enabled={settings.studyReminders}
                onChange={() => handleToggle('studyReminders')}
              />
              <NotificationToggle 
                label="Weekly Progress Report" 
                description="A summary of your learning velocity and mastery gains."
                enabled={settings.weeklyProgress}
                onChange={() => handleToggle('weeklyProgress')}
              />
              <NotificationToggle 
                label="Achievement Alerts" 
                description="Celebrate when you unlock badges or hit streaks."
                enabled={settings.achievementAlerts}
                onChange={() => handleToggle('achievementAlerts')}
              />
              <NotificationToggle 
                label="Product Updates" 
                description="Be the first to know about new features."
                enabled={settings.newFeatures}
                onChange={() => handleToggle('newFeatures')}
              />
            </div>
          </div>

          <div className="flex justify-end">
            <button 
              onClick={handleSave}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg font-bold hover:bg-blue-700 transition flex items-center gap-2 shadow-lg hover:shadow-blue-500/25"
            >
              <Save className="w-4 h-4" /> Save Preferences
            </button>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <NotificationHistory items={history} />
          
          <div className="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-xl border border-yellow-100 dark:border-yellow-900/40">
            <h4 className="font-bold text-yellow-800 dark:text-yellow-200 text-sm mb-2">Note on Privacy</h4>
            <p className="text-xs text-yellow-700 dark:text-yellow-300">
              We respect your inbox. You can unsubscribe from any non-essential email directly from the footer of the email.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
