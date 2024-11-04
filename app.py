# Interface Streamlit
st.title("Traitement d'Image avec Palette de Couleurs")
uploaded_file = st.file_uploader("Choisissez une image", type=["jpg", "jpeg", "png"])
Nc = st.slider("Nombre de Clusters", 2, 7, 4)
Nd = st.slider("Nombre de Couleurs dans la Palette", 2, len(pal), 6)

# Fixer la dimension maximale de l'image à 400
dim_max = 400  

if uploaded_file is not None:
    traiter_img(uploaded_file, Nc, Nd, dim_max)

if 'modified_image' in st.session_state:
    st.image(st.session_state.modified_image, caption="Image Modifiée", width=int(1.5 * dim_max))

# Mettez à jour la partie pour afficher les boutons
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
            st.session_state.selected_colors[cl] = j
            new_img_arr = nouvelle_img(img_arr, labels, cl_proches, st.session_state.selected_colors, pal)
            st.session_state.modified_image = new_img_arr.astype('uint8')
