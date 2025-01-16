import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import branca.colormap as cm


def show(nb_voitures, bornes_completes, bornes, carte_vehicules_bornes_reg, carte_vehicules_bornes_dep, carte_bornes_tmja_reg, carte_bornes_tmja_dep, bornes_tmja_par_annee):
    """
    Affiche les statistiques descriptives avec filtres intégrés.

    Args:
        nb_voitures (pd.DataFrame): Données des véhicules électriques par commune, département et région.
        bornes_completes (pd.DataFrame): Données des bornes de recharge par Aménageurs & Opérateurs.
        bornes (pd.DataFrame): Données des bornes de recharge par commune, département et région.
    """

    years = ["Toutes les années"] + \
        sorted(nb_voitures['annee'].unique())

    st.title("Statistiques descriptives")
    # st.write("Bienvenue sur la page des statistiques descriptives.")

    # ---- Filtres dans la barre latérale ----
    st.sidebar.header("Filtres")

    # Filtre par année
    years = ["Toutes les années"] + \
        sorted(nb_voitures['annee'].unique())
    selected_year = st.sidebar.selectbox("Choisissez une année", options=years)

    # Niveau de granularité
    granularite = st.sidebar.selectbox("Choisissez le niveau de granularité", options=["Aucun", "Région", "Département", "Commune"])

    # Options dynamiques en fonction du niveau choisi
    if granularite == "Région":
        options = ["Toutes les régions"] + \
            sorted(nb_voitures['nom_region'].unique())
        selected_option = st.sidebar.selectbox("Sélectionnez une région", options=options)
    elif granularite == "Département":
        options = ["Tous les départements"] + \
            sorted(nb_voitures['nom_departement'].unique())
        selected_option = st.sidebar.selectbox("Sélectionnez un département", options=options)
    elif granularite == "Commune":
        options = ["Toutes les communes"] + \
            sorted(nb_voitures['libgeo'].unique())
        selected_option = st.sidebar.selectbox("Sélectionnez une commune", options=options)
    else:
        selected_option = "Aucun"

    # ---- Filtrage des données ----
    filtered_data = nb_voitures.copy()
    filtered_data_bornes = bornes_completes.copy()

    # Appliquer le filtre par année
    if selected_year != "Toutes les années":
        filtered_data = filtered_data[filtered_data['annee'] == selected_year] # Données filtrées pour véhicules
        filtered_data_bornes = filtered_data_bornes[filtered_data_bornes['Annee'] == selected_year]

    # Appliquer le filtre par région, département ou commune
    if granularite == "Région" and selected_option != "Toutes les régions":
        # Véhicules
        filtered_data = filtered_data[filtered_data['nom_region'] == selected_option]

        # Bornes de recharge
        filtered_data_bornes = filtered_data_bornes[filtered_data_bornes["nom_region"] == selected_option]

    elif granularite == "Département" and selected_option != "Tous les départements":
        # Véhicules
        filtered_data = filtered_data[filtered_data['nom_departement'] == selected_option]

        # Bornes de recharge
        filtered_data_bornes = filtered_data_bornes[filtered_data_bornes["nom_departement"] == selected_option]

    elif granularite == "Commune" and selected_option != "Toutes les communes":
        # Véhicules
        filtered_data = filtered_data[filtered_data['libgeo'] == selected_option]

        # Bornes de recharge
        filtered_data_bornes = filtered_data_bornes[filtered_data_bornes["libgeo"] == selected_option]


    top_data = nb_voitures.copy() # Top 10 par niveau de granularité de véhicules
    top_bornes_data = bornes.copy() # Top 10 par niveau de granularité des bornes de recharge

    # derniere_annee = top_data['annee'].max()
    if selected_year != "Toutes les années":
        derniere_annee = selected_year
        top_bornes_data = top_bornes_data[top_bornes_data['Annee'] == selected_year]
    else:
        derniere_annee = top_data['annee'].max()

    # Filtrer les données pour ne conserver que celles de la dernière année
    top_data = top_data[top_data['annee'] == derniere_annee]

    # Appliquer le filtre par région, département ou commune
    if granularite == "Région":
        # Véhicules
        top_data = top_data.groupby('nom_region', as_index=False)['nb_vp_rechargeables_el'].sum()
        top_data["Nom"] = top_data["nom_region"]

        # Bornes de recharge
        top_bornes_data = bornes.groupby('nom_region', as_index=False)['nb_borne'].sum()
        top_bornes_data["Nom"] = top_bornes_data["nom_region"]
    elif granularite == "Département":
        # Véhicules
        top_data = top_data.groupby('nom_departement', as_index=False)['nb_vp_rechargeables_el'].sum()
        top_data["Nom"] = top_data["nom_departement"]

        # Bornes de recharge
        top_bornes_data = bornes.groupby('nom_departement', as_index=False)['nb_borne'].sum()
        top_bornes_data["Nom"] = top_bornes_data["nom_departement"]
    elif granularite == "Commune":
        # Véhicules
        top_data = top_data.groupby('libgeo', as_index=False)['nb_vp_rechargeables_el'].sum()
        top_data["Nom"] = top_data["libgeo"]

        # Bornes de recharge
        top_bornes_data = bornes.groupby('commune', as_index=False)['nb_borne'].sum()
        top_bornes_data["Nom"] = top_bornes_data["commune"]
    else:
        # Véhicules
        top_data = top_data.groupby('libgeo', as_index=False)['nb_vp_rechargeables_el'].sum()
        top_data["Nom"] = top_data["libgeo"]

        # Bornes de recharge
        top_bornes_data = top_bornes_data.groupby('commune', as_index=False)['nb_borne'].sum()
        top_bornes_data["Nom"] = top_bornes_data["commune"]


    # Déterminer le suffixe du titre dynamique
    title_suffix = ""
    if selected_option not in ["Aucun", "Toutes les régions", "Tous les départements", "Toutes les communes"]:
        title_suffix = f" - {selected_option}"
    if selected_option == "Aucun":
        title_suffix = f" - France"
    if selected_year != "Toutes les années":
        title_suffix += f" (Année : {selected_year})"

    # Calcul des valeurs globales
    voitures = filtered_data.groupby('annee')['nb_vp_rechargeables_el'].sum().reset_index()
    total_vehicles = voitures['nb_vp_rechargeables_el'].max()  # Nombre total de véhicules électriques
    bornes_annee = bornes.groupby('Annee')['nb_borne_cumul'].sum().reset_index()
    total_bornes = bornes_annee['nb_borne_cumul'].max()  # Nombre total de bornes (valeur cumulée maximale)
    ratio_vehicles_per_borne = total_vehicles / total_bornes  # Ratio véhicules par borne

    # Affichage en trois colonnes
    col1, col2, col3 = st.columns(3)

    col1.markdown(f"<h5 style='font-weight: bold;'>Véhicules électriques</h5>"
                f"<p style='font-size: 30px;'>{total_vehicles:,}".replace(",", " ") + "</p>"
                f"<p style='font-size: 12px; color: blue;'>{title_suffix}</p>", unsafe_allow_html=True)

    col2.markdown(f"<h5 style='font-weight: bold;'>Bornes de recharge</h5>"
                f"<p style='font-size: 30px;'>{total_bornes:,}".replace(",", " ") + "</p>"
                f"<p style='font-size: 12px; color: blue;'>{title_suffix}</p>", unsafe_allow_html=True)

    col3.markdown(f"<h5 style='font-weight: bold;'>Véhicules par borne</h5>"
                f"<p style='font-size: 30px;'>{ratio_vehicles_per_borne:.2f}</p>"
                f"<p style='font-size: 12px; color: blue;'>{title_suffix}</p>", unsafe_allow_html=True)


    # ---- Onglets pour navigation ----
    tab1, tab2, tab3 = st.tabs([
        "Véhicules électriques",
        "Bornes de recharge",
        "Analyses croisées"
    ])

    # ---- Analyse : Nombre de véhicules électriques ----
    with tab1:
        st.subheader(f"Analyse du nombre de véhicules électriques{title_suffix}")
        agg_vehicules = filtered_data.groupby('annee')['nb_vp_rechargeables_el'].sum().reset_index()
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
        agg_vehicules = filtered_data.groupby('annee')['nb_vp_rechargeables_el'].sum().reset_index()

        # Graphique interactif avec Plotly
        fig1 = px.bar(
            agg_vehicules,
            x='annee',
            y='nb_vp_rechargeables_el',
            title=f"Évolution du nombre de véhicules électriques{title_suffix}",
            labels={'annee': 'Année', 'nb_vp_rechargeables_el': 'Nombre de véhicules électriques'}
        )
        fig1.update_traces(textposition='outside')
        fig1.update_xaxes(tickformat="%Y", tickmode="linear", dtick="M12")
        st.plotly_chart(fig1)

        # ---- Top 10 par granularité ----
        st.subheader(
            "Top 10 nombre de véhicules électriques")

        # Tri et sélection des 10 premiers
        top_data = top_data.sort_values(by='nb_vp_rechargeables_el', ascending=False).head(10)

        # Graphique interactif : Top 10
        fig_top = px.bar(
            top_data,
            x='nb_vp_rechargeables_el',
            y='Nom',
            orientation='h',
            title=f"Top 10 {'ville' if granularite == 'Aucun' else granularite.lower()}s avec le plus grand nombre de véhicules électriques",
            labels={'Nom': f"{'ville' if granularite == 'Aucun' else granularite.lower()}", 'nb_vp_rechargeables_el': 'Nombre de véhicules électriques'},
            # text='Nombre de véhicules'
        )

        # Affichage du graphique
        st.plotly_chart(fig_top)

        st.subheader(f"Analyse du ratio véhicules électriques / total{title_suffix}")

        # Calculer le ratio pour chaque entrée
        filtered_data['ratio_ve'] = filtered_data['nb_vp_rechargeables_el'] / \
            filtered_data['nb_vp']

        # Agréger les données par année
        agg_ratio = filtered_data.groupby('annee')['ratio_ve'].mean().reset_index()

        # Graphique du ratio véhicules électriques / véhicules au total
        fig_ratio = px.line(
            agg_ratio,
            x='annee',
            y='ratio_ve',
            title=f"Évolution du ratio véhicules électriques / total{title_suffix}",
            labels={'annee': 'Année', 'ratio_ve': 'Ratio véhicules électriques / total'},
            markers=True
        )
        fig_ratio.update_yaxes(tickformat=".2%")  # Affichage en pourcentage
        fig_ratio.update_xaxes(tickformat="%Y", tickmode="linear", dtick="M12")
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

        agg_bornes = agg_bornes.groupby('Annee')['nb_borne_cumul'].sum().reset_index()

        # Graphique évolution du nombre de bornes de recharge
        fig2 = px.line(
            agg_bornes,
            x='Annee',
            y='nb_borne_cumul',
            title=f"Évolution du nombre de bornes de recharge{title_suffix}",
            labels={'Annee': 'Année', 'nb_borne_cumul': 'Nombre de bornes de recharge'},
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
        top_bornes_data2 = top_bornes_data.sort_values(by='nb_borne', ascending=False).head(10)

        # Graphique du Top 10
        fig_top_bornes = px.bar(
            top_bornes_data2,
            x='nb_borne',
            y='Nom',
            title=f"Top 10 des {"ville" if granularite == "Aucun" else granularite.lower()}s avec le plus de bornes de recharge",
            labels={'Nom': f'{"ville" if granularite == "Aucun" else granularite.lower()}', 'nb_borne': 'Nombre de bornes de recharge'},
        )
        fig_top_bornes.update_traces(textposition='outside')
        fig_top_bornes.update_layout(xaxis_tickangle=-45)

        # Affichage du graphique
        st.plotly_chart(fig_top_bornes)

        st.subheader("Aménageurs & Opérateurs")
        st.write("")


        # ---- 1. Évolution du nombre d'Aménageurs et d'Opérateurs ----
        evolution_am_op = (
            filtered_data_bornes.groupby(['Annee'])
            .agg(
                nb_amenageurs=('nom_amenageur', 'nunique'),
                nb_operateurs=('nom_operateur', 'nunique')
            )
            .reset_index()
        )

        fig3 = px.line(
            evolution_am_op,
            x='Annee',
            y=['nb_amenageurs', 'nb_operateurs'],
            title="Évolution du nombre d'Aménageurs et d'Opérateurs",
            labels={'value': 'Nombre', 'variable': 'Catégorie'},
            markers=True
        )
        fig3.update_layout(legend_title="Catégorie", xaxis_title="Année", yaxis_title="Nombre")
        st.plotly_chart(fig3)

        # ---- 2. Top 10 des Aménageurs et Opérateurs par nombre de bornes ----
        top_amenageurs = (
            filtered_data_bornes.groupby('nom_amenageur')['nb_borne_cumul']
            .sum()
            .reset_index()
            .sort_values(by='nb_borne_cumul', ascending=False)
            .head(10)
        )

        top_operateurs = (
            filtered_data_bornes.groupby('nom_operateur')['nb_borne_cumul']
            .sum()
            .reset_index()
            .sort_values(by='nb_borne_cumul', ascending=False)
            .head(10)
        )

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Top 10 Aménageurs par nombre de bornes")
            fig4 = px.bar(
                top_amenageurs,
                x='nb_borne_cumul',
                y='nom_amenageur',
                orientation='h',
                title="Top 10 Aménageurs",
                labels={'nb_borne_cumul': 'Nombre de bornes', 'nom_amenageur': 'Aménageur'},
                # text='nb_borne_cumul'
            )
            fig4.update_traces(textposition='outside')
            st.plotly_chart(fig4)

        with col2:
            st.subheader("Top 10 Opérateurs par nombre de bornes")
            fig5 = px.bar(
                top_operateurs,
                x='nb_borne_cumul',
                y='nom_operateur',
                orientation='h',
                title="Top 10 Opérateurs",
                labels={'nb_borne_cumul': 'Nombre de bornes', 'nom_operateur': 'Opérateur'},
                text='nb_borne_cumul'
            )
            fig5.update_traces(textposition='outside')
            st.plotly_chart(fig5)



    # ---- Analyses croisées ----
    with tab3:
        st.subheader(f"Analyses croisées{title_suffix}")
        st.write("Évolution comparée du nombre de véhicules électriques et des bornes de recharge par année")

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
                fig6 = go.Figure()

                # Ajout des données pour les bornes
                fig6.add_trace(go.Scatter(
                    x=evolution_data['annee'],
                    y=evolution_data['nb_borne_cumul'],
                    name='Nombre de bornes',
                    mode='lines+markers',
                    line=dict(color='blue'),
                    yaxis='y1'  # Premier axe Y
                ))

                # Ajout des données pour les véhicules
                fig6.add_trace(go.Scatter(
                    x=evolution_data['annee'],
                    y=evolution_data['nb_vehicles'],
                    name='Nombre de véhicules électriques',
                    mode='lines+markers',
                    line=dict(color='green'),
                    yaxis='y2'  # Deuxième axe Y
                ))

                # Configuration des axes Y
                fig6.update_layout(
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
                fig6.update_xaxes(tickformat="%Y", tickmode="linear", dtick="M12")

                # Graphique 2 : Ratio véhicules par borne
                fig7 = px.line(
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
                fig7.update_traces(mode="lines+markers")
                fig7.update_layout(
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
                fig7.update_xaxes(tickformat="%Y", tickmode="linear", dtick="M12")

                st.plotly_chart(fig6)
                st.plotly_chart(fig7)

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

            fig_trafic = go.Figure()

            fig_trafic.add_trace(go.Scatter(
                x=bornes_tmja_par_annee['annee'],
                y=bornes_tmja_par_annee['tmja_moyen'],
                mode='lines+markers',
                line=dict(color='blue', dash='solid'),
                marker=dict(symbol='circle', size=8),
                name='TMJA'
            ))

            fig_trafic.update_layout(
                title="TMJA par année",
                xaxis_title="Année",
                yaxis_title="TMJA",
                template="plotly_white",
                showlegend=True,
                title_font=dict(size=16),
                xaxis=dict(title_font=dict(size=12)),
                yaxis=dict(title_font=dict(size=12)),
            )

            fig_trafic.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128, 128, 128, 0.3)')
            fig_trafic.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128, 128, 128, 0.3)')

            st.plotly_chart(fig_trafic)
