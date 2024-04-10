"""
Generation code service main routers.
"""
import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from code_generator.commons.logger_helper import DATE_FORMAT, FMT_NOW_DETAILS
from code_generator.service.routers.analyzer import router as analyzer
from code_generator.service.routers.generator import router as generator

logging.basicConfig(
    level=logging.INFO, format=FMT_NOW_DETAILS, datefmt=DATE_FORMAT, stream=sys.stdout
)

app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials = False
)

app.include_router(generator, prefix="/api/generate", tags=["Generator"])
app.include_router(analyzer, prefix="/api/analyze", tags=["Zip Analyzer"])
