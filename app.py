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

st.title("Tylice - Personnalisation d'images avec Upload-Lift")

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

# Téléchargement de l'image via Upload-Lift
uploaded_image = st.file_uploader("Téléchargez votre image personnalisée avec Upload-Lift", type=["jpg", "jpeg", "png"])

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

# Fonction pour utiliser Upload-Lift
def get_uploaded_image_url(image):
    # Simule une URL retournée par Upload-Lift (remplacez par la logique réelle si disponible)
    # Par exemple, si Upload-Lift retourne une URL publique après upload.
    return f"https://upload-lift-example.com/{datetime.now().strftime('%Y%m%d%H%M%S')}_{image.name}"

# Fonction de traitement des couleurs dominantes
def process_image(image, num_colors):
    img_arr = np.array(image)
    pixels = img_arr.reshape(-1, 3)
    kmeans = KMeans(n_clusters=num_colors, random_state=0).fit(pixels)
    labels = kmeans.labels_
    centers = kmeans.cluster_centers_

    return labels, centers, img_arr

# Traitement de l'image téléchargée
if uploaded_image is not None:
    # Ouvrir et redimensionner l'image
    image = Image.open(uploaded_image).convert("RGB")
    width, height = image.size
    dim = 350
    new_width = dim if width > height else int((dim / height) * width)
    new_height = dim if height >= width else int((dim / width) * height)
    resized_image = image.resize((new_width, new_height))

    # Transformation des couleurs dominantes
    labels, centers, img_arr = process_image(resized_image, num_selections)

    # Génération d'une nouvelle image avec des couleurs dominantes
    new_img_arr = np.zeros_like(img_arr)
    sorted_indices = np.argsort(-np.bincount(labels) / len(labels))
    selected_colors = np.array(centers, dtype=int)
    for i in range(img_arr.shape[0]):
        for j in range(img_arr.shape[1]):
            lbl = labels[i * img_arr.shape[1] + j]
            new_img_arr[i, j] = selected_colors[sorted_indices[lbl]]

    new_image = Image.fromarray(new_img_arr.astype('uint8'))

    # Afficher l'image transformée
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        st.image(new_image, use_container_width=True)

    # Générer une URL via Upload-Lift
    upload_lift_url = get_uploaded_image_url(uploaded_image)

    # Ajout au panier avec l'URL de l'image
    if st.button("Ajouter au panier"):
        variant_id = "50063717106003" if num_selections == 4 else "50063717138771"
        encoded_url = urllib.parse.quote(upload_lift_url)
        shopify_cart_url = f"https://tylice2.myshopify.com/cart/add.js?id={variant_id}&quantity=1&properties%5BImage%5D={encoded_url}"
        st.markdown(f"[Ajoutez au panier avec l'image]({shopify_cart_url})", unsafe_allow_html=True)
        st.markdown(f"[Voir l'image sur Upload-Lift]({upload_lift_url})", unsafe_allow_html=True)

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
