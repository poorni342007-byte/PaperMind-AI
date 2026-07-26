# Make schemas easily importable across application services and routes

from .auth import (
    UserSignupSchema,
    UserLoginSchema,
    UserResponseSchema,
    TokenSchema,
    TokenDataSchema
)
from .document import DocumentResponseSchema
from .chat import ChatRequestSchema, ChatResponseSchema
from .notes import NotesRequestSchema, NotesResponseSchema, ConceptSchema
from .quiz import (
    QuizRequestSchema,
    QuizQuestionSchema,
    QuizResponseSchema,
    QuizAttemptSubmitSchema
)
