"use client";

import React from 'react';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend
} from 'recharts';

interface RadarData {
  subject: string;
  A: number;
  fullMark: number;
}

const defaultData: RadarData[] = [
  { subject: 'Knowledge', A: 120, fullMark: 150 },
  { subject: 'Speed', A: 98, fullMark: 150 },
  { subject: 'Accuracy', A: 86, fullMark: 150 },
  { subject: 'Consistency', A: 99, fullMark: 150 },
  { subject: 'Endurance', A: 85, fullMark: 150 },
  { subject: 'Recall', A: 65, fullMark: 150 },
];

const ExamReadinessRadar = ({ data }: { data?: RadarData[] }) => {
  const chartData = data || defaultData;

  return (
    <div className="w-full h-80 bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700">
      <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">Exam Readiness Profile</h3>
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={chartData}>
          <PolarGrid stroke="#e5e7eb" />
          <PolarAngleAxis dataKey="subject" tick={{ fill: '#4b5563', fontSize: 12 }} />
          <PolarRadiusAxis angle={30} domain={[0, 150]} tick={false} axisLine={false} />
          <Radar
            name="Current Level"
            dataKey="A"
            stroke="#8b5cf6"
            strokeWidth={2}
            fill="#8b5cf6"
            fillOpacity={0.3}
          />
          <Legend />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ExamReadinessRadar;
