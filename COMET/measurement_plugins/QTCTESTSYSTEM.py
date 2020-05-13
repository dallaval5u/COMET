# This file conducts a full test on the KIT Test Card nearly automatically

import logging
import sys
sys.path.append('../COMET')
from time import time, sleep
from ..utilities import transformation
from .forge_tools import tools

class QTCTESTSYSTEM_class(tools):

    def __init__(self, main_class):
        """
        This class can conduct a stripscan. Furthermore, it is baseclass for shortend stripscan measurements like
        singlestrip and freqquencyscan. These measurements, in principal do the same like stripscan but only on one
        strip. Therefore, we can derive.

        :param main_class:
        """
        self.main = main_class
        super(QTCTESTSYSTEM_class, self).__init__(self.main.framework, self.main)
        self.log = logging.getLogger(__name__)

        # Aux. classes
        self.trans = transformation()
        self.vcw = self.main.framework["VCW"]
        self.switching = self.main.switching

        # These are generall parameters which can either be changed here or in the settings in the optional parameter seen above
        self.device_configs = {
            # Devices Configs
            "BiasSMU": "BiasSMU",
            "LCRMeter": "LCRMeter",
            "DischargeSMU": "2410SMU",
            "Switching": "temphum_controller",
            "Elmeter": "Elektrometer",
            "SMU2": "2410SMU",

            # Commands Configs
            "Discharge": ("set_terminal", "FRONT"),
            "OutputON": ("set_output", "1"),
            "OutputOFF": ("set_output", "0"),
            "GetReadSMU": "get_read",  # This read can be a single current read or current, voltage pair
            "GetReadLCR": "get_read",
            "GetReadSMU2": "get_read",
            "GetReadElmeter": "get_read",

            # General Configs for the measurement
            "BaseConfig": [],
            "IstripConfig": [],
            "IdielConfig": [],
            "IdarkConfig": [],
            "RpolyConfig": [],
            "RintConfig": [],
            "CacConfig": [],
            "CintConfig": [],

        }

        self.log.info("Acquiring devices for QTC test measurements...")
        self.discharge_SMU = None
        self.bias_SMU = None
        self.LCR_meter = None
        self.discharge_switching = None
        self.elmeter = None
        self.SMU2 = None
        try:
            self.bias_SMU = self.main.devices[self.device_configs["BiasSMU"]]
            self.LCR_meter = self.main.devices[self.device_configs["LCRMeter"]]
            self.discharge_SMU = self.main.devices[self.device_configs["DischargeSMU"]]
            self.elmeter = self.main.devices[self.device_configs["Elmeter"]]
            self.SMU2 = self.main.devices[self.device_configs["SMU2"]]
            self.discharge_switching = self.main.devices[self.device_configs["Switching"]]
        except KeyError as valErr:
            self.log.critical(
                "One or more devices could not be found for the QTC test measurements. Error: {}".format(valErr))

        # Misc.
        self.job = self.main.job_details
        self.sensor_pad_data = self.main.framework["Configs"]["additional_files"]["Pad_files"]["KIT_probecard"]["CARD"]
        self.height = 5000 # 5 mm height movement
        self.samples = 1000 # The amount of samples each measurement must have
        self.T = self.main.framework['Configs']['config']['settings']["trans_matrix"]
        self.V0 = self.main.framework['Configs']['config']['settings']["V0"]
        self.justlength = 24
        self.project = self.main.job_details["Project"]
        self.sensor = self.main.job_details["Sensor"]
        self.current_voltage = self.main.framework['Configs']['config']['settings'].get("bias_voltage", 0)
        self.cal_to = {"Cac": 1000, "Cac_beta": 1000, "Cint": 1000000, "Cint_beta": 1000000} # Hz
        self.open_corrections = {}

        # Varaibels for testsystem and GUI
        self.main.framework['Configs']['config']['settings']["QTC_test"] = {}
        self.main.framework['Configs']['config']['settings']["QTC_test"]['proceed'] = False
        self.main.framework['Configs']['config']['settings']["QTC_test"]['text'] = "This is the QTC test, init text"
        self.main.framework['Configs']['config']['settings']["QTC_test"]['currenttest'] = "None"

        if "Rint_MinMax" not in self.main.framework['Configs']['config']['settings']:
            self.main.framework['Configs']['config']['settings']["Rint_MinMax"] = [-1.,1.,0.1]
            self.log.warning("No Rint boundaries given, defaulting to [-1.,1.,0.1]. Consider adding it to your settings")

        # Check if alignment is present or not, if not stop measurement
        if not self.main.framework['Configs']['config']['settings']["Alignment"]:
            self.log.error("Alignment is missing. Only non table critical measurements will be conducted!")
            self.validalignment = False
        else:
            self.validalignment = True

        self.log = logging.getLogger(__name__)
        self.main.queue_to_main.put({"INFO": "Initialization of Setup test finished."})


    def run(self):
        """Does all the testing"""

        # Do device empty tests - Do switching uncontacted and do self.samples measurements
        self.empty_measurements()

        # Do the probe card measurements - Contact the probe card and measurer the KIT resistors and capacitors
        if self.validalignment:
            self.test_card_measurements()

        # Save the data to an ASCII/JSON file
        self.save_results()

    def empty_measurements(self):
        """Does the device empty measurement. It switches to the measurement and then takes samples. The card is
        not contacted at this time"""
        pass

    def test_card_measurements(self):
        """Does the KIT test card measurements. It switches either to Rpoly, Cac, or Cint and conducts the measuremnt
        on the card. Each measurement will be repeated self.samples times and the table will recontact every time."""
        pass

    def save_results(self):
        """Saves everything to a file"""

    def stop_everything(self):
        """Stops the measurement
        A signal will be genereated and send to the event loops, which sets the statemachine to stop all measurements"""
        self.main.queue_to_main.put({"Warning": "Stop QTC test was called..."})
        order = {"ABORT_MEASUREMENT": True}  # just for now
        self.main.queue_to_main.put(order)
        self.log.warning("Measurement STOP was called, check logs for more information")
