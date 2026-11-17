# Categories for reader comments on 30Sekunden.
CANDIDATE_LABELS = [
    "sachliche Kritik",
    "Zustimmung oder Lob",
    "Frage oder Bitte um Information",
    "Sarkasmus oder Ironie",
    "Empörung oder Beleidigung",
    "Off-Topic oder Spam",
]

# Sentence the model checks for each label, "{}" is replaced by the label.
HYPOTHESIS_TEMPLATE = "Dieser Kommentar ist {}."
