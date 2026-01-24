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

  const isLowTime = timeLeft < 60;

  return (
    <div 
      className={`flex items-center gap-2 font-mono text-xl font-bold transition-colors duration-300 ${
        isLowTime 
          ? 'text-red-600 dark:text-red-400 animate-pulse' 
          : 'text-blue-600 dark:text-blue-400'
      }`}
      role="timer"
      aria-live={isLowTime ? 'assertive' : 'off'}
    >
      <Clock className="w-5 h-5" aria-hidden="true" />
      <span className="sr-only">Time remaining: </span>
      {formatTime(timeLeft)}
    </div>
  );
}
