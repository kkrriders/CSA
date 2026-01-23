import { useEffect, useState } from 'react';
import { Clock } from 'lucide-react';

interface TimerProps {
  seconds: number;
  onTimeUp?: () => void;
}

export default function Timer({ seconds, onTimeUp }: TimerProps) {
  const [timeLeft, setTimeLeft] = useState(seconds);

  useEffect(() => {
    setTimeLeft(seconds);
  }, [seconds]);

  useEffect(() => {
    if (timeLeft <= 0) {
      onTimeUp?.();
      return;
    }

    const timer = setInterval(() => {
      setTimeLeft((prev) => prev - 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [timeLeft, onTimeUp]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className={`flex items-center gap-2 font-mono text-xl font-bold ${
      timeLeft < 60 ? 'text-red-600' : 'text-blue-600'
    }`}>
      <Clock className="w-5 h-5" />
      {formatTime(timeLeft)}
    </div>
  );
}
