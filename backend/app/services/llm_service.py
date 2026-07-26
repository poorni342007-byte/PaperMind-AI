import os
import google.generativeai as genai
from typing import Dict, Any, List

class LLMService:
    """
    Service managing communications with Google Gemini Generative AI API.
    Uses GEMINI_API_KEY from environment variables and available Gemini models.
    """

    _configured = False

    @classmethod
    def configure_gemini(cls):
        """
        Configures Gemini API key from environment variables.
        """
        if not cls._configured:
            api_key = os.getenv("GEMINI_API_KEY", "").strip()
            if api_key:
                genai.configure(api_key=api_key)
                cls._configured = True
                print("[LLMService] Gemini API configured successfully!")
            else:
                print("[LLMService] WARNING: GEMINI_API_KEY is missing from environment variables.")

    @classmethod
    async def generate_response(
        cls,
        system_prompt: str,
        user_message: str,
        preferred_models: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generates grounded response using Gemini API with automatic model fallback.
        
        Args:
            system_prompt: Grounding rules / System instructions
            user_message: Formatted prompt containing document context and user question
            preferred_models: Candidate model names to try in order
            
        Returns:
            Dict: {"success": bool, "answer": str, "model_used": str, "error": str}
        """
        cls.configure_gemini()

        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            return {
                "success": False,
                "answer": "Gemini API key is missing. Please set GEMINI_API_KEY in your .env file.",
                "model_used": None,
                "error": "GEMINI_API_KEY not set."
            }

        if preferred_models is None:
            preferred_models = [
                "gemini-2.5-flash",
                "gemini-flash-latest",
                "gemini-2.5-flash-lite",
                "gemini-2.5-pro"
            ]

        full_prompt = f"{system_prompt}\n\n{user_message}"

        last_error = ""
        for model_name in preferred_models:
            try:
                print(f"[LLMService] Sending request to Gemini API model '{model_name}'...")
                model = genai.GenerativeModel(model_name)
                
                response = model.generate_content(
                    full_prompt,
                    generation_config={
                        "temperature": 0.1,  # Low temperature for factual, grounded answers
                        "top_p": 0.9
                    }
                )

                answer_text = response.text.strip() if response and response.text else ""
                
                if answer_text:
                    print(f"[LLMService] Received response successfully from Gemini model '{model_name}'")
                    return {
                        "success": True,
                        "answer": answer_text,
                        "model_used": model_name,
                        "error": None
                    }
            except Exception as e:
                last_error = str(e)
                print(f"[LLMService] Model '{model_name}' returned error: {last_error}")
                continue

        return {
            "success": False,
            "answer": f"An error occurred while generating answer with Gemini: {last_error}",
            "model_used": None,
            "error": last_error
        }
