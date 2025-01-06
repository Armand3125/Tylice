# Téléchargement de l'image sur Cloudinary
cloudinary_url = upload_to_cloudinary(img_buffer)
if cloudinary_url:
    variant_id = "50063717106003" if num_selections == 4 else "50063717138771"
    encoded_url = urllib.parse.quote(cloudinary_url)
    
    # Construction de l'URL de redirection vers la page du panier
    shopify_cart_url = (
        f"https://tylice2.myshopify.com/cart?id={variant_id}&quantity=1&properties%5BImage%5D={encoded_url}"
    )
    
    # Ajout du lien redirigeant directement vers le panier
    st.markdown(f"[Accéder au panier avec l'image générée]({shopify_cart_url})", unsafe_allow_html=True)
