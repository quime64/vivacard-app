import streamlit as st
import time
from gtts import gTTS
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# Configuración básica
st.set_page_config(page_title="Cardia AI", page_icon="💌")

# --- TEXTOS Y TRADUCCIONES ---
TEXTOS = {
    "Español": {
        "titulo": "💌 Generador de Tarjetas",
        "subtitulo": "Crea tarjetas con alma en segundos.",
        "boton": "✨ Generar Archivos",
        "exito": "¡Listo! Baja y descarga tus archivos.",
        "ocasion": "Ocasión",
        "de": "De parte de:",
        "para": "Para:",
        "mensaje": "Mensaje:",
        "descarga_img": "Descargar Imagen",
        "descarga_audio": "Descargar Audio",
        "lang_code": "es"
    },
    "English": {
        "titulo": "💌 Card Generator",
        "subtitulo": "Create soulful cards in seconds.",
        "boton": "✨ Generate Files",
        "exito": "Done! Scroll down to download.",
        "ocasion": "Occasion",
        "de": "From:",
        "para": "To:",
        "mensaje": "Message:",
        "descarga_img": "Download Image",
        "descarga_audio": "Download Audio",
        "lang_code": "en"
    }
}

# --- BARRA LATERAL (CONTROLES) ---
idioma = st.sidebar.radio("Idioma / Language", ["Español", "English"])
t = TEXTOS[idioma]

st.title(t["titulo"])
st.write(t["subtitulo"])

# Entradas de datos
ocasion = st.sidebar.selectbox(t["ocasion"], ["Cumpleaños", "Amor", "Navidad", "Fe"])
remitente = st.sidebar.text_input(t["de"], "Alex")
destinatario = st.sidebar.text_input(t["para"], "Sam")
mensaje = st.text_area(t["mensaje"], "Escribe algo bonito...")

# --- FUNCIÓN: CREAR IMAGEN ---
def crear_imagen(ocasion, para, de, texto):
    # Crear fondo de color
    color = (255, 230, 230) # Rosado suave por defecto
    if "Cumpleaños" in ocasion: color = (255, 215, 0) # Dorado
    if "Navidad" in ocasion: color = (200, 50, 50) # Rojo
    if "Fe" in ocasion: color = (135, 206, 235) # Azul cielo
    
    img = Image.new('RGB', (500, 500), color=color)
    d = ImageDraw.Draw(img)
    
    # Intentar cargar fuente, si falla usar la básica
    try:
        fnt = ImageFont.load_default()
    except:
        fnt = ImageFont.load_default()

    # Escribir textos en la imagen
    # Usamos posiciones fijas para evitar errores
    d.text((20, 20), f"{ocasion}", fill=(0,0,0), font=fnt)
    d.text((20, 60), f"Para: {para}", fill=(0,0,0), font=fnt)
    d.text((20, 100), f"{texto}", fill=(0,0,0), font=fnt)
    d.text((20, 400), f"De: {de}", fill=(0,0,0), font=fnt)
    
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- BOTÓN MÁGICO ---
if st.button(t["boton"]):
    with st.spinner("Creando... / Creating..."):
        time.sleep(1)
        
        # 1. Generar Audio (Sin f-strings largos para evitar errores)
        if idioma == "Español":
            texto_completo = "Hola " + destinatario + ". " + mensaje + ". De " + remitente
        else:
            texto_completo = "Hi " + destinatario + ". " + mensaje + ". From " + remitente
            
        tts = gTTS(text=texto_completo, lang=t["lang_code"])
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        
        # 2. Generar Imagen
        img_bytes = crear_imagen(ocasion, destinatario, remitente, mensaje)
        
        # 3. Mostrar Resultados
        st.success(t["exito"])
        
        st.image(img_bytes, caption="Tu Tarjeta / Your Card")
        st.download_button(t["descarga_img"], img_bytes, "tarjeta.png", "image/png")
        
        st.audio(audio_buffer)
        st.download_button(t["descarga_audio"], audio_buffer, "audio.mp3", "audio/mpeg")
