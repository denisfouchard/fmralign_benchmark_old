from benchopt import BaseDataset, safe_import_context


# Protect the import with `safe_import_context()`. This allows:
# - skipping import to speed up autocompletion in CLI.
# - getting requirements info when all dependencies are not installed.
with safe_import_context() as import_ctx:
    from benchmark_utils.config import DATA_PATH_NEUROMOD, MEMORY
    from pathlib import Path
    from nilearn import masking, maskers, image
    import pandas as pd


# All datasets must be named `Dataset` and inherit from `BaseDataset`
class Dataset(BaseDataset):
    # Name to select the dataset in the CLI and to display the results.
    name = "Neuromod"

    # List of parameters to generate the datasets. The benchmark will consider
    # the cross product for each key in the dictionary.
    # Any parameters 'param' defined here is available as `self.param`.
    parameters = {
        "target": [
            "sub-01",
            "sub-02",
            "sub-03",
            "sub-05",
        ],
    }

    # List of packages needed to run the dataset. See the corresponding
    # section in objective.py
    install_cmd = "conda"
    requirements = ["nilearn", "pandas"]

    def __init__(self):
        self.subjects = [
            "sub-01",
            "sub-02",
            "sub-03",
            "sub-05",
        ]

    def load_neuromod(self, subject, data_path):
        alignment_contrasts = image.load_img(
            data_path
            / "3mm"
            / (
                f"{subject}_task-life_space-"
                "MNI152NLin2009cAsym_desc-postproc_bold.nii.gz"
            )
        )
        decoding_contrasts = image.load_img(
            data_path / "3mm" / f"{subject}.nii.gz"
        )
        labels = pd.read_csv(
            data_path / "3mm" / f"{subject}_labels.csv",
            header=None,
        ).values.ravel()
        return alignment_contrasts, decoding_contrasts, labels

    def get_data(self):
        # The return arguments of this function are passed as keyword arguments
        # to `Objective.set_data`. This defines the benchmark's
        # API to pass data. It is customizable for each benchmark.
        data_path = Path(DATA_PATH_NEUROMOD)

        # Create a masker to extract the data from the brain volume.
        masker_path = data_path / (
            "tpl-MNI152NLin2009cAsym_res-3mm_"
            "label-GM_desc-thr02_probseg.nii.gz"
        )
        connected_mask = masking.compute_background_mask(
            masker_path, connected=True
        )
        mask = maskers.NiftiMasker(connected_mask, memory=MEMORY).fit()

        dict_alignment = dict()
        dict_decoding = dict()
        dict_labels = dict()
        for subject in self.subjects:
            (
                alignment_contrasts,
                decoding_contrasts,
                labels,
            ) = self.load_neuromod(subject, data_path)
            dict_labels[subject] = labels

            if subject == self.target:
                data_alignment_target = alignment_contrasts
                data_decoding_target = decoding_contrasts
            else:
                dict_alignment[subject] = alignment_contrasts
                dict_decoding[subject] = decoding_contrasts

        # The dictionary defines the keyword arguments for `Objective.set_data`
        return dict(
            dict_alignment=dict_alignment,
            dict_decoding=dict_decoding,
            data_alignment_target=data_alignment_target,
            data_decoding_target=data_decoding_target,
            dict_labels=dict_labels,
            target=self.target,
            mask=mask,
        )
