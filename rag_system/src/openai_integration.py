"""
OpenAI API Integration
Handles API calls to OpenAI chat models
"""
import logging
import json
from typing import Optional, Dict
from pathlib import Path
import sys

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

sys.path.append(str(Path(__file__).parent.parent))

from config.config import (
    OPENAI_API_KEY, OPENAI_MODEL, GENERATION_CONFIG, LOGS_DIR
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / "openai_api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class OpenAIAPI:
    """Wrapper for OpenAI API"""

    def __init__(self, api_key: Optional[str] = None, model_name: str = OPENAI_MODEL):
        """
        Initialize OpenAI API

        Args:
            api_key: OpenAI API key (from OPENAI_API_KEY config if not provided)
            model_name: Model name to use
        """
        self.api_key = api_key or OPENAI_API_KEY
        self.model_name = model_name
        self.temperature = GENERATION_CONFIG.get("temperature", 0.3)
        self.max_output_tokens = GENERATION_CONFIG.get("max_output_tokens", 1024)

        if OpenAI is None:
            raise ImportError(
                "openai package is not installed. Run: pip install -r requirements.txt"
            )

        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY not found. Please set it in .env file or pass as argument.\n"
                "How to get API key:\n"
                "1. Go to https://platform.openai.com/\n"
                "2. Create or open your API project\n"
                "3. Generate an API key\n"
                "4. Add to .env: OPENAI_API_KEY=your_key_here"
            )

        self.client = OpenAI(api_key=self.api_key)
        logger.info(f"[OK] OpenAI API initialized with model: {self.model_name}")

    def generate_response(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
        Generate response from OpenAI API

        Args:
            prompt: Input prompt
            system_instruction: Optional system instruction/context

        Returns:
            Generated response text
        """
        try:
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_output_tokens,
            )

            text = response.choices[0].message.content if response.choices else None
            if not text:
                logger.warning("Empty response from OpenAI API")
                return "I couldn't generate a response. Please try again."

            return text.strip()

        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            raise

    def generate_rag_response(self, question: str, context: str) -> str:
        """
        Generate RAG response using retrieved context
        """
        from config.config import SYSTEM_PROMPT

        prompt = SYSTEM_PROMPT.format(context=context, question=question)
        logger.info(f"Generating RAG response with OpenAI for: {question[:50]}...")
        return self.generate_response(prompt)

    def evaluate_answer(self, user_answer: str, retrieved_answer: str) -> Dict:
        """
        Evaluate user answer against retrieved correct answer
        """
        evaluation_prompt = f"""You are an expert evaluator. Compare the two answers and provide evaluation in JSON format.

USER ANSWER: "{user_answer}"

CORRECT ANSWER: "{retrieved_answer}"

Provide your evaluation as JSON with these fields:
1. "similarity_score" (0-1): How similar are the answers in meaning?
2. "correctness" ("correct"/"partially_correct"/"incorrect"): Assessment of correctness
3. "confidence" (0-1): Your confidence in this assessment
4. "explanation": Brief explanation of differences if any

Return ONLY valid JSON, no other text."""

        response = self.generate_response(evaluation_prompt)

        try:
            import re
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass

        return {
            "similarity_score": 0.5,
            "correctness": "unknown",
            "confidence": 0.0,
            "explanation": "Could not parse evaluation JSON"
        }

    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            response = self.generate_response("Say 'API connection successful' in one sentence.")
            logger.info(f"[OK] API connection successful: {response[:60]}...")
            return True
        except Exception as e:
            logger.error(f"[ERROR] API connection failed: {str(e)}")
            return False

    def get_model_info(self) -> Dict:
        """Return basic model info"""
        return {"name": self.model_name}


def test_openai_setup(api_key: Optional[str] = None) -> bool:
    """
    Test OpenAI API setup

    Args:
        api_key: Optional API key to test

    Returns:
        True if setup is successful
    """
    try:
        api = OpenAIAPI(api_key=api_key)
        success = api.test_connection()
        if success:
            logger.info("=" * 60)
            logger.info("OpenAI API Setup: [OK] SUCCESS")
            logger.info("=" * 60)
        return success
    except Exception as e:
        logger.error(f"Setup test failed: {str(e)}")
        return False


if __name__ == "__main__":
    logger.info("OpenAI API Integration Module Ready")
