import Link from 'next/link';
import { BookOpen, Brain, Clock, Target, TrendingUp, Award } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Brain className="w-8 h-8 text-blue-600" />
            <span className="text-2xl font-bold text-gray-900">Adaptive Learning</span>
          </div>
          <div className="flex gap-4">
            <Link
              href="/auth/login"
              className="px-4 py-2 text-gray-700 hover:text-gray-900 transition"
            >
              Login
            </Link>
            <Link
              href="/auth/register"
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Get Started
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
          Master Any Subject with
          <span className="text-blue-600"> AI-Powered Learning</span>
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Upload your study materials and get personalized questions with real exam conditions.
          AI analyzes your performance and adapts to your learning style.
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/auth/register"
            className="px-8 py-4 bg-blue-600 text-white rounded-lg text-lg font-semibold hover:bg-blue-700 transition shadow-lg"
          >
            Start Learning Free
          </Link>
          <Link
            href="/auth/login"
            className="px-8 py-4 border-2 border-gray-300 text-gray-700 rounded-lg text-lg font-semibold hover:border-gray-400 transition"
          >
            Login
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center mb-12">Why Choose Us?</h2>
        <div className="grid md:grid-cols-3 gap-8">
          <FeatureCard
            icon={<BookOpen className="w-8 h-8" />}
            title="Upload Any Material"
            description="PDF or Markdown files - AI extracts content and generates questions automatically"
          />
          <FeatureCard
            icon={<Clock className="w-8 h-8" />}
            title="Real Exam Conditions"
            description="90-second timer per question, strict navigation, no going back - just like real exams"
          />
          <FeatureCard
            icon={<Brain className="w-8 h-8" />}
            title="AI Pattern Detection"
            description="Detects if you're guessing, confused, or have knowledge gaps with smart analysis"
          />
          <FeatureCard
            icon={<Target className="w-8 h-8" />}
            title="Weakness Mapping"
            description="AI identifies your weak topics and prioritizes what you need to study most"
          />
          <FeatureCard
            icon={<TrendingUp className="w-8 h-8" />}
            title="Adaptive Targeting"
            description="Next test automatically focuses on your weak areas for maximum improvement"
          />
          <FeatureCard
            icon={<Award className="w-8 h-8" />}
            title="Detailed Explanations"
            description="AI explains why you got it wrong and helps you understand the concept"
          />
        </div>
      </section>

      {/* How It Works */}
      <section className="container mx-auto px-4 py-16 bg-white rounded-2xl shadow-lg my-16">
        <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
        <div className="grid md:grid-cols-4 gap-8">
          <Step number="1" title="Upload" description="Upload your PDF or Markdown study material" />
          <Step number="2" title="Generate" description="AI creates questions from your content" />
          <Step number="3" title="Test" description="Take timed tests with strict exam rules" />
          <Step number="4" title="Improve" description="AI analyzes and guides your improvement" />
        </div>
      </section>

      {/* CTA */}
      <section className="container mx-auto px-4 py-20 text-center">
        <h2 className="text-4xl font-bold mb-6">Ready to Transform Your Learning?</h2>
        <p className="text-xl text-gray-600 mb-8">
          Join students achieving better results with AI-powered adaptive learning
        </p>
        <Link
          href="/auth/register"
          className="px-12 py-4 bg-blue-600 text-white rounded-lg text-lg font-semibold hover:bg-blue-700 transition shadow-lg inline-block"
        >
          Get Started Now
        </Link>
      </section>

      {/* Footer */}
      <footer className="border-t bg-white mt-20">
        <div className="container mx-auto px-4 py-8 text-center text-gray-600">
          <p>&copy; 2024 Adaptive Learning Platform. Built with AI for better learning.</p>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="p-6 bg-white rounded-xl shadow-lg hover:shadow-xl transition">
      <div className="text-blue-600 mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  );
}

function Step({ number, title, description }: { number: string; title: string; description: string }) {
  return (
    <div className="text-center">
      <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
        {number}
      </div>
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  );
}
