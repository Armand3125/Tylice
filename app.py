import streamlit as st
import requests
import json
import urllib.parse
from PIL import Image
import io
from sklearn.cluster import KMeans
import numpy as np
from datetime import datetime

# Shopify Storefront Access
SHOPIFY_STORE_URL = "https://tylice2.myshopify.com"
STOREFRONT_ACCESS_TOKEN = "cc89c5d179a1bbd47e34fda34a26b27a"
VARIANT_ID_4_COLORS = "50063717106003"  # ID pour 4 couleurs
VARIANT_ID_6_COLORS = "50063717138771"  # ID pour 6 couleurs

# Cloudinary config
CLOUDINARY_URL = "https://api.cloudinary.com/v1_1/dprmsetgi/image/upload"
CLOUDINARY_UPLOAD_PRESET = "image_upload_tylice"

# Streamlit UI
st.title("Tylice - Personnalisation d'images")

# Téléchargement de l'image
uploaded_image = st.file_uploader("Téléchargez une image", type=["jpg", "jpeg", "png"])

# Sélection du nombre de couleurs
col1, col2 = st.columns([2, 5])

if "num_selections" not in st.session_state:
    st.session_state.num_selections = 4

with col1:
    if st.button("4 Couleurs : 7.95 €"):
        st.session_state.num_selections = 4

with col2:
    if st.button("6 Couleurs : 11.95 €"):
        st.session_state.num_selections = 6

num_selections = st.session_state.num_selections

# Fonction pour uploader l'image sur Cloudinary
def upload_to_cloudinary(image_buffer):
    files = {"file": image_buffer}
    data = {"upload_preset": CLOUDINARY_UPLOAD_PRESET}
    response = requests.post(CLOUDINARY_URL, files=files, data=data)
    if response.status_code == 200:
        return response.json()["secure_url"]
    else:
        st.error("Erreur lors de l'envoi à Cloudinary")
        return None

# Fonction pour créer un panier dans Shopify
def create_cart():
    url = f"{SHOPIFY_STORE_URL}/api/2023-01/graphql.json"
    query = """
    mutation {
      cartCreate(input: {}) {
        cart {
          id
        }
        userErrors {
          field
          message
        }
      }
    }
    """
    headers = {
        "X-Shopify-Storefront-Access-Token": STOREFRONT_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json={"query": query})
    data = response.json()
    if "data" in data and "cartCreate" in data["data"] and "cart" in data["data"]["cartCreate"]:
        return data["data"]["cartCreate"]["cart"]["id"]
    else:
        st.error(f"Erreur lors de la création du panier : {data}")
        return None

# Fonction pour ajouter un produit au panier Shopify
def add_to_cart(cart_id, variant_id, image_url):
    url = f"{SHOPIFY_STORE_URL}/api/2023-01/graphql.json"
    query = f"""
    mutation {{
      cartLinesAdd(cartId: "{cart_id}", lines: [
        {{
          quantity: 1,
          merchandiseId: "gid://shopify/ProductVariant/{variant_id}",
          attributes: [
            {{ key: "Image", value: "{image_url}" }}
          ]
        }}
      ]) {{
        cart {{
          id
          lines(first: 5) {{
            edges {{
              node {{
                quantity
                merchandise {{
                  title
                }}
              }}
            }}
          }}
        }}
        userErrors {{
          field
          message
        }}
      }}
    }}
    """
    headers = {
        "X-Shopify-Storefront-Access-Token": STOREFRONT_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json={"query": query})
    return response.json()

# Traitement de l'image téléchargée
if uploaded_image:
    image = Image.open(uploaded_image).convert("RGB")
    width, height = image.size
    dim = 350
    new_width = dim if width > height else int((dim / height) * width)
    new_height = dim if height >= width else int((dim / width) * height)

    resized_image = image.resize((new_width, new_height))
    img_arr = np.array(resized_image)

    # Application de KMeans
    pixels = img_arr.reshape(-1, 3)
    kmeans = KMeans(n_clusters=num_selections, random_state=0).fit(pixels)
    labels = kmeans.labels_
    centers = kmeans.cluster_centers_

    # Création d'une nouvelle image avec les couleurs sélectionnées
    new_img_arr = np.zeros_like(img_arr)
    for i in range(img_arr.shape[0]):
        for j in range(img_arr.shape[1]):
            lbl = labels[i * img_arr.shape[1] + j]
            new_img_arr[i, j] = centers[lbl]

    new_image = Image.fromarray(new_img_arr.astype("uint8"))
    img_buffer = io.BytesIO()
    new_image.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    # Afficher l'image traitée
    st.image(new_image, caption="Image traitée", use_column_width=True)

    # Uploader l'image sur Cloudinary
    cloudinary_url = upload_to_cloudinary(img_buffer)
    if cloudinary_url:
        st.markdown(f"URL de l'image : [Voir l'image]({cloudinary_url})")

        # Création d'un panier
        cart_id = create_cart()
        if cart_id:
            st.write(f"Panier créé avec l'ID : {cart_id}")

            # Ajouter l'image et le produit au panier
            variant_id = VARIANT_ID_4_COLORS if num_selections == 4 else VARIANT_ID_6_COLORS
            result = add_to_cart(cart_id, variant_id, cloudinary_url)
            st.write("Résultat de l'ajout au panier : ", result)
