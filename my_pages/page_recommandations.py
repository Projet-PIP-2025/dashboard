import streamlit as st


def show(carte_borne_pred,carte_bornes_axes):
    selected_year = st.slider(
    "Sélectionnez une année :",
    min_value=1,
    max_value=24,
    value=23,  # Valeur par défaut
    step=1,
    key="slider_year_vehicule"
    )
    selected_year = str(selected_year)
    code = f"Carte_Trimestre_{selected_year}.html"
    carte_utilise = carte_borne_pred[code]
    st.title("Carte Interactive")
    st.components.v1.html(carte_utilise, height=500, width=800)

    selected_rayon = st.slider(
    "Sélectionnez une année :",
    min_value=20,
    max_value=60,
    value=20,  # Valeur par défaut
    step=20,
    key="slider_rayon_axes"
    )

    selected_rayon = str(selected_rayon)
    code_axe = f"carte_bornes_axes_{selected_rayon}.html"
    carte_utilise_axes = carte_bornes_axes[code_axe]
    st.title("Carte Interactive")
    st.components.v1.html(carte_utilise_axes, height=500, width=800)
