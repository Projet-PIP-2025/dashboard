import streamlit as st
import folium # type: ignore
from streamlit_folium import folium_static # type: ignore
import json
import numpy as np
import plotly.express as px

def create_map(nb_voiture_commune_dep, geojson_data,col_granu):
    # Initialisation de la carte centrée sur la France
    map = folium.Map(location=[46.603354, 1.8883344], zoom_start=6, tiles='CartoDB positron')

    # Conversion des données en dictionnaire pour relier avec le GeoJSON
    vehicle_dict = nb_voiture_commune_dep.set_index(col_granu)['nb_vp_rechargeables_el'].to_dict()

    # Ajout des données au GeoJSON
    for feature in geojson_data['features']:
        feature_code = feature['properties']['code']
        feature['properties']['vehicles'] = vehicle_dict.get(feature_code, 'N/A')

    # Ajout d'un choropleth pour afficher les données
    folium.Choropleth(
        geo_data=geojson_data,
        name="Véhicules électriques par département",
        data=nb_voiture_commune_dep,
        columns=[col_granu, 'nb_vp_rechargeables_el'],
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

def show(nb_voiture_commune_dep,nb_voiture_commune_dep2, geojson_data_com, geojson_data_dep, geojson_data_reg):
    st.title("Page 1 : Présentation des données")
    st.write("Bienvenue sur la page de présentation des données.")
    nb_voiture_commune_dep = nb_voiture_commune_dep2

    selected_years = st.sidebar.multiselect(
        "Sélectionnez les années à inclure :",
        options=nb_voiture_commune_dep2["annee"].unique(),
        default=nb_voiture_commune_dep2["annee"].unique()
    )

    # Sélection du niveau de granularité
    granularity = st.sidebar.selectbox(
        "Sélectionnez le niveau de granularité :",
        options=["département", "commune", "région"]
    )


    if granularity == "commune":
        nb_voiture_commune_dep = nb_voiture_commune_dep2[["codgeo","libgeo","nb_vp_rechargeables_el","nb_vp","annee"]]
        nb_voiture_commune_dep = nb_voiture_commune_dep[nb_voiture_commune_dep["annee"].isin(selected_years)]
        nb_voiture_commune_dep.drop(columns=["annee"], inplace=True)
        nb_voiture_commune_dep = nb_voiture_commune_dep.groupby(['libgeo', 'codgeo']).agg({
        'nb_vp_rechargeables_el': 'sum',
        'nb_vp': 'sum'
        }).reset_index()
        col_granu = "codgeo"



        # Affichage de la carte
        map = create_map(nb_voiture_commune_dep, geojson_data_com, col_granu)
        folium_static(map, width=800, height=600)

    elif granularity == "région":
        nb_voiture_commune_dep = nb_voiture_commune_dep2[["code_region","nom_region",'reg_code_name',"nb_vp_rechargeables_el","nb_vp","annee"]]
        nb_voiture_commune_dep = nb_voiture_commune_dep[nb_voiture_commune_dep["annee"].isin(selected_years)]
        nb_voiture_commune_dep.drop(columns=["annee"], inplace=True)
        nb_voiture_commune_dep = nb_voiture_commune_dep.groupby(['nom_region', 'code_region']).agg({
        'nb_vp_rechargeables_el': 'sum',
        'nb_vp': 'sum'
        }).reset_index()
        col_granu = "code_region"

        # Affichage de la carte
        map = create_map(nb_voiture_commune_dep, geojson_data_reg, col_granu)
        folium_static(map, width=800, height=600)

    else:
        nb_voiture_commune_dep = nb_voiture_commune_dep[["code_dep","nom_departement",'dept_code_name',"nb_vp_rechargeables_el","nb_vp","annee"]]
        nb_voiture_commune_dep = nb_voiture_commune_dep[nb_voiture_commune_dep["annee"].isin(selected_years)]
        nb_voiture_commune_dep.drop(columns=["annee"], inplace=True)
        nb_voiture_commune_dep = nb_voiture_commune_dep.groupby(['nom_departement', 'code_dep']).agg({'nb_vp_rechargeables_el': 'sum','nb_vp': 'sum'
        }).reset_index()
        col_granu = "code_dep"

        # Affichage de la carte
        map = create_map(nb_voiture_commune_dep, geojson_data_dep, col_granu)
        folium_static(map, width=800, height=600)
    st.sidebar.markdown("---")   
    # Sélection du niveau de granularité
    granularity_histo = st.sidebar.selectbox(
        "Sélectionnez le niveau de granularité :",
        options=["region","total"]
    )
    # affiche une barre horizontale dans st.sidebar.
    
    # Affichage une barre horizontale
    st.markdown("---")
    if granularity_histo:
        if granularity_histo == "total":
            nb_voiture_commune_dep = nb_voiture_commune_dep2[['nb_vp_rechargeables_el', 'annee']]
            grouped_data = nb_voiture_commune_dep.groupby(['annee']).agg({'nb_vp_rechargeables_el': 'sum'}).reset_index()

            # Création de l'histogramme avec Plotly
            fig = px.bar(
                grouped_data,
                x='annee',
                y='nb_vp_rechargeables_el',
                labels={'annee': 'Année', 'nb_vp_rechargeables_el': 'Nombre de véhicules rechargeables'},
                title="Histogramme du nombre de véhicules rechargeables par année",
                color='annee'
            )
            
            # Affichage de l'histogramme
            st.plotly_chart(fig)
        elif granularity_histo == "region":
            granularity_histo = st.sidebar.multiselect(
        "Sélectionnez une région :",
        options=nb_voiture_commune_dep2["nom_region"].unique())
            nb_voiture_commune_dep = nb_voiture_commune_dep2[['nb_vp_rechargeables_el',"nom_region",'annee']]
            nb_voiture_commune_dep = nb_voiture_commune_dep[nb_voiture_commune_dep["nom_region"].isin(granularity_histo)]
            grouped_data = nb_voiture_commune_dep.groupby(['annee',"nom_region"]).agg({'nb_vp_rechargeables_el': 'sum'}).reset_index()

            # Création de l'histogramme avec Plotly
            fig = px.bar(
                grouped_data,
                x='annee',
                y='nb_vp_rechargeables_el',
                labels={'annee': 'Année', 'nb_vp_rechargeables_el': 'Nombre de véhicules rechargeables'},
                title="Histogramme du nombre de véhicules rechargeables par année",
                color='nom_region'
            )
    # Ajoute ici le contenu spécifique à cette page
