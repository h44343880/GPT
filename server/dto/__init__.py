from pydantic import BaseModel, Field

class GPTAudioRequest(BaseModel):
    question: str = Field(..., description="Question for ChatGPT")
