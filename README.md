# TWAIN AI Backend

A FastAPI-based backend service with MongoDB integration for the TWAIN application.

## Features

- FastAPI REST API
- MongoDB database integration
- Async and sync database operations
- Persona scraping and analysis
- Campaign generation
- Content generation for multiple channels

## Setup

### Prerequisites

- Python 3.8+
- MongoDB Atlas account (or local MongoDB)

### Installation

1. Clone the repository and navigate to the backend directory:
```bash
cd twain_ai_backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   - Create a `.env` file in the root directory
   - Add your Gemini API key:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
   - The MongoDB URL is already configured in the code

### MongoDB Configuration

The MongoDB connection is configured with the following settings:
- **URL**: MongoDB Atlas cluster connection string
- **Database**: TWAIN
- **Collections**: Will be created automatically as needed

## Running the Application

### Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

- `POST /persona` - Create persona from URL and description
- `POST /ideas` - Generate outreach ideas based on persona
- `POST /create_campaign` - Create outreach campaign with content

## Database Operations

The application provides both async and sync database operations:

### Async Operations (Recommended)
- `insert_document()`
- `find_documents()`
- `update_document()`
- `delete_document()`

### Sync Operations
- `insert_document_sync()`
- `find_documents_sync()`

## Project Structure

```
twain_ai_backend/
├── app/
│   ├── config/          # Configuration settings
│   ├── controllers/     # Business logic controllers
│   ├── database/        # Database connection and utilities
│   ├── models/          # Data models
│   ├── routes/          # API route definitions
│   ├── schemas/         # Pydantic schemas
│   └── utils/           # Utility functions
├── requirements.txt      # Python dependencies
└── README.md           # This file
```

## Database Collections

The following collections will be created automatically:
- `personas` - Stored persona data
- `campaigns` - Generated campaign data
- `ideas` - Generated outreach ideas

## Error Handling

The application includes comprehensive error handling for:
- Database connection issues
- Invalid input data
- API processing errors
- MongoDB operation failures

## Logging

Database operations are logged with appropriate log levels:
- INFO: Successful operations
- ERROR: Failed operations with detailed error messages

## Security Notes

- The MongoDB connection string is hardcoded in the config for development
- For production, use environment variables and secure connection strings
- Consider implementing authentication and authorization
