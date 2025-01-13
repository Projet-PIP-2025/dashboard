import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import plotly.express as px


def show(voiture_commune, voiture_region, bornes, bornes_vehicules_dep, bornes_vehicules_reg):
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
    filtered_data_croisee_reg = bornes_vehicules_reg.copy()
    filtered_data_croisee_reg = pd.merge(filtered_data_croisee_reg, voiture_commune[[
                                         "code_region", "nom_region"]], left_on="Code Région", right_on="code_region")
    filtered_data_croisee_dep = bornes_vehicules_dep.copy()
    filtered_data_croisee_dep = pd.merge(filtered_data_croisee_dep, voiture_commune[[
                                         "code_dep", "nom_departement"]], left_on="Departement", right_on="code_dep")

    # Appliquer le filtre par année
    if selected_year != "Toutes les années":
        filtered_data = filtered_data[filtered_data['annee'] == selected_year]

    # Appliquer le filtre par région, département ou commune
    if granularite == "Région" and selected_option != "Toutes les régions":
        filtered_data = filtered_data[filtered_data['nom_region']
                                      == selected_option]
        filtered_data_croisee_reg = filtered_data_croisee_reg[
            filtered_data_croisee_reg["nom_region"] == selected_option]
    elif granularite == "Département" and selected_option != "Tous les départements":
        filtered_data = filtered_data[filtered_data['nom_departement']
                                      == selected_option]
        filtered_data_croisee_dep = filtered_data_croisee_dep[
            filtered_data_croisee_dep["nom_departement"] == selected_option]
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

        agg_bornes = agg_bornes.groupby(
            'Annee')['nb_borne_cumul'].sum().reset_index()

        # agg_bornes.columns = ['Annee', 'Nombre_de_bornes']

        # Tri par année
        # agg_bornes = agg_bornes.sort_values(by='Annee')

        # Graphique interactif avec Plotly
        fig2 = px.line(
            agg_bornes,
            x='Annee',
            y='nb_borne_cumul',
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
        agg_bornes = agg_bornes.groupby(
            'annee')['nb_borne_cumul'].sum().reset_index()

        # agg_bornes = agg_bornes['annee'].value_counts().reset_index()
        # agg_bornes.columns = ['annee', 'nb_bornes']
        # agg_bornes = agg_bornes.sort_values(by='annee')

        # Agrégation des véhicules électriques par année
        agg_vehicles = filtered_data.groupby(
            'annee')['nb_vp_rechargeables_el'].sum().reset_index()
        agg_vehicles.columns = ['annee', 'nb_vehicles']

        # Fusion des deux séries temporelles
        evolution_data = pd.merge(
            agg_bornes, agg_vehicles, on='annee', how='inner')

        # Calcul du ratio véhicules par borne
        evolution_data['ratio_vehicles_per_borne'] = evolution_data['nb_vehicles'] / \
            evolution_data['nb_borne_cumul']

        # Vérification si les données sont disponibles
        if evolution_data.empty:
            st.warning("Aucune donnée disponible pour l'analyse.")
        else:
            # Graphique interactif avec Plotly
            fig3 = px.line(
                evolution_data,
                x='annee',
                y=['nb_borne_cumul', 'nb_vehicles'],
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
                yaxis=dict(range=[0, 150]),
                # xaxis=dict(range=[2020, 2024, 1]),
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

            st.plotly_chart(fig3)
            st.plotly_chart(fig4)

            if selected_option == "Aucun":
                fig5 = px.scatter(
                    filtered_data_croisee_reg,
                    x='Nombre bornes',
                    hover_data=['Code Région', 'region'],
                    y='nb_vp_rechargeables_el',
                    size_max=32,
                    opacity=0.8,
                    title="Relation entre le nombre de bornes et de véhicules rechargeables par Région",
                    labels={
                        "Nombre bornes": "Nombre de Bornes",
                        "nb_vp_rechargeables_el": "Nombre de Véhicules Rechargeables",
                    },
                )

                fig5.update_layout(
                    xaxis_title="Nombre de Bornes",
                    yaxis_title="Nombre de Véhicules Rechargeables",
                    showlegend=False,
                )

                fig5.update_xaxes(showspikes=False)
                st.plotly_chart(fig5)

                fig6 = px.scatter(
                    filtered_data_croisee_dep,
                    x="nb_bornes",
                    y="nb_vp_rechargeables_el",
                    hover_data=["Departement", "Nom Departement"],
                    size=None,
                    opacity=0.8,
                    title="Relation entre le nombre de bornes et de véhicules rechargeables par Département",
                    labels={
                        "nb_bornes": "Nombre de Bornes",
                        "nb_vp_rechargeables_el": "Nombre de Véhicules Rechargeables",
                    },
                )

                fig6.update_layout(
                    xaxis_title="Nombre de Bornes",
                    yaxis_title="Nombre de Véhicules Rechargeables",
                    showlegend=False,
                )
                fig6.update_xaxes(showspikes=False)
                st.plotly_chart(fig6)

                fig8 = px.scatter(
                    filtered_data_croisee_reg,
                    x='region',
                    y='Ratio',
                    opacity=0.8,
                    size_max=32,
                    title="Ratio Véhicules par Bornes par Région",
                    labels={
                        "region": "Région",
                        "Ratio": "Ratio Véhicules par Bornes",
                    }
                )

                fig8.add_shape(
                    type='line',
                    x0=-0.5, x1=1, y0=10, y1=10,
                    line=dict(color='red', dash='dash', width=1.5),
                    xref='paper', yref='y',
                    name="y = 10",
                )

                fig8.update_layout(
                    xaxis_title="Régions",
                    yaxis_title="Ratio",
                    xaxis=dict(tickangle=90),
                    yaxis=dict(range=[0, 40]),
                    margin=dict(b=100),
                    showlegend=False
                )

                fig8.update_xaxes(showspikes=False)
                st.plotly_chart(fig8)

                fig7 = px.scatter(
                    filtered_data_croisee_dep,
                    x="Nom Departement",
                    y="Ratio vehicules par bornes",
                    title="Ratio Véhicules par Bornes par Département",
                    labels={
                        "Departement": "Département",
                        "Ratio vehicules par bornes": "Ratio Véhicules par Bornes",
                    },
                    opacity=0.8,
                )

                fig7.add_shape(
                    type="line",
                    x0=0, x1=1, y0=10, y1=10,
                    xref="paper",
                    yref="y",
                    line=dict(color="red", dash="dash", width=1.5),
                    name="y = 10",
                )

                fig7.update_layout(
                    xaxis=dict(tickangle=90),
                    yaxis=dict(range=[0, 75]),
                    margin=dict(b=100),
                    xaxis_title="Département",
                    yaxis_title="Ratio Véhicules par Bornes",
                )

                fig7.update_xaxes(showspikes=False)
                st.plotly_chart(fig7)
