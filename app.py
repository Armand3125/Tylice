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

st.title("Tylice - Personnalisation d'images")

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
uploaded_image = st.file_uploader("Téléchargez votre image personnalisée", type=["jpg", "jpeg", "png"])

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

# Traitement de l'image téléchargée
if uploaded_image is not None:
    image = Image.open(uploaded_image).convert("RGB")
    width, height = image.size
    dim = 350
    new_width = dim if width > height else int((dim / height) * width)
    new_height = dim if height >= width else int((dim / width) * height)

    resized_image = image.resize((new_width, new_height))
    img_arr = np.array(resized_image)

    px_per_cm = 25
    new_width_cm = round(new_width / px_per_cm, 1)
    new_height_cm = round(new_height / px_per_cm, 1)

    pixels = img_arr.reshape(-1, 3)
    kmeans = KMeans(n_clusters=num_selections, random_state=0).fit(pixels)
    labels = kmeans.labels_
    centers = kmeans.cluster_centers_

    sorted_indices = np.argsort(-np.bincount(labels) / len(labels))
    selected_colors = [np.array(centers[i], dtype=int).tolist() for i in sorted_indices]

    new_image = Image.fromarray(np.zeros_like(img_arr).astype('uint8'))
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        st.image(new_image, use_container_width=True)

    img_buffer = io.BytesIO()
    new_image.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    if st.button("Ajouter au panier"):
        cloudinary_url = upload_to_cloudinary(img_buffer)
        if cloudinary_url:
            variant_id = "50063717106003" if num_selections == 4 else "50063717138771"
            encoded_url = urllib.parse.quote(cloudinary_url)
            shopify_cart_url = f"https://tylice2.myshopify.com/cart/add.js?id={variant_id}&quantity=1&properties%5BImage%5D={encoded_url}"
            st.markdown(f"[Ajoutez au panier avec l'image]({shopify_cart_url})", unsafe_allow_html=True)
            st.markdown(f"[Voir l'image sur Cloudinary]({cloudinary_url})", unsafe_allow_html=True)
