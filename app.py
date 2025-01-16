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
    nb_voitures = pd.read_csv("data/nb_voiture_annee_cdr.csv", encoding="utf-8")
    nb_voiture_commune = pd.read_csv("data/nb_voiture_commune.csv", encoding="utf-8")
    nb_voiture_dep = pd.read_csv("data/nb_voiture_dep.csv", encoding="utf-8")
    nb_voiture_reg = pd.read_csv("data/nb_voiture_reg.csv", encoding="utf-8")
    bornes_vehicules_dep = pd.read_csv("data/croisement_donnee_borne_voiture_departement.csv", encoding="utf-8")
    bornes_vehicules_reg = pd.read_csv("data/croisement_donnee_borne_voiture_region.csv", encoding="utf-8")
    bornes = pd.read_csv("data/bornes_completes.csv", encoding="utf-8")
    bornes2 = pd.read_csv("data/Bornes_nettoye2.csv" , delimiter = ";", encoding="utf-8")
    bornes_completes = pd.read_csv("data/bornes_completes2.csv", encoding="utf-8") # Données utilisées pour Aménageurs & Opérateurs (statistiques)
    bornes_pred = pd.read_csv("data/Pred_Borne_fr.csv" , delimiter = ";", encoding="utf-8")
    pred_reg = pd.read_csv("data/Pred_Reg_tout.csv" , delimiter = ";", encoding="utf-8")
    pred_ve = pd.read_csv("data/Pred_ve_tout.csv" , delimiter = ";", encoding="utf-8")
    population2 = pd.read_csv("data/population2.csv", encoding="utf-8")
    trafic_dep = pd.read_csv("data/tmja_dep_df.csv", encoding="utf-8")
    trafic_reg = pd.read_csv("data/tmja_reg.csv", encoding="utf-8")
    reco_borne_ve = pd.read_csv("data/tab_reco_borne_pour_ve.csv" , delimiter = ";", encoding="utf-8")
    bornes_tmja_par_annee = pd.read_csv("data/bornes_tmja_ratio_annee.csv", encoding="utf-8")

    # bornes_sans_date =
    with open("data/carte_interactive_avec_bornes.html", "r", encoding="utf-8") as file:
        carte_html = file.read()
    with open("data/Carte_html/carte_commune_2023.html", "r", encoding="utf-8") as file:
        carte_html_commune = file.read()
    with open("data/carte_tmja_troncons.html", "r", encoding="utf-8") as file:
        carte_html2 = file.read()

    # -- Données geojson --
    with open("data/communes.geojson", 'r', encoding="utf-8") as f:
        geojson_data_com = json.load(f)
    with open("data/france_departments.geojson", 'r', encoding="utf-8") as f:
        geojson_data_dep = json.load(f)
    with open("data/regions.geojson", 'r', encoding="utf-8") as f:
        geojson_data_reg = json.load(f)

    # -- Page Stat --
    with open("data/Carte_html/carte_vehicule_borne_reg.html", "r", encoding="utf-8") as file:
        carte_vehicule_borne_reg = file.read()
    with open("data/Carte_html/carte_vehicule_borne_dep.html", "r", encoding="utf-8") as file:
        carte_vehicule_borne_dep = file.read()
    with open("data/Carte_html/carte_tmja_reg.html", "r", encoding="utf-8") as file:
        carte_tmja_reg = file.read()
    with open("data/Carte_html/carte_tmja_dep.html", "r", encoding="utf-8") as file:
        carte_tmja_dep = file.read()
    with open("data/Carte_html/carte_bornes_tmja_reg.html", "r", encoding="utf-8") as file:
        carte_bornes_tmja_reg = file.read()
    with open("data/Carte_html/carte_bornes_tmja_dep.html", "r", encoding="utf-8") as file:
        carte_bornes_tmja_dep = file.read()

    return reco_borne_ve,pred_ve, pred_reg, bornes_pred, bornes_vehicules_dep, bornes_vehicules_reg, trafic_reg, trafic_dep, population2, bornes2, bornes, nb_voiture_commune, nb_voiture_dep, nb_voiture_reg, geojson_data_com, geojson_data_dep, geojson_data_reg, nb_voitures, bornes_completes, carte_html_commune,carte_html2,carte_html,carte_vehicule_borne_reg,carte_vehicule_borne_dep,carte_tmja_reg,carte_tmja_dep,carte_bornes_tmja_reg,carte_bornes_tmja_dep, bornes_tmja_par_annee

reco_borne_ve,pred_ve, pred_reg, bornes_pred, bornes_vehicules_dep, bornes_vehicules_reg, trafic_reg, trafic_dep, population2, bornes2, bornes, nb_voiture_commune, nb_voiture_dep, nb_voiture_reg, geojson_data_com, geojson_data_dep, geojson_data_reg, nb_voitures, bornes_completes, carte_html_commune,carte_html2,carte_html, carte_vehicule_borne_reg, carte_vehicule_borne_dep, carte_tmja_reg, carte_tmja_dep, carte_bornes_tmja_reg, carte_bornes_tmja_dep, bornes_tmja_par_annee = load_data()


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
        page_presentations.show(carte_html2,trafic_reg,trafic_dep, population2,bornes, nb_voiture_commune, nb_voiture_dep, nb_voiture_reg,
                                geojson_data_com, geojson_data_dep, geojson_data_reg, carte_tmja_reg, carte_tmja_dep)
        page_presentations.show(carte_html2,trafic_reg,trafic_dep, population2,bornes, nb_voiture_commune, nb_voiture_dep, nb_voiture_reg,
                                geojson_data_com, geojson_data_dep, geojson_data_reg, carte_tmja_reg, carte_tmja_dep)

    elif selected_page == "Statistiques":
        page_stat.show(nb_voitures, bornes_completes, bornes, carte_vehicule_borne_reg, carte_vehicule_borne_dep, carte_bornes_tmja_reg, carte_bornes_tmja_dep, bornes_tmja_par_annee)

    elif selected_page == "Prédictions":
        page_predictions.show(bornes_pred, pred_reg, pred_ve)

    elif selected_page == "Recommandations":
        page_recommandations.show(reco_borne_ve)


if __name__ == "__main__":
    main()