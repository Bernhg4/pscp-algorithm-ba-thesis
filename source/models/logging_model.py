class ProgLogfile:
    def __init__(self,start,instance,algorithm):
        self.start = start
        self.instance = instance
        self.algorithm = algorithm
        self.all_timestamps = []
        self.all_violations = []
        self.all_changes = []

    def __str__(self):
        return f"{self.instance}_{self.algorithm}: [{len(self.all_timestamps)}]"

    def add_point(self,timestamp, violations,changes):
        self.all_timestamps.append(timestamp)
        self.all_violations.append(violations)
        self.all_changes.append(changes)
