import streamlit as st
import folium
from streamlit_folium import folium_static
import plotly.express as px
from folium.plugins import HeatMap
from streamlit_folium import folium_static


def create_map(nb_voiture_commune_dep, geojson_data,col_granu, info_carte):
    # Initialisation de la carte centrée sur la France
    map = folium.Map(location=[46.603354, 1.8883344], zoom_start=6, tiles='CartoDB positron')

    if info_carte == "nombre de véhicule":
        # Conversion des données en dictionnaire pour relier avec le GeoJSON
        col = 'nb_vp_rechargeables_el'
    elif info_carte == "ratio de véhicule électrique par rapport au total":
        # Conversion des données en dictionnaire pour relier avec le GeoJSON
        col = 'ratio_elec_total'

    vehicle_dict = nb_voiture_commune_dep.set_index(col_granu)[col].to_dict()
    # Mets les keys au format list str
    vehicle_dict = {str(k): v for k, v in vehicle_dict.items()}
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

def create_map_borne(nb_voiture_commune_dep, geojson_data,col_granu):
    # Initialisation de la carte centrée sur la France
    print(nb_voiture_commune_dep.columns)
    map = folium.Map(location=[46.603354, 1.8883344], zoom_start=6, tiles='CartoDB positron')


    col = 'nb_borne_cumul'



    vehicle_dict = nb_voiture_commune_dep.set_index(col_granu)[col].to_dict()
    # Mets les keys au format list str
    vehicle_dict = {str(k): v for k, v in vehicle_dict.items()}
    # comment faire un tolist sur un dict.keys() ?
    print(list(vehicle_dict.keys()))
    print([feature['properties']['code'] for feature in geojson_data['features']])
    # Ajout des données au GeoJSON
    for feature in geojson_data['features']:
        feature_code = feature['properties']['code']
        feature['properties']['vehicles'] = vehicle_dict.get(feature_code, 'N/A')

    # Ajout d'un choropleth pour afficher les données
    folium.Choropleth(
        geo_data=geojson_data,
        name="Bornes par territoires",
        data=nb_voiture_commune_dep,
        columns=[col_granu, col],
        key_on='feature.properties.code',
        fill_color='YlGnBu',
        fill_opacity=0.7,
        line_opacity=0.05,
        legend_name="Nombre de bornes"
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

def create_map_population(dataset, geojson_data, col_granu, col_year, info_carte="Population"):
    """
    Crée une carte interactive pour visualiser les données démographiques.

    Args:
        dataset (pd.DataFrame): Données filtrées pour l'année et la granularité choisies.
        geojson_data (dict): Données GeoJSON correspondantes à la granularité.
        col_granu (str): Colonne utilisée pour relier les données géographiques et populationnelles.
        col_year (str): Colonne représentant l'année sélectionnée dans les données.
        info_carte (str): Légende de la carte.

    Returns:
        folium.Map: Carte interactive.
    """
    # Initialisation de la carte centrée sur la France
    map = folium.Map(location=[46.603354, 1.8883344], zoom_start=6, tiles='CartoDB positron')

    # Convertir les données en dictionnaire
    population_dict = dataset.set_index(col_granu)[col_year].to_dict()

    # Mettre les clés au format chaîne de caractères (nécessaire pour GeoJSON)
    population_dict = {str(k): v for k, v in population_dict.items()}

    # Ajout des données de population aux propriétés GeoJSON
    for feature in geojson_data['features']:
        feature_code = str(feature['properties']['code'])
        feature['properties']['population'] = population_dict.get(feature_code, 'N/A')

    # Ajouter un choropleth pour afficher les données de population
    folium.Choropleth(
        geo_data=geojson_data,
        name=f"{info_carte} par territoires",
        data=dataset,
        columns=[col_granu, col_year],
        key_on='feature.properties.code',
        fill_color='YlGnBu',
        fill_opacity=0.7,
        line_opacity=0.05,
        legend_name=info_carte
    ).add_to(map)

    # Ajouter des info-bulles interactives pour afficher des informations détaillées
    folium.GeoJson(
        geojson_data,
        name="Détails",
        tooltip=folium.GeoJsonTooltip(
            fields=['code', 'nom', 'population'],
            aliases=['Code :', 'Nom :', f'{info_carte} :']
        )
    ).add_to(map)

    # Ajout des contrôles de couches
    folium.LayerControl().add_to(map)

    return map

def show(carte_html2, trafic_reg,trafic_dep, population, bornes, nb_voiture_commune, nb_voiture_dep, nb_voiture_reg,
                                geojson_data_com, geojson_data_dep, geojson_data_reg, carte_tmja_reg, carte_tmja_dep):
    st.title("Page 1 : Présentation des données")
    st.write("Bienvenue sur la page de présentation des données.")
    tab1, tab2, tab3, tab4 = st.tabs([
        "Véhicules électriques",
        "Bornes de recharge",
        "Population",
        "Trafic"
    ])
    with tab1:
        with st.container():
            # Utiliser des colonnes pour aligner les filtres
            col1, col2, col3 = st.columns([1, 1, 2])  # Largeurs ajustables

            # Filtre de l'année
            with col1:
                selected_year = st.slider(
                    "Sélectionnez une année :",
                    min_value=int(nb_voiture_reg["annee"].min()),
                    max_value=int(nb_voiture_reg["annee"].max()),
                    value=2023,  # Valeur par défaut
                    step=1,
                    key="slider_year_vehicule"
                )

            # Filtre de granularité
            with col2:
                granularity = st.selectbox(
                    "Niveau de granularité :",
                    options=["département", "commune", "région"],
                    key="slider_granularity_vehicule"
                )

            # Filtre d'information
            with col3:
                info_carte = st.selectbox(
                    "Information à afficher :",
                    options=["nombre de véhicule", "ratio de véhicule électrique par rapport au total"],
                    key="slider_info_carte_vehicule"
                )
        if granularity == "commune":
            col_granu = "codgeo"
            geojson_data = geojson_data_com
            dataset = nb_voiture_commune
            dataset = dataset[dataset["annee"] == selected_year]
            dataset.drop(columns=["annee"], inplace=True)
            dataset["ratio_elec_total"] = dataset["nb_vp_rechargeables_el"]	/ dataset["nb_vp"]
            # Fait ca en pourcentage nb_voiture_commune_dep["ratio_elec_total"] avec 2 chiffres après la virgule
            dataset["ratio_elec_total"] = dataset["ratio_elec_total"] * 100
            dataset["ratio_elec_total"] = dataset["ratio_elec_total"].round(2)


        elif granularity == "région":
            col_granu = "code_region"
            geojson_data = geojson_data_reg
            dataset = nb_voiture_reg
            dataset = dataset[dataset["annee"] == selected_year]
            dataset.drop(columns=["annee"], inplace=True)
            dataset["ratio_elec_total"] = dataset["nb_vp_rechargeables_el"]	/ dataset["nb_vp"]
            # Fait ca en pourcentage nb_voiture_commune_dep["ratio_elec_total"] avec 2 chiffres après la virgule
            dataset["ratio_elec_total"] = dataset["ratio_elec_total"] * 100
            dataset["ratio_elec_total"] = dataset["ratio_elec_total"].round(2)


        else:
            col_granu = "code_dep"
            geojson_data = geojson_data_dep
            dataset = nb_voiture_dep
            dataset = dataset[dataset["annee"] == selected_year]
            dataset.drop(columns=["annee"], inplace=True)
            dataset["ratio_elec_total"] = dataset["nb_vp_rechargeables_el"]	/ dataset["nb_vp"]
            # Fait ca en pourcentage nb_voiture_commune_dep["ratio_elec_total"] avec 2 chiffres après la virgule
            dataset["ratio_elec_total"] = dataset["ratio_elec_total"] * 100
            dataset["ratio_elec_total"] = dataset["ratio_elec_total"].round(2)
        map = create_map(dataset, geojson_data, col_granu, info_carte)
        folium_static(map, width=800, height=600)

    with tab2:
        bornes_com = bornes[["commune","code_insee","Annee","nb_borne_cumul"]]
        bornes_dep = bornes[["Departement_selon_insee","Annee","nom_departement","nb_borne_cumul"]]
        bornes_reg = bornes[["Annee","code_region","nom_region","nb_borne_cumul"]]
        bornes_dep = bornes_dep.groupby(["Departement_selon_insee","nom_departement","Annee"]).agg({'nb_borne_cumul': 'sum'}).reset_index()
        bornes_reg = bornes_reg.groupby(["code_region","nom_region","Annee"]).agg({'nb_borne_cumul': 'sum'}).reset_index()
        with st.container():
            # Utiliser des colonnes pour aligner les filtres
            col_borne1, col_borne2 = st.columns([1, 1])

            # Filtre de l'année
            with col_borne1:
                selected_year2 = st.slider(
                    "Sélectionnez une année :",
                    min_value=int(bornes["Annee"].min()),
                    max_value=int(bornes["Annee"].max()),
                    value=2024,  # Valeur par défaut
                    step=1,
                    key="slider_year_borne"
                )

            # Filtre de granularité
            with col_borne2:
                granularity2 = st.selectbox(
                    "Niveau de granularité :",
                    options=["département", "commune", "région"],
                    key="slider_granularity_borne"
                )

            if granularity2 == "commune":
                col_granu = "code_insee"
                geojson_data = geojson_data_com
                dataset = bornes_com
            elif granularity2 == "région":
                col_granu = "code_region"
                geojson_data = geojson_data_reg
                dataset = bornes_reg
            else:
                col_granu = "Departement_selon_insee"
                geojson_data = geojson_data_dep
                dataset = bornes_dep

            # Filtrer par année
            dataset = dataset[dataset["Annee"] == selected_year2]
            dataset.drop(columns=["Annee"], inplace=True)

            # Créer la carte avec les bornes
            map = create_map_borne(dataset, geojson_data, col_granu)
            folium_static(map, width=800, height=600)

    with tab3:
        col_annee = ["p13_pop","p14_pop","p15_pop","p16_pop",
                     "p17_pop","p18_pop","p19_pop","p20_pop","p21_pop","p22_pop"]
        dictionnaire = {2013: "p13_pop", 2014: "p14_pop", 2015: "p15_pop", 2016: "p16_pop",
                        2017: "p17_pop", 2018: "p18_pop", 2019: "p19_pop", 2020: "p20_pop",
                        2021: "p21_pop", 2022: "p22_pop"}
        population_com = population[['codgeo_insee', 'libgeo'] + col_annee]
        population_dep = population[['dep', 'nom_departement'] + col_annee]
        population_reg = population[['reg', 'nom_region'] + col_annee]
        population_dep = population.groupby(['dep', 'nom_departement'])[col_annee].sum().reset_index()
        population_reg = population.groupby(['reg', 'nom_region'])[col_annee].sum().reset_index()
        with st.container():
            # Utiliser des colonnes pour aligner les filtres
            col_pop1, col_pop2 = st.columns([1, 1])

            # Filtre de l'année
            with col_pop1:
                selected_year3 = st.slider(
                    "Sélectionnez une année :",
                    min_value=2013,
                    max_value=2022,
                    value=2022,  # Valeur par défaut
                    step=1,
                    key="slider_year_pop"
                )
            selected_year3 = dictionnaire[selected_year3]
            # Filtre de granularité
            with col_pop2:
                granularity3 = st.selectbox(
                    "Niveau de granularité :",
                    options=["département", "commune", "région"],
                    key="slider_granularity_pop"
                )

            if granularity3 == "commune":
                col_granu = "codgeo_insee"
                geojson_data = geojson_data_com
                dataset = population_com
            elif granularity3 == "reg":
                col_granu = "code_region"
                geojson_data = geojson_data_reg
                dataset = population_reg
            else:
                col_granu = "dep"
                geojson_data = geojson_data_dep
                dataset = population_dep

            # Créer la carte avec les bornes
            map = create_map_population(dataset, geojson_data, col_granu, selected_year3, info_carte="Population")
            folium_static(map, width=800, height=600)

    with tab4:

        # Utiliser des colonnes pour aligner les filtres
        granularity4 = st.selectbox(
            "Niveau de granularité :",
            options=["trafic", "région", "département"],
            key="slider_granularity_traf"
        )

        if granularity4 == "région":
            st.subheader("TMJA  moyen selon la région")
            st.components.v1.html(carte_tmja_reg, height=500, width=800)
        elif granularity4 == "trafic":
            st.subheader("Carte trafic journalier par axe routier")
            st.components.v1.html(carte_html2, height=500, width=800)
        elif granularity4 == "département":
            st.subheader("TMJA moyen selon la région")
            st.components.v1.html(carte_tmja_dep, height=500, width=800)
