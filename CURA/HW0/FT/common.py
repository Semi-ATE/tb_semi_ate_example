# -*- coding: utf-8 -*-
"""
HW0/FT/common.py


Don't edit this file. It is bound to be regenerated if the project
configuration changes. Any manual edits will be lost in that case.
"""
import json
import os
import sys
import pathlib
import traceback
from ate_test_app.sequencers.Sequencer import Sequencer
from ate_test_app.sequencers.SequencerBase import SequencerBase
from ate_test_app.auto_script.AutoScriptBase import AutoScriptBase
from ate_test_app.sequencers import Harness
from ate_test_app.stages_sequence_generator.stages_sequence_generator import StagesSequenceGenerator
from ate_test_app.sequencers.mqtt.MqttConnection import MqttConnection
from ate_semiateplugins.pluginmanager import get_plugin_manager
from ate_common.logger import Logger, LogLevel


class Context:
    def __init__(
        self,
        source: str,
        params: dict,
        sequencer: SequencerBase,
        auto_script: AutoScriptBase,
        execution_strategy: StagesSequenceGenerator,
        mqtt: MqttConnection,
        harness_strategy: Harness):
        self.harness = Sequencer(sequencer, params, execution_strategy, mqtt, harness_strategy)
        self.logger = Logger(source, self.harness)

        # Logging is available @ Info Level during startup of the
        # sequencer. After the C'tor has finished, we automatically
        # revert to "Warrning"
        self.logger.set_logger_level(LogLevel.Info)
        try:
            self.auto_script = auto_script
            self.harness.set_after_terminate_callback(lambda: self.auto_script.after_terminate_teardown())
            self.harness.set_logger(self.logger)
            sequencer.set_logger(self.logger)
            sequencer.set_auto_script(self.auto_script)

            # Tester
            testers = get_plugin_manager().hook.get_tester(tester_name="Semi_ATE File configuration Tester", logger=self.logger)
            assert len(testers) < 2, "The testertype Semi_ATE File configuration Tester maps to multiple testers. Check installed plugins."
            assert len(testers) == 1, "The testertype Semi_ATE File configuration Tester is not available or installed on this machine."

            from semi_ate_testers.testers.file_configuration_tester import FileConfigurationTester
            self.tester: FileConfigurationTester = testers[0]
            sequencer.set_tester_instance(self.tester)

            from ate_test_app.actuators.Temperature.Temperature import TemperatureProxy
            self.Temperature_instance = TemperatureProxy()
            self.Temperature_instance.set_mqtt_client(self.harness)
            from ate_test_app.actuators.Magnetic_Field.Magnetic_Field import Magnetic_FieldProxy
            self.Magnetic_Field_instance = Magnetic_FieldProxy()
            self.Magnetic_Field_instance.set_mqtt_client(self.harness)

            self.setup_plugins(self.logger)
        except Exception as e:
            exc = traceback.format_exc()
            self.logger.log_message(LogLevel.Error, exc)
            # Exceptions in this stage are per definition fatal
            sys.exit()

        self.logger.set_logger_level(LogLevel.Warning)

    def setup_plugins(self, logger: Logger):
        instrument_dict = {}
        instruments = get_plugin_manager().hook.get_instrument(instrument_name="SemiCtrl.Control", logger=logger)
        assert len(instruments) < 2, "The instrumenttype SemiCtrl.Control maps to multiple instruments. Check installed plugins."
        assert len(instruments) == 1, "The instrumenttype SemiCtrl.Control is not available or installed on this machine."
        self.SemiCtrl_Control_instance = instruments[0]
        instrument_dict['SemiCtrl.Control'] = self.SemiCtrl_Control_instance

        apply_configuration(instrument_dict)

        self.gp_dict = {}
        gpfuncs = get_plugin_manager().hook.get_general_purpose_function(func_name="Pylab_Ml.Setup", logger=logger)
        assert len(gpfuncs) < 2, "The functiontype Pylab_Ml.Setup maps to multiple functions. Check installed plugins."
        assert len(gpfuncs) == 1, "The functiontype Pylab_Ml.Setup is not available or installed on this machine."
        self.Pylab_Ml_Setup_instance = gpfuncs[0]
        self.gp_dict['Pylab_Ml.Setup'] = self.Pylab_Ml_Setup_instance
        gpfuncs = get_plugin_manager().hook.get_general_purpose_function(func_name="Pylab_Ml.Registermaster", logger=logger)
        assert len(gpfuncs) < 2, "The functiontype Pylab_Ml.Registermaster maps to multiple functions. Check installed plugins."
        assert len(gpfuncs) == 1, "The functiontype Pylab_Ml.Registermaster is not available or installed on this machine."
        self.Pylab_Ml_Registermaster_instance = gpfuncs[0]
        self.gp_dict['Pylab_Ml.Registermaster'] = self.Pylab_Ml_Registermaster_instance

        apply_configuration(self.gp_dict)

    def get_logger(self) -> Logger:
        return self.logger

    def after_exception_callback(self, source: str, error: Exception):
        self.auto_script.after_exception_teardown(source, error)

    def after_cycle_callback(self):
        self.auto_script.after_cycle_teardown()


def apply_configuration(feature_dict):
    from pathlib import Path
    for name, instance in feature_dict.items():
        config_file_path = Path(__file__).parent.joinpath("..", f"{name}.json")
        configuration = {}
        if config_file_path.exists():
            with open(config_file_path) as reader:
                configuration = json.loads(reader.read())

        instance.apply_configuration(configuration)


def make_context(
    source: str,
    params: dict,
    sequencer: SequencerBase,
    auto_script: AutoScriptBase,
    execution_strategy: StagesSequenceGenerator,
    mqtt: MqttConnection,
    harness_strategy: Harness
    ) -> Context:
    return Context(source, params, sequencer, auto_script, execution_strategy, mqtt, harness_strategy)