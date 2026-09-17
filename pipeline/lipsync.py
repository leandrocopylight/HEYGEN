import os
import subprocess
import torch

def run_wav2lip(image_or_video_path: str, audio_path: str, output_path: str = "output_lip.mp4", checkpoint_path: str = "checkpoints/wav2lip_gan.pth") -> str:
    """Executa sincronização labial usando Wav2Lip-GAN."""
    if not os.path.exists(image_or_video_path):
        raise FileNotFoundError(f"Arquivo visual não encontrado: {image_or_video_path}")
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Arquivo de áudio não encontrado: {audio_path}")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    cmd = [
        "python", "Wav2Lip/inference.py",
        "--checkpoint_path", checkpoint_path,
        "--face", image_or_video_path,
        "--audio", audio_path,
        "--outfile", output_path,
        "--pads", "0", "10", "0", "0",
        "--resize_factor", "1"
    ]
    
    # Se GPU estiver disponível
    if not torch.cuda.is_available():
        cmd.append("--nosmooth")
        
    try:
        subprocess.run(cmd, check=True)
        return output_path
    except Exception as e:
        print(f"[Erro] Falha na execução do Wav2Lip: {e}")
        raise e

def run_liveportrait(image_path: str, audio_path: str, output_path: str = "output_liveportrait.mp4") -> str:
    """Executa animação e sincronia labial via LivePortrait."""
    # LivePortrait CLI runner
    cmd = [
        "python", "LivePortrait/inference.py",
        "--source_image", image_path,
        "--driving_audio", audio_path,
        "--output_dir", os.path.dirname(os.path.abspath(output_path))
    ]
    try:
        subprocess.run(cmd, check=True)
        return output_path
    except Exception as e:
        print(f"[Erro LivePortrait]: {e}")
        raise e
