import streamlit as st


def show(carte_borne_pred,carte_bornes_axes,dico_graphes_reco):
    dico_trimestres = {
        'T1-2025': '1', 'T2-2025': '2', 'T3-2025': '3', 'T4-2025': '4',
        'T1-2026': '5', 'T2-2026': '6', 'T3-2026': '7', 'T4-2026': '8',
        'T1-2027': '9', 'T2-2027': '10', 'T3-2027': '11', 'T4-2027': '12',
        'T1-2028': '13', 'T2-2028': '14', 'T3-2028': '15', 'T4-2028': '16',
        'T1-2029': '17', 'T2-2029': '18', 'T3-2029': '19', 'T4-2029': '20',
        'T1-2030': '21', 'T2-2030': '22', 'T3-2030': '23', 'T4-2030': '24'
    }
    col1, col2 = st.columns([1, 1])
    # Liste des trimestres (les clés du dictionnaire)
    with col1:
        st.write("Liste des trimestres :")
        trimestres = list(dico_trimestres.keys())

        selected_key = st.selectbox(
        "Sélectionnez un trimestre :",
        options=trimestres,  # Les clés comme options
        index=22  # Par défaut, T3-2030
        )
        selected_year = dico_trimestres[selected_key]
        code = f"Carte_Trimestre_{selected_year}.html"
        carte_utilise = carte_borne_pred[code]
        st.title("Carte Interactive")
        st.components.v1.html(carte_utilise, height=500, width=650)

    with col2:
        st.write("Liste des trimestres :")
        region = ['Île-de-France',
                        'Centre-Val de Loire',
                        'Bourgogne-Franche-Comté',
                        'Normandie',
                        'Hauts-de-France',
                        'Grand Est',
                        'Pays de la Loire',
                        'Bretagne',
                        'Nouvelle-Aquitaine',
                        'Occitanie',
                        'Auvergne-Rhône-Alpes',
                        "Provence-Alpes-Côte d'Azur",
                        'Corse',
                        'Toutes les régions']

        selected_key = st.selectbox(
        "Sélectionnez un trimestre :",
        options=region
        )

        code = f"graph_region_{selected_key}.html"
        carte_utilise = dico_graphes_reco[code]
        st.title("Carte Interactive")
        st.markdown(
            """
            L’Union européenne préconise un ratio de 1 borne de recharge pour 10 véhicules électriques 
            ([Ref4](https://www.zeplug.com/news/7-chiffres-cles-sur-les-bornes-de-recharge-pour-vehicule-electrique-en-france#:~:text=déjà%20fortement%20alimentée.-,10%20véhicules%20électriques%20pour%20un%20point%20de%20charge%20public%20en,1%20borne%20pour%2010%20véhicules%20!)). Pour cet objectif, nous avons créé une recommandation qui se 
            rapproche d’un dixième de la prédiction du nombre de voitures de 2030. Cette courbe part donc 
            du nombre de bornes existantes en 2024 pour au final atteindre le nombre de bornes pour valider 
            cet objectif.
            """
        )

        st.components.v1.html(carte_utilise, height=500, width=800)
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.title("Carte Interactive")
    with col2:
        selected_rayon = st.slider(
        "Sélectionnez une année :",
        min_value=20,
        max_value=60,
        value=20,  # Valeur par défaut
        step=20,
        key="slider_rayon_axes"
        )
        selected_rayon = str(selected_rayon)
        st.markdown(
            """
Nous avions pour objectif de créer une visualisation claire afin de savoir où est-ce qu’il manque des bornes, pour cela nous nous sommes notamment basés sur un objectif de l’union européenne qui est d’avoir une borne électrique tous les 60 kilomètres maximum tout le long du réseau routier principal européen, d’ici 2026.
Nous avons donc pensé à créer une carte nous permettant de visualiser où il faudrait ajouter des bornes de recharge afin de respecter cet objectif, mais aussi d'autres objectifs potentiels plus ambitieux : avoir une borne tous les 20 et 40 kilomètres. 
            """
        )
    with col1:
        code_axe = f"carte_bornes_axes_{selected_rayon}.html"
        carte_utilise_axes = carte_bornes_axes[code_axe]
        st.components.v1.html(carte_utilise_axes, height=500, width=650)