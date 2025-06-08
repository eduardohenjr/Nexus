from fastapi import FastAPI, Request, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, Dict
import requests
import os

app = FastAPI()

# Armazenamento simples em memória (por usuário)
user_contexts: Dict[str, str] = {}

# API Key para autenticação simples
API_KEY = os.environ.get("NEXUS_API_KEY", "minha-chave-secreta")

# Modelo LLM (exemplo usando OpenAI, pode adaptar para outro)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_MODEL = "gpt-3.5-turbo"


class AskRequest(BaseModel):
    question: str
    user_id: str


class ContextRequest(BaseModel):
    user_id: str
    context: str

# Middleware simples de autenticação


@app.middleware("http")
async def check_api_key(request: Request, call_next):
    api_key = request.headers.get("x-api-key")
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida")
    return await call_next(request)


@app.post("/ask")
async def ask(req: AskRequest):
    context = user_contexts.get(req.user_id, "")
    prompt = (
        "Você é o Nexus, um assistente de IA. Responda em português de forma clara e objetiva. "
        "Se a pergunta for sobre o computador, use apenas as informações fornecidas no contexto abaixo. "
        "Se não souber a resposta, diga que não tem essa informação.\n"
    )
    if context:
        prompt += f"Contexto do usuário: {context}\n"
    prompt += f"Usuário: {req.question}\nNexus:"
    # Exemplo com OpenAI (pode adaptar para outro LLM)
    if not OPENAI_API_KEY:
        return {"answer": "LLM não configurado no backend online."}
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": prompt}
        ],
        "max_tokens": 512,
        "temperature": 0.2
    }
    try:
        resp = requests.post(OPENAI_URL, headers=headers,
                             json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        answer = data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        answer = f"Erro ao consultar o LLM: {e}"
    return {"answer": answer}


@app.post("/update-context")
async def update_context(req: ContextRequest):
    user_contexts[req.user_id] = req.context
    return {"status": "ok"}
