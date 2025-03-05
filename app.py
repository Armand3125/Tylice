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
        f"https://tylice.com/cart/add?id={variant_id}&quantity=1&properties[Image]={encoded_image_url}"
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

# =========================================
# Listes de palettes fixes pour les Exemples
# =========================================
palettes_examples_4 = [
    ["NC", "RE", "JO", "BJ"],
    ["NC", "BM", "BG", "BJ"],
    ["NC", "BM", "JO", "BJ"],
    ["NC", "VB", "OM", "BJ"],
]

palettes_examples_6 = [
    ["NC", "VB", "RE", "OM", "JO", "BJ"],
    ["NC", "BF", "BM", "BC", "BG", "BJ"],
    ["NC", "VGa", "BM", "GA", "JO", "BJ"],
    ["NC", "BF", "VGa", "VG", "VL", "BJ"],
]

# =========================================
# Configuration du titre et du style
# =========================================
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
        /* Liens simples sans encadré */
        .shopify-link {
            font-size: 16px;
            font-weight: bold;
            text-decoration: none;
            color: #242833;
        }
        .dimension-text {
            font-size: 14px;
            font-weight: bold;
            color: #555;
            margin: 0;
        }
        .add-to-cart-button { margin-top: 10px; }
        .label {
            font-size: 14px;
            font-weight: bold;
            color: #ffffff;
            background-color: #242833;
            padding: 5px 10px;
            border-radius: 5px;
            display: inline-block;
            margin-left: 10px;
        }
        /* Boutons en haut avec couleur #64AF96 */
        div.stButton > button {
            background-color: #64AF96 !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 5px !important;
            padding: 8px 16px !important;
            font-size: 14px !important;
            margin: 0 !important;
            width: 100% !important;
        }
        div.stButton > button:hover {
            background-color: #539E7D !important;
        }
        div.row-widget.stHorizontal { gap: 0 !important; }
    </style>
"""
st.markdown(css, unsafe_allow_html=True)

# =========================================
# Initialisation des variables de session
# =========================================
if "num_selections" not in st.session_state:
    st.session_state.num_selections = None
if "show_personalization" not in st.session_state:
    st.session_state.show_personalization = False
if "show_examples" not in st.session_state:
    st.session_state.show_examples = False

# =========================================
# Section 1: Téléchargement de l'image
# =========================================
uploaded_image = st.file_uploader("Télécharger une image", type=["jpg", "jpeg", "png"])

# =========================================
# Section 2: Boutons de sélection
# =========================================
if uploaded_image is not None:
    # Dès le téléversement d'une image, afficher par défaut les Exemples
    if not st.session_state.show_examples and not st.session_state.show_personalization:
        st.session_state.show_examples = True

    # Boutons en haut sur toute la largeur, ordre : Exemples, 4 Couleurs, 6 Couleurs
    col_ex, col_4, col_6 = st.columns([1, 1, 1])
    with col_ex:
        st.button("Exemples", key="show_examples_btn", on_click=lambda: setattr(st.session_state, "show_examples", True))
    with col_4:
        st.button("4 Couleurs : 7.95 €", key="select_4_btn", on_click=lambda: setattr(st.session_state, "num_selections", 4))
    with col_6:
        st.button("6 Couleurs : 11.95 €", key="select_6_btn", on_click=lambda: setattr(st.session_state, "num_selections", 6))

    # =========================================
    # Section Personnalisation
    # =========================================
    if st.session_state.num_selections in [4, 6]:
        num_selections = st.session_state.num_selections
        st.header("Personnalisations")

        image_pers = Image.open(uploaded_image).convert("RGB")
        resized_image_pers, img_arr_pers, labels_pers, sorted_indices_pers, new_width_pers, new_height_pers = process_image(image_pers, num_clusters=num_selections)

        px_per_cm = 25
        new_width_cm = round(new_width_pers / px_per_cm, 1)
        new_height_cm = round(new_height_pers / px_per_cm, 1)

        # Bouton Choisir cette image
        price = "7.95" if num_selections == 4 else "11.95"
        st.button(f"Choisir cette image - {price} €", key=f"choose_{num_selections}", on_click=lambda: st.session_state.update({
            "selected_image": resized_image_pers, "width_cm": new_width_cm, "height_cm": new_height_cm, "price": price}))

        if "selected_image" in st.session_state:
            st.image(st.session_state.selected_image, width=500)
            st.write(f"Dimensions: {st.session_state.width_cm} cm x {st.session_state.height_cm} cm")
            st.write(f"Prix: {st.session_state.price} €")

    # =========================================
    # Section Exemples de Recoloration
    # =========================================
    if st.session_state.show_examples:
        st.header("Exemples de Recoloration")

        image = Image.open(uploaded_image).convert("RGB")
        st.subheader("Palettes 4 Couleurs")
        cols_display = st.columns(2)
        col_count = 0
        for palette in palettes_examples_4:
            num_clusters = len(palette)
            palette_colors = [pal[color] for color in palette]
            resized_image, img_arr, labels, sorted_indices, new_width, new_height = process_image(image, num_clusters=num_clusters)
            recolored_image = recolor_image(img_arr, labels, sorted_indices, palette_colors)
            img_buffer = io.BytesIO()
            recolored_image.save(img_buffer, format="PNG")
            img_buffer.seek(0)
            cloudinary_url = upload_to_cloudinary(img_buffer)
            price = "7.95"
            if cloudinary_url:
                shopify_cart_url = generate_shopify_cart_url(cloudinary_url, num_colors=num_clusters)
                combined_html = generate_label_and_button_examples(num_clusters, price, shopify_cart_url)
            else:
                combined_html = "Erreur lors de l'ajout au panier."
            with cols_display[col_count % 2]:
                st.image(recolored_image, use_container_width=True, width=350)
                st.markdown(combined_html, unsafe_allow_html=True)
            col_count += 1
            if col_count % 2 == 0:
                st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
        st.subheader("Palettes 6 Couleurs")
        cols_display = st.columns(2)
        col_count = 0
        for palette in palettes_examples_6:
            num_clusters = len(palette)
            palette_colors = [pal[color] for color in palette]
            resized_image, img_arr, labels, sorted_indices, new_width, new_height = process_image(image, num_clusters=num_clusters)
            recolored_image = recolor_image(img_arr, labels, sorted_indices, palette_colors)
            img_buffer = io.BytesIO()
            recolored_image.save(img_buffer, format="PNG")
            img_buffer.seek(0)
            cloudinary_url = upload_to_cloudinary(img_buffer)
            price = "11.95"
            if cloudinary_url:
                shopify_cart_url = generate_shopify_cart_url(cloudinary_url, num_colors=num_clusters)
                combined_html = generate_label_and_button_examples(num_clusters, price, shopify_cart_url)
            else:
                combined_html = "Erreur lors de l'ajout au panier."
            with cols_display[col_count % 2]:
                st.image(recolored_image, use_container_width=True, width=350)
                st.markdown(combined_html, unsafe_allow_html=True)
            col_count += 1
            if col_count % 2 == 0:
                st.markdown("<br>", unsafe_allow_html=True)
