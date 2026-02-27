class Document:
    def __init__(self, nom, type_fichier, chemin, proprietaire):
        self.nom          = nom
        self.type_fichier = type_fichier   # docx, pptx, pdf
        self.chemin       = chemin
        self.proprietaire = proprietaire

class Conversion:
    def __init__(self, id_document, type_source, type_cible, chemin_resultat):
        self.id_document    = id_document
        self.type_source    = type_source   # docx, pptx
        self.type_cible     = type_cible    # pdf
        self.chemin_resultat = chemin_resultat

class Signature:
    def __init__(self, id_document, signataire, date_signature, chemin_signe):
        self.id_document    = id_document
        self.signataire     = signataire
        self.date_signature = date_signature
        self.chemin_signe   = chemin_signe