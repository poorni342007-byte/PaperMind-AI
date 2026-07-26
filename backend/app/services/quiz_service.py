import json
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, status

from app.config import documents_collection, quiz_history_collection
from app.services.llm_service import LLMService

class QuizService:
    """
    Business service layer managing study quizzes generation.
    Formulates prompts requesting MCQs and parses returned JSON structures.
    """

    @staticmethod
    def _clean_and_parse_json(raw_text: str) -> dict:
        """
        Cleans code fence markers (like ```json ... ```) and parses to dict.
        """
        cleaned = raw_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
            
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
            
        cleaned = cleaned.strip()
        
        try:
            return json.loads(cleaned)
        except Exception as err:
            print(f"[Quiz Service] JSON parsing error on: {cleaned[:200]}... Error: {err}")
            raise ValueError(f"Failed to parse model JSON: {str(err)}")

    @classmethod
    async def generate_quiz(cls, document_id: str, quiz_type: str, difficulty: str, current_user: dict) -> dict:
        """
        Processes quiz generation:
        1. Fetches paper extracted text.
        2. Formulates prompt requesting target questions.
        3. Invokes Gemini and parses output datasets.
        4. Logs quiz record inside MongoDB history collection.
        """
        # Validate MongoDB document ID structure
        try:
            doc_obj_id = ObjectId(document_id)
        except (InvalidId, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Document ID format provided."
            )

        # Lookup document in database
        doc = await documents_collection.find_one({"_id": doc_obj_id})
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target research document not found."
            )

        extracted_text = doc.get("extracted_text", "")
        if not extracted_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No text extracted from this PDF. Please verify extraction is complete."
            )

        # Truncate text to avoid token overflows (~40,000 characters is plenty)
        truncated_text = extracted_text[:40000]

        # Formulate instructions prompt
        prompt = f"""You are a helpful academic study assistant.
Generate a self-study quiz from the following research paper text content.
Your response MUST be formatted strictly as a single JSON object.
Do not wrap it in markdown code blocks like ```json ... ```. Just return raw JSON.

Target Quiz Type: {quiz_type} (e.g. MCQs, True/False, or Short Answer)
Target Difficulty: {difficulty} (e.g. Easy, Medium, or Hard)

=== Research Paper Text ===
{truncated_text}

=== Required Output JSON Schema ===
{{
  "questions": [
    {{
      "question": "The question text explaining a concept, formula, or detail from the paper.",
      "options": [
        "First option choice",
        "Second option choice",
        "Third option choice",
        "Fourth option choice"
      ],
      "correct_option_index": 2, // 0-indexed location of the correct answer (0, 1, 2, or 3)
      "explanation": "Detailed educator feedback explaining why option 3 is correct."
    }}
  ]
}}
"""

        print(f"[Quiz Service] Querying Gemini for structured quiz questions...")
        raw_response = LLMService.generate_response(prompt)
        
        # Check if LLMService triggered a fallback due to empty API keys
        if "simulated fallback response" in raw_response:
            # Generate mock quizzes matching schema
            quiz_data = {
                "questions": [
                    {
                        "question": f"This is a simulated fallback self-study question on the paper '{doc['filename']}'. Set GEMINI_API_KEY to retrieve live quiz sets.",
                        "options": [
                            "Simulated Choice A",
                            "Simulated Choice B",
                            "Correct Choice C (Target)",
                            "Simulated Choice D"
                        ],
                        "correct_option_index": 2,
                        "explanation": "Live queries will parse methodologies, formulas, and data coordinates dynamically."
                    }
                ]
            }
        else:
            try:
                # Clean and parse JSON response
                quiz_data = cls._clean_and_parse_json(raw_response)
            except Exception as e:
                # Fallback structure if JSON parse fails
                print(f"[Quiz Service Warning] JSON parsing failed, using recovery fallback schema: {e}")
                quiz_data = {
                    "questions": [
                        {
                            "question": "Quiz generated successfully, but the model output could not be parsed to JSON schema. Review raw text.",
                            "options": [
                                "Raw Answer Block A",
                                "Raw Answer Block B",
                                "See explanation for raw text preview",
                                "Raw Answer Block D"
                            ],
                            "correct_option_index": 2,
                            "explanation": raw_response[:200] + "..."
                        }
                    ]
                }

        # Build quiz document database record
        quiz_record = {
            "user_id": str(current_user["_id"]),
            "document_id": document_id,
            "quiz_type": quiz_type,
            "difficulty": difficulty,
            "questions": quiz_data.get("questions", []),
            "created_at": datetime.utcnow()
        }

        try:
            result = await quiz_history_collection.insert_one(quiz_record)
            quiz_record["id"] = str(result.inserted_id)
        except Exception as e:
            print(f"[Quiz Service Warning] Failed to log quiz to database: {e}")
            quiz_record["id"] = "local_only_id"

        return quiz_record

    @staticmethod
    async def get_quiz_history(current_user: dict) -> list:
        """
        Retrieves all previously generated study quizzes for the active user sorted by date.
        """
        cursor = quiz_history_collection.find({"user_id": str(current_user["_id"])}).sort("created_at", -1)
        history = []
        async for quiz in cursor:
            history.append({
                "id": str(quiz["_id"]),
                "user_id": quiz["user_id"],
                "document_id": quiz["document_id"],
                "quiz_type": quiz["quiz_type"],
                "difficulty": quiz["difficulty"],
                "questions": quiz.get("questions", []),
                "created_at": quiz["created_at"]
            })
        return history
