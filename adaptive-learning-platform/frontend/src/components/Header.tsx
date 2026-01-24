"use client";

import React from 'react';
import { Brain } from 'lucide-react';
import { useAuthStore } from '@/lib/store';
import { ThemeToggle } from '@/components/ThemeToggle';
import Link from 'next/link';

export default function Header() {
  const { user, logout } = useAuthStore();

  return (
    <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 transition-colors duration-200">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <Link href="/dashboard" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
          <Brain className="w-8 h-8 text-blue-600 dark:text-blue-500" />
          <span className="text-2xl font-bold text-gray-900 dark:text-white">Adaptive Learning</span>
        </Link>
        <div className="flex items-center gap-4">
          <ThemeToggle />
          <span className="text-gray-700 dark:text-gray-300 font-medium">{user?.name}</span>
          <button
            onClick={logout}
            className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}
