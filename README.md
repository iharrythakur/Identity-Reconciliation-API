# BiteSpeed Backend Task – Identity Reconciliation

A FastAPI-based backend system for reconciling customer identities across multiple data sources. This system links customer records based on matching email addresses or phone numbers, creating unified customer profiles.

## Features

- **Identity Reconciliation**: Automatically links customer records based on matching identifiers
- **Primary/Secondary Contact Management**: Maintains a hierarchical structure with primary and secondary contacts
- **RESTful API**: Clean, documented API endpoints
- **PostgreSQL Database**: Robust relational database with proper indexing
- **Docker Support**: Easy deployment with Docker and Docker Compose
- **Database Migrations**: Alembic for schema management
- **Comprehensive Testing**: Test script with various scenarios

## Problem Statement

At BiteSpeed, we collect customer data from multiple sources. Often, these sources provide partially overlapping information. For example, one source might tell us a customer has email `foo@bar.com`, while another may say the same customer has phone number `+919999999999`.

We want to reconcile these identities to create a unified customer profile. This task involves designing a backend system to link these fragments and expose a simple API for customer identity resolution.

## Solution Overview

The system implements the following logic:

1. **New Contact Creation**: If no matching contact exists, create a new primary contact
2. **Identity Linking**: If a contact with matching email or phone number exists, link them under a single primary contact
3. **Primary Contact Selection**: The oldest contact (based on createdAt) becomes the primary
4. **Secondary Contact Management**: Other contacts become secondary, with linkedId pointing to the primary
5. **New Identifier Addition**: If a new identifier (email/phone) was submitted and not found, insert it as a secondary contact linked to the primary

## API Endpoints

### POST /identify

Identifies and reconciles contact identities based on email and/or phone number.

**Request Body:**

```json
{
  "email": "foo@bar.com",
  "phoneNumber": "+919999999999"
}
```

**Response:**

```json
{
  "primaryContactId": 3,
  "emails": ["foo@bar.com"],
  "phoneNumbers": ["+919999999999"],
  "secondaryContactIds": [1, 2]
}
```

### GET /health

Health check endpoint.

**Response:**

```json
{
  "status": "healthy"
}
```

## Database Schema

```sql
CREATE TABLE contacts (
  id SERIAL PRIMARY KEY,
  phoneNumber VARCHAR(20),
  email VARCHAR(255),
  linkedId INTEGER,
  linkPrecedence ENUM('primary', 'secondary'),
  createdAt TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updatedAt TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  deletedAt TIMESTAMP WITH TIME ZONE
);
```

## Setup Instructions

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL (if running locally)

### Option 1: Using Docker (Recommended)

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd BiteSpeed
   ```

2. **Start the services:**

   ```bash
   docker-compose up -d
   ```

3. **The API will be available at:**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs

### Option 2: Local Development

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL:**

   - Create a database named `bitespeed`
   - Update the `DATABASE_URL` in `config.py` if needed

3. **Run database migrations:**

   ```bash
   alembic upgrade head
   ```

4. **Start the application:**
   ```bash
   uvicorn main:app --reload
   ```

## Usage Examples

### Example 1: Creating First Contact

```bash
curl -X POST "http://localhost:8000/identify" \
     -H "Content-Type: application/json" \
     -d '{"email": "foo@bar.com"}'
```

**Response:**

```json
{
  "primaryContactId": 1,
  "emails": ["foo@bar.com"],
  "phoneNumbers": [],
  "secondaryContactIds": []
}
```

### Example 2: Linking Existing Contacts

```bash
curl -X POST "http://localhost:8000/identify" \
     -H "Content-Type: application/json" \
     -d '{"email": "foo@bar.com", "phoneNumber": "+919999999999"}'
```

**Response:**

```json
{
  "primaryContactId": 1,
  "emails": ["foo@bar.com"],
  "phoneNumbers": ["+919999999999"],
  "secondaryContactIds": [2]
}
```

### Example 3: Adding New Identifiers

```bash
curl -X POST "http://localhost:8000/identify" \
     -H "Content-Type: application/json" \
     -d '{"email": "newemail@example.com", "phoneNumber": "+919999999999"}'
```

**Response:**

```json
{
  "primaryContactId": 1,
  "emails": ["foo@bar.com", "newemail@example.com"],
  "phoneNumbers": ["+919999999999"],
  "secondaryContactIds": [2, 3]
}
```

## Testing

Run the test script to see various scenarios in action:

```bash
python test_api.py
```

This will demonstrate:

1. Creating first contact with email only
2. Creating second contact with phone only
3. Linking existing contacts
4. Adding new emails to existing contacts
5. Adding new phones to existing contacts
6. Creating completely new contacts
7. Error handling for invalid requests

## Edge Cases Handled

- **Circular Linking**: Prevents infinite loops in contact relationships
- **Duplicate Identifiers**: Handles cases where the same email/phone appears multiple times
- **Partial Matches**: Correctly links contacts when only one identifier matches
- **Multiple Primary Contacts**: Automatically consolidates multiple primary contacts into one
- **Soft Deletes**: Supports soft deletion with `deletedAt` field
- **Timestamp Management**: Automatically manages `createdAt` and `updatedAt` fields

## Project Structure

```
BiteSpeed/
├── main.py              # FastAPI application entry point
├── models.py            # SQLAlchemy database models
├── schemas.py           # Pydantic request/response schemas
├── services.py          # Business logic for identity reconciliation
├── database.py          # Database connection and session management
├── config.py            # Configuration settings
├── test_api.py          # Test script with various scenarios
├── requirements.txt     # Python dependencies
├── docker-compose.yml   # Docker services configuration
├── Dockerfile           # Application container definition
├── alembic.ini          # Alembic configuration
├── alembic/             # Database migration files
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
└── README.md            # This file
```

## API Documentation

Once the application is running, you can access:

- **Interactive API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative Documentation**: http://localhost:8000/redoc (ReDoc)

## Database Migrations

To create a new migration:

```bash
alembic revision --autogenerate -m "Description of changes"
```

To apply migrations:

```bash
alembic upgrade head
```

To rollback migrations:

```bash
alembic downgrade -1
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of the BiteSpeed backend task assignment.
