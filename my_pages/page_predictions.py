import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt




def create_pred(pd_hist) :

    # Création des dates au format datetime (pour un plot plus clair)
    # Convertir la colonne "Annee" au format datetime
    pd_hist["Annee"] = pd.to_datetime(pd_hist["Annee"], format='%Y', errors='coerce')

    # Extraire l'année (inutile dans ce cas, mais inclus pour cohérence avec votre code)
    pd_hist["Annee"] = pd_hist["Annee"].dt.year

    

    # Affichage graphique du résultat
    #split_index = pd_hist[pd_hist['Annee'] >= 2025].index[0]

    noir = pd_hist[pd_hist['Annee'] <= 2025]
    bleu = pd_hist[pd_hist['Annee'] >= 2025]

    #   Tracer la courbe continue avec deux segments de couleur
    fig, ax = plt.subplots(figsize=(10, 6))

    # Première partie : avant 2025 (en noir)
    ax.plot(
        noir['Annee'],
        noir['Total'],
        color='black', label='Avant 2025'
    )

    # Deuxième partie : 2025 et après (en bleu)
    ax.plot(
        bleu['Annee'],
        bleu['Total'],
        color='blue', label=' Prédiction après 2025'
    )

    # Troisième partie : avant 2025 (en noir)
    ax.plot(
        noir['Annee'],
        noir['Total_max'],
        color='white'
    )

    # Quatrième partie : 2025 et après (en bleu)
    ax.plot(
        bleu['Annee'],
        bleu['Total_max'],
        color='white'
    )

    # Cinquième partie : fixation des objectifs
    ax.plot(pd_hist['Annee'], [400000] * 20, color='red', linestyle='--')
    ax.scatter(2030, 400000, color='red', label='Objectif Horizon 2030', zorder=5)

    ax.set_xticks(pd_hist["Annee"])

    # Intervalles de confiance
    #ax.fill_between(pd_hist['Annee'][:split_index + 1], pd_hist['Total'][:split_index + 1], pd_hist['Total_max'][:split_index + 1], color="gray", alpha=0.3) # Pour les réels
    #ax.fill_between(pd_hist['Annee'][split_index:], pd_hist['Total'][split_index:], pd_hist['Total_max'][split_index:], color="gray", alpha=0.3, label=" Marge de 30% de bornes supplémentaires") # Pour les prédictions

    ax.fill_between(
        noir['Annee'],
        noir['Total'],
        noir['Total_max'],
        color="gray",
        alpha=0.3
    )

    # Pour la partie à partir de 2025
    ax.fill_between(
        bleu['Annee'],
        bleu['Total'],
        bleu['Total_max'],
        color="gray",
        alpha=0.3,
        label="Marge de 30% de bornes supplémentaires"
    )

    # Ajouter des légendes et des étiquettes
    ax.set_xlabel("Année")
    ax.set_ylabel("Valeur")
    ax.set_title("Évolution des nombres de Bornes")
    ax.legend()
    ax.grid(True)

    # Afficher le graphique dans Streamlit
    st.pyplot(fig)








def show(bornes_pred,pred_reg, pred_ve, dico_graphes):
    # st.title("Page 3 : Page de prédiction")
    create_pred(bornes_pred)
    # Ensuite on affiche le graphique de prédiction globale sur les véhicules (Raissa)
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    # Liste des trimestres (les clés du dictionnaire)
    with col2:
        region = st.selectbox(
        "Selection Région :",
        options=['Total','Île-de-France','Centre-Val de Loire','Bourgogne-Franche-Comté','Normandie',
 'Hauts-de-France','Grand Est','Pays de la Loire','Bretagne','Nouvelle-Aquitaine','Occitanie',
 'Auvergne-Rhône-Alpes',"Provence-Alpes-Côte d'Azur",'Corse']
        )
    code = f"forecast_{region}.html"
    with col1:
        st.title("Prédiction du nombre de véhicules électriques")
    graphe_html_choisi = dico_graphes[code]
    st.components.v1.html(graphe_html_choisi, height=1050, width=1350)
