# ================================================================
# ETAPA 2 - CORRIGIDA (Cole este código na célula da Etapa 2 do Colab)
# ================================================================

# Correção essencial: permite asyncio.run() dentro do loop já ativo do Colab
import nest_asyncio
nest_asyncio.apply()

import os, asyncio, edge_tts, subprocess, torch
import gradio as gr

AVAILABLE_VOICES = {
    'Portugues (Brasil) - Antonio (Masculino Natural)': 'pt-BR-AntonioNeural',
    'Portugues (Brasil) - Francisca (Feminino Natural)': 'pt-BR-FranciscaNeural',
    'Portugues (Brasil) - Thalita (Feminino Jovem)': 'pt-BR-ThalitaNeural',
    'Ingles (EUA) - Guy (Masculino)': 'en-US-GuyNeural',
    'Ingles (EUA) - Jenny (Feminino)': 'en-US-JennyNeural',
    'Espanhol - Alvaro (Masculino)': 'es-ES-AlvaroNeural',
    'Espanhol - Elvira (Feminino)': 'es-ES-ElviraNeural',
}

async def _synthesize_edge_tts(text, voice, output_path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)
    return output_path

def generate_speech(text, voice_name, output_path):
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_synthesize_edge_tts(text, voice_name, output_path))
    return output_path

def run_wav2lip(face_path, audio_path, output_path='workspace/temp/raw_lip.mp4'):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cmd = [
        'python', 'Wav2Lip/inference.py',
        '--checkpoint_path', 'checkpoints/wav2lip_gan.pth',
        '--face', face_path,
        '--audio', audio_path,
        '--outfile', output_path,
        '--pads', '0', '10', '0', '0',
        '--resize_factor', '1'
    ]
    subprocess.run(cmd, check=True)
    return output_path

def enhance_video(video_path, fidelity=0.6):
    cmd = [
        'python', 'CodeFormer/inference_codeformer.py',
        '-w', str(fidelity),
        '--input_path', video_path,
        '--bg_upsampler', 'realesrgan',
        '--face_upsample',
        '-o', 'workspace/output'
    ]
    subprocess.run(cmd, check=True)
    enhanced_path = os.path.join('workspace/output/results', os.path.basename(video_path))
    return enhanced_path if os.path.exists(enhanced_path) else video_path

def process_pipeline(image_input, mode, text, voice, audio_input, use_enhance, fidelity):
    if image_input is None:
        raise gr.Error('Por favor, envie uma foto ou video para o avatar!')
    os.makedirs('workspace/temp', exist_ok=True)
    os.makedirs('workspace/output', exist_ok=True)
    if mode == 'Digitar Texto (TTS)':
        if not text.strip():
            raise gr.Error('Digite o texto a ser falado.')
        audio_path = 'workspace/temp/audio.wav'
        voice_id = AVAILABLE_VOICES.get(voice, 'pt-BR-AntonioNeural')
        generate_speech(text, voice_id, audio_path)
    else:
        if not audio_input:
            raise gr.Error('Envie um arquivo de audio.')
        audio_path = audio_input
    lip_output = run_wav2lip(image_input, audio_path)
    if use_enhance:
        return enhance_video(lip_output, fidelity)
    return lip_output

with gr.Blocks(title='AI Avatar Studio', theme=gr.themes.Soft()) as demo:
    gr.Markdown('# Gere avatares realistas com sincronia labial e alta definicao.')
    with gr.Row():
        with gr.Column():
            img_in = gr.Image(type='filepath', label='Foto do Avatar')
            mode_in = gr.Radio(['Digitar Texto (TTS)', 'Enviar Arquivo de Audio'], value='Digitar Texto (TTS)', label='Modo')
            text_in = gr.Textbox(label='Texto', placeholder='Ola! Seja bem-vindo...', lines=3)
            voice_in = gr.Dropdown(list(AVAILABLE_VOICES.keys()), value='Portugues (Brasil) - Antonio (Masculino Natural)', label='Voz')
            audio_in = gr.Audio(type='filepath', label='Audio Opcional')
            enhance_in = gr.Checkbox(value=True, label='Ativar CodeFormer (dentes e olhos nitidos)')
            fid_in = gr.Slider(0.1, 1.0, value=0.6, step=0.1, label='Fidelidade Facial')
            btn = gr.Button('Gerar Video do Avatar', variant='primary', size='lg')
        with gr.Column():
            vid_out = gr.Video(label='Video Final', autoplay=True)
    btn.click(process_pipeline, inputs=[img_in, mode_in, text_in, voice_in, audio_in, enhance_in, fid_in], outputs=vid_out)

demo.launch(share=True, debug=True)
