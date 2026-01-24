import httpx
import json
from typing import List, Dict, Any, Optional
from app.core.config import get_settings

settings = get_settings()


class LLMService:
    """Service to interact with various LLM providers"""

    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.client = httpx.AsyncClient(timeout=120.0)

    async def generate_completion(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate completion from LLM"""
        if self.provider == "ollama":
            return await self._ollama_completion(prompt, system_prompt)
        elif self.provider == "huggingface":
            return await self._huggingface_completion(prompt, system_prompt)
        elif self.provider == "lmstudio":
            return await self._lmstudio_completion(prompt, system_prompt)
        elif self.provider == "openrouter":
            return await self._openrouter_completion(prompt, system_prompt)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    async def _ollama_completion(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate completion using Ollama"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = await self.client.post(
                f"{settings.OLLAMA_BASE_URL}/api/chat",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "messages": messages,
                    "stream": False
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["message"]["content"]
        except Exception as e:
            raise Exception(f"Ollama API error: {str(e)}")

    async def _huggingface_completion(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate completion using HuggingFace"""
        try:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

            headers = {
                "Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}",
                "Content-Type": "application/json"
            }

            response = await self.client.post(
                f"https://api-inference.huggingface.co/models/{settings.HUGGINGFACE_MODEL}",
                headers=headers,
                json={"inputs": full_prompt, "parameters": {"max_new_tokens": 2000}}
            )
            response.raise_for_status()
            result = response.json()
            return result[0]["generated_text"]
        except Exception as e:
            raise Exception(f"HuggingFace API error: {str(e)}")

    async def _lmstudio_completion(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate completion using LM Studio"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = await self.client.post(
                f"{settings.LM_STUDIO_BASE_URL}/v1/chat/completions",
                json={
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception(f"LM Studio API error: {str(e)}")

    async def _openrouter_completion(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate completion using OpenRouter"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            headers = {
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "Adaptive Learning Platform"
            }

            response = await self.client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json={
                    "model": settings.OPENROUTER_MODEL,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception(f"OpenRouter API error: {str(e)}")

    async def generate_questions_from_context(
        self,
        context: str,
        topic: str,
        num_questions: int = 5,
        difficulty: str = "medium",
        question_type: str = "mcq"
    ) -> List[Dict[str, Any]]:
        """Generate questions from given context"""

        system_prompt = """You are an expert educational content creator. Your task is to generate high-quality questions from the provided text.

Rules:
1. Questions MUST be strictly based on the provided context
2. Do NOT create generic questions or hallucinate information
3. Questions should test understanding, not just memorization
4. For MCQs: Include 4 options with only ONE correct answer
5. Include detailed explanations
6. Return ONLY valid JSON, no additional text"""

        user_prompt = f"""
Context: {context}

Topic: {topic}
Difficulty: {difficulty}
Question Type: {question_type}
Number of Questions: {num_questions}

Generate {num_questions} {question_type} questions with {difficulty} difficulty from the above context.

Return a JSON array where each question has this structure:
{{
  "question_text": "The question text",
  "question_type": "{question_type}",
  "difficulty": "{difficulty}",
  "topic": "{topic}",
  "options": [
    {{"text": "Option A", "is_correct": false}},
    {{"text": "Option B", "is_correct": true}},
    {{"text": "Option C", "is_correct": false}},
    {{"text": "Option D", "is_correct": false}}
  ],
  "correct_answer": "The correct answer text",
  "explanation": "Why this is correct and why others are wrong",
  "source_context": "Relevant excerpt from context"
}}

IMPORTANT: Return ONLY the JSON array, no markdown, no additional text.
"""

        try:
            response = await self.generate_completion(user_prompt, system_prompt)

            # Clean response (remove markdown code blocks if present)
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            # Parse JSON
            questions = json.loads(response)

            return questions
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse LLM response as JSON: {str(e)}")
        except Exception as e:
            raise Exception(f"Question generation error: {str(e)}")

    async def explain_wrong_answer(
        self,
        question: str,
        user_answer: str,
        correct_answer: str,
        context: str,
        behavioral_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Generate detailed explanation WITH behavioral grounding

        ANTI-HALLUCINATION MEASURES:
        - Requires source context
        - Includes behavioral signals
        - Must cite specific paragraphs
        """

        # Build behavioral insight
        behavioral_note = ""
        if behavioral_context:
            time_spent = behavioral_context.get("time_spent", 0)
            skipped = behavioral_context.get("skipped", False)
            hesitation = behavioral_context.get("hesitation_count", 0)

            if skipped:
                behavioral_note = f"\n\nBehavioral note: Student skipped this question after {time_spent}s, suggesting possible avoidance or uncertainty."
            elif time_spent < 20:
                behavioral_note = f"\n\nBehavioral note: Student answered quickly ({time_spent}s), possibly guessing."
            elif time_spent > 60:
                behavioral_note = f"\n\nBehavioral note: Student spent {time_spent}s and hesitated {hesitation} times, indicating confusion."

        system_prompt = """You are a patient tutor explaining mistakes.

CRITICAL RULES:
1. Base explanation ONLY on the provided context
2. Cite specific paragraphs from context
3. Consider the student's behavior (time, hesitation, etc)
4. DO NOT hallucinate information not in the context
5. If context is insufficient, acknowledge it"""

        user_prompt = f"""
Question: {question}

Student's Answer: {user_answer}
Correct Answer: {correct_answer}
{behavioral_note}

Source Context from Document:
{context}

Provide explanation in JSON format:
{{
  "source_paragraph": "EXACT quote from context that answers this question",
  "section_reference": "Which section/paragraph this came from",
  "why_wrong": "Why student's reasoning was flawed (considering their behavior)",
  "concept_explanation": "Explain concept using ONLY information from context",
  "common_mistake": "If this is a common misconception",
  "behavioral_insight": "What their time/hesitation suggests about their understanding"
}}

CRITICAL: Quote source_paragraph EXACTLY from context. Do not invent.

Return ONLY valid JSON.
"""

        try:
            response = await self.generate_completion(user_prompt, system_prompt)

            # Clean and parse
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            explanation = json.loads(response)

            # Ensure required fields exist
            explanation.setdefault("source_paragraph", context[:200] + "...")
            explanation.setdefault("section_reference", "Source material")
            explanation.setdefault("behavioral_insight", "Based on your response pattern")

            return explanation
        except Exception as e:
            # Fallback with grounding
            return {
                "source_paragraph": context[:200] + "...",
                "section_reference": "Source material",
                "why_wrong": f"Your answer '{user_answer}' is incorrect.",
                "concept_explanation": f"The correct answer is '{correct_answer}'. Review the source context.",
                "common_mistake": "Review the concept carefully.",
                "behavioral_insight": behavioral_note if behavioral_note else "N/A"
            }

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
