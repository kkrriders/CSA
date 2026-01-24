"use client";

import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

const data = [
  { session: 'S1', score: 65, avg: 60 },
  { session: 'S2', score: 70, avg: 62 },
  { session: 'S3', score: 68, avg: 65 },
  { session: 'S4', score: 85, avg: 68 },
  { session: 'S5', score: 82, avg: 70 },
  { session: 'S6', score: 90, avg: 72 },
];

const SessionComparisonChart = () => {
  return (
    <div className="w-full h-80 bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700">
      <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">Session Performance vs Average</h3>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          margin={{
            top: 5,
            right: 30,
            left: 20,
            bottom: 5,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
          <XAxis dataKey="session" axisLine={false} tickLine={false} />
          <YAxis axisLine={false} tickLine={false} />
          <Tooltip cursor={{fill: '#f9fafb'}} />
          <Legend />
          <Bar dataKey="score" name="Your Score" fill="#3b82f6" radius={[4, 4, 0, 0]} />
          <Bar dataKey="avg" name="Class Average" fill="#d1d5db" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default SessionComparisonChart;
