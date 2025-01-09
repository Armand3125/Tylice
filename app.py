import streamlit as st
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import io
import requests
from datetime import datetime

# Shopify Cart Endpoint
SHOPIFY_CART_URL = "https://tylice2.myshopify.com/cart/add.js"

# Variant IDs pour vos produits
VARIANT_ID_4_COLORS = "50063717106003"
VARIANT_ID_6_COLORS = "50063717138771"

# Fonction pour ajouter au panier via une requête POST
def add_to_cart(variant_id, quantity=1, properties=None):
    data = {
        "id": variant_id,
        "quantity": quantity,
        "properties": properties or {},
    }
    headers = {
        "Content-Type": "application/json",
    }
    response = requests.post(SHOPIFY_CART_URL, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Erreur lors de l'ajout au panier : {response.status_code}")
        st.error(response.text)
        return None

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

# Application Streamlit
st.title("Tylice - Ajout au Panier Shopify")

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
    labels = kmeans.labels_
    centers = kmeans.cluster_centers_

    centers_rgb = np.array(centers, dtype=int)
    pal_rgb = np.array(list(pal.values()), dtype=int)
    distances = np.linalg.norm(centers_rgb[:, None] - pal_rgb[None, :], axis=2)

    ordered_colors_by_cluster = []
    for i in range(num_selections):
        closest_colors_idx = distances[i].argsort()
        ordered_colors_by_cluster.append([list(pal.keys())[idx] for idx in closest_colors_idx])

    cluster_counts = np.bincount(labels)
    total_pixels = len(labels)
    cluster_percentages = (cluster_counts / total_pixels) * 100

    sorted_indices = np.argsort(-cluster_percentages)
    sorted_ordered_colors_by_cluster = [ordered_colors_by_cluster[i] for i in sorted_indices]

    cols = st.columns(num_selections * 2)
    selected_colors = []
    for i, cluster_index in enumerate(sorted_indices):
        with cols[i * 2]:
            st.markdown("<div class='color-container'>", unsafe_allow_html=True)
            for j, color_name in enumerate(sorted_ordered_colors_by_cluster[i]):
                color_rgb = pal[color_name]
                margin_class = "first-box" if j == 0 else ""
                st.markdown(
                    f"<div class='color-box {margin_class}' style='background-color: rgb{color_rgb}; width: 80px; height: 20px; border-radius: 5px; margin-bottom: 4px;'></div>",
                    unsafe_allow_html=True
                )
            st.markdown("</div>", unsafe_allow_html=True)

        with cols[i * 2 + 1]:
            selected_color_name = st.radio("", sorted_ordered_colors_by_cluster[i], key=f"radio_{i}", label_visibility="hidden")
            selected_colors.append(pal[selected_color_name])

    # Ajouter l'image au panier
    if st.button("Ajouter au panier"):
        # Simuler une URL d'upload pour l'image
        image_url = f"https://upload-lift-example.com/{uploaded_image.name}"

        # Sélection du bon variant ID
        variant_id = VARIANT_ID_4_COLORS if num_selections == 4 else VARIANT_ID_6_COLORS

        # Ajouter au panier avec des propriétés personnalisées
        response = add_to_cart(
            variant_id=variant_id,
            quantity=1,
            properties={
                "Image": image_url,  # URL de l'image uploadée
                "Couleurs dominantes": ", ".join([f"rgb{color}" for color in selected_colors]),
            },
        )
        if response:
            st.success("Produit ajouté au panier avec succès !")
            st.json(response)

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
