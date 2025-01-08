import streamlit as st
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import io
from datetime import datetime
import requests
import urllib.parse

# Shopify Admin API Config
SHOPIFY_STORE_URL = "https://tylice2.myshopify.com"
SHOPIFY_API_ADMIN_TOKEN = "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"
VARIANT_ID_4_COLORS = "50063717106003"  # ID pour 4 couleurs
VARIANT_ID_6_COLORS = "50063717138771"  # ID pour 6 couleurs

# Cloudinary Config
CLOUDINARY_URL = "https://api.cloudinary.com/v1_1/dprmsetgi/image/upload"
CLOUDINARY_UPLOAD_PRESET = "image_upload_tylice"

st.title("Tylice - Personnalisation d'images")

# Téléchargement de l'image
uploaded_image = st.file_uploader("Téléchargez une image", type=["jpg", "jpeg", "png"])

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

# Fonction pour uploader l'image sur Cloudinary
def upload_to_cloudinary(image_buffer):
    files = {"file": image_buffer}
    data = {"upload_preset": CLOUDINARY_UPLOAD_PRESET}
    response = requests.post(CLOUDINARY_URL, files=files, data=data)
    if response.status_code == 200:
        return response.json()["secure_url"]
    else:
        st.error("Erreur lors de l'envoi à Cloudinary")
        return None

# Fonction pour ajouter au panier via Admin API
def add_to_cart(variant_id, image_url):
    url = f"{SHOPIFY_STORE_URL}/cart/add.js"
    payload = {
        "items": [
            {
                "id": variant_id,
                "quantity": 1,
                "properties": {
                    "Image": image_url
                }
            }
        ]
    }
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": SHOPIFY_API_ADMIN_TOKEN
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        st.success("Produit ajouté avec succès au panier Shopify principal !")
        st.write(response.json())
    else:
        st.error("Erreur lors de l'ajout au panier Shopify")
        st.write(response.json())

# Fonction pour consulter l'état du panier
def get_cart_state():
    url = f"{SHOPIFY_STORE_URL}/cart.js"
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": SHOPIFY_API_ADMIN_TOKEN
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        st.success("État du panier récupéré avec succès !")
        st.write(response.json())
    else:
        st.error("Erreur lors de la récupération de l'état du panier.")
        st.write(response.json())

# Traitement de l'image téléchargée
if uploaded_image:
    image = Image.open(uploaded_image).convert("RGB")
    width, height = image.size
    dim = 350
    new_width = dim if width > height else int((dim / height) * width)
    new_height = dim if height >= width else int((dim / width) * height)

    resized_image = image.resize((new_width, new_height))
    img_arr = np.array(resized_image)

    # Application de KMeans
    pixels = img_arr.reshape(-1, 3)
    kmeans = KMeans(n_clusters=num_selections, random_state=0).fit(pixels)
    labels = kmeans.labels_
    centers = kmeans.cluster_centers_

    # Création d'une nouvelle image avec les couleurs sélectionnées
    new_img_arr = np.zeros_like(img_arr)
    for i in range(img_arr.shape[0]):
        for j in range(img_arr.shape[1]):
            lbl = labels[i * img_arr.shape[1] + j]
            new_img_arr[i, j] = centers[lbl]

    new_image = Image.fromarray(new_img_arr.astype("uint8"))
    img_buffer = io.BytesIO()
    new_image.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    # Afficher l'image traitée
    st.image(new_image, caption="Image traitée", use_column_width=True)

    # Uploader l'image sur Cloudinary
    cloudinary_url = upload_to_cloudinary(img_buffer)
    if cloudinary_url:
        st.markdown(f"URL de l'image : [Voir l'image]({cloudinary_url})")

        # Ajouter au panier
        variant_id = VARIANT_ID_4_COLORS if num_selections == 4 else VARIANT_ID_6_COLORS
        if st.button("Ajouter au panier"):
            add_to_cart(variant_id, cloudinary_url)

# Bouton pour consulter l'état du panier
if st.button("Consulter l'état du panier"):
    get_cart_state()
