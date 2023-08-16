from .suite import Suite
from .lake_cleaner_experiment import LakeCleanerExperiment


class LakeCleanerSuite(Suite):
    def __init__(self, dataset_name: str, error_generator: int = 0):
        super().__init__("LakeCleaner", "error_correction", dataset_name, error_generator)
        self.suppress_plotting = True

    def run(self,
            max_error_rate: float,
            min_error_rate: float = 0.1, 
            error_step_size: float = 0.1, 
            runs_per_error_rate: int = 5, 
            error_intervals: int = 0, 
            **kwargs):
        experiment = LakeCleanerExperiment(0.1, "LakeCleaner", "data-gov-sandbox")
        experiment.run()
        self.results = experiment.result()
        return self