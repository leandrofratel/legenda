import os
import whisper
from moviepy.editor import VideoFileClip
import streamlit as st

######################## Classe que legenda os vídeos ########################

class Transcrever_e_legendar:
    """Cria uma legenda ou extrai o texto do vídeo."""
    def __init__(self, video, modelo_whisper):
        """Inicializa a classe e extrai o nome do arquivo."""
        self.video = video
        self.model = whisper.load_model(modelo_whisper)
        self.video_name = os.path.splitext(os.path.basename(video))[0]

    def extrair_audio(self):
        """Recebe o arquivo de vídeo e extrai o áudio para '.wav'."""
        meu_audio = VideoFileClip(self.video).audio
        caminho_audio = f'{self.video_name}.wav'
        meu_audio.write_audiofile(caminho_audio, codec="pcm_s16le")
        return caminho_audio

    def guardar_transcricao(self, texto):
        """Guarda o arquivo transcrito em um txt."""
        nome_arquivo = f'{self.video_name}_transcricao.txt'
        with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
            arquivo.write(texto)
        return nome_arquivo

    def legendar_transcricao(self, caminho_audio):
        """Recebe um arquivo de áudio e transforma em (.srt) legenda de vídeo."""
        result = self.model.transcribe(caminho_audio)
        result_texto = result['text']
        
        # Salva a transcrição
        txt_path = self.guardar_transcricao(result_texto)
        
        # Salva o SRT
        srt_path = f'{self.video_name}.srt'
        with open(srt_path, 'w', encoding='utf-8') as arquivo:
            for i, segment in enumerate(result['segments'], start=1):
                inicio = self.format_timestamp(segment["start"])
                fim = self.format_timestamp(segment["end"])
                legenda = segment["text"].strip()
                
                arquivo.write(f'{i}\n')
                arquivo.write(f'{inicio} --> {fim}\n')
                arquivo.write(f'{legenda}\n\n')
        
        return txt_path, srt_path

    @staticmethod
    def format_timestamp(seconds):
        """Formata timestamp em HH:MM:SS,SSS para padrão SRT."""
        millis = int((seconds % 1) * 1000)
        seconds = int(seconds)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"

######################## Interface com Streamlit ########################

# Configurações do Streamlit
st.set_page_config(
    page_title="Assistente de Legenda",
    layout="wide"
)

# Título do Streamlit
st.title("Transcrição e Legendas de Vídeo com Whisper")

# Sidebar com seleção do modelo
modelo_whisper = st.sidebar.selectbox(
    "Escolha o modelo do Whisper:",
    ["tiny", "base", "small", "medium", "large"]
)

# Upload do arquivo de vídeo
video_file = st.file_uploader("Carregue um vídeo", type=["mp4", "mkv", "mov"])

if video_file is not None:
    # Salva o vídeo no disco temporariamente
    video_path = f"temp_{video_file.name}"
    with open(video_path, "wb") as f:
        f.write(video_file.getbuffer())

    # Processa o vídeo
    st.write("Processando o vídeo...")

    # Inicializa a classe com o vídeo e o modelo escolhido
    transcritor = Transcrever_e_legendar(video_path, modelo_whisper)
    
    # Extrai o áudio
    caminho_audio = transcritor.extrair_audio()
    
    # Gera a transcrição e legenda
    txt_path, srt_path = transcritor.legendar_transcricao(caminho_audio)
    
    # Exibe opções de download
    st.success("Processamento concluído!")
    
    with open(txt_path, "r") as file:
        st.download_button("Baixar Transcrição (.txt)", file, file_name=f"{txt_path}")
        
    with open(caminho_audio, "rb") as file:
        st.download_button("Baixar Áudio (.wav)", file, file_name=f"{caminho_audio}")
    
    with open(srt_path, "r") as file:
        st.download_button("Baixar Legendas (.srt)", file, file_name=f"{srt_path}")
