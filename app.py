import streamlit as st
import time
from gtts import gTTS
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Cardia AI", page_icon="💌", layout="centered")

# --- 1. DICCIONARIO DE IDIOMAS ---
TEXTOS = {
    "Español": {
        "titulo": "💌 Cardia AI",
        "subtitulo": "Generador de Tarjetas con Alma",
        "sidebar_tit": "Personaliza tu mensaje",
        "idioma": "Idioma / Language",
        "ocasion": "Ocasión",
        "opciones_ocasion": ["Cumpleaños", "Bodas", "Navidad", "Condolencias", "Fe", "Amor"],
        "de": "Tu nombre (De parte de):",
        "para": "Destinatario (Para):",
        "mensaje": "Mensaje especial:",
        "boton": "✨ Crear Tarjeta Mágica",
        "spinner": "Generando voz y diseño...",
        "exito": "¡Tu tarjeta ha sido creada!",
        "desc_img": "Descargar Tarjeta (PNG)",
        "desc_audio": "Descargar Audio (MP3)",
        "voz_code": "es",
        "msg_ejemplo": "Te deseo un día lleno de alegría."
    },
    "English": {
        "titulo": "💌 Cardia AI",
        "subtitulo": "Soulful Card Generator",
        "sidebar_tit": "Customize your message",
        "idioma": "Select Language",
        "ocasion": "Occasion",
        "opciones_ocasion": ["Birthday", "Wedding", "Christmas", "Sympathy", "Faith", "Love"],
        "de": "Your Name (From):",
        "para": "Recipient (To):",
        "mensaje": "Special Message:",
        "boton": "✨ Create Magic Card",
        "spinner": "Generating voice and design...",
        "exito": "Your card has been created!",
        "desc_img": "Download Card (PNG)",
        "desc_audio": "Download Audio (MP3)",
        "voz_code": "en",
        "msg_ejemplo": "Wishing you a day full of joy."
    }
}

# --- 2. LÓGICA DE COLORES ("EL ALMA") ---
def obtener_color_fondo(ocasion_texto):
    if "Cumpleaños" in ocasion_texto or "Birthday" in ocasion_texto:
        return (255, 223, 186) # Durazno
    elif "Bodas" in ocasion_texto or "Wedding" in ocasion_texto:
        return (255, 240, 245) # Lavanda
    elif "Navidad" in ocasion_texto or "Christmas" in ocasion_texto:
        return (200, 50, 50) # Rojo
    elif "Condolencias" in ocasion_texto or "Sympathy" in ocasion_texto:
        return (220, 220, 220) # Gris
    elif "Fe" in ocasion_texto or "Faith" in ocasion_texto:
        return (224, 255, 255) # Celeste
    elif "Amor" in ocasion_texto or "Love" in ocasion_texto:
        return (255, 182, 193) # Rosa
    else:
        return (255, 255, 255)

# --- 3. GENERADOR DE IMAGEN (MEJORADO) ---
def generar_imagen_tarjeta(ocasion, de, para, mensaje, textos_ui):
    color_bg = obtener_color_fondo(ocasion)
    img = Image.new('RGB', (600, 600), color=color_bg)
    d = ImageDraw.Draw(img)
    
    # Intentamos cargar la fuente por defecto
    try:
        font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()

    # Color del texto
    fill_color = (255, 255, 255) if color_bg == (200, 50, 50) else (0, 0, 0)

    # Escribimos los textos con un poco más de separación
    # Nota: Sin archivos de fuentes externas, el tamaño es fijo, 
    # pero podemos centrarlo mejor.
    
    d.text((50, 50), f"~ {ocasion} ~", font=font, fill=fill_color)
    d.text((50, 100), f"{textos_ui['para']} {para}", font=font, fill=fill_color)
    
    # Mensaje (Hacemos que salte de línea si es largo)
    margin = 50
    offset = 180
    for line in mensaje.split('\n'):
        d.text((margin, offset), line, font=font, fill=fill_color)
        offset += 20 
    
    d.text((50, 500), f"{textos_ui['de']} {de}", font=font, fill=fill_color)
    
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- INTERFAZ PRINCIPAL ---
idioma_sel = st.sidebar.radio("🌐", ["Español", "English"], horizontal=True)
t = TEXTOS[idioma_sel]

st.title(t["titulo"])
st.markdown(f"*{t['subtitulo']}*")
st.markdown("---")

st.sidebar.header(t["sidebar_tit"])
ocasion_input = st.sidebar.selectbox(t["ocasion"], t["opciones_ocasion"])
remitente_input = st.sidebar.text_input(t["de"], "Alex")
destinatario_input = st.sidebar.text_input(t["para"], "Sam")
mensaje_input = st.text_area(t["mensaje"], t["msg_ejemplo"])

if st.button(t["boton"], type="primary"):
    with st.spinner(t["spinner"]):
        time.sleep(1)
        
        # 1. AUDIO (Corregido para evitar error de reproducción)
        if idioma_sel == "Español":
            texto_leer = f"Hola {destinatario_input}. {mensaje_input}. De parte de {remitente_input}."
        else:
            texto_leer = f"Hi {destinatario_input}. {mensaje_input}. From {remitente_input}."
            
        tts = gTTS(text=texto_leer, lang=t["voz_code"])
        audio_io = BytesIO()
        tts.write_to_fp(audio_io)
        audio_io.seek(0)  # <--- ¡ESTA ES LA CURA MÁGICA! (Rebobinar cinta)
        
        # 2. IMAGEN
        img_data = generar_imagen_tarjeta(ocasion_input, remitente_input, destinatario_input, mensaje_input, t)
        
        # 3. MOSTRAR RESULTADOS
        st.success(t["exito"])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(img_data, caption=f"Tarjeta de {ocasion_input}")
            st.download_button(t["desc_img"], img_data, "tarjeta.png", "image/png")
            
        with col2:
            st.audio(audio_io, format='audio/mp3')
            st.download_button(t["desc_audio"], audio_io, "mensaje.mp3", "audio/mpeg")
