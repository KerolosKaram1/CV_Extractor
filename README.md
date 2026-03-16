## CV_Extractor

Production-oriented FastAPI backend that accepts CV uploads (PDF or DOCX), extracts text, and uses the Qwen LLM model via OpenRouter to extract the candidate full name and skills.

### Features

- **Upload CVs** in PDF or DOCX format.
- **Extract raw text** from CV files using:
  - `PyPDF2` for PDF.
  - `python-docx` for DOCX.
- **Call Qwen via OpenRouter** using the OpenAI-compatible SDK.
- **Structured LLM output**: the model is prompted to return strict JSON:

```json
{
  "name": "John Doe",
  "skills": ["Python", "Machine Learning", "SQL"]
}
```

### Project structure

- `src/main.py` – FastAPI application factory and app entrypoint.
- `src/api/routers/skills_router.py` – `/skills/extract` endpoint for CV skill extraction.
- `src/core/config.py` – Settings management via `pydantic-settings` loading from `.env`.
- `src/clients/llm_client.py` – OpenRouter/Qwen client using the OpenAI SDK, enforcing JSON output.
- `src/services/skill_extraction_service.py` – Orchestrates CV text reading and LLM extraction.
- `src/models/schemas.py` – Pydantic response models (`SkillsResponse`).
- `src/utils/file_utils.py` – Utilities for reading CV text from PDF/DOCX uploads.

### Environment configuration

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your_api_key_here
LLM_MODEL=qwen/qwen2.5-7b-instruct
```

### Installation

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
```

### Running the API

From the project root:

```bash
uvicorn src.main:app --reload
```

Swagger / OpenAPI docs will be available at `http://127.0.0.1:8000/docs`.

### Example request

```bash
curl -X POST "http://127.0.0.1:8000/skills/extract" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/cv.pdf"
```

Example response:

```json
{
  "name": "John Doe",
  "skills": ["Python", "Machine Learning", "SQL"]
}
```

