# Travel Assistant Project Instructions

This project creates a conversational AI travel assistant for Southeast Asia trip planning using:
- React frontend with chatbot interface
- Python backend with RAG using LangChain and OpenAI
- Document storage for travel plans
- Conversation history management

## Project Structure
- `/frontend` - React chatbot interface
- `/backend` - Python Flask API with RAG
- `/travel_plans` - User travel documents storage
- `/documents` - RAG knowledge base documents

## Development Guidelines
- Follow React best practices for frontend components
- Use proper error handling for API calls
- Implement secure API key management
- Ensure responsive design for mobile devices
- Use TypeScript for better code quality

## API Endpoints
- POST /chat - Main chat interface
- GET /history - Retrieve conversation history  
- DELETE /history - Clear conversation history
- POST /documents - Upload travel documents

## Environment Variables Required
- OPENAI_API_KEY
- FLASK_ENV
- FRONTEND_URL (for CORS)