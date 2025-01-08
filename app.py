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
    "VL": (174, 150, 212), "VG": (63, 142, 67), "RE": (222, 67, 67), "BM": (0, 120, 191),
    "OM": (249, 153, 99), "VGa": (59, 102, 94), "BG": (163, 216, 225), "VM": (236, 0, 140),
    "GA": (166, 169, 170), "VB": (94, 67, 183), "BF": (4, 47, 86),
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

# Fonction pour gérer les requêtes Shopify avec cookies et headers
def shopify_request_with_cookies(session, method, url, headers=None, data=None):
    try:
        if method == "GET":
            response = session.get(url, headers=headers)
        elif method == "POST":
            response = session.post(url, headers=headers, json=data)
        else:
            st.error("Méthode HTTP non supportée.")
            return None

        # Afficher les logs
        st.write("Request URL:", url)
        st.write("Response Status Code:", response.status_code)
        st.write("Response Headers:", response.headers)
        st.write("Response Cookies:", response.cookies.get_dict())
        st.write("Response Body:", response.json() if response.headers.get("Content-Type") == "application/json" else response.text)

        return response
    except Exception as e:
        st.error(f"Erreur lors de la requête : {e}")
        return None

# Fonction pour vérifier le contenu du panier Shopify
def check_cart_content(session):
    try:
        cart_url = "https://tylice2.myshopify.com/cart.js"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = session.get(cart_url, headers=headers)
        st.write("Cart Content:", response.json())
    except Exception as e:
        st.error(f"Erreur lors de la récupération du panier : {e}")

# Traitement principal de l'image et ajout au panier
if uploaded_image is not None:
    image = Image.open(uploaded_image).convert("RGB")
    resized_image = image.resize((350, 350))
    img_buffer = io.BytesIO()
    resized_image.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    cloudinary_url = upload_to_cloudinary(img_buffer)
    if cloudinary_url:
        variant_id = "50063717106003"
        encoded_url = urllib.parse.quote(cloudinary_url)
        shopify_cart_url = (
            f"https://tylice2.myshopify.com/cart/add.js?id={variant_id}&quantity=1&properties%5BImage%5D={encoded_url}"
        )

        # Utiliser une session pour gérer les cookies
        session = requests.Session()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        if st.button("Ajouter au panier"):
            response = shopify_request_with_cookies(session, "GET", shopify_cart_url, headers=headers)
            if response and response.status_code == 200:
                st.success("Produit ajouté au panier avec succès !")

        if st.button("Vérifier le panier"):
            check_cart_content(session)

# Affichage des conseils d'utilisation
st.markdown("""
    ### 📝 Conseils d'utilisation :
    - Les couleurs les plus compatibles avec l'image apparaissent en premier.
    - Préférez des images avec un bon contraste et des éléments bien définis.
    - Une **image carrée** donnera un meilleur résultat.
    - Il est recommandé d'inclure au moins une **zone de noir ou de blanc** pour assurer un bon contraste.
    - Utiliser des **familles de couleurs** (ex: blanc, jaune, orange, rouge) peut produire des résultats visuellement intéressants.
    - **Expérimentez** avec différentes combinaisons pour trouver l'esthétique qui correspond le mieux à votre projet !
""", unsafe_allow_html=True)
