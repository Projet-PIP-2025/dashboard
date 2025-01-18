import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt




def create_pred(pd_hist) :

    # Affichage graphique du résultat
    split_index = pd_hist[pd_hist['Annee'] >= 2025].index[0]

    #   Tracer la courbe continue avec deux segments de couleur
    fig, ax = plt.subplots(figsize=(10, 6))

    # Première partie : avant 2025 (en noir)
    ax.plot(
        pd_hist['Annee'][:split_index + 1],
        pd_hist['Total'][:split_index + 1],
        color='black', label='Avant 2025'
    )

    # Deuxième partie : 2025 et après (en bleu)
    ax.plot(
        pd_hist['Annee'][split_index:],
        pd_hist['Total'][split_index:],
        color='blue', label=' Prédiction après 2025'
    )

    # Troisième partie : avant 2025 (en noir)
    ax.plot(
        pd_hist['Annee'][:split_index + 1],
        pd_hist['Total_max'][:split_index + 1],
        color='white'
    )

    # Quatrième partie : 2025 et après (en bleu)
    ax.plot(
        pd_hist['Annee'][split_index:],
        pd_hist['Total_max'][split_index:],
        color='white'
    )

    # Cinquième partie : fixation des objectifs
    ax.plot(pd_hist['Annee'], [400000] * 20, color='red', linestyle='--', label='Objectif Horizon 2030')

    # Intervalles de confiance
    ax.fill_between(pd_hist['Annee'][:split_index + 1], pd_hist['Total'][:split_index + 1], pd_hist['Total_max'][:split_index + 1], color="gray", alpha=0.3) # Pour les réels
    ax.fill_between(pd_hist['Annee'][split_index:], pd_hist['Total'][split_index:], pd_hist['Total_max'][split_index:], color="gray", alpha=0.3, label="Intervalle de Confiance 30 %") # Pour les prédictions

    # Ajouter des légendes et des étiquettes
    ax.set_xlabel("Année")
    ax.set_ylabel("Valeur")
    ax.set_title("Évolution des nombres de Bornes")
    ax.legend()
    ax.grid(True)

    # Afficher le graphique dans Streamlit
    st.pyplot(fig)








def show(bornes_pred,pred_reg, pred_ve):
    st.title("Page 3 : Page de prédiction")
    st.write("Bienvenue sur la page de prédiction.")
    st.write("Prédiction de l'évolution du nombre de bornes")
    create_pred(bornes_pred)
    # Ensuite on affiche le graphique de prédiction globale sur les véhicules (Raissa)
    st.write("Prédiction de l'évolution du nombre de véhicules électriques")

    pred_ve["date_arrete"] = pd.to_datetime(pred_ve["date_arrete"])
    pred_ve["Annee"] = pred_ve["date_arrete"].dt.year
    


    noir = pred_ve[pred_ve['Annee'] <= 2025]
    bleu = pred_ve[pred_ve['Annee'] >= 2025]
    fig, ax = plt.subplots(figsize=(10, 6))


    ax.plot(
        noir['date_arrete'],
        noir['prediction_nb_vp_rechargeables_el'],
        color='black', label='Avant 2025'
    )


    ax.plot(
        bleu['date_arrete'],
        bleu['prediction_nb_vp_rechargeables_el'],  
        color='blue', label=' Prédiction après 2025'       
    )

    # Cinquième partie : fixation des objectifs
    ax.plot(pred_ve['date_arrete'], [4800000] * len(pred_ve['Annee']), color='red', linestyle='--', label='Objectif Horizon 2030')

    ax.set_xlabel("Année")
    ax.set_ylabel("Valeur")
    ax.set_title("Évolution des nombres de véhicules électriques")
    ax.legend()
    ax.grid(True)

    # Afficher le graphique dans Streamlit
    st.pyplot(fig)





    # On s'occupe de la prédiction du ratio par régions avec le ratio de 1 borne 10 véhicules

    st.write("Prédictions par régions")
    st.sidebar.header("Filtres")
    options = ["Toutes les régions"] + \
            sorted(pred_reg['Nom_Région'].unique()) 
    selected_option = st.sidebar.selectbox(
            "Sélectionnez une région", options=options)
    
    
    pred_reg = pred_reg[pred_reg['Nom_Région'] == selected_option] 

    # On tri les valeurs par années de façon ascendante
    pred_reg = pred_reg.sort_values(by='date_arrete')

    # Déterminer le suffixe du titre dynamique
    title_suffix = ""
    if selected_option  != "Toutes les régions" : 
        title_suffix = f" - {selected_option}"
    
    # Titre graph
    st.subheader(f"Analyse du nombre de véhicules électriques{title_suffix}")

    pred_reg["date_arrete"] = pd.to_datetime(pred_reg["date_arrete"])
    pred_reg["Annee"] = pred_reg["date_arrete"].dt.year
    #split_index = pred_reg[pred_reg['Annee'] >= 2025].index[0] 


    noir = pred_reg[pred_reg['Annee'] <= 2025]
    bleu = pred_reg[pred_reg['Annee'] >= 2025]
    fig, ax = plt.subplots(figsize=(10, 6))

    print(pred_reg)

    ax.plot(
        noir['date_arrete'],
        noir['nb_vp_rechargeables_el'],
        color='black', label='Avant 2025'
    )

    # pred_reg['date_arrete'][:split_index + 1]
    # pred_reg['nb_vp_rechargeables_el'][:split_index + 1]
    # Deuxième partie : 2025 et après (en bleu)
    ax.plot(
        bleu['date_arrete'],
        bleu['nb_vp_rechargeables_el'],  # Problème : il n'y a que la partie bleu qui s'affiche (elle ne s'arrète pas)
        color='blue', label=' Prédiction après 2025'       # Voir sur le split index...
    )

    #pred_reg['date_arrete'][split_index:],
    #pred_reg['nb_vp_rechargeables_el'][split_index:]
    ax.set_xlabel("Année")
    ax.set_ylabel("Valeur")
    ax.set_title("Évolution des nombres de véhicules électriques")
    ax.legend()
    ax.grid(True)

    # Afficher le graphique dans Streamlit
    st.pyplot(fig)
