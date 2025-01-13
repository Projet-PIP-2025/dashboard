import streamlit as st
import numpy as np
import darts
import pandas as pd
from darts import TimeSeries
from darts.models import ExponentialSmoothing
import matplotlib.pyplot as plt




def create_pred(borne_data) :
    # On enlève les valeurs nulles de dates de mise en service dans le DataFrame
    borne_data = borne_data.dropna(subset=['date_mise_en_service'])
    borne_data["date_mise_en_service"] = pd.to_datetime(borne_data["date_mise_en_service"])

    # On créer les colonnes Mois_Annee
    borne_data["Mois"] = borne_data["date_mise_en_service"].dt.month
    borne_data["Mois_Annee"] = borne_data["date_mise_en_service"].dt.to_period("M")

    #print(borne_data["Mois_Annee"])
    #return borne_data

    # On initialise le DataFrame du nombre de bornes crées par Années
    temps_ma = pd.DataFrame()
    temps_ma["Mois_Annee"] = borne_data["Mois_Annee"].value_counts().index
    temps_ma["Mois_Annee"] = temps_ma["Mois_Annee"].dt.to_timestamp()


    temps_ma["nb"] = borne_data["Mois_Annee"].value_counts().values
    temps_ma["nb_max"] = borne_data["Mois_Annee"].value_counts().values * 1.43

    # On drop les informations pour 2025 car pas complètes
    temps_ma = temps_ma.drop(index=108)     # 108 index de Janvier 2025 (à vérifier)

    # On créer une série avec les Mois_Années et le nombre de bornes associé, transforme les Nan en 0 (en passant par le format DataFrame)
    series_mois = TimeSeries.from_dataframe(temps_ma, "Mois_Annee", "nb", fill_missing_dates=True)
    series_pandas = series_mois.pd_series()
    series_pandas = series_pandas.fillna(0)
    series_mois = TimeSeries.from_series(series_pandas)


    # On refait pareil avec la borne max (Intervalle de Confiance)
    series_mois_max = TimeSeries.from_dataframe(temps_ma, "Mois_Annee", "nb_max", fill_missing_dates=True)
    series_pandas_max = series_mois_max.pd_series()
    series_pandas_max = series_pandas_max.fillna(0)
    series_mois_max = TimeSeries.from_series(series_pandas_max)

    # Implémentation du modèle
    model = ExponentialSmoothing()
    model.fit(series_mois)
    prediction = model.predict(84)  # 84 est le nombre de mois pour arriver a la fin d'année de 2032

    # Pareil pour l'intervalle de confiance
    model.fit(series_mois_max)
    prediction_max = model.predict(84)

    # Ajout des prédictions (de Création de Bornes par Années) au tableau
    temps_ma = temps_ma.sort_values(by='Mois_Annee')
    temps_ma = temps_ma.reset_index()

    last_date = temps_ma["Mois_Annee"][128]
    dates_pred = pd.date_range(start=last_date, periods=85, freq='M')[1:]

    df_pred = pd.DataFrame({
    'Mois_Annee': dates_pred
    })
    df_pred['nb'] = prediction.values()
    df_pred['nb_max'] = prediction_max.values()

    df_pred['index'] = [temps_ma['index'].iloc[-1]] * len(df_pred)
    temps_ma_updated = pd.concat([temps_ma, df_pred], ignore_index=True)

    # On somme le résultat des prédictions des mois sur les années
    listeval = []
    listeval_max = []
    liste_an = []
    for i in range(2012,2032) :
        tab = temps_ma_updated[temps_ma_updated["Mois_Annee"].dt.year == i]
        listeval.append(tab["nb"].sum())
        listeval_max.append(tab["nb_max"].sum())
        liste_an.append(i)
    
    pd_hist = pd.DataFrame({
        'Annee': liste_an,
        'nb': listeval,
        'nb_max': listeval_max
    })
    # On ajoute au tableau les additions de Créations de bornes, pour obtenir le nombre de bornes sur le territoire au temps donné
    liste_somme = []
    liste_somme_max = []
    s = 0
    for i in listeval :
        s = s + i
        liste_somme.append(s)

    s = 0
    for i in listeval_max :
        s = s + i
        liste_somme_max.append(s)

    pd_hist["Total"] = liste_somme
    pd_hist["Total_max"] = liste_somme_max

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








def show(bornes):
    st.title("Page 3 : Page de prédiction")
    st.write("Bienvenue sur la page de prédiction.")
    st.write("Prédiction de l'évolution du nombre de bornes")
    create_pred(bornes)
    #st.write(borne_data["date_mise_en_service"].head())
    #st.write("Type :", type(borne_data["date_mise_en_service"].iloc[0]))
    #st.write(borne_data["Mois_Annee"].head())
    # Ajoute ici le contenu spécifique à cette page