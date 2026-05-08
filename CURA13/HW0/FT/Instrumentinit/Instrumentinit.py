#!/usr/bin/env conda run -n ATE python
# -*- coding: utf-8 -*-
"""
By jung
"""

import os
import sys
from pathlib import Path
test_path = os.path.abspath(Path(__file__).joinpath('..'))
sys.path.append(test_path)

from harness.tp_tasks import TP_tasks
from Instrumentinit_BC import Instrumentinit_BC


class Instrumentinit(Instrumentinit_BC):

    '''
    for debug puposes, a logger is available to log information and propagate them to the UI.
    logging can be used as described below:
    self.log_info(<message>)
    self.log_debug(<message>)
    self.log_warning(<message>)
    self.log_error(<message>)
    self.log_measure(<message>)

    <do_not_touch>
    Init the necessary instruments to the default values

    Input Parameter | Shmoo | Min | Default | Max | Unit | fmt
    ----------------+-------+-----+---------+-----+------+----
    ip.Temperature  |  Yes  | -40 |   25    | 170 | °C   | .0f

    Parameter         | MPR | LSL |   (LTL) |  Nom  | (UTL)   | USL  | Unit | fmt
    ------------------+-----+-----+---------+-------+---------+------+------+----
    op.result         | No  |  -∞ |   0.000 | 0.000 | 0.000   | +∞   | ˽    | .3f
    op.temperature    | No  |  -∞ | -45.000 | 0.000 | 170.000 | +∞   | ˽    | .3f
    </do_not_touch>

    '''

    def do(self):
        """Default implementation for test."""
        self.context.tptasks_instance = TP_tasks(self, "tptasks")
        if hasattr(self.context, 'SemiCtrl_Control_instance'):
            self.context.SemiCtrl_Control_instance.init(self)      # call workaround for breakpoints and define the shortnames

        self.regs._interface = self.tester.interface
        if self.regs.filename is None:
            self.regs.filename = os.getcwd() + '/../harness/' + os.getenv("REGISTERMASTER")
            self.regs.init()

        # self.regs.reset_regs(default=0)
        self.regs.reset_regs()
        self.logger.set_logger_level(15)

        self.setup.initialization(self)  # use workarea/harness/tb_projectsetup.json for initializing the instrument to their init values

        # tcc.interface.debug = True

        # Todo: umschaltung von Power HALAPB auf SMU machen (switchover, wie querstroeme vermeiden? wie in matlab?)
        # tcc.smu.onoff = 1
        # tcc.smu.voltage = 5
        # tcc.smu1.onoff = 0

        self.regs.use = "tlm" if hasattr(self.tester.interface, 'tlm') else 'biph'

        self.tester.thermo.head = 'down'
        self.tester.thermo.flow = 'on'
        temperature = self.tester.thermo.temp

        self.log_info("InstrumentInit done")
        self.op.result.write(0)
        self.op.temperature.write(temperature)
