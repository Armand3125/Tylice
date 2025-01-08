import streamlit as st
from PIL import Image
import io
from datetime import datetime
import requests
import urllib.parse

st.title("Tylice")

# Fonction pour télécharger l'image sur Cloudinary
def upload_to_cloudinary(image_buffer):
    url = "https://api.cloudinary.com/v1_1/dprmsetgi/image/upload"
    files = {"file": image_buffer}
    data = {"upload_preset": "image_upload_tylice"}
    try:
        response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            return response.json()["secure_url"]
        else:
            return None
    except Exception as e:
        st.error(f"Erreur Cloudinary : {e}")
        return None

# Téléchargement de l'image
uploaded_image = st.file_uploader("Télécharger une image", type=["jpg", "jpeg", "png"])

if uploaded_image is not None:
    image = Image.open(uploaded_image).convert("RGB")
    resized_image = image.resize((350, 350))
    img_buffer = io.BytesIO()
    resized_image.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    cloudinary_url = upload_to_cloudinary(img_buffer)
    if cloudinary_url:
        variant_id = "50063717106003"
        encoded_url = urllib.parse.quote(cloudinary_url)
        shopify_cart_url = (
            f"https://tylice2.myshopify.com/cart/add.js?id={variant_id}&quantity=1&properties%5BImage%5D={encoded_url}"
        )

        # Intégration de JavaScript pour ouvrir une fenêtre temporaire
        js_code = f"""
            <script>
                function openCartAndClose() {{
                    var win = window.open("{shopify_cart_url}", "_blank", "width=500,height=500");
                    setTimeout(() => {{
                        if (win) win.close();
                        alert("Produit ajouté au panier avec succès !");
                    }}, 1500);  // Ferme la fenêtre après 1.5 seconde
                }}
            </script>
            <button onclick="openCartAndClose()">Ajouter au panier</button>
        """
        st.markdown(js_code, unsafe_allow_html=True)

# Conseils
st.markdown("""
    ### 📝 Conseils d'utilisation :
    - Téléchargez une image de bonne qualité.
    - Les dimensions carrées donnent de meilleurs résultats.
    - Une fois ajouté, consultez votre panier pour confirmer.
""", unsafe_allow_html=True)
