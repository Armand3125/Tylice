import streamlit as st
from sklearn.cluster import KMeans
from scipy.spatial import distance
from PIL import Image
import numpy as np

pal = {
    "Noir_Charbon": (0, 0, 0), "Blanc_Jade": (255, 255, 255),
    "Jaune_Or": (228, 189, 104), "Bleu_Cyan": (0, 134, 214),
    "Violet_Lila": (174, 150, 212), "Vert_Gui": (63, 142, 67),
    "Rouge_Ecarlate": (222, 67, 67), "Bleu_Marine": (0, 120, 191),
    "Orange_Mandarine": (249, 153, 99), "Vert_Galaxie": (59, 102, 94),
    "Bleu_Glacier": (163, 216, 225), "Violet_Magenta": (236, 0, 140),
    "Gris_Argent": (166, 169, 170), "Violet_Basic": (94, 67, 183),
}

def proches(c, pal):
    dists = [(n, distance.euclidean(c, col)) for n, col in pal.items()]
    return sorted(dists, key=lambda x: x[1])

def proches_lim(c, pal, n):
    return [n for n, _ in proches(c, pal)[:n]]

def nouvelle_img(img_arr, labels, cl_proches, selected_colors, pal):
    color_map = {i: pal[cl_proches[i][selected_colors[i]]] for i in range(len(cl_proches))}
    img_mapped = np.array([color_map[label] for label in labels])
    return img_mapped.reshape(img_arr.shape)

def traiter_img(img, Nc, Nd, dim_max):
    try:
        img = Image.open(img).convert('RGB')
        img.thumbnail((dim_max, dim_max))
        img_arr = np.array(img)

        pixels = img_arr.reshape(-1, 3)
        kmeans = KMeans(n_clusters=Nc, random_state=0).fit(pixels)
        cl_centers = kmeans.cluster_centers_
        labels = kmeans.labels_

        cl_proches = [proches_lim(cl_centers[i], pal, Nd) for i in range(Nc)]

        if 'selected_colors' not in st.session_state:
            st.session_state.selected_colors = [0] * Nc

        new_img_arr = nouvelle_img(img_arr, labels, cl_proches, st.session_state.selected_colors, pal)
        st.session_state.modified_image = new_img_arr.astype('uint8')

        for i in range(Nc):
            st.write(f"Cluster {i + 1}")
            col_options = cl_proches[i]
            cols = st.columns(len(col_options))
            for j, color in enumerate(col_options):
                rgb = pal[color]
                rgb_str = f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"
                button_style = f"background-color: {rgb_str}; width: 50px; height: 20px;"
                button_style += "border: 3px solid red;" if st.session_state.selected_colors[i] == j else "border: 1px solid black;"

                if cols[j].button(label="", key=f'button_{i}_{j}', help=color, use_container_width=True):
                    st.session_state.selected_colors[i] = j
                    new_img_arr = nouvelle_img(img_arr, labels, cl_proches, st.session_state.selected_colors, pal)
                    st.session_state.modified_image = new_img_arr.astype('uint8')

                cols[j].markdown(f"<div style='{button_style}'></div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Une erreur est survenue : {e}")

st.title("Traitement d'Image avec Palette de Couleurs")
uploaded_file = st.file_uploader("Choisissez une image", type=["jpg", "jpeg", "png"])
Nc = st.slider("Nombre de Clusters", 2, 7, 4)
Nd = st.slider("Nombre de Couleurs dans la Palette", 2, len(pal), 6)
dim_max = st.number_input("Dimension maximale de l'image", min_value=100, max_value=1000, value=400, step=50)

if uploaded_file is not None:
    traiter_img(uploaded_file, Nc, Nd, dim_max)

if 'modified_image' in st.session_state:
    st.image(st.session_state.modified_image, caption="Image Modifiée", width=int(0.6 * dim_max))

if st.button("Rafraîchir l'image"):
    if uploaded_file is not None:
        traiter_img(uploaded_file, Nc, Nd, dim_max)
