import os
import time
from typing import Tuple, Dict, Any
from multiprocessing import Process
from methods.garf_original.main import main as garf_original
from .experiment import Experiment
from insert_error import insert_error_original, insert_error, insert_errors_bart, BART, ORIGINAL, DETECTION
from eva import evaluate_original, evaluate, evaluate_detection


class GARFExperiment(Experiment):
    def __init__(self, error_rate: float, method_name: str, dataset: str, error_generator: int = 1):
        super().__init__(error_rate, method_name, dataset, error_generator)
        self.base_dir = os.path.join(os.getcwd(), "methods", "garf_original")

    def run(self, **kwargs):
        path = f"{self.dataset}_copy"
        path_ori = path.strip('_copy')
        # insert errors
        if self.error_generator == ORIGINAL:
            insert_error_original(path_ori, path, self.error_rate, self.base_dir)
            errors = None
        elif self.error_generator == BART:
            errors = insert_errors_bart(path_ori, path, self.base_dir)
        else:
            errors = insert_error(path_ori, path, self.error_rate, self.base_dir)
            
        
        g_h = kwargs["g_h"] if "g_h" in kwargs else 64
        g_e = kwargs["g_e"] if "g_e" in kwargs else 64
        
        remove_amount_of_error_tuples = kwargs["remove_amount_of_error_tuples"]
        start_time = time.time()
        process_kwargs = {
            "flag": 2, 
            "order": 1, 
            "remove_amount_of_error_tuples": remove_amount_of_error_tuples, 
            "dataset": self.dataset,
            "g_h": g_h,
            "g_e": g_e,
        }
        process = Process(target=self.worker, args=(process_kwargs,))
        process.start()
        process.join()
        
        process_kwargs["order"] = 0
        del process_kwargs["remove_amount_of_error_tuples"]
        
        process = Process(target=self.worker, args=(process_kwargs,))
        process.start()
        process.join()
        end_time = time.time()
        
        if self.error_generator == ORIGINAL:
            precision, recall, f1 = evaluate_original(path_ori, path, self.base_dir)
        elif self.error_generator == DETECTION:
            precision, recall, f1 = evaluate_detection(path_ori, path, self.base_dir, errors)
        else:
            precision, recall, f1 = evaluate(path_ori, path, self.base_dir, errors)
            
        print(f"The complete runtime of this fix is {end_time - start_time} Error rate is {self.error_rate}")
        self.precision = precision
        self.recall = recall
        self.f1 = f1
        self.runtime = end_time - start_time
        return self
    
    @staticmethod
    def worker(kwargs: Dict[str, Any] = dict()):
        if "flag" not in kwargs:
            raise ValueError("Flag is not set")
        if "order" not in kwargs:
            raise ValueError("Order is not set")
        if "dataset" not in kwargs:
            raise ValueError("Dataset is not set")
        remove_amount_of_error_tuples = 0
        if "remove_amount_of_error_tuples" in kwargs:
            remove_amount_of_error_tuples = kwargs["remove_amount_of_error_tuples"]
        flag = kwargs["flag"]
        order = kwargs["order"]
        dataset = kwargs["dataset"]
        g_h = kwargs["g_h"] if "g_h" in kwargs else 64
        g_e = kwargs["g_e"] if "g_e" in kwargs else 64
        
        os.chdir(os.path.join(os.getcwd(), "methods", "garf_original"))
        garf_original(flag, order, remove_amount_of_error_tuples, dataset, g_h, g_e)
        
    def result(self) -> Tuple[float, float, float, float]:
        return self.precision, self.recall, self.f1, self.runtime
