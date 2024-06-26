from fastapi import APIRouter, HTTPException

from services.question_generator import QuestionGenerator

router = APIRouter(
    prefix="/questions",
    tags=['Generate Questions']
)

question_generator = QuestionGenerator()


@router.get("/generate_question")
async def generate_question(topic: str = "baseball"):
    try:
        question = question_generator.generate_question(topic)
        return {"question": question}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
