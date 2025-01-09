import streamlit as st
import folium # type: ignore
from streamlit_folium import folium_static # type: ignore
import json
import numpy as np
import plotly.express as px

def create_map(nb_voiture_commune_dep, geojson_data,col_granu, info_carte):
    # Initialisation de la carte centrée sur la France
    map = folium.Map(location=[46.603354, 1.8883344], zoom_start=6, tiles='CartoDB positron')

    if info_carte == "nombre de véhicule":
        # Conversion des données en dictionnaire pour relier avec le GeoJSON
        col = 'nb_vp_rechargeables_el'
    elif "ratio de véhicule électrique par rapport au total":
        # Conversion des données en dictionnaire pour relier avec le GeoJSON
        col = 'ratio_elec_total'

    vehicle_dict = nb_voiture_commune_dep.set_index(col_granu)[col].to_dict()
    # Ajout des données au GeoJSON
    for feature in geojson_data['features']:
        feature_code = feature['properties']['code']
        feature['properties']['vehicles'] = vehicle_dict.get(feature_code, 'N/A')

    # Ajout d'un choropleth pour afficher les données
    folium.Choropleth(
        geo_data=geojson_data,
        name="Véhicules électriques par département",
        data=nb_voiture_commune_dep,
        columns=[col_granu, col],
        key_on='feature.properties.code',
        fill_color='YlGnBu',
        fill_opacity=0.7,
        line_opacity=0.05,
        legend_name="Nombre de véhicules électriques"
    ).add_to(map)
    # Ajout de tooltips interactifs
    folium.GeoJson(
        geojson_data,
        name="Détails",
        tooltip=folium.GeoJsonTooltip(
            fields=['code', 'nom', 'vehicles'],
            aliases=['Code :', 'Nom:', 'Véhicules électriques:']
        )
    ).add_to(map)

    # Ajout des contrôles de couches
    folium.LayerControl().add_to(map)
    
    return map

def show(bornes, nb_voiture_commune, nb_voiture_dep, nb_voiture_reg,
                                geojson_data_com, geojson_data_dep, geojson_data_reg):



    st.title("Page 1 : Présentation des données")
    st.write("Bienvenue sur la page de présentation des données.")

    selected_year = st.sidebar.slider(
    "Sélectionnez une année :",
    min_value=int(nb_voiture_reg["annee"].min()),
    max_value=int(nb_voiture_reg["annee"].max()),
    value=2024,  # Valeur par défaut
    step=1)

    # Sélection du niveau de granularité
    granularity = st.sidebar.selectbox(
        "Sélectionnez le niveau de granularité :",
        options=["département", "commune", "région"]
    )

    info_carte = st.sidebar.selectbox(
        "Sélectionnez quelle information afficher :",
        options=["nombre de véhicule", "ratio de véhicule électrique par rapport au total"]
    )
    if granularity == "commune":

        col_granu = "codgeo"
        geojson_data = geojson_data_com
        dataset = nb_voiture_commune
        dataset = dataset[dataset["annee"] == selected_year]
        dataset.drop(columns=["annee"], inplace=True)


    elif granularity == "région":

        col_granu = "code_region"
        geojson_data = geojson_data_reg
        dataset = nb_voiture_reg
        dataset = dataset[dataset["annee"] == selected_year]
        dataset.drop(columns=["annee"], inplace=True)

    else:
        col_granu = "code_dep"
        geojson_data = geojson_data_dep
        dataset = nb_voiture_dep
        dataset = dataset[dataset["annee"] == selected_year]
        dataset.drop(columns=["annee"], inplace=True)

    
    """nb_voiture_commune_dep["ratio_elec_total"] = nb_voiture_commune_dep["nb_vp_rechargeables_el"]	/ nb_voiture_commune_dep["nb_vp"]
    # Fait ca en pourcentage nb_voiture_commune_dep["ratio_elec_total"] avec 2 chiffres après la virgule
    nb_voiture_commune_dep["ratio_elec_total"] = nb_voiture_commune_dep["ratio_elec_total"] * 100
    nb_voiture_commune_dep["ratio_elec_total"] = nb_voiture_commune_dep["ratio_elec_total"].round(2)"""
    map = create_map(dataset, geojson_data, col_granu, info_carte)
    folium_static(map, width=800, height=600)
