       /* Boutons en haut avec couleur #64AF96 */
        div.stButton > button {
            background-color: #64AF96 !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 5px !important;
            padding: 8px 16px !important;
            font-size: 14px !important;
            margin: 0 !important;
            width: 100% !important;
        }
        div.stButton > button:hover {
            background-color: #539E7D !important;
        # Ajout du message d'avertissement
        st.markdown(
            "<p style='color: #64AF96; font-size: 16px; font-weight: bold;'>"
            "L'affichage de cette section n'est pas optimisé pour les appareils mobiles. "
            "Pour une meilleure expérience et un affichage plus fluide, nous vous recommandons d'utiliser la version ordinateur.</p>",
            unsafe_allow_html=True

        )

        rectangle_width = 80 if num_selections == 4 else 50
        rectangle_height = 20
        cols_personalization = st.columns(num_selections * 2)

        image_pers = Image.open(uploaded_image).convert("RGB")
        resized_image_pers, img_arr_pers, labels_pers, sorted_indices_pers, new_width_pers, new_height_pers = process_image(image_pers, num_clusters=num_selections)

        px_per_cm = 25
        new_width_cm = round(new_width_pers / px_per_cm, 1)
        new_height_cm = round(new_height_pers / px_per_cm, 1)

        if img_arr_pers.shape[-1] == 3:
            pixels_pers = img_arr_pers.reshape(-1, 3)
            kmeans_pers = KMeans(n_clusters=num_selections, random_state=0).fit(pixels_pers)
            labels_pers = kmeans_pers.labels_
            centers_pers = kmeans_pers.cluster_centers_

            centers_rgb_pers = np.array(centers_pers, dtype=int)
            pal_rgb = np.array(list(pal.values()), dtype=int)
            distances_pers = np.linalg.norm(centers_rgb_pers[:, None] - pal_rgb[None, :], axis=2)

            ordered_colors_by_cluster = []
            for i in range(num_selections):
                closest_colors_idx = distances_pers[i].argsort()
                ordered_colors_by_cluster.append([list(pal.keys())[idx] for idx in closest_colors_idx])

            cluster_counts_pers = np.bincount(labels_pers)
            total_pixels_pers = len(labels_pers)
            cluster_percentages_pers = (cluster_counts_pers / total_pixels_pers) * 100

            sorted_indices_pers = np.argsort(-cluster_percentages_pers)
            sorted_ordered_colors_by_cluster_pers = [ordered_colors_by_cluster[i] for i in sorted_indices_pers]

            selected_colors = []
            selected_color_names = []
            for i, cluster_index in enumerate(sorted_indices_pers):
                with cols_personalization[i * 2]:
                    st.markdown("<div class='color-container'>", unsafe_allow_html=True)
                    for j, color_name in enumerate(sorted_ordered_colors_by_cluster_pers[i]):
                        color_rgb = pal[color_name]
                        margin_class = "first-box" if j == 0 else ""
                        st.markdown(
                            f"<div class='color-box {margin_class}' style='background-color: rgb{color_rgb}; width: {rectangle_width}px; height: {rectangle_height}px; border-radius: 5px; margin-bottom: 4px;'></div>",
                            unsafe_allow_html=True
                        )
                    st.markdown("</div>", unsafe_allow_html=True)
                with cols_personalization[i * 2 + 1]:
                    selected_color_name = st.radio("", sorted_ordered_colors_by_cluster_pers[i], key=f"radio_{i}_pers", label_visibility="hidden")
                    selected_colors.append(pal[selected_color_name])
                    selected_color_names.append(selected_color_name)

            new_img_arr_pers = np.zeros_like(img_arr_pers)
            for i in range(img_arr_pers.shape[0]):
                for j in range(img_arr_pers.shape[1]):
                    lbl = labels_pers[i * img_arr_pers.shape[1] + j]
                    new_color_index = np.where(sorted_indices_pers == lbl)[0][0]
                    new_img_arr_pers[i, j] = selected_colors[new_color_index]

            new_image_pers = Image.fromarray(new_img_arr_pers.astype('uint8'))
            resized_image_pers_final = new_image_pers

            col1_pers, col2_pers, col3_pers = st.columns([1, 6, 1])
            with col2_pers:
                st.image(resized_image_pers_final, use_container_width=True)
                # Création d'une ligne à 3 colonnes sous l'image
                cols_info = st.columns([1,1,1])
                with cols_info[0]:
                    st.markdown(f"<p class='dimension-text'>{new_width_cm} cm x {new_height_cm} cm</p>", unsafe_allow_html=True)
                with cols_info[1]:
                    st.markdown(f"<div class='label'>{num_selections} Couleurs - {'7.95' if num_selections == 4 else '11.95'} €</div>", unsafe_allow_html=True)
                with cols_info[2]:
                    img_buffer_pers = io.BytesIO()
                    new_image_pers.save(img_buffer_pers, format="PNG")
                    img_buffer_pers.seek(0)
                    cloudinary_url_pers = upload_to_cloudinary(img_buffer_pers)
                    if not cloudinary_url_pers:
                        st.error("Erreur lors du téléchargement de l'image. Veuillez réessayer.")
                    else:
                        shopify_cart_url_pers = generate_shopify_cart_url(cloudinary_url_pers, num_selections)
                        st.markdown(f"<a href='{shopify_cart_url_pers}' class='shopify-link' target='_blank'>Ajouter au panier</a>", unsafe_allow_html=True)

    # =========================================
    # Section Exemples de Recoloration
    # =========================================
    if st.session_state.show_examples:
        st.header("Exemples de Recoloration")

        image = Image.open(uploaded_image).convert("RGB")
        st.subheader("Palettes 4 Couleurs")
        cols_display = st.columns(2)
        col_count = 0
        for palette in palettes_examples_4:
            num_clusters = len(palette)
            palette_colors = [pal[color] for color in palette]
            resized_image, img_arr, labels, sorted_indices, new_width, new_height = process_image(image, num_clusters=num_clusters)
            recolored_image = recolor_image(img_arr, labels, sorted_indices, palette_colors)
            img_buffer = io.BytesIO()
            recolored_image.save(img_buffer, format="PNG")
            img_buffer.seek(0)
            cloudinary_url = upload_to_cloudinary(img_buffer)
            price = "7.95"
            if cloudinary_url:
                shopify_cart_url = generate_shopify_cart_url(cloudinary_url, num_colors=num_clusters)
                combined_html = generate_label_and_button_examples(num_clusters, price, shopify_cart_url)
            else:
                combined_html = "Erreur lors de l'ajout au panier."
            with cols_display[col_count % 2]:
                st.image(recolored_image, use_container_width=True, width=350)
                st.markdown(combined_html, unsafe_allow_html=True)
            col_count += 1
            if col_count % 2 == 0:
                st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
        st.subheader("Palettes 6 Couleurs")
        cols_display = st.columns(2)
        col_count = 0
        for palette in palettes_examples_6:
            num_clusters = len(palette)
            palette_colors = [pal[color] for color in palette]
            resized_image, img_arr, labels, sorted_indices, new_width, new_height = process_image(image, num_clusters=num_clusters)
            recolored_image = recolor_image(img_arr, labels, sorted_indices, palette_colors)
            img_buffer = io.BytesIO()
            recolored_image.save(img_buffer, format="PNG")
            img_buffer.seek(0)
            cloudinary_url = upload_to_cloudinary(img_buffer)
            price = "11.95"
            if cloudinary_url:
                shopify_cart_url = generate_shopify_cart_url(cloudinary_url, num_colors=num_clusters)
                combined_html = generate_label_and_button_examples(num_clusters, price, shopify_cart_url)
            else:
                combined_html = "Erreur lors de l'ajout au panier."
            with cols_display[col_count % 2]:
                st.image(recolored_image, use_container_width=True, width=350)
                st.markdown(combined_html, unsafe_allow_html=True)
            col_count += 1
            if col_count % 2 == 0:
                st.markdown("<br>", unsafe_allow_html=True)
