import streamlit as st
import pandas as pd
import folium  # type: ignore
from streamlit_folium import folium_static  # type: ignore
import json
import numpy as np
import plotly.express as px
from streamlit_option_menu import option_menu

from my_pages import page_presentations, page_stat, page_predictions

st.set_page_config(page_title="Dashboard : Voiture électrique",
                   page_icon="🚘", layout="wide")

# Chargement des données


@st.cache_data
def load_data():
    # Chargement des fichiers CSV

    nb_voiture_commune = pd.read_csv("C:\\Users\\MRH4\OneDrive - MODEL RH\\Bureau\\Dossier_git\\data\\nb_voiture_commune.csv")
    nb_voiture_dep = pd.read_csv("C:\\Users\\MRH4\OneDrive - MODEL RH\\Bureau\\Dossier_git\\data\\nb_voiture_dep.csv")
    nb_voiture_reg = pd.read_csv("C:\\Users\\MRH4\OneDrive - MODEL RH\\Bureau\\Dossier_git\\data\\nb_voiture_reg.csv")


    bornes = pd.read_csv("data/Bornes_nettoye2.csv",sep=";",encoding="utf-8")



    with open("data/communes.geojson", 'r') as f:
        geojson_data_com = json.load(f)

    with open("data/france_departments.geojson", 'r') as f:
        geojson_data_dep = json.load(f)

    with open("data/regions.geojson", 'r') as f:
        geojson_data_reg = json.load(f)

    return bornes, nb_voiture_commune,nb_voiture_dep, nb_voiture_reg, geojson_data_com, geojson_data_dep, geojson_data_reg


bornes, nb_voiture_commune, nb_voiture_dep, nb_voiture_reg, geojson_data_com, geojson_data_dep, geojson_data_reg = load_data()


def main():
    selected_page = option_menu(
        menu_title=None,  # No title
        options=["Accueil", "Carte", "Statistiques", "Prédictions"],  # Options
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

    if selected_page == "Accueil":
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

    elif selected_page == "Carte":
        page_presentations.show(bornes, nb_voiture_commune, nb_voiture_dep, nb_voiture_reg,
                                 geojson_data_com, geojson_data_dep, geojson_data_reg)

    elif selected_page == "Statistiques":
        page_stat.show()

    elif selected_page == "Prédictions":
        page_predictions.show()


if __name__ == "__main__":
    main()
