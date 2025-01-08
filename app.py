import streamlit as st
import pandas as pd
import folium  # type: ignore
from streamlit_folium import folium_static  # type: ignore
import json
import numpy as np
import plotly.express as px

from my_pages import page_presentations, page_stat, page_predictions

# Chargement des données
@st.cache_data
def load_data():
    # Chargement des fichiers CSV
    nb_voiture_commune_dep = pd.read_csv("data/nb_voiture_commune_dep.csv")
    nb_voiture_commune_dep2 = pd.read_csv("data/nb_voiture_annee_cdr.csv")

    # Ajout d'une colonne combinée pour le département
    nb_voiture_commune_dep['dept_code_name'] = nb_voiture_commune_dep['code_dep'].astype(str) + ' - ' + nb_voiture_commune_dep['nom_departement']

    nb_voiture_commune_dep2["codgeo"] = nb_voiture_commune_dep2["codgeo"].astype(str)
    nb_voiture_commune_dep2["code_dep"] = nb_voiture_commune_dep2["code_dep"].astype(str)
    nb_voiture_commune_dep2["code_region"] = nb_voiture_commune_dep2["code_region"].astype(str)
    nb_voiture_commune_dep2['dept_code_name'] = nb_voiture_commune_dep2['code_dep'].astype(str) + ' - ' + nb_voiture_commune_dep2['nom_departement']
    nb_voiture_commune_dep2['reg_code_name'] = nb_voiture_commune_dep2['code_region'].astype(str) + ' - ' + nb_voiture_commune_dep2['nom_region']
    nb_voiture_commune_dep2['com_code_name'] = nb_voiture_commune_dep2['codgeo'].astype(str) + ' - ' + nb_voiture_commune_dep2['libgeo']

    with open("data/communes.geojson", 'r') as f:
        geojson_data_com = json.load(f)

    with open("data/france_departments.geojson", 'r') as f:
        geojson_data_dep = json.load(f)

    with open("data/regions.geojson", 'r') as f:
        geojson_data_reg = json.load(f)

    return nb_voiture_commune_dep, nb_voiture_commune_dep2, geojson_data_com, geojson_data_dep, geojson_data_reg


nb_voiture_commune_dep, nb_voiture_commune_dep2, geojson_data_com, geojson_data_dep, geojson_data_reg = load_data()

def main():
    st.sidebar.title("Navigation")  # Crée une barre latérale pour la navigation
    page = st.sidebar.radio("Aller à", ["Présentation", "Statistiques descriptives", "Prédiction"])

    # Appeler la fonction correspondante à la page choisie
    if page == "Présentation":
        page_presentations.show(nb_voiture_commune_dep, nb_voiture_commune_dep2, geojson_data_com, geojson_data_dep, geojson_data_reg)
    elif page == "Statistiques descriptives":
        page_stat.show()
    elif page == "Prédiction":
        page_predictions.show()

if __name__ == "__main__":
    main()
