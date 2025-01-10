import streamlit as st
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import io
import requests
import urllib.parse

# =========================================
# Fonctionnalités Réutilisables
# =========================================

def upload_to_cloudinary(image_buffer):
    """
    Uploads an image to Cloudinary and returns the secure URL.
    """
    url = "https://api.cloudinary.com/v1_1/dprmsetgi/image/upload"
    files = {"file": image_buffer}
    data = {"upload_preset": "image_upload_tylice"}
    try:
        response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            return response.json()["secure_url"]
        else:
            st.error(f"Erreur Cloudinary: {response.text}")
            return None
    except Exception as e:
        st.error(f"Erreur Cloudinary: {e}")
        return None

def generate_shopify_cart_url(cloudinary_url, num_colors):
    """
    Generates a Shopify cart URL with the given image URL and variant ID based on the number of colors.
    """
    variant_id = "50063717106003" if num_colors == 4 else "50063717138771"
    encoded_image_url = urllib.parse.quote(cloudinary_url)
    shopify_cart_url = (
        f"https://tylice2.myshopify.com/cart/add?id={variant_id}&quantity=1&properties[Image]={encoded_image_url}"
    )
    return shopify_cart_url

def process_image(image, num_clusters):
    """
    Processes the image by resizing and applying KMeans clustering.
    Returns the resized image array, labels, and sorted cluster indices.
    """
    width, height = image.size
    dim = 350  # Réduction à 350 pixels pour la plus grande dimension
    new_width = dim if width > height else int((dim / height) * width)
    new_height = dim if height >= width else int((dim / width) * height)

    resized_image = image.resize((new_width, new_height))
    img_arr = np.array(resized_image)

    pixels = img_arr.reshape(-1, 3)
    kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(pixels)
    labels = kmeans.labels_
    centers = kmeans.cluster_centers_

    grayscale_values = np.dot(centers, [0.2989, 0.5870, 0.1140])
    sorted_indices = np.argsort(grayscale_values)  # Trier du plus sombre au plus clair

    return resized_image, img_arr, labels, sorted_indices, new_width, new_height

def recolor_image(img_arr, labels, sorted_indices, palette_colors):
    """
    Recolors the image array based on the provided palette colors.
    """
    recolored_img_arr = np.zeros_like(img_arr)
    for i in range(img_arr.shape[0]):
        for j in range(img_arr.shape[1]):
            lbl = labels[i * img_arr.shape[1] + j]
            sorted_index = np.where(sorted_indices == lbl)[0][0]
            recolored_img_arr[i, j] = palette_colors[sorted_index]
    recolored_image = Image.fromarray(recolored_img_arr.astype('uint8'))
    return recolored_image

# =========================
# Dictionnaire des couleurs
# =========================
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

# ====================================
# Listes de palettes fixes pour les Exemples
# ====================================
palettes_examples_4 = [
    ["NC", "RE", "JO", "BJ"],
    ["NC", "BM", "BG", "BJ"],
    ["NC", "BM", "JO", "BJ"],
    ["NC", "VB", "OM", "BJ"],
]

palettes_examples_6 = [
    ["NC", "VB", "RE", "OM", "JO", "BJ"],
    ["NC", "BF", "BM", "BC", "BG", "BJ"],
    ["NC", "VGa", "BM", "GA", "JO", "BJ"],  # Palette improvisée 1
    ["NC", "BF", "VGa", "VG", "VL", "BJ"],  # Palette improvisée 2
]

# ====================================
# Configuration du titre et du style
# ====================================
st.title("Tylice")

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
        .shopify-link { font-size: 20px; font-weight: bold; text-decoration: none; color: #2e86de; }
        .dimension-text { font-size: 16px; font-weight: bold; color: #555; }
        .add-to-cart-button { margin-top: 10px; }
    </style>
"""
st.markdown(css, unsafe_allow_html=True)

# =========================================
# Section 1: Téléchargement de l'image
# =========================================
uploaded_image = st.file_uploader("Télécharger une image", type=["jpg", "jpeg", "png"])

# =========================================
# Sections conditionnelles après upload d'image
# =========================================
if uploaded_image is not None:
    # =========================================
    # Section 2: Sélection du nombre de couleurs
    # =========================================
    col1, col2 = st.columns([2, 5])

    with col1:
        if st.button("4 Couleurs : 7.95 €", key="select_4"):
            st.session_state.num_selections = 4
    with col2:
        if st.button("6 Couleurs : 11.95 €", key="select_6"):
            st.session_state.num_selections = 6

    # Initialisation du nombre de sélections si non défini
    if "num_selections" not in st.session_state:
        st.session_state.num_selections = 4  # Valeur par défaut

    num_selections = st.session_state.num_selections

    # =========================================
    # Section 3: Personnalisations
    # =========================================
    st.header("Personnalisations")

    rectangle_width = 80 if num_selections == 4 else 50
    rectangle_height = 20
    cols_personalization = st.columns(num_selections * 2)

    image_pers = Image.open(uploaded_image).convert("RGB")
    resized_image_pers, img_arr_pers, labels_pers, sorted_indices_pers, new_width_pers, new_height_pers = process_image(
        image_pers, num_clusters=num_selections
    )

    # Conversion de pixels à centimètres (350px = 14cm, soit 25px/cm)
    px_per_cm = 25
    new_width_cm = round(new_width_pers / px_per_cm, 1)  # Arrondi à 1 décimale (en cm)
    new_height_cm = round(new_height_pers / px_per_cm, 1)  # Arrondi à 1 décimale (en cm)

    if img_arr_pers.shape[-1] == 3:
        pixels_pers = img_arr_pers.reshape(-1, 3)
        kmeans_pers = KMeans(n_clusters=num_selections, random_state=0).fit(pixels_pers)
        labels_pers = kmeans_pers.labels_
        centers_pers = kmeans_pers.cluster_centers_

        centers_rgb_pers = np.array(centers_pers, dtype=int)
        pal_rgb = np.array(list(pal.values()), dtype=int)
        distances_pers = np.linalg.norm(centers_rgb_pers[:, None] - pal_rgb[None, :], axis=2)

        ordered_colors_by_cluster = []
        for i in range(num_selections):
            closest_colors_idx = distances_pers[i].argsort()
            ordered_colors_by_cluster.append([list(pal.keys())[idx] for idx in closest_colors_idx])

        cluster_counts_pers = np.bincount(labels_pers)
        total_pixels_pers = len(labels_pers)
        cluster_percentages_pers = (cluster_counts_pers / total_pixels_pers) * 100

        sorted_indices_pers = np.argsort(-cluster_percentages_pers)
        sorted_percentages_pers = cluster_percentages_pers[sorted_indices_pers]
        sorted_ordered_colors_by_cluster_pers = [ordered_colors_by_cluster[i] for i in sorted_indices_pers]

        selected_colors = []
        selected_color_names = []
        for i, cluster_index in enumerate(sorted_indices_pers):
            with cols_personalization[i * 2]:
                st.markdown("<div class='color-container'>", unsafe_allow_html=True)
                for j, color_name in enumerate(sorted_ordered_colors_by_cluster_pers[i]):
                    color_rgb = pal[color_name]
                    margin_class = "first-box" if j == 0 else ""
                    st.markdown(
                        f"<div class='color-box {margin_class}' style='background-color: rgb{color_rgb}; width: {rectangle_width}px; height: {rectangle_height}px; border-radius: 5px; margin-bottom: 4px;'></div>",
                        unsafe_allow_html=True
                    )
                st.markdown("</div>", unsafe_allow_html=True)

            with cols_personalization[i * 2 + 1]:
                selected_color_name = st.radio(
                    "", sorted_ordered_colors_by_cluster_pers[i],
                    key=f"radio_{i}_pers",
                    label_visibility="hidden"
                )
                selected_colors.append(pal[selected_color_name])
                selected_color_names.append(selected_color_name)

        # Recolorisation de l'image basée sur les sélections de l'utilisateur
        new_img_arr_pers = np.zeros_like(img_arr_pers)
        for i in range(img_arr_pers.shape[0]):
            for j in range(img_arr_pers.shape[1]):
                lbl = labels_pers[i * img_arr_pers.shape[1] + j]
                new_color_index = np.where(sorted_indices_pers == lbl)[0][0]
                new_img_arr_pers[i, j] = selected_colors[new_color_index]

        new_image_pers = Image.fromarray(new_img_arr_pers.astype('uint8'))
        resized_image_pers_final = new_image_pers

        # Affichage de l'image recolorée
        col1_pers, col2_pers, col3_pers = st.columns([1, 6, 1])
        with col2_pers:
            st.image(resized_image_pers_final, use_container_width=True)

        # Préparation pour l'upload et l'ajout au panier
        img_buffer_pers = io.BytesIO()
        new_image_pers.save(img_buffer_pers, format="PNG")
        img_buffer_pers.seek(0)

        cloudinary_url_pers = upload_to_cloudinary(img_buffer_pers)
        if not cloudinary_url_pers:
            st.error("Erreur lors du téléchargement de l'image. Veuillez réessayer.")
        else:
            shopify_cart_url_pers = generate_shopify_cart_url(cloudinary_url_pers, num_selections)

            # Affichage dimensions et bouton "Ajouter au panier" sur une seule ligne
            col1_cart, col2_cart, col3_cart, col4_cart = st.columns([4, 4, 4, 4])
            with col2_cart:
                st.markdown(f"<p class='dimension-text'> {new_width_cm} cm x {new_height_cm} cm</p>", unsafe_allow_html=True)
            with col3_cart:
                st.markdown(f"<a href='{shopify_cart_url_pers}' class='shopify-link' target='_blank'>Ajouter au panier</a>", unsafe_allow_html=True)

    # =========================================
    # Section 4: Exemples de Recoloration
    # =========================================
    st.header("Exemples de Recoloration")

    image = Image.open(uploaded_image).convert("RGB")
    resized_image, img_arr, labels, sorted_indices, new_width, new_height = process_image(image, num_clusters=num_selections)

    # Déterminer les palettes et le nombre de clusters
    if num_selections == 4:
        palettes = palettes_examples_4
        num_clusters = 4
    else:
        palettes = palettes_examples_6
        num_clusters = 6

    # Affichage de l'image recolorée pour chaque palette (2 par ligne)
    col_count = 0
    cols_display = st.columns(2)

    for palette in palettes:
        palette_colors = [pal[color] for color in palette]

        recolored_image = recolor_image(img_arr, labels, sorted_indices, palette_colors)

        # Convert recolored image to buffer for upload
        img_buffer = io.BytesIO()
        recolored_image.save(img_buffer, format="PNG")
        img_buffer.seek(0)

        # Upload to Cloudinary
        cloudinary_url = upload_to_cloudinary(img_buffer)

        # Generate Shopify cart URL if upload is successful
        if cloudinary_url:
            shopify_cart_url = generate_shopify_cart_url(cloudinary_url, num_selections)
            add_to_cart_button = f"<a href='{shopify_cart_url}' class='shopify-link' target='_blank'>Ajouter au panier</a>"
        else:
            shopify_cart_url = None
            add_to_cart_button = "Erreur lors de l'ajout au panier."

        with cols_display[col_count % 2]:
            st.image(recolored_image, caption=f"Palette: {' - '.join(palette)}", use_container_width=True, width=350)
            if cloudinary_url:
                st.markdown(f"<div class='add-to-cart-button'>{add_to_cart_button}</div>", unsafe_allow_html=True)
            else:
                st.error("Erreur lors de l'upload de l'image.")

        col_count += 1

# =========================================
# Section 5: Affichage des conseils d'utilisation
# =========================================
st.markdown("""
    ### 📝 Conseils d'utilisation :
    - Les couleurs les plus compatibles avec l'image apparaissent en premier.
    - Préférez des images avec un bon contraste et des éléments bien définis.
    - Une **image carrée** donnera un meilleur résultat.
    - Il est recommandé d'inclure au moins une **zone de noir ou de blanc** pour assurer un bon contraste.
    - Utiliser des **familles de couleurs** (ex: blanc, jaune, orange, rouge) peut produire des résultats visuellement intéressants.
    - **Expérimentez** avec différentes combinaisons pour trouver l'esthétique qui correspond le mieux à votre projet !
""", unsafe_allow_html=True)
