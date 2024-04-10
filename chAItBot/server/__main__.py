"""
Main server entry point
"""
import os
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from server.routers.bot import router as bot
from server.routers.document import router as document_router
from server.routers.category_database import router as category_database_router
from server.routers.knowledge_database import router as knowledge_database_router
from server.routers.unanswered_questions import router as unanswered_questions_router
from server.routers.setting import router as setting_router

app = FastAPI(allow_query_parameters=False)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("BACKOFFICE_URL")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bot, prefix="/api/v1/Chatbot", tags=["Bot"])
app.include_router(unanswered_questions_router, prefix="/api/v1/QuestionWithoutAnswer", tags=["UnansweredQuestions"])
app.include_router(category_database_router, prefix="/api/v1/Category", tags=["Category"])
app.include_router(knowledge_database_router, prefix="/api/v1/KnowledgeBase", tags=["KnowledgeBase"])
app.include_router(setting_router, prefix="/api/v1/Setting", tags=["Setting"])
app.include_router(document_router, prefix="/api/v1/document", tags=["files"])


# Main entry point.
# Used mainly for debugging purposes.
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
