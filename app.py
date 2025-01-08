import streamlit as st
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import io
import base64
import requests
import urllib.parse
from datetime import datetime

STORE_URL = "https://tylice2.myshopify.com"

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

st.title("Tylice - Création d'images personnalisées")

# Fonction pour télécharger une image vers Cloudinary
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

# Fonction pour ajouter un produit au panier Shopify
def add_to_cart_shopify(variant_id, image_url):
    cart_add_url = f"{STORE_URL}/cart/add.js"
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
    }
    response = requests.post(cart_add_url, headers=headers, json=payload)
    return response.json()

# Téléchargement de l'image
uploaded_image = st.file_uploader("Télécharger une image", type=["jpg", "jpeg", "png"])

if "num_selections" not in st.session_state:
    st.session_state.num_selections = 4

if uploaded_image is not None:
    image = Image.open(uploaded_image).convert("RGB")
    resized_image = image.resize((350, 350))
    img_arr = np.array(resized_image)

    pixels = img_arr.reshape(-1, 3)
    kmeans = KMeans(n_clusters=st.session_state.num_selections, random_state=0).fit(pixels)
    labels = kmeans.labels_
    centers = kmeans.cluster_centers_

    selected_colors = [tuple(map(int, center)) for center in centers]
    new_img_arr = np.array([selected_colors[label] for label in labels])
    new_img_arr = new_img_arr.reshape(img_arr.shape)
    new_image = Image.fromarray(new_img_arr.astype('uint8'))

    st.image(new_image, caption="Image personnalisée")

    img_buffer = io.BytesIO()
    new_image.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    image_base64 = f"data:image/png;base64,{base64.b64encode(img_buffer.getvalue()).decode('utf-8')}"
    cloudinary_url = upload_to_cloudinary(img_buffer)

    if not cloudinary_url:
        st.error("Erreur lors du téléchargement de l'image. Veuillez réessayer.")
    else:
        variant_id = "50063717106003" if st.session_state.num_selections == 4 else "50063717138771"

        if st.button("Ajouter au panier"):
            result = add_to_cart_shopify(variant_id, cloudinary_url)
            if "items" in result:
                st.success("Produit ajouté avec succès au panier Shopify !")
                st.json(result)
            else:
                st.error(f"Erreur lors de l'ajout au panier : {result}")

st.markdown("""
    ### 📝 Conseils d'utilisation :
    - Téléchargez une image pour créer un produit personnalisé.
    - Les couleurs sont automatiquement sélectionnées à partir de votre image.
    - Ajoutez facilement votre produit personnalisé au panier Shopify.
""", unsafe_allow_html=True)
