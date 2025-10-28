from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from groq import Groq
import asyncio
import os
import json
import re
import base64
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
mistral_api_key = os.getenv("MISTRAL_API_KEY")

class TextInput(BaseModel):
    text: str

class ImageInput(BaseModel):
    image: str

class ResponseScore(BaseModel):
    response: str
    question: str
    category: str

class DepressionAnalysis(BaseModel):
    total_score: int
    responses: list

thinking_data = {"ocean": "", "mbti": "", "lexical": ""}

async def refine_thinking(raw_thinking: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a writing assistant. Convert technical analysis into natural explanations. Remove all references to JSON, code, formatting, or technical terms. Output ONLY the refined thinking content directly, without any introductory phrases like 'Here is' or 'The rewritten analysis'. Start immediately with the actual analysis."},
            {"role": "user", "content": f"Convert this to natural language, removing technical terms. Output only the analysis content:\n\n{raw_thinking}"}
        ],
        temperature=0.5,
        max_tokens=5000
    )
    return response.choices[0].message.content.strip()

async def analyze_ocean(text: str):
    prompt = f"""Analyze the following text for OCEAN personality traits. Use Chain of Thought reasoning.

First, think step-by-step about each trait:
- Openness (1=conventional, routine-focused | 5=creative, abstract, curious, imaginative)
- Conscientiousness (1=spontaneous, disorganized | 5=organized, disciplined, goal-oriented, reliable)
- Extraversion (1=reserved, solitary | 5=outgoing, energetic, social, talkative)
- Agreeableness (1=competitive, critical | 5=cooperative, empathetic, trusting, warm)
- Neuroticism (1=calm, stable | 5=anxious, emotional, stressed, worried)

Text: "{text}"

Think through your reasoning, then provide your final answer as JSON:
{{"openness": 3, "conscientiousness": 4, "extraversion": 2, "agreeableness": 5, "neuroticism": 1, "confidence": 0.8}}"""
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a personality analysis expert. Think step-by-step, then provide JSON at the end."},
            {"role": "user", "content": "Text: 'I love exploring new ideas and thinking outside the box. Routine bores me.'"},
            {"role": "assistant", "content": '{"openness": 5, "conscientiousness": 2, "extraversion": 3, "agreeableness": 3, "neuroticism": 2, "confidence": 0.85}'},
            {"role": "user", "content": "Text: 'I always plan everything in advance and stick to my schedule. Organization is key.'"},
            {"role": "assistant", "content": '{"openness": 2, "conscientiousness": 5, "extraversion": 3, "agreeableness": 3, "neuroticism": 1, "confidence": 0.9}'},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=10000
    )
    
    content = response.choices[0].message.content.strip()
    if not content:
        raise ValueError("Empty response from model")
    
    json_start = content.rfind('{')
    if json_start > 0:
        raw_thinking = content[:json_start].strip()
        thinking_data["ocean"] = raw_thinking
    
    match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
    if match:
        return json.loads(match.group())
    raise ValueError(f"No valid JSON found in response: {content[:200]}")

async def analyze_mbti(text: str):
    prompt = f"""Analyze the following text for MBTI dimensions. Use Chain of Thought reasoning.

Think step-by-step about each dimension:
- E/I: Extraversion(-5: very outgoing, social) to Introversion(+5: very reserved, reflective)
- S/N: Sensing(-5: concrete, practical, detail-focused) to Intuition(+5: abstract, theoretical, big-picture)
- T/F: Thinking(-5: logical, objective, analytical) to Feeling(+5: empathetic, values-driven, personal)
- J/P: Judging(-5: structured, planned, decisive) to Perceiving(+5: flexible, spontaneous, adaptable)

Text: "{text}"

Think through your reasoning, determine the 4-letter type, then provide JSON:
{{"ei": 2, "sn": -3, "tf": 1, "jp": -2, "type": "INFP", "confidence": 0.7}}"""
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a personality analysis expert. Think step-by-step, then provide JSON at the end."},
            {"role": "user", "content": "Text: 'I prefer deep conversations over small talk. Abstract concepts fascinate me.'"},
            {"role": "assistant", "content": '{"ei": 3, "sn": 4, "tf": 1, "jp": 0, "type": "INFJ", "confidence": 0.8}'},
            {"role": "user", "content": "Text: 'I love parties and meeting new people! Life is about having fun and being spontaneous.'"},
            {"role": "assistant", "content": '{"ei": -4, "sn": -1, "tf": 2, "jp": 3, "type": "ENFP", "confidence": 0.85}'},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=10000
    )
    
    content = response.choices[0].message.content.strip()
    if not content:
        raise ValueError("Empty response from model")
    
    json_start = content.rfind('{')
    if json_start > 0:
        raw_thinking = content[:json_start].strip()
        thinking_data["mbti"] = raw_thinking
    
    match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
    if match:
        return json.loads(match.group())
    raise ValueError(f"No valid JSON found in response: {content[:200]}")

async def analyze_lexical(text: str):
    prompt = f"""Analyze the following text for lexical features. Use Chain of Thought reasoning.

Think step-by-step about each feature:
- Formality (1=casual, slang, contractions | 5=formal, professional, proper grammar)
- Emotional Intensity (1=neutral, detached, factual | 5=passionate, expressive, emotional)
- Complexity (1=simple vocabulary, short sentences | 5=sophisticated vocabulary, complex sentences)
- Certainty (1=hesitant, uncertain, questioning | 5=confident, assertive, definitive)
- Social Orientation (1=self-focused, individual | 5=other-focused, community, relationships)

Text: "{text}"

Think through your reasoning, then provide JSON:
{{"formality": 3, "emotional_intensity": 2, "complexity": 4, "certainty": 3, "social_orientation": 5, "confidence": 0.8}}"""
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a linguistic analysis expert. Think step-by-step, then provide JSON at the end."},
            {"role": "user", "content": "Text: 'gonna meet up with friends later lol cant wait!!'"},
            {"role": "assistant", "content": '{"formality": 1, "emotional_intensity": 4, "complexity": 1, "certainty": 4, "social_orientation": 5, "confidence": 0.95}'},
            {"role": "user", "content": "Text: 'The implementation of this methodology requires careful consideration of various parameters.'"},
            {"role": "assistant", "content": '{"formality": 5, "emotional_intensity": 1, "complexity": 5, "certainty": 3, "social_orientation": 1, "confidence": 0.9}'},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=10000
    )
    
    content = response.choices[0].message.content.strip()
    if not content:
        raise ValueError("Empty response from model")
    
    json_start = content.rfind('{')
    if json_start > 0:
        raw_thinking = content[:json_start].strip()
        thinking_data["lexical"] = raw_thinking
    
    match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
    if match:
        return json.loads(match.group())
    raise ValueError(f"No valid JSON found in response: {content[:200]}")

def calculate_hybrid_score(ocean, mbti, lexical):
    ocean_avg = sum([ocean["openness"], ocean["conscientiousness"], ocean["extraversion"], 
                     ocean["agreeableness"], ocean["neuroticism"]]) / 5 * 20
    
    mbti_avg = (abs(mbti["ei"]) + abs(mbti["sn"]) + abs(mbti["tf"]) + abs(mbti["jp"])) / 4
    mbti_normalized = (mbti_avg + 5) * 10
    
    lexical_avg = sum([lexical["formality"], lexical["emotional_intensity"], lexical["complexity"],
                       lexical["certainty"], lexical["social_orientation"]]) / 5 * 20
    
    return (ocean_avg * 2 + mbti_normalized * 2 + lexical_avg * 1) / 5

async def classify_personality(ocean, mbti, lexical):
    prompt = f"""Based on the following personality analysis, create a concise personality type label (1-2 words) and a brief description (3-5 words).

OCEAN Scores:
- Openness: {ocean['openness']}/5
- Conscientiousness: {ocean['conscientiousness']}/5
- Extraversion: {ocean['extraversion']}/5
- Agreeableness: {ocean['agreeableness']}/5
- Neuroticism: {ocean['neuroticism']}/5

MBTI Type: {mbti['type']}

Lexical Features:
- Formality: {lexical['formality']}/5
- Complexity: {lexical['complexity']}/5

Provide only JSON:
{{"type": "Creative Thinker", "description": "Imaginative and analytical"}}"""
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a personality expert. Create concise, meaningful personality labels. Return only JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=100
    )
    
    content = response.choices[0].message.content.strip()
    match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
    if match:
        return json.loads(match.group())
    return {"type": "Unique Individual", "description": "Complex personality profile"}

async def extract_chat_with_mistral(base64_image: str):
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {mistral_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "pixtral-12b-2409",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Extract all messages from this WhatsApp chat screenshot. Identify messages by bubble color: GREEN bubbles are from the USER, WHITE/GRAY/BLACK bubbles are from OTHER person. Return ONLY valid JSON with this exact format: {\"user_content\": [\"message1\", \"message2\"], \"other_content\": [\"message1\", \"message2\"]}. Include only the message text, no timestamps or names."},
                            {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}"}
                        ]
                    }
                ],
                "max_tokens": 2000
            }
        )
        content = response.json()["choices"][0]["message"]["content"].strip()
        match = re.search(r'\{[^{}]*"user_content"[^{}]*"other_content"[^{}]*\}', content, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError("Failed to extract chat data")

async def analyze_social_behavior(user_messages: list, other_messages: list):
    user_text = " ".join(user_messages)
    other_text = " ".join(other_messages)
    
    prompt = f"""Analyze this person's social media behavior based on their WhatsApp messages. Use clinical psychological metrics.

User's Messages: {user_text}
Other Person's Messages: {other_text}

Analyze these clinical metrics (1-5 scale):
- Response Engagement (1=dismissive, brief | 5=engaged, detailed responses)
- Emotional Expressiveness (1=flat, minimal emotion | 5=highly expressive, emotive)
- Conversation Initiation (1=passive, reactive | 5=proactive, initiates topics)
- Social Reciprocity (1=self-focused, ignores cues | 5=balanced, reciprocal)
- Attachment Style (1=avoidant, distant | 5=secure, warm)
- Communication Clarity (1=vague, ambiguous | 5=clear, direct)
- Empathy Display (1=low empathy, dismissive | 5=high empathy, validating)
- Boundary Management (1=poor boundaries | 5=healthy boundaries)

Return JSON:
{{"response_engagement": 3, "emotional_expressiveness": 4, "conversation_initiation": 2, "social_reciprocity": 4, "attachment_style": 3, "communication_clarity": 4, "empathy_display": 5, "boundary_management": 3, "confidence": 0.8, "behavioral_summary": "Brief description"}}"""
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a clinical psychologist analyzing social media behavior patterns. Return only JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=1000
    )
    
    content = response.choices[0].message.content.strip()
    match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
    if match:
        return json.loads(match.group())
    raise ValueError("Failed to analyze behavior")

@app.post("/api/score-response")
@app.post("/score-response")
async def score_response(input_data: ResponseScore):
    """Score a single response on 0-3 scale using LLM"""
    prompt = f"""You are a clinical psychologist scoring depression assessment responses.

Question: {input_data.question}
Category: {input_data.category}
User Response: {input_data.response}

Score this response on a 0-3 scale:
0 = No symptoms / Positive state
1 = Mild symptoms / Slight concern
2 = Moderate symptoms / Notable concern  
3 = Severe symptoms / Significant concern

For example:
- "I feel great, really happy lately" = 0
- "I feel a bit down sometimes" = 1
- "I feel sad most days" = 2
- "I feel hopeless and can't see a way out" = 3

For suicidal ideation questions, be especially careful:
- No thoughts = 0
- Fleeting thoughts, wouldn't act = 1
- Frequent thoughts, considering = 2
- Active plans or strong urges = 3

Consider the intensity, frequency, and severity in the response.

Return ONLY a JSON object:
{{"score": 2, "reasoning": "Brief explanation", "crisis": false}}"""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a clinical psychologist. Score responses accurately and return only JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=200
        )
        
        content = response.choices[0].message.content.strip()
        match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
        if match:
            result = json.loads(match.group())
            score = result.get("score", 1)
            crisis = input_data.category == "suicidal_ideation" and score >= 2
            return {"score": score, "reasoning": result.get("reasoning", ""), "crisis": crisis}
        return {"score": 1, "reasoning": "Default score", "crisis": False}
    except Exception as e:
        print(f"Scoring error: {e}")
        return {"score": 1, "reasoning": "Error in scoring", "crisis": False}

@app.post("/api/analyze-depression")
@app.post("/analyze-depression")
async def analyze_depression(input_data: DepressionAnalysis):
    """Provide personalized analysis and recommendations based on total score"""
    score = input_data.total_score
    responses_text = " ".join(input_data.responses)
    
    # Determine severity level
    if score <= 5:
        level = "Minimal"
        severity = "minimal"
    elif score <= 10:
        level = "Mild"
        severity = "mild"
    elif score <= 15:
        level = "Moderate"
        severity = "moderate"
    elif score <= 20:
        level = "Moderately Severe"
        severity = "moderately_severe"
    else:
        level = "Severe"
        severity = "severe"
    
    prompt = f"""You are a compassionate mental health counselor providing personalized support.

Assessment Results:
- Total Score: {score}/30
- Severity Level: {level}
- User's Responses: {responses_text[:500]}

Provide:
1. A warm, empathetic message (2-3 sentences) acknowledging their current state
2. 3-5 specific, actionable recommendations tailored to their severity level

For {severity} level:
- Focus on practical, immediate self-care steps
- Be encouraging but realistic
- Include professional help suggestion if score > 15
- Avoid clinical jargon
- Be warm and supportive

Return JSON:
{{
    "message": "Warm, personalized message here",
    "recommendations": [
        "Specific recommendation 1",
        "Specific recommendation 2",
        "Specific recommendation 3"
    ]
}}"""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a warm, empathetic mental health counselor. Provide personalized, actionable support. Return only JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        content = response.choices[0].message.content.strip()
        match = re.search(r'\{[^{}]*"message"[^{}]*"recommendations"[^{}]*\}', content, re.DOTALL)
        if match:
            result = json.loads(match.group())
            return {
                "level": level,
                "message": result.get("message", "You're taking an important step by checking in with yourself."),
                "recommendations": result.get("recommendations", [
                    "Practice deep breathing for 5 minutes daily",
                    "Reach out to a friend or family member",
                    "Maintain a regular sleep schedule"
                ])
            }
    except Exception as e:
        print(f"Analysis error: {e}")
    
    # Fallback recommendations
    return {
        "level": level,
        "message": "You're taking an important step by checking in with yourself. That takes courage.",
        "recommendations": [
            "Try to maintain a regular sleep schedule - aim for 7-8 hours",
            "Spend 10-15 minutes outside in natural light each day",
            "Connect with someone you trust, even if just for a brief chat",
            "Engage in one activity you used to enjoy, even if you don't feel like it",
            "Consider speaking with a mental health professional" if score > 15 else "Practice self-compassion - be kind to yourself"
        ]
    }

@app.post("/api/analyze-whatsapp")
@app.post("/analyze-whatsapp")
async def analyze_whatsapp(input_data: ImageInput):
    try:
        chat_data = await extract_chat_with_mistral(input_data.image)
        analysis = await analyze_social_behavior(chat_data["user_content"], chat_data["other_content"])
        
        return {
            "chat_data": chat_data,
            "social_behavior": analysis,
            "personality_type": {
                "type": "Social Communicator",
                "description": analysis.get("behavioral_summary", "Analyzed from chat patterns")
            }
        }
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
@app.post("/analyze")
async def analyze_text(input_data: TextInput):
    text = input_data.text.strip()
    word_count = len(text.split())
    
    if word_count < 5:
        raise HTTPException(status_code=400, detail="Text must contain at least 5 words")
    if word_count > 300:
        raise HTTPException(status_code=400, detail="Text must not exceed 300 words")
    
    confidence_level = "low" if word_count < 50 else "medium" if word_count < 100 else "high"
    
    try:
        ocean, mbti, lexical = await asyncio.gather(
            analyze_ocean(text),
            analyze_mbti(text),
            analyze_lexical(text)
        )
        
        refined_ocean, refined_mbti, refined_lexical = await asyncio.gather(
            refine_thinking(thinking_data["ocean"]),
            refine_thinking(thinking_data["mbti"]),
            refine_thinking(thinking_data["lexical"])
        )
        
        hybrid_score = calculate_hybrid_score(ocean, mbti, lexical)
        personality = await classify_personality(ocean, mbti, lexical)
        
        return {
            "ocean": ocean,
            "mbti": mbti,
            "lexical": lexical,
            "hybrid_score": round(hybrid_score, 2),
            "personality_type": personality,
            "confidence_level": confidence_level,
            "word_count": word_count,
            "thinking": {
                "ocean": refined_ocean,
                "mbti": refined_mbti,
                "lexical": refined_lexical
            }
        }
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# app.mount("/", StaticFiles(directory="../", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
