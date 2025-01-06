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

# Variables pour gérer la sélection et l'affichage de couleurs
rectangle_width = 80 if num_selections == 4 else 50
rectangle_height = 20
cols = st.columns(num_selections * 2)

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

    # Conversion de pixels à centimètres (350px = 14cm, soit 25px/cm)
    px_per_cm = 25
    new_width_cm = round(new_width / px_per_cm, 1)  # Arrondi à 1 décimale (en cm)
    new_height_cm = round(new_height / px_per_cm, 1)  # Arrondi à 1 décimale (en cm)

    if img_arr.shape[-1] == 3:
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
        sorted_percentages = cluster_percentages[sorted_indices]
        sorted_ordered_colors_by_cluster = [ordered_colors_by_cluster[i] for i in sorted_indices]

        selected_colors = []
        selected_color_names = []
        for i, cluster_index in enumerate(sorted_indices):
            with cols[i * 2]:
                st.markdown("<div class='color-container'>", unsafe_allow_html=True)
                for j, color_name in enumerate(sorted_ordered_colors_by_cluster[i]):
                    color_rgb = pal[color_name]
                    margin_class = "first-box" if j == 0 else ""
                    st.markdown(
                        f"<div class='color-box {margin_class}' style='background-color: rgb{color_rgb}; width: {rectangle_width}px; height: {rectangle_height}px; border-radius: 5px; margin-bottom: 4px;'></div>",
                        unsafe_allow_html=True
                    )
                st.markdown("</div>", unsafe_allow_html=True)

            with cols[i * 2 + 1]:
                selected_color_name = st.radio("", sorted_ordered_colors_by_cluster[i], key=f"radio_{i}", label_visibility="hidden")
                selected_colors.append(pal[selected_color_name])
                selected_color_names.append(selected_color_name)

        new_img_arr = np.zeros_like(img_arr)
        for i in range(img_arr.shape[0]):
            for j in range(img_arr.shape[1]):
                lbl = labels[i * img_arr.shape[1] + j]
                new_color_index = np.where(sorted_indices == lbl)[0][0]
                new_img_arr[i, j] = selected_colors[new_color_index]

        new_image = Image.fromarray(new_img_arr.astype('uint8'))
        resized_image = new_image

        col1, col2, col3 = st.columns([1, 6, 1])
        with col2:
            st.image(resized_image, use_container_width=True)

        img_buffer = io.BytesIO()
        new_image.save(img_buffer, format="PNG")
        img_buffer.seek(0)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{''.join(selected_color_names)}_{timestamp}.png"

        col1, col2, col3, col4 = st.columns([4, 5, 5, 4])
        with col2:
            st.markdown(f"**{new_width_cm} cm x {new_height_cm} cm**")

        # Téléchargement de l'image sur Cloudinary
        cloudinary_url = upload_to_cloudinary(img_buffer)
        if cloudinary_url:
            variant_id = "50063717106003" if num_selections == 4 else "50063717138771"
            encoded_url = urllib.parse.quote(cloudinary_url)

            # Afficher le bouton d'ajout au panier
            if st.button("Ajouter au panier"):
                st.markdown(f"""
                    <script>
                    // Envoi d'un message à l'iframe pour ajouter l'article au panier
                    window.parent.postMessage({{
                        type: 'addToCart',
                        variantId: '{variant_id}',
                        imageUrl: '{cloudinary_url}'
                    }}, '*');
                    alert("Image ajoutée au panier !");
                    </script>
                """, unsafe_allow_html=True)

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
