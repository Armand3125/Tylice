# app.py
import streamlit as st
from sklearn.cluster import KMeans
from scipy.spatial import distance
from PIL import Image
import numpy as np
import io
import os

# Définition de la palette de couleurs
pal = {
    "Noir_Charbon": (0, 0, 0), "Blanc_Jade": (255, 255, 255),
    "Jaune_Or": (228, 189, 104), "Bleu_Cyan": (0, 134, 214),
    "Violet_Lila": (174, 150, 212), "Vert_Gui": (63, 142, 67),
    "Rouge_Ecarlate": (222, 67, 67), "Bleu_Marine": (0, 120, 191),
    "Orange_Mandarine": (249, 153, 99), "Vert_Galaxie": (59, 102, 94),
    "Bleu_Glacier": (163, 216, 225), "Violet_Magenta": (236, 0, 140),
    "Gris_Argent": (166, 169, 170), "Violet_Basic": (94, 67, 183),
}

# Fonction pour trouver les couleurs les plus proches dans la palette
def proches(c, pal):
    dists = [(n, distance.euclidean(c, col)) for n, col in pal.items()]
    return sorted(dists, key=lambda x: x[1])

def proches_lim(c, pal, n):
    return [n for n, _ in proches(c, pal)[:n]]

# Fonction pour générer une nouvelle image
def nouvelle_img(img_arr, labels, cl, idx, pal):
    new_img_arr = np.zeros_like(img_arr)
    for i in range(img_arr.shape[0]):
        for j in range(img_arr.shape[1]):
            lbl = labels[i * img_arr.shape[1] + j]
            cl_idx = np.where(sorted_cls == lbl)[0][0]
            color_idx = idx[cl_idx]
            new_img_arr[i, j] = pal[cl[cl_idx][color_idx]]
    return new_img_arr

# Fonction principale pour traiter l'image
def traiter_img(image, Nc, Nd, dim_max):
    img = Image.open(image).convert('RGB')
    img.thumbnail((dim_max, dim_max))
    img_arr = np.array(img)

    # K-means clustering
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

    initial_img = Image.fromarray(initial_img_arr.astype('uint8'))
    return initial_img, cl_proches, labels

# Interface utilisateur avec Streamlit
st.title("Clustering de Couleurs d'Image")

# Chargement de l'image
uploaded_file = st.file_uploader("Choisissez une image", type=["jpg", "jpeg", "png"])
Nc = st.slider("Nombre de clusters:", 2, 7, 4)
Nd = st.slider("Nombre de choix de couleurs:", 2, len(pal), 6)
dim_max = st.number_input("Dimension maximale de l'image:", value=400, step=50)

if uploaded_file is not None:
    initial_img, cl_proches, labels = traiter_img(uploaded_file, Nc, Nd, dim_max)

    # Affichage de l'image initiale avec clustering
    st.image(initial_img, caption="Image de base avec clustering", use_column_width=True)

    # Choix de couleurs pour chaque cluster
    idx = [0] * len(sorted_cls)
    for i, cl_idx in enumerate(sorted_cls):
        st.write(f"Cluster {i+1}")
        color_buttons = []
        for j, col_name in enumerate(cl_proches[i]):
            color_buttons.append(st.button(col_name, key=f"color_{i}_{j}"))

        # Générer une image avec la couleur sélectionnée
        if st.button("Appliquer les modifications"):
            new_img_arr = nouvelle_img(np.array(initial_img), labels, cl_proches, idx, pal)
            new_img = Image.fromarray(new_img_arr.astype('uint8'))
            st.image(new_img, caption="Image mise à jour", use_column_width=True)
