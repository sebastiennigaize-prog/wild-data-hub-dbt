import os

from dotenv import load_dotenv


load_dotenv()


API_BASE_URL = "https://api.worldbank.org/v2"
PER_PAGE = 20000
REQUEST_TIMEOUT = 30
REQUEST_DELAY = 0.5
HASH_LIMIT = 50000

INDICATORS = {
    "NY.GDP.MKTP.CD": "PIB",
    "NY.GDP.PCAP.CD": "PIB_par_habitant",
    "NY.GDP.MKTP.KD.ZG": "Croissance_PIB",
    "SP.POP.TOTL": "Population",
    "SP.DYN.LE00.IN": "Esperance_vie",
    "SL.UEM.TOTL.ZS": "Chomage",
    "FP.CPI.TOTL.ZG": "Inflation",
    "EG.ELC.ACCS.ZS": "Acces_electricite",
    "EN.GHG.CO2.PC.CE.AR5": "CO2_par_habitant",
    "SP.DYN.CBRT.IN": "Taux_natalite",
    "SE.SEC.ENRR": "Scolarisation_secondaire",
    "SE.TER.ENRR": "Scolarisation_superieur",
    "SE.PRM.CMPT.ZS": "Achevement_primaire",
    "SH.XPD.CHEX.GD.ZS": "Depense_de_sante",
    "SE.XPD.TOTL.GD.ZS": "Depense_publique_education",
    "SE.ADT.LITR.ZS": "Alphabetisation_adultes",
}

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
DATASET_ID = "world_bank_raw"
TABLE_ID = "raw_data"

FULL_TABLE_ID = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"