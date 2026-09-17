import os
import gradio as gr
from pipeline.tts import AVAILABLE_VOICES, generate_speech
from pipeline.lipsync import run_wav2lip
from pipeline.enhancer import enhance_face_frames

def process_avatar(
    input_image_or_video,
    audio_mode,
    input_text,
    selected_voice,
    uploaded_audio,
    enable_enhancer,
    fidelity_weight
):
    """Função principal que orquestra todo o pipeline."""
    if input_image_or_video is None:
        raise gr.Error("Por favor, envie uma foto ou vídeo do avatar.")

    os.makedirs("workspace/temp", exist_ok=True)
    os.makedirs("workspace/output", exist_ok=True)

    # 1. Obter ou Gerar Áudio
    if audio_mode == "Digitar Texto (TTS)":
        if not input_text or len(input_text.strip()) == 0:
            raise gr.Error("Por favor, digite o texto que o avatar deve falar.")
        audio_path = "workspace/temp/tts_audio.wav"
        voice_id = AVAILABLE_VOICES.get(selected_voice, "pt-BR-AntonioNeural")
        generate_speech(input_text, voice_name=voice_id, output_path=audio_path)
    else:
        if uploaded_audio is None:
            raise gr.Error("Por favor, envie um arquivo de áudio.")
        audio_path = uploaded_audio

    # 2. Executar Sincronia Labial
    raw_video_output = "workspace/temp/raw_lip.mp4"
    run_wav2lip(
        image_or_video_path=input_image_or_video,
        audio_path=audio_path,
        output_path=raw_video_output
    )

    # 3. Aplicar Restauração Facial (CodeFormer) se solicitado
    final_output_path = "workspace/output/final_avatar.mp4"
    if enable_enhancer:
        enhanced = enhance_face_frames(
            video_path=raw_video_output,
            output_path=final_output_path,
            fidelity_weight=fidelity_weight
        )
        return enhanced
    else:
        return raw_video_output

def create_ui():
    custom_css = """
    .gradio-container { font-family: 'Inter', sans-serif; }
    .header-box { text-align: center; margin-bottom: 20px; }
    """
    
    with gr.Blocks(title="AI Avatar Studio (HeyGen Open-Source)", css=custom_css, theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            """
            # 🎬 AI Avatar Studio (HeyGen Open-Source)
            ### Gere vídeos de avatares falantes ultra-realistas com sincronia labial e restauração facial em alta definição.
            """
        )
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 1. Avatar Visual")
                media_input = gr.Image(type="filepath", label="Foto do Avatar (ou Vídeo Base)")
                
                gr.Markdown("### 2. Áudio / Fala")
                audio_type = gr.Radio(
                    choices=["Digitar Texto (TTS)", "Enviar Arquivo de Áudio"],
                    value="Digitar Texto (TTS)",
                    label="Modo de Áudio"
                )
                
                text_prompt = gr.Textbox(
                    label="Texto a ser falado",
                    placeholder="Olá! Seja muito bem-vindo a este projeto de inteligência artificial...",
                    lines=3
                )
                
                voice_dropdown = gr.Dropdown(
                    choices=list(AVAILABLE_VOICES.keys()),
                    value="Português (Brasil) - Antônio (Masculino Natural)",
                    label="Voz do Avatar"
                )
                
                audio_file = gr.Audio(
                    type="filepath",
                    label="Upload de Áudio (se selecionado)",
                    visible=True
                )

                gr.Markdown("### 3. Melhoria Facial (Upscaler)")
                use_enhancer = gr.Checkbox(value=True, label="Ativar Restauração CodeFormer (Dentes e Pele Nítidos)")
                fidelity = gr.Slider(minimum=0.1, maximum=1.0, value=0.6, step=0.1, label="Fidelidade Facial (0.6 Recomendado)")
                
                generate_btn = gr.Button("🚀 Gerar Vídeo do Avatar", variant="primary", size="lg")

            with gr.Column(scale=1):
                gr.Markdown("### 4. Resultado Final")
                video_output = gr.Video(label="Vídeo Renderizado", autoplay=True)
                gr.Markdown("💡 *O vídeo gerado pode ser baixado em alta resolução clicando com o botão direito ou no ícone de download.*")

        generate_btn.click(
            fn=process_avatar,
            inputs=[
                media_input,
                audio_type,
                text_prompt,
                voice_dropdown,
                audio_file,
                use_enhancer,
                fidelity
            ],
            outputs=video_output
        )

    return demo

if __name__ == "__main__":
    demo = create_ui()
    # share=True cria o túnel público do Gradio para acessar remotamente
    demo.launch(share=True, debug=True)
