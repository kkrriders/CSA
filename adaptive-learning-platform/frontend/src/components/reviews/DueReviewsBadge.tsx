"use client";

import React from 'react';

interface DueReviewsBadgeProps {
  count: number;
}

export default function DueReviewsBadge({ count }: DueReviewsBadgeProps) {
  if (count <= 0) return null;

  return (
    <span className="bg-red-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full min-w-[1.25rem] text-center border-2 border-white dark:border-gray-900">
      {count > 99 ? '99+' : count}
    </span>
  );
}
