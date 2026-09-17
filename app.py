import streamlit as st
import requests
import time
import os
import io
from pathlib import Path

# ─── Configuracao da pagina ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Avatar Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS personalizado ────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .subtitle {
        color: #888;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    .status-box {
        background: #1e1e2e;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .success-box {
        background: #1a2e1a;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        border-left: 4px solid #4caf50;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102,126,234,0.4);
    }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar: Configuracao da conexao ─────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/video-projector.png", width=70)
    st.markdown("## ⚙️ Configuracao")
    st.markdown("---")

    colab_url = st.text_input(
        "🔗 URL do Servidor Colab",
        placeholder="https://xxxx.ngrok-free.app",
        help="Cole aqui a URL gerada pelo notebook do Google Colab"
    )

    if colab_url:
        try:
            r = requests.get(f"{colab_url.rstrip('/')}/", timeout=5)
            if r.status_code == 200:
                st.success("✅ Conectado ao servidor GPU!")
                data = r.json()
                st.caption(f"GPU: {data.get('gpu', 'T4 NVIDIA')}")
            else:
                st.error("❌ Servidor nao respondeu")
        except:
            st.warning("⚠️ Nao foi possivel conectar. Verifique a URL.")

    st.markdown("---")
    st.markdown("### 📋 Como usar")
    st.markdown("""
    1. Abra o `colab_server.py` no Google Colab
    2. Selecione **GPU T4** nas configuracoes
    3. Execute as celulas em ordem
    4. Cole a URL gerada aqui em cima
    5. Faca o upload da foto e do audio
    6. Clique em **Gerar Video**!
    """)

# ─── Cabecalho ────────────────────────────────────────────────────────────────
st.markdown('<p class="main-title">🎬 Avatar Studio</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Sincronizacao labial com GPU NVIDIA T4 via Google Colab</p>', unsafe_allow_html=True)

# ─── Area principal ───────────────────────────────────────────────────────────
col_esq, col_dir = st.columns([1, 1], gap="large")

with col_esq:
    st.markdown("### 📷 Foto ou Video do Avatar")
    foto = st.file_uploader(
        "Envie a imagem do avatar",
        type=["jpg", "jpeg", "png", "mp4"],
        help="Foto (JPG/PNG) ou video curto (MP4) com o rosto do avatar"
    )
    if foto:
        if foto.type.startswith("image"):
            st.image(foto, caption="Avatar carregado", use_column_width=True)
        else:
            st.video(foto)

    st.markdown("### 🎙️ Arquivo de Audio")
    audio = st.file_uploader(
        "Envie o audio para sincronizar",
        type=["mp3", "wav", "m4a", "ogg", "flac"],
        help="Qualquer duracao - o avatar vai sincronizar os labios com este audio"
    )
    if audio:
        st.audio(audio)
        tamanho_mb = len(audio.getvalue()) / (1024 * 1024)
        st.caption(f"📁 Arquivo: {audio.name} ({tamanho_mb:.1f} MB)")

with col_dir:
    st.markdown("### 🎬 Resultado")

    # Estado da sessao
    if "job_id" not in st.session_state:
        st.session_state.job_id = None
    if "video_bytes" not in st.session_state:
        st.session_state.video_bytes = None

    # Botao gerar
    pode_gerar = bool(foto and audio and colab_url)
    if st.button("🚀 Gerar Video com Sincronia Labial", disabled=not pode_gerar):
        if not colab_url:
            st.error("Configure a URL do servidor Colab na barra lateral!")
        else:
            st.session_state.job_id = None
            st.session_state.video_bytes = None

            with st.spinner("Enviando arquivos para o servidor GPU..."):
                try:
                    foto_bytes = foto.getvalue()
                    audio_bytes = audio.getvalue()
                    resposta = requests.post(
                        f"{colab_url.rstrip('/')}/processar",
                        files={
                            "foto": (foto.name, foto_bytes, foto.type),
                            "audio": (audio.name, audio_bytes, audio.type),
                        },
                        timeout=60
                    )
                    if resposta.status_code == 200:
                        st.session_state.job_id = resposta.json()["job_id"]
                        st.success(f"✅ Job iniciado: `{st.session_state.job_id}`")
                    else:
                        st.error(f"Erro ao enviar: {resposta.text}")
                except Exception as e:
                    st.error(f"Erro de conexao: {e}")

    # Acompanhar progresso
    if st.session_state.job_id and not st.session_state.video_bytes:
        job_id = st.session_state.job_id

        st.markdown("---")
        st.markdown("#### ⏳ Progresso do Processamento")

        barra = st.progress(0)
        texto_status = st.empty()
        log_box = st.empty()
        btn_atualizar = st.empty()

        for _ in range(300):  # poll por ate 10 minutos
            try:
                r = requests.get(f"{colab_url.rstrip('/')}/status/{job_id}", timeout=10)
                dados = r.json()
                pct = dados.get("progress", 0)
                msg = dados.get("message", "...")
                status = dados.get("status", "")

                barra.progress(pct / 100)
                texto_status.markdown(f"""
                <div class="status-box">
                    <b>Status:</b> {msg}<br>
                    <b>Progresso:</b> {pct}%
                </div>
                """, unsafe_allow_html=True)

                if status == "done":
                    barra.progress(1.0)
                    texto_status.markdown("""
                    <div class="success-box">
                        ✅ <b>Video gerado com sucesso!</b>
                    </div>
                    """, unsafe_allow_html=True)

                    # Baixar video
                    vid_resp = requests.get(f"{colab_url.rstrip('/')}/baixar/{job_id}", timeout=120)
                    if vid_resp.status_code == 200:
                        st.session_state.video_bytes = vid_resp.content
                    break

                elif status == "error":
                    st.error(f"❌ Erro: {msg}")
                    break

            except Exception as e:
                log_box.warning(f"Aguardando resposta do servidor... ({e})")

            time.sleep(3)
            st.rerun()

    # Exibir video final
    if st.session_state.video_bytes:
        st.markdown("---")
        st.markdown("#### 🎬 Video Sincronizado")
        st.video(st.session_state.video_bytes)
        st.download_button(
            label="⬇️ Baixar Video (MP4)",
            data=st.session_state.video_bytes,
            file_name="avatar_sincronizado.mp4",
            mime="video/mp4",
            use_container_width=True
        )

    if not pode_gerar and not st.session_state.video_bytes:
        st.info("👈 Configure a URL do Colab e envie a foto e o audio para comecar.")
