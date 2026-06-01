# -*- coding: utf-8 -*-
"""
IntegrityCheck AI - Plataforma BI
Entrenamiento del Modelo 2: Detección de Plagio Textual (TF-IDF + Cosine Similarity)
Autor: Grupo 4 - Universidad Peruana
"""

import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from config_ml import RUTA_MODELO_PLAGIO, NLP_MAX_FEATURES, NLP_NGRAM_RANGE

def obtener_corpus_referencia() -> list:
    """
    Retorna un corpus de textos académicos de referencia (tesis, artículos, etc.)
    para cruzar contra los trabajos entregados por los alumnos.
    """
    return [
        "El análisis de algoritmos eficientes para la resolución de problemas combinatorios es vital en la computación cuántica moderna.",
        "Los principios de la constitución peruana de 1993 establecen un modelo económico social de mercado basado en la libre competencia.",
        "La anatomía del corazón humano comprende cuatro cavidades principales: dos aurículas y dos ventrículos que bombean sangre oxigenada.",
        "El modelo de las cinco fuerzas de Porter permite analizar la estructura competitiva de un sector industrial para definir estrategias corporativas.",
        "La inteligencia artificial en la detección de anomalías se enfoca en identificar patrones raros que no concuerdan con el comportamiento esperado.",
        "El derecho penal general estudia los presupuestos de la punibilidad y las consecuencias jurídicas del delito en la doctrina nacional.",
        "La farmacología y el estudio de los fármacos clínicos evalúa la absorción, distribución, metabolismo y excreción de compuestos orgánicos.",
        "La administración estratégica de recursos permite optimizar el desempeño y el retorno sobre la inversión en medianas empresas peruanas."
    ]

def entrenar() -> None:
    print("=== Entrenando Modelo de Plagio Textual (TF-IDF NLP) ===")
    
    corpus = obtener_corpus_referencia()
    
    # Configurar vectorizador TF-IDF según la especificación técnica
    vectorizer = TfidfVectorizer(
        max_features=NLP_MAX_FEATURES,
        ngram_range=NLP_NGRAM_RANGE,
        stop_words=['el', 'la', 'los', 'las', 'un', 'una', 'de', 'para', 'en', 'con', 'y', 'o'] # stop words en español
    )
    
    # Ajustar y transformar el corpus
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    # Guardar en un diccionario para la serialización
    modelo_plagio = {
        "vectorizer": vectorizer,
        "tfidf_matrix": tfidf_matrix,
        "corpus_referencia": corpus
    }
    
    # Guardar en archivo pickle
    joblib.dump(modelo_plagio, RUTA_MODELO_PLAGIO)
    print(f"Modelo NLP de plagio guardado exitosamente en: {RUTA_MODELO_PLAGIO}")
    print(f"Corpus de referencia cargado con {len(corpus)} documentos base.")

if __name__ == "__main__":
    entrenar()
