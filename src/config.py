import configparser

class Config:
    def __init__(self, filepath: str = "config.ini"):
        parser = configparser.ConfigParser()
        parser.read(filepath)
        
        default_weight = float(parser["DEFAULTS"]["WEIGHT"])
        
        try:
            self.header_weight: float = float(parser["WEIGHTS"]["HEADER"])
        except KeyError:
            self.header_weight: float = default_weight
        
        try:
            self.bold_weight: float = float(parser["WEIGHTS"]["BOLD"])
        except KeyError:
            self.bold_weight: float = default_weight
            
        try:
            self.title_weight: float = float(parser["WEIGHTS"]["TITLE"])
        except KeyError:
            self.title_weight: float = default_weight
            
        try:
            self.k_results: int = int(parser["GENERAL"]["KRESULTS"])
        except KeyError:
            self.k_results: int = default_weight