import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import anthropic
from dotenv import load_dotenv
from resume import RESUME

load_dotenv()

SYSTEM_PROMPT = f"""You are an expert cover letter writer with years of experience helping candidates land interviews at top companies.

Your task: write a compelling, personalized cover letter based on the candidate's resume and a job description.

Guidelines:
- Carefully read the job description and identify the top 3-5 requirements or keywords
- Highlight the most relevant experiences and achievements from the resume that match those requirements
- Keep the letter to 3-4 paragraphs (approximately 250-350 words)
- Do NOT include date, address block, salutation, or closing signature
- Output ONLY the cover letter body paragraphs — no preamble, no meta-commentary
- Start directly with the opening paragraph

CANDIDATE RESUME:
{RESUME}"""

TONE_INSTRUCTIONS = {
    "formal": "Write in a formal, professional tone. Use sophisticated vocabulary and maintain a serious, respectful register.",
    "conversational": "Write in a warm, conversational tone. Sound approachable and human, while still being professional.",
    "enthusiastic": "Write in an enthusiastic, energetic tone. Show genuine excitement about the role and company.",
}

app = FastAPI()

api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    raise RuntimeError("ANTHROPIC_API_KEY environment variable is not set.")
client = anthropic.Anthropic(api_key=api_key)


class GenerateRequest(BaseModel):
    job_description: str
    tone: str


class GenerateResponse(BaseModel):
    cover_letter: str
    cache_hit: bool


@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    if request.tone not in TONE_INSTRUCTIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tone. Must be one of: {', '.join(TONE_INSTRUCTIONS)}",
        )

    tone_instruction = TONE_INSTRUCTIONS[request.tone]
    user_message = (
        f"Job Description:\n{request.job_description}\n\n"
        f"Tone instruction: {tone_instruction}\n\n"
        f"Write the cover letter now."
    )

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=800,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_message}],
        )
    except anthropic.APIError as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate cover letter: {e}")

    cover_letter = next(
        (block.text for block in response.content if block.type == "text"), ""
    )
    cache_hit = (getattr(response.usage, "cache_read_input_tokens", 0) or 0) > 0

    return GenerateResponse(cover_letter=cover_letter, cache_hit=cache_hit)


# Mount static files AFTER route definitions
app.mount("/", StaticFiles(directory="static", html=True), name="static")
