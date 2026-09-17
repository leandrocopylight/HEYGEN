# Avatar Studio - Sincronizacao Labial com GPU NVIDIA T4

Interface local bonita + processamento na GPU T4 gratuita do Google Colab.

---

## Como usar (passo a passo completo)

### Parte 1: Iniciar o servidor GPU no Google Colab

1. Abra o [Google Colab](https://colab.research.google.com/)
2. Crie um novo notebook em branco
3. Va em **Ambiente de execucao > Alterar tipo de ambiente de execucao > GPU T4**
4. Crie a **Celula 1** e cole:

```python
# Instalacao (rode apenas 1 vez por sessao)
!nvidia-smi
!apt-get update -y -q && apt-get install -y -q ffmpeg
!pip install -q fastapi uvicorn python-multipart pyngrok

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
```

5. Crie a **Celula 2** e cole o conteudo do arquivo `colab_server.py` (a parte dentro das aspas triplas da CELULA 2)

6. Execute a Celula 2. Uma URL sera gerada assim:
   ```
   SERVIDOR ONLINE!
   URL PUBLICA: https://xxxx.ngrok-free.app
   ```

7. Copie essa URL.

---

### Parte 2: Rodar a interface no seu PC

**Opcao A - Instalacao automatica (recomendado):**
- Clique duas vezes no arquivo `setup.bat`
- O navegador abrira automaticamente em `http://localhost:8501`

**Opcao B - Manual:**
```bash
pip install streamlit requests
streamlit run app.py
```

---

### Parte 3: Usar o Avatar Studio

1. Na barra lateral, cole a URL do Colab (ex: `https://xxxx.ngrok-free.app`)
2. Um icone verde confirma a conexao com a GPU
3. Faca o upload da **foto ou video** do avatar
4. Faca o upload do **audio** (qualquer duracao - MP3, WAV, M4A...)
5. Clique em **Gerar Video com Sincronia Labial**
6. Acompanhe o progresso em tempo real com barra e porcentagem
7. Quando pronto, veja o video e clique em **Baixar Video**

---

## Estrutura do Projeto

```
avatar-studio-local/
├── app.py                  # Interface Streamlit local (roda no seu PC)
├── colab_server.py         # Codigo do servidor GPU (roda no Colab)
├── requirements_local.txt  # Dependencias locais
├── setup.bat               # Instalador Windows (1 clique)
└── README.md               # Este arquivo
```

---

## Tempo de Processamento Estimado (GPU T4)

| Duracao do Audio | Tempo Estimado |
|:---|:---|
| 1 minuto | ~30 segundos |
| 5 minutos | ~2 a 3 minutos |
| 20 minutos | ~8 a 12 minutos |
| 30 minutos | ~12 a 20 minutos |

---

## Licenca

Projeto educacional e de pesquisa utilizando modelos open-source.
