from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, engine
from models import Base
from schemas import IdentifyRequest, IdentifyResponse
from services import IdentityService
import logging

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BiteSpeed Identity Reconciliation API",
    description="API for reconciling customer identities across multiple data sources",
    version="1.0.0"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/")
async def root():
    return {"message": "BiteSpeed Identity Reconciliation API"}


@app.post("/identify", response_model=IdentifyResponse)
async def identify_contact(
    request: IdentifyRequest,
    db: Session = Depends(get_db)
):
    """
    Identify and reconcile contact identities based on email and/or phone number.

    - **email**: Optional email address
    - **phoneNumber**: Optional phone number

    Returns a unified customer profile with all linked contacts.
    """
    try:
        # Validate input
        if not request.email and not request.phoneNumber:
            raise HTTPException(
                status_code=400,
                detail="At least one of email or phoneNumber must be provided"
            )

        # Create service instance and process request
        identity_service = IdentityService(db)
        result = identity_service.identify_contact(
            email=request.email,
            phone_number=request.phoneNumber
        )

        logger.info(f"Successfully identified contact: {result}")
        return IdentifyResponse(**result)

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
