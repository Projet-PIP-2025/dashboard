import streamlit as st
from streamlit_option_menu import option_menu

st.set_page_config(page_title="Dashboard GRP 8", page_icon="🚘", layout="wide")

selected = option_menu(
    menu_title=None,  # No title
    options=["Accueil", "Carte", "Statistiques"],  # Options
    icons=["house", "map", "bar-chart-line"],  # Icons
    menu_icon="cast",  # Menu Icon
    default_index=0,  # Default
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#fafafa"},
        "icon": {"color": "orange", "font-size": "25px"},
        "nav-link": {
            "font-size": "16px",
            "text-align": "left",
            "margin": "0px",
            "--hover-color": "#eee",
        },
        "nav-link-selected": {"background-color": "#02ab2f"},
    },
)

if selected == "Accueil":
    st.title("Bienvenue sur le Dashboard des Véhicules Électriques")
    st.markdown(
        """
        Ce dashboard présente des données sur les véhicules électriques en France.  
        Vous pouvez explorer les données par région, département et commune.
        """
    )
    st.subheader("Navigation")
    st.markdown(
        """
        Utilisez le menu en haut de la page pour naviguer entre les différentes sections :
        * **Carte:** Visualisez les données sur une carte interactive.
        * **Statistiques:** Explorez les données à travers des graphiques.
        """
    )

elif selected == "Carte":
    st.write("Page Carte")

elif selected == "Statistiques":
    st.write("Page Statistiques")
