"""
intelligence_engine.py — Structured Extraction & Conversation Coaching Engine
"""

import json
from typing import Dict, Any, List

def build_interview_analysis_prompt(transcript_text: str) -> str:
    return f"""You are the MEMENTO Conversation Analysis & Interview Coaching Engine.
Analyze the following timestamped transcript of a real-world conversation/interview.

TRANSCRIPT:
{transcript_text}

Extract the following structured sections into valid JSON:
1. "summary": A concise 2-sentence executive summary of the conversation.
2. "topics": List of main subjects discussed.
3. "questions_analysis": [
     {{"question": "...", "asker": "...", "answered_directly": true/false, "feedback": "..."}}
   ]
4. "commitments": [
     {{"who": "...", "promise": "...", "deadline": "...", "timestamp_sec": 0}}
   ]
5. "communication_mistakes": [
     {{"timestamp_sec": 0, "quote": "...", "critique": "e.g. rambled without metric / filler words / interrupted"}}
   ]
6. "strengths": [
     {{"timestamp_sec": 0, "praise": "e.g. clear technical tradeoff explained concisely"}}
   ]
7. "speaking_ratio": {{"user_pct": 45, "partner_pct": 55}}

RULES:
- Do not fabricate names, deadlines, or claims.
- Every observation must link back to what was explicitly said.
- Output ONLY valid JSON matching this schema.
"""

def parse_coaching_response(raw_json_str: str) -> Dict[str, Any]:
    try:
        # Strip potential markdown code fences
        clean = raw_json_str.strip()
        if clean.startswith("```json"):
            clean = clean[7:]
        if clean.endswith("```"):
            clean = clean[:-3]
        return json.loads(clean.strip())
    except Exception as e:
        return {"error": f"Failed to parse LLM JSON: {e}", "raw": raw_json_str}

