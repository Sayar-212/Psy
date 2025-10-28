# PsyGen - AI-Powered Psychological Analysis Platform

A comprehensive web-based psychological analysis platform that uses advanced AI models to provide personality insights, mental health assessments, and social behavior analysis.

## 🎯 Features

### 1. **Personality Analysis (PsyGen)**
- **OCEAN Model Analysis**: Evaluates Openness, Conscientiousness, Extraversion, Agreeableness, and Neuroticism
- **MBTI Type Detection**: Determines Myers-Briggs personality type (16 types)
- **Lexical Analysis**: Analyzes writing style, formality, emotional intensity, complexity, certainty, and social orientation
- **Hybrid Scoring**: Combines all three models for comprehensive personality assessment
- **Chain-of-Thought Reasoning**: Provides transparent AI reasoning for each analysis

### 2. **Mental Health Assessment (PsyMood)**
- **Depression Screening**: Interactive questionnaire based on clinical depression scales
- **AI-Powered Scoring**: Each response scored 0-3 using LLM analysis
- **Personalized Recommendations**: Tailored mental health suggestions based on severity
- **Crisis Detection**: Identifies high-risk responses requiring immediate attention
- **Severity Levels**: Minimal, Mild, Moderate, Moderately Severe, Severe (0-30 scale)

### 3. **Social Behavior Analysis (WhatsApp Chat Analyzer)**
- **Chat Extraction**: Uses Pixtral vision model to extract messages from screenshots
- **Behavioral Metrics**: Analyzes 8 clinical psychological dimensions
  - Response Engagement
  - Emotional Expressiveness
  - Conversation Initiation
  - Social Reciprocity
  - Attachment Style
  - Communication Clarity
  - Empathy Display
  - Boundary Management
- **Visual Results**: Radar charts and detailed behavioral insights

### 4. **Social Media Analysis**
- Analyzes social media content for personality traits
- Provides behavioral summaries and insights

### 5. **AI Chatbot (PsyRule)**
- Interactive mental health support chatbot
- Conversational interface for psychological guidance

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **AI Models**: 
  - Groq API (Llama 3.3 70B Versatile, Llama 3.1 8B Instant)
  - Mistral AI (Pixtral 12B for vision tasks)
- **Key Libraries**: 
  - `pydantic` for data validation
  - `httpx` for async HTTP requests
  - `uvicorn` for ASGI server

### Frontend
- **Pure HTML/CSS/JavaScript** (No frameworks)
- **Responsive Design**: Mobile-friendly interface
- **Chart.js**: For data visualization (radar charts)
- **Modern UI**: Glassmorphism effects, smooth animations

### Deployment
- **Vercel**: Configured for serverless deployment
- **CORS**: Enabled for cross-origin requests

## 📁 Project Structure

```
Psy/
├── backend/
│   ├── main.py              # FastAPI backend with all endpoints
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment variables template
├── index.html               # Landing page
├── login.html               # Authentication page
├── dashboard.html           # Main dashboard
├── psygen.html              # Personality analysis interface
├── psygen-results.html      # Personality results display
├── psymood.html             # Depression assessment interface
├── results.html             # Depression results display
├── whatsapp-chat.html       # WhatsApp chat upload interface
├── whatsapp-results.html    # Social behavior results
├── social-analyzer.html     # Social media analysis
├── social-writeup.html      # Social analysis results
├── psyrule.html             # AI chatbot interface
├── *.css                    # Styling files
├── *.js                     # JavaScript logic
├── vercel.json              # Vercel deployment config
└── README.md                # This file
```

## 🚀 Setup & Installation

### Prerequisites
- Python 3.8+
- Node.js (for local development server)
- Groq API Key
- Mistral AI API Key

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Create .env file with your API keys
GROQ_API_KEY=your_groq_api_key
MISTRAL_API_KEY=your_mistral_api_key
```

4. Run the server:
```bash
python main.py
```

Backend will run on `http://localhost:8000`

### Frontend Setup

1. Serve the frontend files using any static server:
```bash
# Using Python
python -m http.server 3000

# Or using Node.js
npx serve
```

2. Open `http://localhost:3000` in your browser

## 🔌 API Endpoints

### POST `/analyze`
Analyzes text for personality traits
- **Input**: `{"text": "your text here"}`
- **Output**: OCEAN scores, MBTI type, lexical features, hybrid score, personality type, thinking process

### POST `/analyze-whatsapp`
Analyzes WhatsApp chat screenshot
- **Input**: `{"image": "base64_encoded_image"}`
- **Output**: Extracted chat data, social behavior metrics, personality insights

### POST `/score-response`
Scores a single depression assessment response
- **Input**: `{"response": "text", "question": "text", "category": "text"}`
- **Output**: Score (0-3), reasoning, crisis flag

### POST `/analyze-depression`
Provides personalized mental health analysis
- **Input**: `{"total_score": 15, "responses": ["response1", "response2"]}`
- **Output**: Severity level, personalized message, recommendations

## 🎨 Key Features Explained

### Personality Analysis Algorithm
1. **Text Input**: User provides 5-300 words of text
2. **Parallel Analysis**: Three models run simultaneously
   - OCEAN: 5 traits scored 1-5
   - MBTI: 4 dimensions scored -5 to +5
   - Lexical: 5 features scored 1-5
3. **Hybrid Score**: Weighted combination (OCEAN×2 + MBTI×2 + Lexical×1) / 5
4. **Personality Classification**: AI generates concise personality label
5. **Transparency**: Chain-of-thought reasoning refined into natural language

### Depression Assessment Flow
1. **9 Questions**: Covering mood, interest, sleep, energy, appetite, self-worth, concentration, psychomotor, suicidal ideation
2. **AI Scoring**: Each response analyzed by LLM for 0-3 score
3. **Total Score**: Sum of all responses (0-30)
4. **Severity Mapping**:
   - 0-5: Minimal
   - 6-10: Mild
   - 11-15: Moderate
   - 16-20: Moderately Severe
   - 21-30: Severe
5. **Personalized Support**: Tailored recommendations based on severity and responses

### WhatsApp Analysis Process
1. **Image Upload**: User uploads chat screenshot
2. **Vision Extraction**: Pixtral model identifies message bubbles by color
   - Green bubbles = User messages
   - White/Gray/Black = Other person's messages
3. **Behavioral Analysis**: 8 clinical metrics evaluated
4. **Visual Results**: Radar chart + detailed insights

## 🔒 Security & Privacy

- **No Data Storage**: All analyses are performed in real-time, no data is stored
- **Client-Side Processing**: Images converted to base64 on client side
- **API Key Security**: Keys should be stored in environment variables
- **CORS Protection**: Configurable origin restrictions

## 🎯 Use Cases

- **Personal Development**: Understand your personality traits and communication style
- **Mental Health Screening**: Quick depression assessment with actionable recommendations
- **Relationship Insights**: Analyze communication patterns in relationships
- **Self-Awareness**: Gain insights into writing style and social behavior
- **Research**: Psychological research and personality studies

## ⚠️ Disclaimer

This platform is for informational and educational purposes only. It is NOT a substitute for professional mental health care. If you're experiencing severe depression, suicidal thoughts, or mental health crisis, please contact:

- **National Suicide Prevention Lifeline**: 988 (US)
- **Crisis Text Line**: Text HOME to 741741
- **International Association for Suicide Prevention**: https://www.iasp.info/resources/Crisis_Centres/

## 🤝 Contributing

This is a personal project. For suggestions or issues, please reach out to the developer.

## 📄 License

All rights reserved. This project is for educational and personal use only.

## 🔮 Future Enhancements

- User authentication and profile management
- Historical analysis tracking
- Multi-language support
- Voice input analysis
- Group chat analysis
- Integration with more psychological models
- Mobile app version

## 📧 Contact

For questions, feedback, or collaboration opportunities, please contact the project maintainer.

---

**Built with ❤️ using AI and modern web technologies**
