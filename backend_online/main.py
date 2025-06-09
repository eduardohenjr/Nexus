from fastapi import FastAPI, Request, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import Optional, Dict
import requests
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou restrinja para ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Armazenamento simples em memória (por usuário)
user_contexts: Dict[str, str] = {}

# API Key para autenticação simples
API_KEY = os.environ.get("NEXUS_API_KEY", "minha-chave-secreta")

# Configuração do LLM local (exemplo com Ollama)
LLM_URL = os.environ.get(
    "NEXUS_LLM_URL", "http://localhost:11434/api/generate")
LLM_MODEL = os.environ.get("NEXUS_LLM_MODEL", "llama3")


class AskRequest(BaseModel):
    question: str
    user_id: str


class ContextRequest(BaseModel):
    user_id: str
    context: str


def verify_api_key(request: Request):
    api_key = request.headers.get("x-api-key")
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida")


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
    payload = {
        "model": LLM_MODEL,
        "prompt": prompt,
        "stream": False
    }
    try:
        resp = requests.post(LLM_URL, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        answer = data.get(
            "response", "Não foi possível obter resposta do modelo.")
    except Exception as e:
        answer = f"Erro ao consultar o modelo local: {e}"
    return {"answer": answer}


@app.post("/update-context")
async def update_context(req: ContextRequest, _: None = Depends(verify_api_key)):
    user_contexts[req.user_id] = req.context
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "Nexus backend online. Use /ask (POST) para perguntas e /update-context (POST) para contexto do agente local."}
