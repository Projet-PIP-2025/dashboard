
import pandas as pd
import folium # type: ignore
import streamlit as st
from streamlit_folium import folium_static # type: ignore
import json
import streamlit as st
import numpy as np
import plotly.express as px



st.set_page_config(
    page_title="Dashboard GRP 8 : Voiture electrique", page_icon="🚘", initial_sidebar_state="expanded", layout="wide"
)


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
    return nb_voiture_commune_dep,nb_voiture_commune_dep2, geojson_data_com, geojson_data_dep, geojson_data_reg

# Création de la carte
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

# Affichage principal
def main():
    st.title("🚘 Carte des Véhicules Électriques par Département")
    st.markdown("Cette application affiche les données sur les véhicules électriques par département en France.")
    # Affichage des données en table
    st.sidebar.header("Données Brutes")
    # Chargement des données
    nb_voiture_commune_dep,nb_voiture_commune_dep2, geojson_data_com, geojson_data_dep, geojson_data_reg = load_data()
    nb_voiture_commune_dep = nb_voiture_commune_dep2

    selected_years = st.sidebar.multiselect(
        "Sélectionnez les années à inclure :",
        options=nb_voiture_commune_dep2["annee"].unique(),
        default=nb_voiture_commune_dep2["annee"].unique()
    )

    # Sélection du niveau de granularité
    granularity = st.sidebar.selectbox(
        "Sélectionnez le niveau de granularité :",
        options=["commune", "département", "région"]
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
        
# Lancer l'application
if __name__ == "__main__":
    main()

