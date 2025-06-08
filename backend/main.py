from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import platform
import os
import psutil

app = FastAPI()

# Permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi"


class Question(BaseModel):
    question: str


@app.post("/ask")
def ask(question: Question):
    # Instruções para o modelo
    instrucoes = (
        "Você é o Nexus, um assistente de IA local. "
        "Responda em português de forma clara e objetiva. "
        "Se a pergunta for sobre o computador, use apenas as informações fornecidas no contexto abaixo. "
        "Se não souber a resposta, diga que não tem essa informação."
    )
    # Coletar mais informações reais do sistema
    system_info = f"Sistema operacional: {platform.system()} {platform.release()}"
    cpu_info = f"CPU: {platform.processor()}"
    ram_info = f"RAM total: {round(psutil.virtual_memory().total / (1024**3), 2)} GB"
    disk = psutil.disk_usage(os.path.expanduser('~'))
    disk_info = f"Disco Home: {round(disk.total / (1024**3), 2)} GB total, {round(disk.free / (1024**3), 2)} GB livres"
    files = os.listdir(os.path.expanduser('~'))[:10]
    files_info = f"Arquivos/pastas em Home: {', '.join(files)}"
    contexto = f"{system_info}\n{cpu_info}\n{ram_info}\n{disk_info}\n{files_info}"

    # Só adiciona contexto se a pergunta for sobre a máquina
    pergunta = question.question.lower()
    if any(palavra in pergunta for palavra in ["sistema", "cpu", "ram", "memória", "disco", "arquivo", "pasta", "windows", "máquina", "computador"]):
        prompt = f"{instrucoes}\n{contexto}\nUsuário: {question.question}\nNexus:"
    else:
        prompt = f"{instrucoes}\nUsuário: {question.question}\nNexus:"

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        answer = data.get(
            "response", "Não foi possível obter resposta do modelo.")
    except Exception as e:
        answer = f"Erro ao consultar o modelo local: {e}"
    return {"answer": answer}
