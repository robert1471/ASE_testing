from ase.calculators.vasp import Vasp
from ase.io import read
import matplotlib.pyplot as plt
import os
import shutil
import ase.dft.kpoints

# --------------------------------------------------------#
#  This module aims to be able to automate calculations  #
#  for my PhD project                                    #
# --------------------------------------------------------#

# Define all possible calculation parameters
systems = ["MnFe2O4", "NiFe2O4", "CuCr2O4", "CuFe2O4"]
inversion = ["inverse", "normal"]
test_names = {"hubbard": [3.5, 4.0, 4.5, 5.0], "k-points": [6, 7, 8], "ecut": [500, 550, 600, 700]}
functionals = ["PBE", "HSE06"]
calculations_types = ["relax", "scf", "bands", "eps"]  # could have parameters for more complex optical calcs


def band_k_path(struct=None, nkpts=20, view_path=False):
    """plots the k-path suggested from Setawayan et al"""
    # get band path
    path = struct.cell.bandpath(npoints=nkpts)

    """if view_path:
        path.plot()
        plt.show()
    return path"""


class VaspCalculations(object):
    def __init__(self, structure, calculations=["scf"], tests=None, output_file="output.out", hubbard_parameters=None):
        self.general_calculation = {"reciprocal": True,
                                    "xc": "PBE",
                                    "setups": 'materialsproject',
                                    "encut": 520,
                                    "kpts": [6, 6, 6],
                                    "ismear": -5,
                                    "sigma": 0.05,
                                    "prec": 'accurate',
                                    "lorbit": 11}

        self.relax = {"ibrion": 2,  # determines how ions are moved and updated (MD or relaxation)
                                  "nsw": 50,  # number of ionic steps
                                  "isif": 3}

        self.scf = {"icharg": 2}

        #self.bands = {"kpts": band_k_path().kpts, "icharg": 11}

        self.eps = {"algo": "exact",
                                "loptics": True,
                                "nbands": "lots",
                                "nedos": 1000}

        self.hse = {"xc": "HSE06"}

        self.hubbard = {"ldau": True,
                                    "ldau_luj": hubbard_parameters,
                                    "ldauprint": 2}

        self.structure = structure
        self.calculations = calculations
        self.output_file = output_file
        self.tests = tests

    def parameter_testing(self, test, values):
        # ------------------------------------------------------------------ #
        #  master function that is used to call all other functions in turn  #
        # ------------------------------------------------------------------ #

        with open(self.output_file, "a+") as out_file:

            out_file.write("-" * 50)
            out_file.write("{} testing with a list of values of {}".format(test, values))

            # define path and check if directory exists
            path_name = "./tests/{}".format(test)

            if not os.path.exists(path_name):
                os.mkdir(path_name)
            os.chdir(path_name)

            out_file.write("Testing calculations running from the directory: {}".format(path_name))

            # list for storage of tested output
            energies = []

            # append the general VASP keywords for the test
            vasp_keywords = self.general_calculation.copy()

            for test_value in values:
                test_path = "./{}".format(test_value)

                if not os.path.exists(test_path):
                    os.mkdir(test_path)
                os.chdir(test_path)

                # statements to find which type of test is being used
                if test == "k-points":
                    test_variable = "kpts"
                    test_value = [test_value, test_value, test_value]
                elif test == "ecut":
                    test_variable = "ecut"
                else:
                    raise ValueError('Error: test requested is not implemented. Please check test argument and try '
                                     'again.')

                # update keywords dictionary to have new test value
                vasp_keywords.update({test_variable: test_value})

                self.structure.set_calculator(Vasp(**vasp_keywords))
                try:
                    energy = self.structure.get_potential_energy()

                except (TypeError, ValueError):
                    print("A VASP error has occurred in test: {} | {}. Please check again".format(test, test_value))
                    energy = 0
                energies.append(energy)
                os.chdir("../")

            out_file.write("{} | Energy")
            out_file.write("-" * 10)
            for value, e in zip(values, energies):
                out_file.write("{} | {}".format(value, energy))

        return energies

    def single_vasp_calculation(self, calculation_type, main_settings, additional_settings, restart=False):
        with open(self.output_file, "w") as vasp_out:
            # defining vasp settings
            vasp_settings = main_settings.copy()
            vasp_settings.update(self.calculation_type)

            if os.path.isfile("OSZICAR"):
                with open("OSZICAR", mode="r") as oszicar_file:
                    shutil.copyfileobj(oszicar_file, vasp_out)


MnFe2O4_structure = read("../Cifs/MnFe2O4-Normal.cif")
MnFe2O4_tests = VaspCalculations(MnFe2O4_structure)

k_test = MnFe2O4_tests.parameter_testing("k-points", [1, 2, 3])

