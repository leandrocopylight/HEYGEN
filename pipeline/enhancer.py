import os
import subprocess
import torch

def enhance_face_frames(video_path: str, output_path: str, fidelity_weight: float = 0.6) -> str:
    """
    Restaura detalhes faciais (dentes, olhos, pele) no vídeo gerado usando CodeFormer / GFPGAN.
    fidelity_weight: 0.0 (mais restauração/beleza) a 1.0 (mais fidelidade ao original).
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Vídeo de entrada não encontrado: {video_path}")

    # Se estiver no ambiente Colab com CodeFormer clonado
    codeformer_dir = "CodeFormer"
    if os.path.exists(codeformer_dir):
        cmd = [
            "python", f"{codeformer_dir}/inference_codeformer.py",
            "-w", str(fidelity_weight),
            "--input_path", video_path,
            "--bg_upsampler", "realesrgan",
            "--face_upsample",
            "-o", "results_enhanced"
        ]
        try:
            subprocess.run(cmd, check=True)
            # O CodeFormer salva os resultados na pasta results_enhanced
            expected_file = os.path.join("results_enhanced", os.path.basename(video_path))
            if os.path.exists(expected_file):
                return expected_file
        except Exception as e:
            print(f"[Aviso] Falha ao executar CodeFormer: {e}. Retornando vídeo original.")
            return video_path
    else:
        print("[Aviso] Repositório CodeFormer não detectado localmente. Pulando etapa de restauração.")
        return video_path

    return video_path
