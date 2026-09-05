from app.models.ai_generation import AIGeneration
from app.repositories.base import BaseRepository


class AIGenerationRepository(BaseRepository[AIGeneration]):
    model = AIGeneration
