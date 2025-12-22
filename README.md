# Travel Assistant

A conversational AI travel assistant for planning Backpacking trips, built with React frontend and Python backend using RAG (Retrieval Augmented Generation) with LangChain and OpenAI.

## Features

- 🤖 Conversational AI chatbot interface
- 🧠 RAG-powered responses using LangChain and OpenAI
- 🗺️ Specialized knowledge about backpacker locations
- 💾 Conversation history with clear functionality  
- 📄 Document storage for travel plans
- 📱 Responsive design for mobile devices

## Project Structure

```
travel-assistant/
├── frontend/           # React TypeScript app
├── backend/            # Python Flask API
├── travel_plans/       # User travel documents storage
├── documents/          # RAG knowledge base documents
└── README.md
```

## Quick Start

### Prerequisites

- Node.js 16+ and npm
- Python 3.8+
- OpenAI API key

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create environment file:
```bash
cp .env.example .env
```

5. Add your OpenAI API key to `.env`:
```
OPENAI_API_KEY=your_openai_api_key_here
```

6. Start the backend server:
```bash
python app.py
```

The backend will run on http://localhost:5000

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will run on http://localhost:3000

## API Endpoints

- `POST /chat` - Send message to the chatbot
- `GET /history` - Retrieve conversation history
- `DELETE /history` - Clear conversation history
- `POST /documents` - Upload travel documents
- `GET /health` - Health check

## Environment Variables

### Backend (.env)
- `OPENAI_API_KEY` - Your OpenAI API key (required)
- `FLASK_ENV` - Flask environment (development/production)
- `FRONTEND_URL` - Frontend URL for CORS (default: http://localhost:3000)

## Usage

1. Open the app at http://localhost:3000
2. The assistant will greet you and ask where you'd like to travel
3. Chat about your travel plans, destinations, activities, etc.
4. Your conversation is automatically saved
5. Travel plans mentioning specific destinations are stored in `travel_plans/`
6. Use the "Clear History" button to start fresh

## Development

### Adding Knowledge Documents

Place `.txt` files in the `documents/` directory to expand the AI's knowledge base. The system will automatically process and include them in responses.

### Customizing the Assistant

Modify the default knowledge in `backend/app.py` or add specialized documents to enhance responses for specific topics.

## Technologies

- **Frontend**: React, TypeScript, CSS3
- **Backend**: Python, Flask, Flask-CORS
- **AI**: OpenAI GPT, LangChain, ChromaDB
- **Storage**: Local file system

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source and available under the MIT License.