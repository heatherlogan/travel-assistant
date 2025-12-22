# Quick Start Instructions

## ⚡ Get Started in 3 Steps

1. **Set up your OpenAI API key:**
   ```bash
   cd backend
   copy .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

2. **Start the backend server:**
   ```bash
   cd backend
   C:/Users/hlogan/Development/travel-assistant/.venv/Scripts/python.exe app.py
   ```

3. **Start the frontend (in a new terminal):**
   ```bash
   cd frontend
   npm start
   ```

## 🌐 Access the App
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## 💡 Usage Tips
- The assistant will ask where you want to travel first
- Mention specific countries/cities to save travel plans
- Use "Clear History" to start fresh conversations
- Add documents to the `/documents` folder to expand the AI's knowledge

## 🔧 Troubleshooting
- Make sure your OpenAI API key is valid and has credits
- Check that both servers are running on the correct ports
- For CORS issues, verify the FRONTEND_URL in backend/.env

Enjoy planning your adventure! 🌴✈️