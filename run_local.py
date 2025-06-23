#!/usr/bin/env python3
"""
Local development script for running the BiteSpeed Identity Reconciliation API
Uses PostgreSQL as configured in the .env file
"""

import os
import sys
import uvicorn
from sqlalchemy import create_engine
from database import Base


def setup_database():
    """Create database tables"""
    from config import DATABASE_URL
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


def main():
    """Main function to run the application"""
    print("Setting up BiteSpeed Identity Reconciliation API...")

    # Setup database
    setup_database()

    print("Starting FastAPI server...")
    print("API will be available at: http://localhost:8000")
    print("Documentation: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")

    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
