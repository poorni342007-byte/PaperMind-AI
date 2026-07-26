import json
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, status

from app.config import documents_collection, notes_history_collection
from app.services.llm_service import LLMService

class NotesService:
    """
    Business service layer managing student study notes generations.
    Uses LLM prompts to summarize papers, parse key takeaways, 
    and build concept-def glossaries in structured JSON formats.
    """

    @staticmethod
    def _clean_and_parse_json(raw_text: str) -> dict:
        """
        Cleans markdown wrappers (like ```json ... ```) and parses strings to dicts.
        """
        cleaned = raw_text.strip()
        # Remove starting code fence blocks
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
            
        # Remove ending code fence blocks
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
            
        cleaned = cleaned.strip()
        
        try:
            return json.loads(cleaned)
        except Exception as err:
            print(f"[Notes Service] JSON parsing error on: {cleaned[:200]}... Error: {err}")
            raise ValueError(f"Failed to parse model JSON: {str(err)}")

    @classmethod
    async def generate_notes(cls, document_id: str, notes_type: str, current_user: dict) -> dict:
        """
        Processes RAG text summaries:
        1. Fetches paper extracted text.
        2. Formulates prompt instructions detailing JSON layouts.
        3. Queries LLM and parses JSON strings.
        4. Saves study notes into MongoDB history collections.
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

        # Truncate input text to avoid token overflow in standard limits (~40,000 characters is plenty)
        truncated_text = extracted_text[:40000]

        # Formulate instructions prompt
        prompt = f"""You are a helpful academic study assistant.
Generate study notes, outlines, and summaries from the following research paper text.
Your response MUST be formatted strictly as a single JSON object.
Do not wrap it in markdown code blocks like ```json ... ```. Just return raw JSON.

Target Complexity Level: {notes_type} (e.g. Simple explanation, Intermediate detail, or Exam Revision focus)

=== Research Paper Text ===
{truncated_text}

=== Required Output JSON Schema ===
{{
  "summary": "A comprehensive high-level summary of the paper in student-friendly terms.",
  "key_takeaways": [
    "First main takeaway from the paper.",
    "Second main takeaway from the paper.",
    "Third main takeaway from the paper."
  ],
  "important_concepts": [
    {{
      "concept_name": "Name of concept or key term 1",
      "definition": "Clear, simple explanation of term 1"
    }},
    {{
      "concept_name": "Name of concept or key term 2",
      "definition": "Clear, simple explanation of term 2"
    }}
  ]
}}
"""

        print(f"[Notes Service] Querying Gemini for structured study notes...")
        raw_response = LLMService.generate_response(prompt)
        
        # Check if LLMService triggered a fallback due to empty API keys
        if "simulated fallback response" in raw_response:
            # Generate mock notes matching schema
            notes_data = {
                "summary": f"This is a simulated fallback summary of the research paper '{doc['filename']}'. Set GEMINI_API_KEY in backend .env to get live generative summaries.",
                "key_takeaways": [
                    "This is a placeholder takeaway.",
                    "Live summaries will extract key figures, methodologies, and metrics dynamically."
                ],
                "important_concepts": [
                    {
                        "concept_name": "RAG",
                        "definition": "Retrieval-Augmented Generation combines search models with generation models to provide grounded answers."
                    }
                ]
            }
        else:
            try:
                # Clean and parse JSON response
                notes_data = cls._clean_and_parse_json(raw_response)
            except Exception as e:
                # Fallback structure if JSON parse fails
                print(f"[Notes Service Warning] JSON parsing failed, using recovery fallback schema: {e}")
                notes_data = {
                    "summary": "Notes generation completed successfully, but the model output could not be parsed to JSON schema. Below is raw text.",
                    "key_takeaways": ["Failed to extract takeaways list."],
                    "important_concepts": [
                        {
                            "concept_name": "Raw Output Preview",
                            "definition": raw_response[:200] + "..."
                        }
                    ]
                }

        # Build notes document database record
        notes_record = {
            "user_id": str(current_user["_id"]),
            "document_id": document_id,
            "notes_type": notes_type,
            "summary": notes_data.get("summary", ""),
            "key_takeaways": notes_data.get("key_takeaways", []),
            "important_concepts": notes_data.get("important_concepts", []),
            "created_at": datetime.utcnow()
        }

        try:
            result = await notes_history_collection.insert_one(notes_record)
            notes_record["id"] = str(result.inserted_id)
        except Exception as e:
            print(f"[Notes Service Warning] Failed to log notes to database: {e}")
            notes_record["id"] = "local_only_id"

        return notes_record

    @staticmethod
    async def get_notes_history(current_user: dict) -> list:
        """
        Retrieves all previously generated study notes for the active user sorted by date.
        """
        cursor = notes_history_collection.find({"user_id": str(current_user["_id"])}).sort("created_at", -1)
        history = []
        async for note in cursor:
            history.append({
                "id": str(note["_id"]),
                "user_id": note["user_id"],
                "document_id": note["document_id"],
                "notes_type": note["notes_type"],
                "summary": note["summary"],
                "key_takeaways": note.get("key_takeaways", []),
                "important_concepts": note.get("important_concepts", []),
                "created_at": note["created_at"]
            })
        return history
