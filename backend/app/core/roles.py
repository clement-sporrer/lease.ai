from enum import Enum


class UserRole(str, Enum):
    partner = "partner"
    client = "client"
    admin = "admin"
    ops = "ops"
    risk = "risk"
    financier = "financier"
    cfo = "cfo"
