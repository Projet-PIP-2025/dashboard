import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import plotly.express as px


def show(voiture_commune, voiture_region, bornes):
    """
    Affiche les statistiques descriptives avec filtres intégrés.

    Args:
        voiture_commune (pd.DataFrame): Données des véhicules électriques par commune et département.
        voiture_region (pd.DataFrame): Données des véhicules électriques par région.
        bornes (pd.DataFrame): Données des bornes de recharge par commune et département.
    """
    st.title("Statistiques descriptives")
    st.write("Bienvenue sur la page des statistiques descriptives.")

    # ---- Filtres dans la barre latérale ----
    st.sidebar.header("Filtres")

    # Filtre par année
    years = ["Toutes les années"] + \
        sorted(voiture_commune['annee'].unique())
    selected_year = st.sidebar.selectbox("Choisissez une année", options=years)

    # Niveau de granularité
    granularite = st.sidebar.selectbox(
        "Choisissez le niveau de granularité",
        options=["Aucun", "Région", "Département", "Commune"]
    )

    # Options dynamiques en fonction du niveau choisi
    if granularite == "Région":
        options = ["Toutes les régions"] + \
            sorted(voiture_commune['nom_region'].unique())
        selected_option = st.sidebar.selectbox(
            "Sélectionnez une région", options=options)
    elif granularite == "Département":
        options = ["Tous les départements"] + \
            sorted(voiture_commune['nom_departement'].unique())
        selected_option = st.sidebar.selectbox(
            "Sélectionnez un département", options=options)
    elif granularite == "Commune":
        options = ["Toutes les communes"] + \
            sorted(voiture_commune['libgeo'].unique())
        selected_option = st.sidebar.selectbox(
            "Sélectionnez une commune", options=options)
    else:
        selected_option = "Aucun"

    # ---- Filtrage des données ----
    filtered_data = voiture_commune.copy()

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
        agg_bornes = bornes.copy()

        # Filtrer les bornes de recharge par année
        if selected_year != "Toutes les années":
            agg_bornes = agg_bornes[agg_bornes['Annee'] == selected_year]

        agg_bornes = agg_bornes['Annee'].value_counts()

        agg_bornes = agg_bornes.reset_index()
        agg_bornes.columns = ['Annee', 'Nombre_de_bornes']

        # Tri par année
        agg_bornes = agg_bornes.sort_values(by='Annee')

        # Graphique interactif avec Plotly
        fig2 = px.line(
            agg_bornes,
            x='Annee',
            y='Nombre_de_bornes',
            title=f"Évolution du nombre de bornes de recharge{title_suffix}",
            labels={'Annee': 'Année',
                    'Nombre_de_bornes': 'Nombre de bornes de recharge'},
            markers=True
        )
        st.plotly_chart(fig2)

    # ---- Analyses croisées ----
    with tab3:
        st.subheader(f"Analyses croisées{title_suffix}")
        st.write(
            "Évolution comparée du nombre de véhicules électriques et des bornes de recharge par année"
        )

        # Préparation des données agrégées pour les bornes
        bornes["annee"] = bornes["Annee"]
        bornes["libgeo"] = bornes["commune"]

        agg_bornes = bornes.copy()
        agg_bornes = agg_bornes['annee'].value_counts().reset_index()
        agg_bornes.columns = ['annee', 'nb_bornes']
        agg_bornes = agg_bornes.sort_values(by='annee')

        # Agrégation des véhicules électriques par année
        agg_vehicles = filtered_data.groupby(
            'annee')['nb_vp_rechargeables_el'].sum().reset_index()
        agg_vehicles.columns = ['annee', 'nb_vehicles']

        # Fusion des deux séries temporelles
        evolution_data = pd.merge(
            agg_bornes, agg_vehicles, on='annee', how='inner')

        # Calcul du ratio véhicules par borne
        evolution_data['ratio_vehicles_per_borne'] = evolution_data['nb_vehicles'] / \
            evolution_data['nb_bornes']

        # Vérification si les données sont disponibles
        if evolution_data.empty:
            st.warning("Aucune donnée disponible pour l'analyse.")
        else:
            # Graphique interactif avec Plotly
            fig3 = px.line(
                evolution_data,
                x='annee',
                y=['nb_bornes', 'nb_vehicles'],
                title=f"Évolution du nombre de bornes et de véhicules électriques par année{
                    title_suffix}",
                labels={
                    'annee': 'Année',
                    'value': 'Nombre',
                    'variable': 'Catégorie'
                },
                markers=True
            )

            # Mise à jour des traces pour les différencier
            fig3.update_traces(mode="lines+markers")
            fig3.update_layout(
                legend_title="Catégorie",
                xaxis_title="Année",
                yaxis_title="Nombre",
                hovermode="x unified"
            )

            # Graphique 2 : Ratio véhicules par borne
            fig4 = px.line(
                evolution_data,
                x='annee',
                y='ratio_vehicles_per_borne',
                title=f"Ratio du nombre de véhicules par borne par année{
                    title_suffix}",
                labels={
                    'annee': 'Année',
                    'ratio_vehicles_per_borne': 'Ratio véhicules/bornes'
                },
                markers=True
            )
            fig4.update_traces(mode="lines+markers")
            fig4.update_layout(
                xaxis_title="Année",
                yaxis_title="Ratio véhicules/bornes",
                hovermode="x unified",
                shapes=[
                    # Ligne horizontale à y=10 pour la référence
                    dict(
                        type="line",
                        x0=evolution_data['annee'].min(),
                        x1=evolution_data['annee'].max(),
                        y0=10,
                        y1=10,
                        line=dict(color="red", width=2, dash="dash"),
                    )
                ]
            )

            # Affichage des graphiques
            st.plotly_chart(fig3)
            st.plotly_chart(fig4)
