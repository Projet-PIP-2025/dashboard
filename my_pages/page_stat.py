import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import branca.colormap as cm
import folium


def show(nb_voitures, bornes, carte_vehicules_bornes_reg, carte_vehicules_bornes_dep, carte_tmja_reg, carte_tmja_dep, carte_bornes_tmja_reg, carte_bornes_tmja_dep):
    """
    Affiche les statistiques descriptives avec filtres intégrés.

    Args:
        voiture_commune (pd.DataFrame): Données des véhicules électriques par commune et département.
        voiture_region (pd.DataFrame): Données des véhicules électriques par région.
        bornes (pd.DataFrame): Données des bornes de recharge par commune et département.
    """

    years = ["Toutes les années"] + \
        sorted(nb_voitures['annee'].unique())

    st.title("Statistiques descriptives")
    st.write("Bienvenue sur la page des statistiques descriptives.")


    # ---- Onglets pour navigation ----
    tab1, tab2, tab3 = st.tabs([
        "Véhicules électriques",
        "Bornes de recharge",
        "Analyses croisées"
    ])

    # ---- Analyse : Nombre de véhicules électriques ----
    with tab1:
        with st.container():
            # Utiliser des colonnes pour aligner les filtres
            col1, col2, col3 = st.columns([1, 1, 2])  # Largeurs ajustables

            with col1:
                selected_year = st.selectbox(
                    "Choisissez une année",
                    options=years,
                    key="slider_year_tab1"
                )
            with col2:
                granularite = st.selectbox(
                    "Choisissez le niveau de granularité",
                    options=["Aucun", "Région", "Département", "Commune"],
                    key="slider_granularity_tab1"
                )
            with col3:
                if granularite == "Région":
                    options = ["Toutes les régions"] + \
                        sorted(nb_voitures['nom_region'].unique())
                    selected_option = st.selectbox(
                        "Sélectionnez une région", options=options, key="slider_option1_tab1")
                elif granularite == "Département":
                    options = ["Tous les départements"] + \
                        sorted(nb_voitures['nom_departement'].unique())
                    selected_option = st.selectbox(
                        "Sélectionnez un département", options=options, key="slider_option2_tab1")
                elif granularite == "Commune":
                    options = ["Toutes les communes"] + \
                        sorted(nb_voitures['libgeo'].unique())
                    selected_option = st.selectbox(
                        "Sélectionnez une commune", options=options, key="slider_option3_tab1")
                else:
                    selected_option = "Aucun"

        # ---- Filtrage des données ----
        filtered_data = nb_voitures.copy()

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



        st.subheader(f"Analyse du nombre de véhicules électriques{title_suffix}")
        agg_vehicules = filtered_data.groupby(
            'annee')['nb_vp_rechargeables_el'].sum().reset_index()

        # Graphique interactif avec Plotly
        fig1 = px.bar(
            agg_vehicules,
            x='annee',
            y='nb_vp_rechargeables_el',
            title=f"Évolution du nombre de véhicules électriques{title_suffix}",
            labels={'annee': 'Année',
                    'nb_vp_rechargeables_el': 'Nombre de véhicules électriques'},
            text='nb_vp_rechargeables_el'
        )
        fig1.update_traces(textposition='outside')
        st.plotly_chart(fig1)

        # ---- Top 10 par granularité ----
        st.subheader(
            "Top 10 nombre de véhicules électriques")

        top_data = filtered_data.copy()
        top_data["Nom"] = top_data["libgeo"]

        # Agrégation des données pour le Top 10
        if granularite == "Région":
            top_data = filtered_data.groupby('nom_region', as_index=False)[
                'nb_vp_rechargeables_el'].sum()
            top_data["Nom"] = top_data["nom_region"]
            # top_data = top_data.rename(
            #     columns={'nom_region': 'Nom', 'nb_vp_rechargeables_el': 'Nombre de véhicules'})
        elif granularite == "Département":
            top_data = filtered_data.groupby('nom_departement', as_index=False)[
                'nb_vp_rechargeables_el'].sum()
            top_data["Nom"] = top_data["nom_departement"]
            # top_data = top_data.rename(
            #     columns={'nom_departement': 'Nom', 'nb_vp_rechargeables_el': 'Nombre de véhicules'})
        elif granularite == "Commune":
            top_data = filtered_data.groupby('libgeo', as_index=False)[
                'nb_vp_rechargeables_el'].sum()
            top_data["Nom"] = top_data["libgeo"]
            # top_data = top_data.rename(
            #     columns={'libgeo': 'Nom', 'nb_vp_rechargeables_el': 'Nombre de véhicules'})

        # Tri et sélection des 10 premiers
        top_data2 = top_data.sort_values(
            by='nb_vp_rechargeables_el', ascending=False).head(10)

        # Graphique interactif : Top 10
        fig_top = px.bar(
            top_data2,
            x='nb_vp_rechargeables_el',
            y='Nom',
            orientation='h',
            title=f"Top 10 {'ville' if granularite == 'Aucun' else granularite.lower()}s avec le plus grand nombre de véhicules électriques",
            labels={'Nom': f'{"ville" if granularite == "Aucun" else granularite.lower()}',
                    'nb_vp_rechargeables_el': 'Nombre de véhicules électriques'},
            # text='Nombre de véhicules'
        )

        # Affichage du graphique
        st.plotly_chart(fig_top)

        st.subheader(
            f"Analyse du ratio véhicules électriques / total{title_suffix}")

        # Calculer le ratio pour chaque entrée
        filtered_data['ratio_ve'] = filtered_data['nb_vp_rechargeables_el'] / \
            filtered_data['nb_vp']

        # Agréger les données par année
        agg_ratio = filtered_data.groupby(
            'annee')['ratio_ve'].mean().reset_index()

        # Graphique interactif avec Plotly
        fig_ratio = px.line(
            agg_ratio,
            x='annee',
            y='ratio_ve',
            title=f"Évolution du ratio véhicules électriques / total{title_suffix}",
            labels={
                'annee': 'Année',
                'ratio_ve': 'Ratio véhicules électriques / total'
            },
            markers=True
        )
        fig_ratio.update_yaxes(tickformat=".2%")  # Affichage en pourcentage
        fig_ratio.update_xaxes(
            tickformat="%Y",
            tickmode="linear",
            dtick="M12")
        st.plotly_chart(fig_ratio)

    # ---- Analyse : Nombre de bornes de recharge ----
    with tab2:
        st.subheader(f"Analyse du nombre de bornes de recharge{title_suffix}")
        agg_bornes = bornes.copy()

        with st.container():
            # Utiliser des colonnes pour aligner les filtres
            col1, col2, col3 = st.columns([1, 1, 2])  # Largeurs ajustables

            with col1:
                selected_year = st.selectbox(
                    "Choisissez une année",
                    options=years,
                    key="slider_year_tab2"
                )
            with col2:
                granularite = st.selectbox(
                    "Choisissez le niveau de granularité",
                    options=["Aucun", "Région", "Département", "Commune"],
                    key="slider_granularity_tab2"
                )
            with col3:
                if granularite == "Région":
                    options = ["Toutes les régions"] + \
                        sorted(nb_voitures['nom_region'].unique())
                    selected_option = st.selectbox(
                        "Sélectionnez une région", options=options, key="slider_option1_tab2")
                elif granularite == "Département":
                    options = ["Tous les départements"] + \
                        sorted(nb_voitures['nom_departement'].unique())
                    selected_option = st.selectbox(
                        "Sélectionnez un département", options=options, key="slider_option2_tab2")
                elif granularite == "Commune":
                    options = ["Toutes les communes"] + \
                        sorted(nb_voitures['libgeo'].unique())
                    selected_option = st.selectbox(
                        "Sélectionnez une commune", options=options, key="slider_option3_tab2")
                else:
                    selected_option = "Aucun"

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
                    'nb_borne_cumul': 'Nombre de bornes de recharge'},
            markers=True
        )
        st.plotly_chart(fig2)

        # ---- Top 10 par granularité ----
        st.subheader("Top 10 par granularité")

        # Agrégation des données pour le Top 10 selon la granularité choisie
        top_bornes_data = bornes.copy()
        top_bornes_data = top_bornes_data.groupby('commune', as_index=False)['nb_borne'].sum()
        top_bornes_data["Nom"] = top_bornes_data["commune"]

        if granularite == "Commune":
            top_bornes_data = top_bornes_data.groupby('commune', as_index=False)[
                'nb_borne'].sum()
            top_bornes_data["Nom"] = top_bornes_data["commune"]
        elif granularite == "Région":
            top_bornes_data = top_bornes_data.groupby('nom_region', as_index=False)[
                'nb_borne'].sum()
            top_bornes_data["Nom"] = top_bornes_data["nom_region"]
        elif granularite == "Département":
            top_bornes_data = top_bornes_data.groupby('nom_departement', as_index=False)[
                'nb_borne'].sum()
            top_bornes_data["Nom"] = top_bornes_data["nom_departement"]

        # Tri et sélection du Top 10
        top_bornes_data2 = top_bornes_data.sort_values(
            by='nb_borne', ascending=False).head(10)

        # print(top_bornes_data2)

        # Graphique interactif du Top 10
        fig_top_bornes = px.bar(
            top_bornes_data2,
            x='nb_borne',
            y='Nom',
            title=f"Top 10 des {'ville' if granularite == 'Aucun' else granularite.lower()}s avec le plus de bornes de recharge",
            labels={'Nom': f'{"ville" if granularite == "Aucun" else granularite.lower()}',
                    'nb_borne': 'Nombre de bornes de recharge'},
        )
        fig_top_bornes.update_traces(textposition='outside')
        fig_top_bornes.update_layout(xaxis_tickangle=-45)

        # Affichage du graphique
        st.plotly_chart(fig_top_bornes)

    # ---- Analyses croisées ----
    with tab3:

        # ---- Onglets pour navigation ----
        subtab3_1, subtab3_2 = st.tabs([
            "Véhicules électriques   vs.   Bornes de recharge",
            "Trafic   vs.   Bornes de recharge"
        ])

        with subtab3_1:
            st.subheader(f"Analyses croisées{title_suffix}")
            st.write(
                "Évolution comparée du nombre de véhicules électriques et des bornes de recharge par année"
            )

            # Utiliser des colonnes pour aligner les filtres
            granularity_tab3_1 = st.selectbox(
                "Niveau de granularité :",
                options=["région", "département"],
                key="slider_granularity_subtab3_1"
            )

            if granularity_tab3_1 == 'région':
                st.subheader("Ratio du nombre de véhicules électriques par bornes selon la région")
                st.components.v1.html(carte_vehicules_bornes_reg, height=500, width=800)
            elif granularity_tab3_1 == 'département':
                st.subheader("Ratio du nombre de véhicules électriques par bornes selon le département")
                st.components.v1.html(carte_vehicules_bornes_dep, height=500, width=800)


            header = st.container()
            header.write("""<div class='fixed-header'/>""", unsafe_allow_html=True)

            ### Custom CSS for the sticky header
            st.markdown(
                """
            <style>
                div[data-testid="stVerticalBlock"] div:has(div.fixed-header) {
                    position: sticky;
                    top: 2.875rem;
                    background-color: white;
                    z-index: 999;
                }
                .fixed-header {
                    border-bottom: 1px solid black;
                }
            </style>
                """,
                unsafe_allow_html=True
            )

            with header:
                # Utiliser des colonnes pour aligner les filtres
                col1, col2, col3 = st.columns([1, 1, 2])  # Largeurs ajustables

                with col1:
                    selected_year = st.selectbox(
                        "Choisissez une année",
                        options=years,
                        key="slider_year_tab3"
                    )
                with col2:
                    granularite = st.selectbox(
                        "Choisissez le niveau de granularité",
                        options=["Aucun", "Région", "Département", "Commune"],
                        key="slider_granularity_tab3"
                    )
                with col3:
                    if granularite == "Région":
                        options = ["Toutes les régions"] + \
                            sorted(nb_voitures['nom_region'].unique())
                        selected_option = st.selectbox(
                            "Sélectionnez une région", options=options, key="slider_option1_tab3")
                    elif granularite == "Département":
                        options = ["Tous les départements"] + \
                            sorted(nb_voitures['nom_departement'].unique())
                        selected_option = st.selectbox(
                            "Sélectionnez un département", options=options, key="slider_option2_tab3")
                    elif granularite == "Commune":
                        options = ["Toutes les communes"] + \
                            sorted(nb_voitures['libgeo'].unique())
                        selected_option = st.selectbox(
                            "Sélectionnez une commune", options=options, key="slider_option3_tab3")
                    else:
                        selected_option = "Aucun"

            # ---- Filtrage des données ----
            filtered_data = nb_voitures.copy()

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
                fig3 = go.Figure()

                # Ajout des données pour les bornes
                fig3.add_trace(go.Scatter(
                    x=evolution_data['annee'],
                    y=evolution_data['nb_borne_cumul'],
                    name='Nombre de bornes',
                    mode='lines+markers',
                    line=dict(color='blue'),
                    yaxis='y1'  # Premier axe Y
                ))

                # Ajout des données pour les véhicules
                fig3.add_trace(go.Scatter(
                    x=evolution_data['annee'],
                    y=evolution_data['nb_vehicles'],
                    name='Nombre de véhicules électriques',
                    mode='lines+markers',
                    line=dict(color='green'),
                    yaxis='y2'  # Deuxième axe Y
                ))

                # Configuration des axes Y
                fig3.update_layout(
                    title=f"Évolution des bornes et véhicules électriques par année{title_suffix}",
                    xaxis=dict(title='Année', tickfont=dict(size=16)),
                    yaxis=dict(
                        title='Nombre de bornes',
                        titlefont=dict(color='blue', size=16),
                        tickfont=dict(color='blue', size=16),
                    ),
                    yaxis2=dict(
                        title='Nombre de véhicules électriques',
                        titlefont=dict(color='green', size=16),
                        tickfont=dict(color='green', size=16),
                        overlaying='y',
                        side='right'
                    ),
                    legend=dict(title='Catégorie', orientation="h",
                                yanchor="bottom", y=1.02, xanchor="right", x=1),
                    hovermode="x unified"
                )
                fig3.update_xaxes(tickformat="%Y", tickmode="linear", dtick="M12")

                # Graphique 2 : Ratio véhicules par borne
                fig4 = px.line(
                    evolution_data,
                    x='annee',
                    y='ratio_vehicles_per_borne',
                    title=f"Ratio du nombre de véhicules par borne par année{title_suffix}",
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
                fig4.update_xaxes(tickformat="%Y", tickmode="linear", dtick="M12")

                st.plotly_chart(fig3)
                st.plotly_chart(fig4)

        with subtab3_2:

            st.subheader(f"Analyses croisées{title_suffix}")
            st.write(
                "Évolution comparée du nombre de véhicules électriques et des bornes de recharge par année"
            )

             # Utiliser des colonnes pour aligner les filtres
            granularity_tab3_2 = st.selectbox(
                "Niveau de granularité :",
                options=["région", "département"],
                key="slider_granularity_subtab3_2"
            )

            if granularity_tab3_2 == 'région':
                st.subheader("Ratio du nombre de bornes de recharge par TMJA selon la région")
                st.components.v1.html(carte_bornes_tmja_reg, height=500, width=800)
            elif granularity_tab3_2 == 'département':
                st.subheader("Ratio du nombre de bornes de recharge par TMJA selon le département")
                st.components.v1.html(carte_bornes_tmja_dep, height=500, width=800)