import statistics

class ResultSto:
    def __init__(self,algorithm, instance, method):
        self.stddev_tuple = ()
        self.results = []
        self.algorithm = algorithm
        self.instance = instance
        self.method = method

    def __str__(self):
        res = self.get_result()
        return f"{self.algorithm}: {self.instance} - ({res[0]}/{res[1]}) {res[2]} s"

    def add_result(self, new_result):
        self.results.append(new_result)

    def get_stand_dev(self):
        return self.stddev_tuple

    def get_best_result(self):

        best_res = min(self.results, key=lambda x: (x[0], x[1]))
        best_tuple = (best_res[0], best_res[1], best_res[2])

        return best_tuple

    def get_result(self):
        # Separate the elements of the tuples
        demand_violations = [x[0] for x in self.results]
        color_changes = [x[1] for x in self.results]
        time_seconds = [x[2] for x in self.results]

        # Calculate the average for each position
        average_violations = round(statistics.mean(demand_violations),2)
        average_changes = round(statistics.mean(color_changes),2)
        average_time = round(statistics.mean(time_seconds),3)

        # Calculate the standard deviation for each position
        stddev_violations = round(statistics.stdev(demand_violations),2)
        stddev_changes = round(statistics.stdev(color_changes),2)
        stddev_time = round(statistics.stdev(time_seconds),3)

        # Display the results
        average_tuple = (average_violations, average_changes, average_time)
        self.stddev_tuple = (stddev_violations, stddev_changes, stddev_time)

        #print("Average:", average_tuple)
        #print("Standard Deviation:", stddev_tuple)

        return average_tuple

class ResultDet:
    def __init__(self,new_result,algorithm, instance, method):
        self.result = new_result
        self.algorithm = algorithm
        self.instance = instance
        self.method = method

    def __str__(self):
        res = self.get_result()
        return f"{self.algorithm}: {self.instance} - ({res[0]}/{res[1]}) {res[2]} s"

    def get_result(self):
        return self.result[0], self.result[1], round(self.result[2], 3)

    def get_best_result(self):
        return self.get_result()