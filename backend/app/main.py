from backend.app.payment import router as payment_router
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.app.search import search_from_query


app = FastAPI(
    title="Agentic Commerce API",
    description="Natural language product discovery using Llama and Neo4j",
    version="1.0.0",
)
app.include_router(payment_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str


@app.get("/")
def root():
    return {
        "message": "Agentic Commerce API is running"
    }


@app.post("/search")
def search(request: SearchRequest):
    """
    Search for products using a natural-language query.

    Pipeline:
        User Query
        -> Intent Extraction
        -> Cypher Generation
        -> Neo4j Search
        -> Product Formatting
        -> Recommendation Agent
        -> Structured Response
    """

    print("\n========== API SEARCH ==========")
    print("QUERY:", request.query)

    # Basic validation
    if not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty."
        )

    try:
        response = search_from_query(request.query)

        print("PRODUCT COUNT:", response.count)
        print("SORT BY:", response.sort_by)

        return response.model_dump()

    except Exception as e:
        print("SEARCH ERROR:", str(e))

        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the search."
        )