import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 1. Autenticación con Google
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file"
]
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scopes
)
gc = gspread.authorize(creds)
sheet = gc.open_by_key(st.secrets["sheet_id"]).sheet1
drive_service = gc.auth.service  # API de Drive para subir archivos

# 2. UI
st.image("https://upload.wikimedia.org/wikipedia/commons/4/4b/Avianca_Cargo_logo.svg", width=180)
st.markdown("## REPORTE DE PELIGROS VOLUNTARIOS (RPV)")

with st.form("rpv_form"):
    fecha = st.date_input("A. Fecha")
    nombre = st.text_input("B. Nombre")
    confidencial = st.checkbox("Marcar como **Confidencial** (oculta el nombre)")
    cargo = st.text_input("C. Cargo")
    descripcion = st.text_area("D. Descripción del peligro")
    evidencias = st.file_uploader(
        "E. Evidencia (imágenes, PDF, video)",
        accept_multiple_files=True,
        type=["png", "jpg", "jpeg", "pdf", "mp4", "mov", "avi"]
    )
    enviar = st.form_submit_button("Enviar")

if enviar:
    enlaces = []
    for fichero in evidencias:
        meta = {
            "name": fichero.name,
            "parents": [st.secrets["drive_folder_id"]]
        }
        upload = drive_service.files().create(
            body=meta,
            media_body=fichero,
            fields="webViewLink"
        ).execute()
        enlaces.append(upload["webViewLink"])

    sheet.append_row([
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "" if confidencial else nombre,
        cargo,
        descripcion,
        ", ".join(enlaces)
    ])
    st.success("✅ Reporte enviado con éxito")
    st.balloons()
