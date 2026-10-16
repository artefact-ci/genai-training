"""Schéma de sortie de l'extraction (TP 1, BONUS). Il sera réutilisé par le routeur du module 3."""
from typing import Literal

from pydantic import BaseModel


class MessageClient(BaseModel):
    categorie: Literal["P1", "P2", "P3", "P4", "P5"]
    produit: Literal["pret", "epargne", "orange_money", "autre"]
    motif: str
    # TODO 5 (BONUS) – Ajoutez les quatre champs manquants avec leur type :
    #   dates (liste de textes), montants_fcfa (liste d'entiers),
    #   urgence et sentiment (Literal avec les valeurs autorisées).
