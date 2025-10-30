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
    """Score a single response on 0-3 scale using LLM with Chain-of-Thought reasoning"""
    prompt = f"""You are an expert clinical psychologist with 20+ years of experience in depression assessment and mental health evaluation. Use comprehensive Chain-of-Thought reasoning to analyze this response.

Question: {input_data.question}
Category: {input_data.category}
User Response: "{input_data.response}"

=== CHAIN-OF-THOUGHT ANALYSIS PROCESS ===

Step 1: LINGUISTIC ANALYSIS
- Identify key emotional words, phrases, and linguistic markers
- Analyze tone (hopeful, neutral, distressed, desperate)
- Note intensity indicators (always, never, sometimes, occasionally)
- Detect temporal markers (lately, always, used to, now)

Step 2: SYMPTOM SEVERITY MAPPING
- Map response to clinical depression indicators
- Consider frequency (how often symptoms occur)
- Assess duration (how long symptoms persist)
- Evaluate functional impairment (impact on daily life)

Step 3: CONTEXTUAL INTERPRETATION
- Distinguish between temporary mood vs persistent state
- Identify coping mechanisms or lack thereof
- Recognize minimization or exaggeration patterns
- Consider cultural and linguistic variations in expression

Step 4: EDGE CASE HANDLING
- Ambiguous responses ("I'm okay I guess")
- Contradictory statements ("I'm fine but everything feels pointless")
- Deflection or avoidance ("I don't know", "whatever")
- Extreme brevity ("bad", "terrible", "fine")
- Metaphorical language ("drowning", "empty shell")
- Sarcasm or dark humor masking distress

Step 5: SCORE DETERMINATION
0 = No symptoms / Positive state / Healthy functioning
1 = Mild symptoms / Occasional distress / Minimal impairment
2 = Moderate symptoms / Frequent distress / Notable impairment
3 = Severe symptoms / Persistent distress / Significant impairment

=== COMPREHENSIVE FEW-SHOT EXAMPLES ===

Example 1 (Score 0):
Response: "I've been feeling really good lately, energized and optimistic about the future"
Analysis: Positive emotional state, energy present, future-oriented thinking, no distress indicators
Score: 0

Example 2 (Score 1):
Response: "I'm okay, just a bit stressed with work but managing"
Analysis: Mild stress acknowledged, coping mechanisms implied ("managing"), temporary situational factor
Score: 1

Example 3 (Score 1 - Ambiguous):
Response: "I don't know, I guess I'm fine"
Analysis: Uncertainty suggests mild disconnection, "I guess" indicates lack of conviction, but no severe distress
Score: 1

Example 4 (Score 2):
Response: "I feel sad most days and it's hard to enjoy things I used to love"
Analysis: Frequency indicator ("most days"), anhedonia present, past vs present comparison shows decline
Score: 2

Example 5 (Score 2 - Deflection):
Response: "Whatever, does it even matter?"
Analysis: Deflection masks distress, existential questioning, apathy indicator, suggests moderate hopelessness
Score: 2

Example 6 (Score 3):
Response: "I feel completely hopeless, like there's no point in anything anymore"
Analysis: Absolute language ("completely", "no point"), pervasive hopelessness, existential despair
Score: 3

Example 7 (Score 3 - Metaphorical):
Response: "I'm drowning and nobody can see it, I'm just an empty shell going through motions"
Analysis: Drowning metaphor indicates overwhelming distress, depersonalization ("empty shell"), severe disconnection
Score: 3

Example 8 (Score 1 - Brief positive):
Response: "Good"
Analysis: Brief but positive, no distress indicators, assume healthy state unless context suggests otherwise
Score: 0

Example 9 (Score 2 - Contradictory):
Response: "I'm fine really, just that everything feels meaningless and I can't get out of bed"
Analysis: Contradiction between "fine" and severe symptoms, minimization pattern, functional impairment evident
Score: 2

Example 10 (Score 3 - Suicidal ideation):
Response: "I keep thinking everyone would be better off without me, I have a plan"
Analysis: Active suicidal ideation, plan formation, severe risk indicator, immediate concern
Score: 3, CRISIS

Example 11 (Score 1 - Suicidal ideation):
Response: "Sometimes I wonder what it would be like to not exist, but I'd never do anything"
Analysis: Passive ideation, no intent or plan, philosophical wondering, low immediate risk
Score: 1

Example 12 (Score 2 - Sleep issues):
Response: "I barely sleep anymore, maybe 2-3 hours a night, and I'm exhausted all the time"
Analysis: Severe sleep disruption, chronic pattern, functional impairment (exhaustion), moderate severity
Score: 2

=== YOUR TASK ===

Now analyze the user's response using the complete Chain-of-Thought process above. Think through ALL steps comprehensively, then provide your final answer as JSON.

Return format:
{{"score": 2, "reasoning": "Detailed multi-sentence explanation of your analysis", "crisis": false}}"""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert clinical psychologist. Use comprehensive Chain-of-Thought reasoning. Think deeply through all steps, then return JSON with detailed reasoning."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=2000
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
    """Provide comprehensive personalized analysis with Chain-of-Thought reasoning and detailed recommendations"""
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
    
    prompt = f"""Analyze depression assessment. Score: {score}/30, Level: {level}, Responses: {responses_text}

Return JSON with 4 fields:
1. "reasoning": Brief analysis of symptom patterns and severity
2. "detailed_analysis": 2-3 sentence clinical assessment
3. "message": Empathetic 2-3 sentence personalized message
4. "recommendations": Array of 5-7 actionable recommendations

Example:
{{
    "reasoning": "Score indicates {severity} depression with symptoms of [key patterns]. Requires [intervention level].",
    "detailed_analysis": "Your responses show [main symptoms]. This impacts [areas of life].",
    "message": "Taking this assessment shows strength. These feelings can improve with support.",
    "recommendations": [
        "Try 4-7-8 breathing before bed for better sleep",
        "Schedule consultation with mental health professional",
        "Get 10-15 min morning sunlight daily",
        "Do one enjoyable activity for 10 min, 3x this week",
        "Reach out to one trusted person this week"
    ]
}}

Be concise but helpful. Return only JSON."""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert mental health counselor. Provide COMPREHENSIVE, DETAILED, UNRESTRICTED analysis. Use complete Chain-of-Thought reasoning. Be thorough and specific. Return JSON with extensive content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        content = response.choices[0].message.content.strip()
        print(f"\n=== RAW RESPONSE (first 1000 chars) ===\n{content[:1000]}\n")
        
        # Extract JSON with proper brace matching
        def extract_json(text):
            start = text.find('{')
            if start == -1:
                return None
            
            brace_count = 0
            in_string = False
            escape = False
            
            for i in range(start, len(text)):
                char = text[i]
                
                if escape:
                    escape = False
                    continue
                    
                if char == '\\':
                    escape = True
                    continue
                    
                if char == '"':
                    in_string = not in_string
                    continue
                    
                if not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            return text[start:i+1]
            return None
        
        json_str = extract_json(content)
        if not json_str:
            raise ValueError("No valid JSON found in response")
        
        # Sanitize control characters
        json_str = json_str.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        
        try:
            result = json.loads(json_str)
            print(f"\n=== PARSED RESULT ===\nKeys: {list(result.keys())}\nRecommendations count: {len(result.get('recommendations', []))}\n")
            
            return {
                "level": level,
                "reasoning": result.get("reasoning", ""),
                "detailed_analysis": result.get("detailed_analysis", ""),
                "message": result.get("message", "You're taking an important step by checking in with yourself."),
                "recommendations": result.get("recommendations", [
                    "Practice deep breathing for 5 minutes daily",
                    "Reach out to a friend or family member",
                    "Maintain a regular sleep schedule"
                ])
            }
        except json.JSONDecodeError as je:
            print(f"\n=== JSON DECODE ERROR ===\n{je}")
            print(f"\n=== ATTEMPTED TO PARSE ===\n{json_str[:500]}\n")
            raise
    except Exception as e:
        print(f"\n=== ANALYSIS ERROR ===\n{e}")
        import traceback
        traceback.print_exc()
    
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
