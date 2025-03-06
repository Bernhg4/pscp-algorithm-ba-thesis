class ProgLogfile:
    def __init__(self,start,instance,algorithm):
        self.sa_mode = False
        self.all_current_changes = []
        self.all_current_violations = []
        self.all_temperatures = []
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

    def add_additional_values(self, temperatures, current_changes, current_violations):
        self.all_temperatures.append(temperatures)
        self.all_current_changes.append(current_changes)
        self.all_current_violations.append(current_violations)

    def set_sa(self):
        self.sa_mode = True

    def reduce_points(self, keep_ratio=0.01):

        #Reduce the number of points by merging runs of identical values.
        #If we have n identical consecutive points in the relevant lists,
        #we only keep 5% (or whatever keep_ratio is)

        # new lists for each attribute
        new_timestamps = []
        new_violations = []
        new_changes = []
        # If we are in SA mode, we also reduce these
        new_current_changes = []
        new_current_violations = []

        # Helper function to check if two points (by index) are identical
        # in the relevant lists.  This is the logic that determines a "run"
        def points_are_equal(idx1, idx2):
            same_viol = (self.all_violations[idx1] == self.all_violations[idx2])
            same_chng = (self.all_changes[idx1] == self.all_changes[idx2])

            if self.sa_mode:
                same_cur_chng = (self.all_current_changes[idx1]
                                 == self.all_current_changes[idx2])
                same_cur_viol = (self.all_current_violations[idx1]
                                 == self.all_current_violations[idx2])
                return all([same_viol, same_chng, same_cur_chng, same_cur_viol])
            else:
                return all([same_viol, same_chng])

        n = len(self.all_timestamps)
        if n == 0:
            return  # Nothing to reduce

        # We will iterate over each point, collect runs of identical points,
        #then only keep a fraction of them
        run_start = 0  # start index for the current run

        for i in range(1, n):
            # Check if the current point continues the run of duplicates
            if not points_are_equal(i - 1, i):
                # We have reached the end of a run at i-1
                run_end = i - 1
                run_length = run_end - run_start + 1

                self._save_run(
                    run_start,
                    run_end,
                    keep_ratio,
                    new_timestamps,
                    new_violations,
                    new_changes,
                    new_current_changes,
                    new_current_violations,
                )
                run_start = i

        # After the loop ends, we still have the last run (from run_start to n-1)
        self._save_run(
            run_start,
            n - 1,
            keep_ratio,
            new_timestamps,
            new_violations,
            new_changes,
            new_current_changes,
            new_current_violations,
        )

        # Replace the old lists with the reduced lists
        self.all_timestamps = new_timestamps
        self.all_violations = new_violations
        self.all_changes = new_changes
        if self.sa_mode:
            self.all_current_changes = new_current_changes
            self.all_current_violations = new_current_violations

    def _save_run(
            self,
            start_idx,
            end_idx,
            keep_ratio,
            new_timestamps,
            new_violations,
            new_changes,
            new_current_changes,
            new_current_violations
    ):

        #Given a run of identical points (start_idx .. end_idx),
        #keep 5% of them (or keep_ratio)

        run_length = end_idx - start_idx + 1

        if run_length == 1:
            # Only one point in this run
            new_timestamps.append(self.all_timestamps[start_idx])
            new_violations.append(self.all_violations[start_idx])
            new_changes.append(self.all_changes[start_idx])
            if self.sa_mode:
                new_current_changes.append(self.all_current_changes[start_idx])
                new_current_violations.append(self.all_current_violations[start_idx])
            return

        if run_length > 1000:
            keep_ratio = keep_ratio / 10
        if run_length > 10000:
            keep_ratio = keep_ratio / 10

        # How many points to skip? e.g., if keep_ratio=0.05, skip_factor=20
        skip_factor = int(round(1.0 / keep_ratio))  # 1 / 0.05 = 20

        for i in range(start_idx, end_idx + 1):
            # Option A: Keep the first and last point always
            #           plus every skip_factor-th point in between
            # (This is a common approach to ensure the run boundaries are kept.)
            idx_in_run = i - start_idx
            if (
                    i == start_idx
                    or i == end_idx
                    or (idx_in_run % skip_factor == 0)
            ):
                new_timestamps.append(self.all_timestamps[i])
                new_violations.append(self.all_violations[i])
                new_changes.append(self.all_changes[i])
                if self.sa_mode:
                    new_current_changes.append(self.all_current_changes[i])
                    new_current_violations.append(self.all_current_violations[i])