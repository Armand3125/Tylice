import streamlit as st
from sklearn.cluster import KMeans
from scipy.spatial import distance
from PIL import Image
import numpy as np
import io
import os

# Définir la palette de couleurs
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

def nouvelle_img(img_arr, labels, cl, idx, pal):
    new_img_arr = np.zeros_like(img_arr)
    for i in range(img_arr.shape[0]):
        for j in range(img_arr.shape[1]):
            lbl = labels[i * img_arr.shape[1] + j]
            cl_idx = np.where(sorted_cls == lbl)[0][0]
            color_idx = idx[cl_idx]
            new_img_arr[i, j] = pal[cl[cl_idx][color_idx]]
    return new_img_arr

def traiter_img(img, Nc, Nd, dim_max):
    img = img.convert('RGB')
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

    initial_img = Image.fromarray(initial_img_arr.astype('uint8'))
    return initial_img

# Interface utilisateur avec Streamlit
st.title("Application de clustering de couleurs")
uploaded_file = st.file_uploader("Télécharge une image", type=["jpg", "jpeg", "png"])
Nc = st.slider("Nombre de clusters (Nc)", min_value=2, max_value=7, value=4)
Nd = st.slider("Nombre de choix de couleurs par cluster (Nd)", min_value=2, max_value=len(pal), value=6)
dim_max = st.number_input("Dimension max", min_value=100, max_value=1000, value=400)

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    result_img = traiter_img(img, Nc, Nd, dim_max)
    st.image(result_img, caption="Image traitée", use_column_width=True)


