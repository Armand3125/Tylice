import streamlit as st
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import io
from datetime import datetime
import requests
import urllib.parse

# Dictionnaire des couleurs
pal = {
    "NC": (0, 0, 0), "BJ": (255, 255, 255),
    "JO": (228, 189, 104), "BC": (0, 134, 214),
    "VL": (174, 150, 212), "VG": (63, 142, 67),
    "RE": (222, 67, 67), "BM": (0, 120, 191),
    "OM": (249, 153, 99), "VGa": (59, 102, 94),
    "BG": (163, 216, 225), "VM": (236, 0, 140),
    "GA": (166, 169, 170), "VB": (94, 67, 183),
    "BF": (4, 47, 86),
}

st.title("Tylice")

# Style personnalisé
css = """
    <style>
        .stRadio div [data-testid="stMarkdownContainer"] p { display: none; }
        .radio-container { display: flex; flex-direction: column; align-items: center; margin: 10px; }
        .color-container { display: flex; flex-direction: column; align-items: center; margin-top: 5px; }
        .color-box { border: 3px solid black; }
        .stColumn { padding: 0 !important; }
        .first-box { margin-top: 15px; }
        .percentage-container { margin-bottom: 0; }
        .button-container { margin-bottom: 20px; }
    </style>
"""
st.markdown(css, unsafe_allow_html=True)

# Téléchargement de l'image
uploaded_image = st.file_uploader("Télécharger une image", type=["jpg", "jpeg", "png"])

# Sélection du nombre de couleurs
if "num_selections" not in st.session_state:
    st.session_state.num_selections = 4

col1, col2 = st.columns([2, 5])

with col1:
    if st.button("4 Couleurs : 7.95 €"):
        st.session_state.num_selections = 4

with col2:
    if st.button("6 Couleurs : 11.95 €"):
        st.session_state.num_selections = 6

num_selections = st.session_state.num_selections

# Fonction pour télécharger l'image sur Cloudinary
def upload_to_cloudinary(image_buffer):
    url = "https://api.cloudinary.com/v1_1/dprmsetgi/image/upload"
    files = {"file": image_buffer}
    data = {"upload_preset": "image_upload_tylice"}
    try:
        response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            return response.json()["secure_url"]
        else:
            return None
    except Exception as e:
        st.error(f"Erreur Cloudinary : {e}")
        return None

# Fonction pour ajouter au panier Shopify
def add_to_shopify_cart(variant_id, image_url):
    cart_url = "https://tylice2.myshopify.com/cart/add.js"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "items": [{
            "id": variant_id,
            "quantity": 1,
            "properties": {"Image": image_url}
        }]
    }
    response = requests.post(cart_url, json=data, headers=headers)
    return response

# Traitement de l'image téléchargée
if uploaded_image is not None:
    image = Image.open(uploaded_image).convert("RGB")
    resized_image = image.resize((350, 350))
    img_buffer = io.BytesIO()
    resized_image.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    cloudinary_url = upload_to_cloudinary(img_buffer)
    if not cloudinary_url:
        st.error("Échec du téléchargement de l'image.")
    else:
        st.image(resized_image, caption="Aperçu de l'image téléchargée", use_column_width=True)

        if st.button("Ajouter au panier"):
            variant_id = "50063717106003" if num_selections == 4 else "50063717138771"
            response = add_to_shopify_cart(variant_id, cloudinary_url)
            if response.status_code == 200:
                st.success("Produit ajouté au panier avec succès !")
            else:
                st.error("Erreur lors de l'ajout au panier.")
                st.write(response.json())
