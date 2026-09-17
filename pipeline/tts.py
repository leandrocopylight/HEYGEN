import asyncio
import os
import edge_tts

AVAILABLE_VOICES = {
    "Português (Brasil) - Antônio (Masculino Natural)": "pt-BR-AntonioNeural",
    "Português (Brasil) - Francisca (Feminino Natural)": "pt-BR-FranciscaNeural",
    "Português (Brasil) - Thalita (Feminino Jovem)": "pt-BR-ThalitaNeural",
    "Inglês (EUA) - Guy (Masculino)": "en-US-GuyNeural",
    "Inglês (EUA) - Jenny (Feminino)": "en-US-JennyNeural",
    "Espanhol - Alvaro (Masculino)": "es-ES-AlvaroNeural",
    "Espanhol - Elvira (Feminino)": "es-ES-ElviraNeural",
}

async def _synthesize_edge_tts(text: str, voice: str, output_path: str, rate: str = "+0%", pitch: str = "+0Hz"):
    """Sintetiza áudio a partir de texto usando Edge TTS de alta fidelidade."""
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await communicate.save(output_path)
    return output_path

def generate_speech(text: str, voice_name: str = "pt-BR-AntonioNeural", output_path: str = "temp_audio.wav", rate: str = "+0%", pitch: str = "+0Hz") -> str:
    """Função síncrona para gerar áudio a partir de texto."""
    if not text or len(text.strip()) == 0:
        raise ValueError("O texto para síntese de voz não pode estar vazio.")
    
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    asyncio.run(_synthesize_edge_tts(text, voice_name, output_path, rate=rate, pitch=pitch))
    return output_path
