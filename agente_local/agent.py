import requests
import psutil
import platform
import time
import os

# Configurações
BACKEND_URL = os.environ.get("NEXUS_BACKEND_URL", "http://localhost:8000")
API_KEY = os.environ.get("NEXUS_API_KEY", "minha-chave-secreta")
USER_ID = os.environ.get("NEXUS_USER_ID", platform.node())
INTERVAL = int(os.environ.get("NEXUS_UPDATE_INTERVAL", 300))  # segundos


def coletar_contexto():
    info = {}
    info["sistema"] = platform.platform()
    info["cpu"] = platform.processor()
    info["ram_total_gb"] = round(psutil.virtual_memory().total / (1024**3), 2)
    info["ram_uso_gb"] = round(psutil.virtual_memory().used / (1024**3), 2)
    info["disco_total_gb"] = round(psutil.disk_usage("/").total / (1024**3), 2)
    info["disco_uso_gb"] = round(psutil.disk_usage("/").used / (1024**3), 2)
    info["arquivos_home"] = os.listdir(os.path.expanduser("~"))[
        :10]  # primeiros 10 arquivos/pastas
    return str(info)


def enviar_contexto():
    contexto = coletar_contexto()
    payload = {
        "user_id": USER_ID,
        "context": contexto
    }
    headers = {"x-api-key": API_KEY}
    try:
        resp = requests.post(f"{BACKEND_URL}/update-context",
                             json=payload, headers=headers, timeout=15)
        print(f"[Nexus Agent] Contexto enviado: {resp.status_code}")
    except Exception as e:
        print(f"[Nexus Agent] Falha ao enviar contexto: {e}")


if __name__ == "__main__":
    print(
        f"[Nexus Agent] Iniciando envio periódico de contexto para {BACKEND_URL} como {USER_ID}")
    while True:
        enviar_contexto()
        time.sleep(INTERVAL)
