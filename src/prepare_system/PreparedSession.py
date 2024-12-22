class PreparedSession():
    def __init__(self, features,UUID):
        self.UUID = UUID
        self.label = features[6]  #modificare
        self.mean_abs_diff_ts = features[0]
        self.mean_abs_diff_am = features[1]
        self.median_long = features[2]
        self.median_lat = features[3]
        self.median_targetIP = features[4]
        self.median_destIP = features[5]

    def to_dict(self):
        return {
            "UUID": self.UUID,
            "label": self.label,
            "mean_abs_diff_ts": float(self.mean_abs_diff_ts),
            "mean_abs_diff_am": float(self.mean_abs_diff_am),
            "median_long": float(self.median_long),
            "median_lat": float(self.median_lat),
            "median_targetIP": self.median_targetIP,
            "median_destIP": self.median_destIP
        }