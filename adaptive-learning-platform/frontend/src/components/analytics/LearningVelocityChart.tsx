"use client";

import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

interface VelocityData {
  name: string;
  velocity: number;
}

const LearningVelocityChart = ({ data }: { data?: VelocityData[] }) => {
  if (!data || data.length === 0) {
    return (
      <div className="w-full h-80 bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700 flex items-center justify-center">
        <div className="text-center">
          <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-2">Learning Velocity</h3>
          <p className="text-gray-500 dark:text-gray-400">No data available yet.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-80 bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700">
      <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">Learning Velocity</h3>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data}
          margin={{
            top: 5,
            right: 30,
            left: 20,
            bottom: 5,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
          <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#6b7280'}} />
          <YAxis axisLine={false} tickLine={false} tick={{fill: '#6b7280'}} />
          <Tooltip 
            contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}}
          />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="velocity" 
            stroke="#3b82f6" 
            strokeWidth={3}
            dot={{ r: 4, strokeWidth: 2 }}
            activeDot={{ r: 8 }} 
            name="Knowledge Acquisition"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default LearningVelocityChart;
