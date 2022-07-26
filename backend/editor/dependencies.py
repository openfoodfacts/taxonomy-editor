from datetime import datetime
from typing import List
from pydantic import BaseModel
from neo4j import GraphDatabase         # Interface with Neo4J
import settings                         # Neo4J settings

# FastAPI
from fastapi import FastAPI, status, Response, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Pydantic: Define data schema
from pydantic import BaseModel

# Data model imports
from models import Header, Footer