"""
Google Gemini API Integration
Handles API calls to Google's Gemini LLM
"""
import logging
import json
from typing import Optional, Dict, List
import google.generativeai as genai
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from config.config import (
    GEMINI_API_KEY, GEMINI_MODEL, GENERATION_CONFIG, LOGS_DIR
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / "gemini_api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class GeminiAPI:
    """Wrapper for Google Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = GEMINI_MODEL):
        """
        Initialize Gemini API
        
        Args:
            api_key: Google API key (from GEMINI_API_KEY config if not provided)
            model_name: Model name to use
        """
        self.api_key = api_key or GEMINI_API_KEY
        self.model_name = model_name
        self.config = GENERATION_CONFIG
        
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Please set it in .env file or pass as argument.\n"
                "How to get API key:\n"
                "1. Go to https://aistudio.google.com/\n"
                "2. Click 'Get API Key' button\n"
                "3. Create a new API key\n"
                "4. Add to .env: GEMINI_API_KEY=your_key_here"
            )
        
        # Configure Gemini API
        genai.configure(api_key=self.api_key)
        
        self.model_name = self._resolve_model_name(model_name)
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=genai.types.GenerationConfig(**self.config)
        )
        
        logger.info(f"[OK] Gemini API initialized with model: {self.model_name}")
    
    def _model_supports_generate_content(self, model_name: str) -> bool:
        """Check if a model exists and supports generateContent."""
        try:
            model = genai.get_model(f"models/{model_name}")
            methods = getattr(model, "supported_generation_methods", [])
            return "generateContent" in methods
        except Exception:
            return False

    def _list_generate_content_models(self) -> List[str]:
        """List available model IDs that support generateContent."""
        try:
            available_models = []
            for model in genai.list_models():
                methods = getattr(model, "supported_generation_methods", [])
                if "generateContent" in methods:
                    name = getattr(model, "name", "")
                    if name.startswith("models/"):
                        name = name.split("/", 1)[1]
                    if name:
                        available_models.append(name)

            def preference_score(model_name: str) -> int:
                """Prefer low-latency flash models over pro/experimental variants."""
                lower_name = model_name.lower()
                score = 0
                if "flash" in lower_name:
                    score += 100
                if "2.0" in lower_name:
                    score += 40
                elif "1.5" in lower_name:
                    score += 30
                elif "2.5" in lower_name:
                    score += 20
                if "pro" in lower_name:
                    score -= 50
                if "vision" in lower_name:
                    score -= 20
                if "exp" in lower_name or "experimental" in lower_name:
                    score -= 20
                return score

            unique_models = list(dict.fromkeys(available_models))
            ranked_models = sorted(
                unique_models,
                key=lambda m: (preference_score(m), m),
                reverse=True
            )
            return ranked_models
        except Exception as e:
            logger.warning(f"Could not list Gemini models: {str(e)}")
            return []

    def _resolve_model_name(self, preferred_model: str) -> str:
        """
        Pick a working model. If the preferred model is unavailable, fall back
        to known alternatives and then to any listed generateContent model.
        """
        fallback_candidates = [
            preferred_model,
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-pro",
        ]
        candidates = list(dict.fromkeys(fallback_candidates))

        for candidate in candidates:
            if self._model_supports_generate_content(candidate):
                if candidate != preferred_model:
                    logger.warning(
                        f"Configured model '{preferred_model}' is unavailable. "
                        f"Falling back to '{candidate}'."
                    )
                return candidate

        listed_models = self._list_generate_content_models()
        if listed_models:
            fallback = listed_models[0]
            logger.warning(
                f"Could not validate preferred model '{preferred_model}'. "
                f"Falling back to available model '{fallback}'."
            )
            return fallback

        logger.warning(
            f"Could not validate model '{preferred_model}'. Using it as-is."
        )
        return preferred_model

    def generate_response(self, prompt: str, 
                         system_instruction: Optional[str] = None) -> str:
        """
        Generate response from Gemini API
        
        Args:
            prompt: Input prompt
            system_instruction: System instruction/context
            
        Returns:
            Generated response text
        """
        try:
            if system_instruction:
                self.model = genai.GenerativeModel(
                    model_name=self.model_name,
                    generation_config=genai.types.GenerationConfig(**self.config),
                    system_instruction=system_instruction
                )
            
            logger.debug(f"Sending prompt to Gemini: {prompt[:100]}...")
            
            response = self.model.generate_content(prompt)
            
            if not response.text:
                logger.warning("Empty response from Gemini API")
                return "I couldn't generate a response. Please try again."
            
            logger.debug(f"Received response: {response.text[:100]}...")
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}")
            raise
    
    def generate_rag_response(self, question: str, context: str) -> str:
        """
        Generate RAG response using retrieved context
        
        Args:
            question: User question
            context: Retrieved context from vector DB
            
        Returns:
            Generated response
        """
        from config.config import SYSTEM_PROMPT
        
        # Format prompt with context and question
        prompt = SYSTEM_PROMPT.format(context=context, question=question)
        
        logger.info(f"Generating RAG response for: {question[:50]}...")
        
        return self.generate_response(prompt)
    
    def evaluate_answer(self, user_answer: str, retrieved_answer: str) -> Dict:
        """
        Evaluate user answer against retrieved correct answer
        
        Args:
            user_answer: User's answer
            retrieved_answer: Correct answer from knowledge base
            
        Returns:
            Evaluation results as dictionary
        """
        evaluation_prompt = f"""You are an expert evaluator. Compare the two answers and provide evaluation in JSON format.

USER ANSWER: \"{user_answer}\"

CORRECT ANSWER: \"{retrieved_answer}\"

Provide your evaluation as JSON with these fields:
1. \"similarity_score\" (0-1): How similar are the answers in meaning?
2. \"correctness\" (\"correct\"/\"partially_correct\"/\"incorrect\"): Assessment of correctness
3. \"confidence\" (0-1): Your confidence in this assessment
4. \"explanation\": Brief explanation of differences if any

Return ONLY valid JSON, no other text."""
        
        logger.info("Evaluating answer with Gemini...")
        
        response = self.generate_response(evaluation_prompt)
        
        # Parse JSON response
        try:
            # Find JSON in response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                logger.info(f"Evaluation result: {result}")
                return result
            else:
                logger.error(f"No JSON found in response: {response}")
                return {
                    "similarity_score": 0.5,
                    "correctness": "unknown",
                    "confidence": 0.0,
                    "explanation": "Could not parse evaluation"
                }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse evaluation JSON: {str(e)}")
            return {
                "similarity_score": 0.5,
                "correctness": "unknown",
                "confidence": 0.0,
                "explanation": f"Parsing error: {str(e)}"
            }
    
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            logger.info("Testing Gemini API connection...")
            response = self.generate_response("Say 'API connection successful' in one sentence.")
            logger.info(f"[OK] API connection successful: {response[:50]}...")
            return True
        except Exception as e:
            logger.error(f"[ERROR] API connection failed: {str(e)}")
            return False
    
    def get_model_info(self) -> Dict:
        """Get information about the model"""
        try:
            model = genai.get_model(f"models/{self.model_name}")
            return {
                "name": model.name,
                "display_name": model.display_name,
                "description": model.description,
                "input_token_limit": model.input_token_limit,
                "output_token_limit": model.output_token_limit,
            }
        except Exception as e:
            logger.error(f"Error getting model info: {str(e)}")
            return {}


def test_gemini_setup(api_key: Optional[str] = None) -> bool:
    """
    Test Gemini API setup
    
    Args:
        api_key: Optional API key to test
        
    Returns:
        True if setup is successful
    """
    try:
        api = GeminiAPI(api_key=api_key)
        success = api.test_connection()
        
        if success:
            logger.info("=" * 60)
            logger.info("Gemini API Setup: [OK] SUCCESS")
            logger.info("=" * 60)
            
            # Show model info
            model_info = api.get_model_info()
            if model_info:
                logger.info(f"Model: {model_info.get('display_name', 'Unknown')}")
                logger.info(f"Input limit: {model_info.get('input_token_limit', 'Unknown')} tokens")
                logger.info(f"Output limit: {model_info.get('output_token_limit', 'Unknown')} tokens")
        
        return success
        
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        logger.info("\nTo set up Gemini API:")
        logger.info("1. Go to https://aistudio.google.com/")
        logger.info("2. Click 'Get API Key' button")
        logger.info("3. Create a new API key")
        logger.info("4. Create .env file in project root:")
        logger.info("   GEMINI_API_KEY=your_key_here")
        return False
    except Exception as e:
        logger.error(f"Setup test failed: {str(e)}")
        return False


if __name__ == "__main__":
    logger.info("Gemini API Integration Module Ready")

