import streamlit as st
import pandas as pd
import folium  # type: ignore
from streamlit_folium import folium_static  # type: ignore
import json
import numpy as np
import plotly.express as px
from streamlit_option_menu import option_menu

from my_pages import page_presentations, page_stat, page_predictions, page_recommandations

st.set_page_config(page_title="Dashboard : Voiture électrique",
                   page_icon="🚘", layout="wide")

# Chargement des données


@st.cache_data
def load_data():
    # Chargement des fichiers CSV

    nb_voitures = pd.read_csv("data/nb_voiture_annee_cdr.csv")
    nb_voiture_commune = pd.read_csv("data/nb_voiture_commune.csv")
    nb_voiture_dep = pd.read_csv("data/nb_voiture_dep.csv")
    nb_voiture_reg = pd.read_csv("data/nb_voiture_reg.csv")
    bornes = pd.read_csv("data/bornes_completes.csv")
    bornes2 = pd.read_csv("data/Bornes_nettoye2.csv", delimiter = ";")
    population2 = pd.read_csv("data/population2.csv")
    trafic_dep = pd.read_csv("data/tmja_dep_df.csv")
    trafic_reg = pd.read_csv("data/tmja_reg.csv")
    # bornes_sans_date = 
    with open("data/communes.geojson", 'r') as f:
        geojson_data_com = json.load(f)
    
    with open("data/france_departments.geojson", 'r') as f:
        geojson_data_dep = json.load(f)
    

    with open("data/regions.geojson", 'r') as f:
        geojson_data_reg = json.load(f)

    return trafic_reg, trafic_dep, population2, bornes2, bornes, nb_voiture_commune, nb_voiture_dep, nb_voiture_reg, geojson_data_com, geojson_data_dep, geojson_data_reg, nb_voitures


trafic_reg, trafic_dep, population2, bornes2, bornes, nb_voiture_commune, nb_voiture_dep, nb_voiture_reg, geojson_data_com, geojson_data_dep, geojson_data_reg, nb_voitures = load_data()


def main():
    selected_page = option_menu(
        menu_title=None,  # No title
        options=["Accueil", "Carte", "Statistiques",
                 "Prédictions", "Recommandations"],  # Options
        icons=["house", "map", "bar-chart-line",
               "graph-up", "lightbulb"],  # Icons
        menu_icon="cast",  # Menu Icon
        default_index=0,  # Default
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "orange", "font-size": "25px"},
            "nav-link": {
                "font-size": "14px",
                "text-align": "center",
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
            * **Prédictions:** Faire des prédictions sur les données.
            * **Recommandations:** Faire des recommandations à partir des prédictions éffectuées.
            """
        )
        st.subheader("Réalisé par :")
        st.markdown(
            """
            * **Thomas**
            * **Koudous**
            * **Raïssa**
            * **Xavier**
            * **Antoine**
            * **Noé**
            * **Paul**
            * **Charly**
            """
        )

    elif selected_page == "Carte":
        page_presentations.show(trafic_reg,trafic_dep, population2,bornes, nb_voiture_commune, nb_voiture_dep, nb_voiture_reg,
                                geojson_data_com, geojson_data_dep, geojson_data_reg)

    elif selected_page == "Statistiques":
        page_stat.show(nb_voitures, nb_voiture_commune, bornes)

    elif selected_page == "Prédictions":
        page_predictions.show(bornes2)

    elif selected_page == "Recommandations":
        page_recommandations.show()


if __name__ == "__main__":
    main()