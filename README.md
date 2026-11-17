# 30Sekunden: Kommentar-Klassifikation

NLP-Inference-Service, der Leserkommentare der Online-Zeitung *30Sekunden* mit einer
Zero-Shot-Classification-Pipeline (`facebook/bart-large-mnli`) in Kategorien einteilt.
Anfragen werden per Microbatching gesammelt, Metriken über Prometheus bereitgestellt
und in Grafana visualisiert.
