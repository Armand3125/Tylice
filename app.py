import streamlit as st
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min

# Palette de couleurs
pal = {
    "NC": (0, 0, 0), "BJ": (255, 255, 255),
    "JO": (228, 189, 104), "BC": (0, 134, 214),
    "VL": (174, 150, 212), "VG": (63, 142, 67),
    "RE": (222, 67, 67), "BM": (0, 120, 191),
    "OM": (249, 153, 99), "VGa": (59, 102, 94),
    "BG": (163, 216, 225), "VM": (236, 0, 140),
    "GA": (166, 169, 170), "VB": (94, 67, 183),
}

st.title("Tylice")

css = """
    <style>
        .stRadio div [data-testid="stMarkdownContainer"] p { display: none; }
        .radio-container { display: flex; flex-direction: column; align-items: center; margin: 0; }
        .color-container { display: flex; flex-direction: column; align-items: center; }
        .color-box { border: 3px solid black; }
        .stColumn { padding: 0 !important; }
        .first-box { margin-top: 15px; }
    </style>
"""
st.markdown(css, unsafe_allow_html=True)

uploaded_image = st.file_uploader("Télécharger une image", type=["jpg", "jpeg", "png"])

if "num_selections" not in st.session_state:
    st.session_state.num_selections = 4

col1, col2 = st.columns([1, 5])

with col1:
    if st.button("4 Couleurs"):
        st.session_state.num_selections = 4

with col2:
    if st.button("6 Couleurs"):
        st.session_state.num_selections = 6

num_selections = st.session_state.num_selections
rectangle_width = 80 if num_selections == 4 else 50
rectangle_height = 20
cols = st.columns(num_selections * 2)

if uploaded_image is not None:
    # Assure que l'image est en RGB pour éviter les problèmes liés au canal alpha ou au mode niveaux de gris
    image = Image.open(uploaded_image).convert("RGB")
    width, height = image.size
    if width > height:
        new_width = 400
        new_height = int((new_width / width) * height)
    else:
        new_height = 400
        new_width = int((new_height / height) * width)
    
    resized_image = image.resize((new_width, new_height))
    img_arr = np.array(resized_image)
    
    # Vérifie que l'image est bien en RGB
    if img_arr.shape[-1] == 3:
        pixels = img_arr.reshape(-1, 3)
        
        # Clustering et sélection de couleurs
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

        selected_colors = []
        for i in range(num_selections):
            with cols[i * 2]:
                st.markdown("<div class='color-container'>", unsafe_allow_html=True)
                for j, color_name in enumerate(ordered_colors_by_cluster[i]):
                    color_rgb = pal[color_name]
                    margin_class = "first-box" if j == 0 else ""
                    st.markdown(
                        f"<div class='color-box {margin_class}' style='background-color: rgb{color_rgb}; width: {rectangle_width}px; height: {rectangle_height}px; border-radius: 5px; margin-bottom: 4px;'></div>",
                        unsafe_allow_html=True
                    )
                st.markdown("</div>", unsafe_allow_html=True)

            with cols[i * 2 + 1]:
                selected_color_name = st.radio("", ordered_colors_by_cluster[i], key=f"radio_{i}", label_visibility="hidden")
                selected_colors.append(pal[selected_color_name])

        new_img_arr = np.zeros_like(img_arr)
        for i in range(img_arr.shape[0]):
            for j in range(img_arr.shape[1]):
                lbl = labels[i * img_arr.shape[1] + j]
                new_img_arr[i, j] = selected_colors[lbl]
        
        new_image = Image.fromarray(new_img_arr.astype('uint8'))
        width, height = new_image.size
        resized_image = new_image.resize((int(width * 1.1), int(height * 1.1)))

        col1, col2, col3 = st.columns([1, 6, 1])
        with col2:
            st.image(resized_image, caption=f"Image avec {num_selections} couleurs", use_column_width=True)
    else:
        st.error("L'image doit être en RGB (3 canaux) pour continuer.")
