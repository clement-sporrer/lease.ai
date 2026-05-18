from enum import Enum


class UserRole(str, Enum):
    # Internal ISEI roles (web back-office)
    admin = "admin"          # ADV — validation dossiers, workflow principal
    commercial = "commercial"  # Pipeline, création et suivi deals
    ops = "ops"              # Activation, livraison, suivi assets
    risk = "risk"            # Analyse et scoring des dossiers
    financier = "financier"  # Packages refi, suivi refinanceurs
    cfo = "cfo"              # Dashboard global, KPIs, trésorerie
    comptable = "comptable"  # Facturation, Pennylane, réconciliation

    # External roles (mobile app)
    partner = "partner"      # Revendeurs IT — création et suivi dossiers
    client = "client"        # Clients finaux — suivi contrat et paiements
