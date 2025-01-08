import streamlit as st
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import io
import base64
import requests

STORE_URL = "https://tylice2.myshopify.com"

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

st.title("Tylice - Création d'images personnalisées")

uploaded_image = st.file_uploader("Téléchargez une image", type=["jpg", "jpeg", "png"])

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

    if st.button("Ajouter au panier"):
        variant_id = "50063717106003" if st.session_state.num_selections == 4 else "50063717138771"
        result = add_to_cart_shopify(variant_id, image_base64)
        if "errors" in result:
            st.error(f"Erreur lors de l'ajout au panier : {result['errors']}")
        else:
            st.success("Produit ajouté avec succès au panier Shopify principal !")
            st.json(result)
