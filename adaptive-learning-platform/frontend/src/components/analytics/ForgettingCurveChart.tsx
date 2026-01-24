"use client";

import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

const data = [
  { day: '0', retention: 100 },
  { day: '1', retention: 55 },
  { day: '3', retention: 35 },
  { day: '7', retention: 25 },
  { day: '14', retention: 20 },
  { day: '30', retention: 15 },
];

const ForgettingCurveChart = () => {
  return (
    <div className="w-full h-80 bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700">
      <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">Estimated Forgetting Curve</h3>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={data}
          margin={{
            top: 10,
            right: 30,
            left: 0,
            bottom: 0,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
          <XAxis dataKey="day" label={{ value: 'Days', position: 'insideBottomRight', offset: -5 }} axisLine={false} tickLine={false} />
          <YAxis label={{ value: 'Retention %', angle: -90, position: 'insideLeft' }} axisLine={false} tickLine={false} />
          <Tooltip />
          <Area type="monotone" dataKey="retention" stroke="#ef4444" fill="#fee2e2" strokeWidth={2} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ForgettingCurveChart;
