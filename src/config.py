import configparser

class Config:
    def __init__(self, filepath: str = "config.ini"):
        parser = configparser.ConfigParser()
        parser.read(filepath)
        
        self.header_weight: float = float(parser["WEIGHTS"]["HEADER"])
        self.bold_weight: float = float(parser["WEIGHTS"]["BOLD"])
        self.title_weight: float = float(parser["WEIGHTS"]["TITLE"])
        self.cosine_similarity: float = float(parser["WEIGHTS"]["COSINE_SIMILARITY"])
        self.alpha: float = float(parser["WEIGHTS"]["ALPHA"])
        self.sim_thresh: float = float(parser["GENERAL"]["SIM_THRESH"])
        self.k_results: int = int(parser["GENERAL"]["KRESULTS"])
        self.r_docs: int = int(parser["GENERAL"]["RDOCS"])