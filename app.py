import streamlit as st
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import io
import urllib.parse
import requests

# Variant IDs pour vos produits
VARIANT_ID_4_COLORS = "50063717106003"
VARIANT_ID_6_COLORS = "50063717138771"

# URL de votre boutique Shopify
SHOPIFY_ADD_TO_CART_URL = "https://tylice2.myshopify.com/cart/add"

# Cloudinary Configuration
CLOUDINARY_URL = "https://api.cloudinary.com/v1_1/dprmsetgi/image/upload"
CLOUDINARY_UPLOAD_PRESET = "image_upload_tylice"

# Fonction pour télécharger une image sur Cloudinary
def upload_to_cloudinary(image_buffer, filename):
    files = {"file": image_buffer}
    data = {"upload_preset": CLOUDINARY_UPLOAD_PRESET, "public_id": filename}
    try:
        response = requests.post(CLOUDINARY_URL, files=files, data=data)
        if response.status_code == 200:
            return response.json().get("secure_url")
        else:
            st.error(f"Erreur Cloudinary : {response.text}")
            return None
    except Exception as e:
        st.error(f"Erreur lors de l'upload Cloudinary : {e}")
        return None

# Application Streamlit
st.title("Tylice - Ajout au Panier Shopify avec Cloudinary")

# Téléchargement de l'image
uploaded_image = st.file_uploader("Téléchargez une image personnalisée", type=["jpg", "jpeg", "png"])

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

if uploaded_image:
    # Affichage de l'image téléchargée
    image = Image.open(uploaded_image).convert("RGB")
    st.image(image, caption="Votre image téléchargée", use_column_width=True)

    # Traitement des couleurs dominantes
    img_arr = np.array(image)
    pixels = img_arr.reshape(-1, 3)
    kmeans = KMeans(n_clusters=num_selections, random_state=0).fit(pixels)
    centers = kmeans.cluster_centers_
    selected_colors = [tuple(map(int, c)) for c in centers]

    st.write("Couleurs dominantes :")
    for color in selected_colors:
        st.markdown(f"<div style='background-color: rgb{color}; width: 50px; height: 20px;'></div>", unsafe_allow_html=True)

    # Préparer l'image pour l'upload
    img_buffer = io.BytesIO()
    image.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    # Télécharger l'image sur Cloudinary
    filename = f"tylice_{uploaded_image.name.split('.')[0]}"
    cloudinary_url = upload_to_cloudinary(img_buffer, filename)

    if cloudinary_url:
        # Préparer les propriétés personnalisées
        properties = {
            "Image": cloudinary_url,
            "Couleurs dominantes": ", ".join([f"rgb{color}" for color in selected_colors]),
        }

        # Encodage des propriétés pour l'URL
        encoded_properties = "&".join([f"properties[{urllib.parse.quote(k)}]={urllib.parse.quote(v)}" for k, v in properties.items()])

        # Sélection du bon variant ID
        variant_id = VARIANT_ID_4_COLORS if num_selections == 4 else VARIANT_ID_6_COLORS

        # Générer le lien de redirection vers Shopify
        shopify_redirect_url = f"{SHOPIFY_ADD_TO_CART_URL}?id={variant_id}&quantity=1&{encoded_properties}"

        # Bouton pour rediriger l'utilisateur
        st.markdown(
            f"<a href='{shopify_redirect_url}' target='_blank' class='button'>Ajouter au panier</a>",
            unsafe_allow_html=True,
        )

# Conseils d'utilisation
st.markdown("""
    ### 📝 Conseils d'utilisation :
    - Les couleurs les plus compatibles avec l'image apparaissent en premier.
    - Préférez des images avec un bon contraste et des éléments bien définis.
    - Une **image carrée** donnera un meilleur résultat.
    - Il est recommandé d'inclure au moins une **zone de noir ou de blanc** pour assurer un bon contraste.
    - Utiliser des **familles de couleurs** (ex: blanc, jaune, orange, rouge) peut produire des résultats visuellement intéressants.
    - **Expérimentez** avec différentes combinaisons pour trouver l'esthétique qui correspond le mieux à votre projet !
""", unsafe_allow_html=True)
