import streamlit as st
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import io
import json

# Variant IDs pour vos produits
VARIANT_ID_4_COLORS = "50063717106003"
VARIANT_ID_6_COLORS = "50063717138771"

# Application Streamlit
st.title("Tylice - Ajout au Panier Shopify avec JavaScript")

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
    centers = kmeans.cluster_centers_
    selected_colors = [tuple(map(int, c)) for c in centers]

    st.write("Couleurs dominantes :")
    for color in selected_colors:
        st.markdown(f"<div style='background-color: rgb{color}; width: 50px; height: 20px;'></div>", unsafe_allow_html=True)

    # Préparer l'image pour l'upload (simulation)
    image_url = f"https://upload-lift-example.com/{uploaded_image.name}"

    # Sélection du bon variant ID
    variant_id = VARIANT_ID_4_COLORS if num_selections == 4 else VARIANT_ID_6_COLORS

    # Propriétés personnalisées
    properties = {
        "Image": image_url,
        "Couleurs dominantes": ", ".join([f"rgb{color}" for color in selected_colors]),
    }

    # Bouton pour ajouter au panier
    if st.button("Ajouter au panier"):
        # Génération du script JavaScript
        js_code = f"""
        <script>
        fetch('/cart/add.js', {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/json',
            }},
            body: JSON.stringify({{
                id: '{variant_id}',
                quantity: 1,
                properties: {json.dumps(properties)}
            }})
        }})
        .then(response => {{
            if (!response.ok) throw new Error('Erreur lors de l\'ajout au panier');
            return response.json();
        }})
        .then(data => {{
            alert('Produit ajouté au panier avec succès !');
            console.log(data);
        }})
        .catch(error => {{
            alert('Erreur : ' + error.message);
        }});
        </script>
        """
        st.markdown(js_code, unsafe_allow_html=True)

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
