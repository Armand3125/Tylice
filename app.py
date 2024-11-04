import streamlit as st
from sklearn.cluster import KMeans
from scipy.spatial import distance
from PIL import Image
import numpy as np

# Palette de couleurs définie
pal = {
    "Noir_Charbon": (0, 0, 0), "Blanc_Jade": (255, 255, 255),
    "Jaune_Or": (228, 189, 104), "Bleu_Cyan": (0, 134, 214),
    "Violet_Lila": (174, 150, 212), "Vert_Gui": (63, 142, 67),
    "Rouge_Ecarlate": (222, 67, 67), "Bleu_Marine": (0, 120, 191),
    "Orange_Mandarine": (249, 153, 99), "Vert_Galaxie": (59, 102, 94),
    "Bleu_Glacier": (163, 216, 225), "Violet_Magenta": (236, 0, 140),
    "Gris_Argent": (166, 169, 170), "Violet_Basic": (94, 67, 183),
}

# Calculer les couleurs les plus proches
def proches(c, pal):
    dists = [(n, distance.euclidean(c, col)) for n, col in pal.items()]
    return sorted(dists, key=lambda x: x[1])

def proches_lim(c, pal, n):
    return [n for n, _ in proches(c, pal)[:n]]

# Créer une nouvelle image en mappant les clusters aux couleurs de la palette
def nouvelle_img(img_arr, labels, cl_proches, selected_colors, pal):
    color_map = {i: pal[cl_proches[i][selected_colors[i]]] for i in range(len(cl_proches))}
    img_mapped = np.array([color_map[label] for label in labels])
    return img_mapped.reshape(img_arr.shape)

@st.cache_data
def traiter_img(img, Nc, Nd, dim_max):
    try:
        img = Image.open(img).convert('RGB')
        img.thumbnail((dim_max, dim_max))
        img_arr = np.array(img)

        pixels = img_arr.reshape(-1, 3)
        kmeans = KMeans(n_clusters=Nc, random_state=0).fit(pixels)
        labels = kmeans.labels_

        uniq, counts = np.unique(labels, return_counts=True)
        total_px = pixels.shape[0]
        cl_counts = dict(zip(uniq, counts))

        sorted_cls = sorted(cl_counts.items(), key=lambda x: x[1], reverse=True)
        cl_proches = [proches_lim(kmeans.cluster_centers_[i], pal, Nd) for i in cl_counts.keys()]

        return img_arr, labels, sorted_cls, total_px, cl_proches  # Retourne les valeurs nécessaires

    except Exception as e:
        st.error(f"Une erreur est survenue : {e}")
        return None, None, None, None, None  # Retournez None pour tous les retours en cas d'erreur

# Interface Streamlit
st.title("Traitement d'Image avec Palette de Couleurs")
uploaded_file = st.file_uploader("Choisissez une image", type=["jpg", "jpeg", "png"])
Nc = st.slider("Nombre de Clusters", 2, 7, 4)
Nd = st.slider("Nombre de Couleurs dans la Palette", 2, len(pal), 6)

# Fixer la dimension maximale de l'image à 400
dim_max = 400  

img_arr, labels, sorted_cls, total_px, cl_proches = None, None, None, None, None  # Initialiser ces variables

if uploaded_file is not None:
    img_arr, labels, sorted_cls, total_px, cl_proches = traiter_img(uploaded_file, Nc, Nd, dim_max)

if 'modified_image' not in st.session_state:
    st.session_state.modified_image = None

# Vérifiez si sorted_cls et total_px ne sont pas None avant de les utiliser
if sorted_cls is not None and total_px is not None and labels is not None:
    if st.session_state.modified_image is not None:
        st.image(st.session_state.modified_image, caption="Image Modifiée", width=int(1.5 * dim_max))

    for idx, (cl, count) in enumerate(sorted_cls):
        percentage = (count / total_px) * 100
        st.write(f"Cluster {idx + 1} - {percentage:.2f}%")
        col_options = cl_proches[cl]
        cols = st.columns(len(col_options))

        for j, color in enumerate(col_options):
            rgb = pal[color]
            rgb_str = f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"

            # Appliquer un encadré autour du bouton sélectionné
            border_style = "border: 2px solid black; border-radius: 5px;" if st.session_state.selected_colors[cl] == j else ""

            # Afficher un rectangle coloré comme fond de bouton
            cols[j].markdown(
                f"<div style='background-color: {rgb_str}; width: 40px; height: 20px; {border_style} display: inline-block;'></div>",
                unsafe_allow_html=True
            )

            # Utiliser un bouton Streamlit
            button_key = f'button_{idx}_{j}_{color}'
            if cols[j].button(label="", key=button_key, help=color):
                # Ne pas recalculer l'image à chaque clic; seulement stocker la sélection
                st.session_state.selected_colors[cl] = j
                # Mettre à jour l'image seulement lorsque tous les choix sont faits
                new_img_arr = nouvelle_img(img_arr, labels, cl_proches, st.session_state.selected_colors, pal)
                st.session_state.modified_image = new_img_arr.astype('uint8')
                st.image(st.session_state.modified_image, caption="Image Modifiée", width=int(1.5 * dim_max))  # Afficher immédiatement la nouvelle image
