"""Schéma de sortie de l'extraction (TP 1). Il est figé ici : le routeur du module 3 aiguille sur `categorie`."""
from typing import Literal

from pydantic import BaseModel, Field


class MessageClient(BaseModel):
    categorie: Literal["P1", "P2", "P3", "P4", "P5"] = Field(
        description="P1 question produit ou frais, P2 consultation d'échéance, P3 anomalie de remboursement, "
                    "P4 demande hors périmètre, P5 suspicion de fraude")
    produit: Literal["pret", "epargne", "orange_money", "autre"]
    motif: str = Field(description="Résumé de la demande en une phrase")
    dates: list[str] = Field(description="Dates citées par le client, au format AAAA-MM-JJ")
    montants_fcfa: list[int] = Field(description="Montants cités par le client, en FCFA")
    urgence: Literal["basse", "moyenne", "haute"]
    sentiment: Literal["satisfait", "neutre", "inquiet", "mecontent"]
