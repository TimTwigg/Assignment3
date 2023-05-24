import configparser

class Config:
    def __init__(self, filepath: str = "config.ini"):
        parser = configparser.ConfigParser()
        parser.read(filepath)
        
        default_weight = parser["DEFAULTS"]["WEIGHT"]
        
        try:
            self.header_weight = parser["WEIGHTS"]["HEADER"]
        except KeyError:
            self.header_weight = default_weight
        
        try:
            self.bold_weight = parser["WEIGHTS"]["BOLD"]
        except KeyError:
            self.bold_weight = default_weight
            
        try:
            self.title_weight = parser["WEIGHTS"]["TITLE"]
        except KeyError:
            self.title_weight = default_weight
            
        try:
            self.k_results = parser["GENERAL"]["KRESULTS"]
        except KeyError:
            self.k_results - default_weight