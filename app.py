import streamlit as st
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import io
import base64
import requests

# Shopify Store URL
STORE_URL = "https://tylice2.myshopify.com"

# Fonction pour ajouter au panier principal Shopify via `/cart/add.js`
def add_to_cart_shopify(variant_id, image_url):
    # URL pour ajouter au panier principal Shopify
    cart_add_url = f"{STORE_URL}/cart/add.js"
    payload = {
        "items": [
            {
                "id": variant_id,  # ID de la variante du produit
                "quantity": 1,  # Quantité à ajouter
                "properties": {
                    "Image": image_url  # Propriété personnalisée pour l'image
                }
            }
        ]
    }
    headers = {
        "Content-Type": "application/json",
    }
    response = requests.post(cart_add_url, headers=headers, json=payload)
    return response.json()

# Dictionnaire des couleurs
pal = {
    "NC": (0, 0, 0), "BJ": (255, 255, 255), "JO": (228, 189, 104), "BC": (0, 134, 214),
    "VL": (174, 150, 212), "VG": (63, 142, 67), "RE": (222, 67, 67), "BM": (0, 120, 191),
    "OM": (249, 153, 99), "VGa": (59, 102, 94), "BG": (163, 216, 225), "VM": (236, 0, 140),
    "GA": (166, 169, 170), "VB": (94, 67, 183), "BF": (4, 47, 86),
}

st.title("Tylice - Création d'images personnalisées")

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

# Traitement de l'image téléchargée
if uploaded_image is not None:
    # Chargement de l'image
    image = Image.open(uploaded_image).convert("RGB")
    resized_image = image.resize((350, 350))  # Redimensionnement fixe pour traitement
    img_arr = np.array(resized_image)

    # Clustering KMeans pour détecter les couleurs dominantes
    pixels = img_arr.reshape(-1, 3)
    kmeans = KMeans(n_clusters=num_selections, random_state=0).fit(pixels)
    labels = kmeans.labels_
    centers = kmeans.cluster_centers_

    # Création de l'image avec les couleurs sélectionnées
    selected_colors = [tuple(map(int, center)) for center in centers]
    new_img_arr = np.array([selected_colors[label] for label in labels])
    new_img_arr = new_img_arr.reshape(img_arr.shape)
    new_image = Image.fromarray(new_img_arr.astype('uint8'))

    # Afficher les résultats
    st.image(new_image, caption="Image personnalisée")

    # Sauvegarder l'image dans un buffer
    img_buffer = io.BytesIO()
    new_image.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    # Encodage Base64 de l'image
    image_base64 = f"data:image/png;base64,{base64.b64encode(img_buffer.getvalue()).decode('utf-8')}"

    # Ajouter au panier Shopify
    if st.button("Ajouter au panier"):
        variant_id = "50063717106003" if num_selections == 4 else "50063717138771"
        result = add_to_cart_shopify(variant_id, image_base64)
        if "errors" in result:
            st.error(f"Erreur lors de l'ajout au panier : {result['errors']}")
        else:
            st.success("Produit ajouté avec succès au panier Shopify principal !")
            st.json(result)
