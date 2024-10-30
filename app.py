import streamlit as st
from sklearn.cluster import KMeans
from scipy.spatial import distance
from PIL import Image
import numpy as np
import io

# Dictionnaire de couleurs
pal = {
    "Noir_Charbon": (0, 0, 0), "Blanc_Jade": (255, 255, 255),
    "Jaune_Or": (228, 189, 104), "Bleu_Cyan": (0, 134, 214),
    "Violet_Lila": (174, 150, 212), "Vert_Gui": (63, 142, 67),
    "Rouge_Ecarlate": (222, 67, 67), "Bleu_Marine": (0, 120, 191),
    "Orange_Mandarine": (249, 153, 99), "Vert_Galaxie": (59, 102, 94),
    "Bleu_Glacier": (163, 216, 225), "Violet_Magenta": (236, 0, 140),
    "Gris_Argent": (166, 169, 170), "Violet_Basic": (94, 67, 183),
}

# Fonction pour trouver les couleurs proches dans la palette
def proches(c, pal):
    dists = [(n, distance.euclidean(c, col)) for n, col in pal.items()]
    return sorted(dists, key=lambda x: x[1])

def proches_lim(c, pal, n):
    return [n for n, _ in proches(c, pal)[:n]]

# Créer une nouvelle image avec les couleurs de la palette
def nouvelle_img(img_arr, labels, cl, idx, pal):
    new_img_arr = np.zeros_like(img_arr)
    for i in range(img_arr.shape[0]):
        for j in range(img_arr.shape[1]):
            lbl = labels[i * img_arr.shape[1] + j]
            cl_idx = np.where(sorted_cls == lbl)[0][0]
            color_idx = idx[cl_idx]
            new_img_arr[i, j] = pal[cl[cl_idx][color_idx]]
    return new_img_arr

# Fonction pour traiter et afficher l'image
def traiter_img(img, Nc, Nd, dim_max):
    img = Image.open(img).convert('RGB')
    img.thumbnail((dim_max, dim_max))
    img_arr = np.array(img)

    pixels = img_arr.reshape(-1, 3)
    kmeans = KMeans(n_clusters=Nc, random_state=0).fit(pixels)
    cl_centers = kmeans.cluster_centers_
    labels = kmeans.labels_

    uniq, counts = np.unique(labels, return_counts=True)
    cl_counts = dict(zip(uniq, counts))
    total_px = pixels.shape[0]
    global sorted_cls
    sorted_cls = sorted(cl_counts.keys(), key=lambda x: cl_counts[x], reverse=True)

    cl_proches = [proches_lim(cl_centers[i], pal, Nd) for i in sorted_cls]
    initial_img_arr = np.zeros_like(img_arr)
    for i in range(img_arr.shape[0]):
        for j in range(img_arr.shape[1]):
            lbl = labels[i * img_arr.shape[1] + j]
            initial_img_arr[i, j] = cl_centers[lbl]

    # Afficher l'image initiale
    st.image(initial_img_arr.astype('uint8'), caption="Image Initiale", use_column_width=True)

    idx = [0] * len(sorted_cls)

    # Sélection des couleurs pour chaque cluster
    for i, cl_idx in enumerate(sorted_cls):
        st.write(f"Cluster {i+1} - {(counts[cl_idx] / total_px) * 100:.2f}%")
        
        # Créer des boutons colorés
        col_options = cl_proches[i]
        selected_color = None
        
        cols = st.columns(len(col_options))  # Créer des colonnes pour les boutons
        for j, col_name in enumerate(col_options):
            rgb = pal[col_name]
            with cols[j]:
                if st.button(f"{col_name}", key=f"btn_{i}_{j}"):
                    selected_color = j
                    idx[i] = selected_color

        # Appliquer la couleur sélectionnée
        if selected_color is not None:
            st.success(f"Vous avez sélectionné: {col_options[selected_color]}")

    # Mise à jour de l'image avec les couleurs sélectionnées
    if st.button("Appliquer les modifications", key="apply_button"):
        new_img_arr = nouvelle_img(img_arr, labels, cl_proches, idx, pal)
        st.image(new_img_arr.astype('uint8'), caption="Image Modifiée", use_column_width=True)

# Widgets d'entrée
st.title("Traitement d'Image avec Palette de Couleurs")
uploaded_file = st.file_uploader("Choisissez une image", type=["jpg", "jpeg", "png"])
Nc = st.slider("Nombre de Clusters", 2, 7, 4)
Nd = st.slider("Nombre de Couleurs dans la Palette", 2, len(pal), 6)
dim_max = st.number_input("Dimension maximale de l'image", min_value=100, max_value=1000, value=400, step=50)

# Lancer le traitement d'image si un fichier est téléchargé
if uploaded_file is not None:
    traiter_img(uploaded_file, Nc, Nd, dim_max)
