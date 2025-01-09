import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import plotly.express as px


def show(voiture_commune_dep, voiture_region, borne_region, borne_commune_dep):
    """
    Affiche les statistiques descriptives avec filtres intégrés.

    Args:
        voiture_commune_dep (pd.DataFrame): Données des véhicules électriques par commune et département.
        voiture_region (pd.DataFrame): Données des véhicules électriques par région.
        borne_region (pd.DataFrame): Données des bornes de recharge par région.
        borne_commune_dep (pd.DataFrame): Données des bornes de recharge par commune et département.
    """
    st.title("Statistiques descriptives")
    st.write("Bienvenue sur la page des statistiques descriptives.")

    # ---- Filtres dans la barre latérale ----
    st.sidebar.header("Filtres")

    # Filtre par année
    years = ["Toutes les années"] + \
        sorted(voiture_commune_dep['annee'].unique())
    selected_year = st.sidebar.selectbox("Choisissez une année", options=years)

    # Niveau de granularité
    granularite = st.sidebar.selectbox(
        "Choisissez le niveau de granularité",
        options=["Aucun", "Région", "Département", "Commune"]
    )

    # Options dynamiques en fonction du niveau choisi
    if granularite == "Région":
        options = ["Toutes les régions"] + \
            sorted(voiture_commune_dep['nom_region'].unique())
        selected_option = st.sidebar.selectbox(
            "Sélectionnez une région", options=options)
    elif granularite == "Département":
        options = ["Tous les départements"] + \
            sorted(voiture_commune_dep['nom_departement'].unique())
        selected_option = st.sidebar.selectbox(
            "Sélectionnez un département", options=options)
    elif granularite == "Commune":
        options = ["Toutes les communes"] + \
            sorted(voiture_commune_dep['libgeo'].unique())
        selected_option = st.sidebar.selectbox(
            "Sélectionnez une commune", options=options)
    else:
        selected_option = "Aucun"

    # ---- Filtrage des données ----
    filtered_data = voiture_commune_dep.copy()

    # Appliquer le filtre par année
    if selected_year != "Toutes les années":
        filtered_data = filtered_data[filtered_data['annee'] == selected_year]

    # Appliquer le filtre par région, département ou commune
    if granularite == "Région" and selected_option != "Toutes les régions":
        filtered_data = filtered_data[filtered_data['nom_region']
                                      == selected_option]
    elif granularite == "Département" and selected_option != "Tous les départements":
        filtered_data = filtered_data[filtered_data['nom_departement']
                                      == selected_option]
    elif granularite == "Commune" and selected_option != "Toutes les communes":
        filtered_data = filtered_data[filtered_data['libgeo']
                                      == selected_option]

    # Déterminer le suffixe du titre dynamique
    title_suffix = ""
    if selected_option not in ["Aucun", "Toutes les régions", "Tous les départements", "Toutes les communes"]:
        title_suffix = f" - {selected_option}"
    if selected_year != "Toutes les années":
        title_suffix += f" (Année : {selected_year})"

    # ---- Onglets pour navigation ----
    tab1, tab2, tab3 = st.tabs([
        "Véhicules électriques",
        "Bornes de recharge",
        "Analyses croisées"
    ])

    # ---- Analyse : Nombre de véhicules électriques ----
    with tab1:
        st.subheader(f"Analyse du nombre de véhicules électriques{
                     title_suffix}")
        agg_vehicules = filtered_data.groupby(
            'annee')['nb_vp_rechargeables_el'].sum().reset_index()

        # Graphique interactif avec Plotly
        fig1 = px.bar(
            agg_vehicules,
            x='annee',
            y='nb_vp_rechargeables_el',
            title=f"Évolution du nombre de véhicules électriques{
                title_suffix}",
            labels={'annee': 'Année',
                    'nb_vp_rechargeables_el': 'Nombre de véhicules électriques'},
            text='nb_vp_rechargeables_el'
        )
        fig1.update_traces(textposition='outside')
        st.plotly_chart(fig1)

    # ---- Analyse : Nombre de bornes de recharge ----
    with tab2:
        st.subheader(f"Analyse du nombre de bornes de recharge{title_suffix}")
        agg_bornes = borne_commune_dep.copy()

        # Filtrer les bornes de recharge par année
        if selected_year != "Toutes les années":
            agg_bornes = agg_bornes[agg_bornes['annee'] == selected_year]

        agg_bornes = agg_bornes.groupby(
            'annee')['nb_bornes_recharge'].sum().reset_index()

        # Graphique interactif avec Plotly
        fig2 = px.line(
            agg_bornes,
            x='annee',
            y='nb_bornes_recharge',
            title=f"Évolution du nombre de bornes de recharge{title_suffix}",
            labels={'annee': 'Année',
                    'nb_bornes_recharge': 'Nombre de bornes de recharge'},
            markers=True
        )
        st.plotly_chart(fig2)

    # ---- Analyses croisées ----
    with tab3:
        st.subheader(f"Analyses croisées{title_suffix}")
        st.write(
            "Relation entre le nombre de véhicules électriques et les bornes de recharge")

        # Fusion des données pour analyse croisée
        agg_croisee = pd.merge(
            filtered_data,
            borne_commune_dep,
            on=['annee', 'nom_region', 'nom_departement', 'libgeo'],
            how='inner'
        )

        # Filtrer les données croisées par année
        if selected_year != "Toutes les années":
            agg_croisee = agg_croisee[agg_croisee['annee'] == selected_year]

        # Graphique interactif avec Plotly
        fig3 = px.scatter(
            agg_croisee,
            x='nb_vp_rechargeables_el',
            y='nb_bornes_recharge',
            title=f"Véhicules électriques vs Bornes de recharge{title_suffix}",
            labels={
                'nb_vp_rechargeables_el': 'Nombre de véhicules électriques',
                'nb_bornes_recharge': 'Nombre de bornes de recharge'
            }
        )
        st.plotly_chart(fig3)
