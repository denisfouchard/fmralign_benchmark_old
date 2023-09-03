from benchopt import BaseSolver, safe_import_context

# Protect the import with `safe_import_context()`. This allows:
# - skipping import to speed up autocompletion in CLI.
# - getting requirements info when all dependencies are not installed.
with safe_import_context() as import_ctx:
    from benchopt.stopping_criterion import SingleRunCriterion
    from fmralign.pairwise_alignment import PairwiseAlignment
    from fmralign.alignment_methods import OptimalTransportAlignment
    from joblib import Memory


# The benchmark solvers must be named `Solver` and
# inherit from `BaseSolver` for `benchopt` to work properly.
class Solver(BaseSolver):

    # Name to select the solver in the CLI and to display the results.
    name = 'ot'

    # List of parameters for the solver. The benchmark will consider
    # the cross product for each key in the dictionary.
    # All parameters 'p' defined here are available as 'self.p'.
    parameters = {
        'n_pieces': [300],
        'reg': [0.1],
    }

    # List of packages needed to run the solver. See the corresponding
    # section in objective.py
    requirements = ['fmralign', 'joblib']
    
    stopping_criterion = SingleRunCriterion()

    def set_objective(self, dict_alignment, data_alignment_target, mask):
        # Define the information received by each solver from the objective.
        # The arguments of this function are the results of the
        # `Objective.get_objective`. This defines the benchmark's API for
        # passing the objective to the solver.
        # It is customizable for each benchmark.
        self.dict_alignment = dict_alignment
        self.data_alignment_target = data_alignment_target
        self.mask = mask

    def run(self, n_iter):
        # This is the function that is called to evaluate the solver.
        # It runs the algorithm for a given a number of iterations `n_iter`.
        # You can also use a `tolerance` or a `callback`, as described in
        # https://benchopt.github.io/performance_curves.html
        
        dict_alignment_estimators = dict()
        for subject in self.dict_alignment.keys():
            source_data = self.dict_alignment[subject]
            
            pairwise_method = OptimalTransportAlignment(reg=self.reg)
            alignment_estimator = PairwiseAlignment(
                alignment_method=pairwise_method,
                n_pieces=self.n_pieces,
                mask=self.mask,
                memory=Memory(),
                memory_level=1,
            ).fit(source_data, self.data_alignment_target)
                
            dict_alignment_estimators[subject] = alignment_estimator
            
        self.dict_alignment_estimators = dict_alignment_estimators
                

    def get_result(self):
        # Return the result from one optimization run.
        # The outputs of this function is a dictionary which defines the
        # keyword arguments for `Objective.evaluate_result`
        # This defines the benchmark's API for solvers' results.
        # it is customizable for each benchmark.
        return self.dict_alignment_estimators
