#!/usr/bin/env conda run -n ATE python
# -*- coding: utf-8 -*-
"""
By jung (jung@micronas.com)
"""

import os
import sys
from pathlib import Path
test_path = os.path.abspath(Path(__file__).joinpath('..'))
sys.path.append(test_path)

from bench_with_inputparameter_BC import bench_with_inputparameter_BC


class bench_with_inputparameter(bench_with_inputparameter_BC):

    '''
    for debug puposes, a logger is available to log information and propagate them to the UI.
    logging can be used as described below:
    self.log_info(<message>)
    self.log_debug(<message>)
    self.log_warning(<message>)
    self.log_error(<message>)
    self.log_measure(<message>)

    <do_not_touch>
    This is a example with some input parameter, and how you get acess to the values.

    Input Parameter | Shmoo |   Min | Default | Max   | Unit | fmt
    ----------------+-------+-------+---------+-------+------+----
    ip.Temperature  |  Yes  |   -40 |   25    | 170   | °C   | .0f
    ip.vdd          |  Yes  | 0.000 |  0.800  | 1.000 | ˽    | .3f

    Parameter         | MPR | LSL | (LTL) |  Nom  | (UTL) | USL  | Unit | fmt
    ------------------+-----+-----+-------+-------+-------+------+------+----
    op.Vout           | No  |  -∞ |  (-∞) | 0.000 | (+∞)  | +∞   | ˽    | .3f
    </do_not_touch>

    '''

    def do(self):
        """Default implementation for test."""
        if hasattr(self.context, 'SemiCtrl_Control_instance'):
            self.context.SemiCtrl_Control_instance.init(self)      # call workaround for breakpoints and define the shortnames

        self.log_info('running the Test "bench_with_input": ')
        self.log_info(f'        Temperature = {self.ip.Temperature._value} ')
        self.log_info(f'        vdd = {self.ip.vdd._value} ')

        Vout = -0.002 * self.ip.Temperature._value + self.ip.vdd._value / 10
        self.log_info(f'        -> Vout = {Vout} ')

        self.op.Vout.write(Vout)

