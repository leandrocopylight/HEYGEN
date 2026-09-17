"""
=======================================================
  AVATAR STUDIO - SERVIDOR DA GPU (RODA NO GOOGLE COLAB)
=======================================================
Cole este arquivo no Google Colab e execute as celulas na ordem.
Ou abra o arquivo colab_server_notebook.py como referencia.
"""

# ============================================================
# CELULA 1: Instalar dependencias e baixar modelos (rode 1x so)
# ============================================================
"""
!nvidia-smi
!apt-get update -y -q && apt-get install -y -q ffmpeg

!pip install -q fastapi uvicorn python-multipart pyngrok requests-toolbelt

import os
if not os.path.exists("Wav2Lip"):
    !git clone -q https://github.com/Rudrabha/Wav2Lip.git

!pip install -q -r Wav2Lip/requirements.txt
!mkdir -p checkpoints Wav2Lip/checkpoints

if not os.path.exists("checkpoints/wav2lip_gan.pth"):
    !wget -q -O checkpoints/wav2lip_gan.pth https://huggingface.co/Akumzy/Wav2Lip-GAN/resolve/main/wav2lip_gan.pth
    !cp checkpoints/wav2lip_gan.pth Wav2Lip/checkpoints/

if not os.path.exists("Wav2Lip/face_detection/detection/sfd/s3fd.pth"):
    !wget -q -O Wav2Lip/face_detection/detection/sfd/s3fd.pth https://huggingface.co/Akumzy/Wav2Lip-GAN/resolve/main/s3fd-619a316848.pth

print("Instalacao concluida!")
"""

# ============================================================
# CELULA 2: Iniciar o servidor da API com tunel publico
# ============================================================
"""
import os, uuid, subprocess, threading, time, re, shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import uvicorn
from pyngrok import ngrok

app = FastAPI(title="Avatar Studio GPU Server")
JOBS = {}
os.makedirs("/tmp/avatar_jobs", exist_ok=True)

def wav2lip_com_progresso(job_id, face_path, audio_path, output_path):
    try:
        JOBS[job_id].update({"status": "processing", "progress": 5, "message": "Iniciando Wav2Lip na GPU T4..."})
        cmd = [
            "python", "Wav2Lip/inference.py",
            "--checkpoint_path", "checkpoints/wav2lip_gan.pth",
            "--face", face_path,
            "--audio", audio_path,
            "--outfile", output_path,
            "--pads", "0", "10", "0", "0",
            "--resize_factor", "1"
        ]
        processo = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        total_frames = None
        frames_feitos = 0
        for linha in processo.stdout:
            linha = linha.strip()
            JOBS[job_id]["log"] = linha

            # Detectar total de frames
            m = re.search(r"Length of mel chunks: (\d+)", linha)
            if m:
                total_frames = int(m.group(1))

            # Detectar progresso
            m2 = re.search(r"(\d+)it", linha)
            if m2 and total_frames:
                frames_feitos = int(m2.group(1))
                pct = min(int((frames_feitos / total_frames) * 90) + 5, 95)
                tempo = None
                m3 = re.search(r"(\d+:\d+)<", linha)
                if m3:
                    tempo = m3.group(1)
                JOBS[job_id].update({
                    "progress": pct,
                    "message": f"Processando frames: {frames_feitos}/{total_frames or '?'} {'- restante: ' + tempo if tempo else ''}",
                })

        processo.wait()
        if processo.returncode == 0 and os.path.exists(output_path):
            JOBS[job_id].update({"status": "done", "progress": 100, "message": "Video pronto! Clique em Baixar Video."})
        else:
            JOBS[job_id].update({"status": "error", "progress": 0, "message": "Erro no Wav2Lip. Verifique a foto/audio."})
    except Exception as e:
        JOBS[job_id].update({"status": "error", "progress": 0, "message": f"Erro: {str(e)}"})

@app.get("/")
def raiz():
    return {"status": "Avatar Studio GPU Server online", "gpu": "NVIDIA T4"}

@app.post("/processar")
async def processar(foto: UploadFile = File(...), audio: UploadFile = File(...)):
    job_id = str(uuid.uuid4())[:8]
    pasta = f"/tmp/avatar_jobs/{job_id}"
    os.makedirs(pasta, exist_ok=True)

    ext_foto = Path(foto.filename).suffix or ".jpg"
    ext_audio = Path(audio.filename).suffix or ".mp3"
    face_path = f"{pasta}/foto{ext_foto}"
    audio_path = f"{pasta}/audio{ext_audio}"
    output_path = f"{pasta}/avatar_final.mp4"

    with open(face_path, "wb") as f:
        f.write(await foto.read())
    with open(audio_path, "wb") as f:
        f.write(await audio.read())

    JOBS[job_id] = {
        "status": "queued",
        "progress": 0,
        "message": "Na fila... aguardando GPU",
        "log": "",
        "face": face_path,
        "audio": audio_path,
        "output": output_path
    }

    t = threading.Thread(target=wav2lip_com_progresso, args=(job_id, face_path, audio_path, output_path))
    t.daemon = True
    t.start()

    return {"job_id": job_id, "mensagem": "Processamento iniciado na GPU T4!"}

@app.get("/status/{job_id}")
def status(job_id: str):
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job nao encontrado")
    j = JOBS[job_id]
    return {
        "status": j["status"],
        "progress": j["progress"],
        "message": j["message"],
    }

@app.get("/baixar/{job_id}")
def baixar(job_id: str):
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job nao encontrado")
    output_path = JOBS[job_id]["output"]
    if os.path.exists(output_path):
        return FileResponse(output_path, media_type="video/mp4", filename="avatar_sincronizado.mp4")
    raise HTTPException(status_code=425, detail="Video ainda nao esta pronto")

# Iniciar servidor em thread separada
def iniciar_servidor():
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")

t = threading.Thread(target=iniciar_servidor, daemon=True)
t.start()
time.sleep(3)

# Criar tunel publico com ngrok (gratis, sem conta)
# Se quiser usar cloudflared ao inves de ngrok, instale com:
# !wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared && chmod +x cloudflared
# tunel = subprocess.Popen(["./cloudflared", "tunnel", "--url", "http://localhost:8000"])

ngrok.set_auth_token("SEU_TOKEN_NGROK_AQUI")  # Opcional: crie conta gratuita em ngrok.com
url_publica = ngrok.connect(8000)
print("=" * 60)
print(f"  SERVIDOR ONLINE!")
print(f"  URL PUBLICA: {url_publica}")
print("=" * 60)
print("  Cole esta URL no campo da interface local no seu PC.")
print("  Deixe esta celula rodando enquanto usar.")
"""
