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

from first_bench_BC import first_bench_BC


class first_bench(first_bench_BC):

    '''
    for debug puposes, a logger is available to log information and propagate them to the UI.
    logging can be used as described below:
    self.log_info(<message>)
    self.log_debug(<message>)
    self.log_warning(<message>)
    self.log_error(<message>)
    self.log_measure(<message>)

    <do_not_touch>
    This is a example for a testbench.

    Input Parameter | Shmoo | Min | Default | Max | Unit | fmt
    ----------------+-------+-----+---------+-----+------+----
    ip.Temperature  |  Yes  | -40 |   25    | 170 | °C   | .0f

    Parameter         | MPR |   LSL | (LTL) |  Nom  | (UTL) | USL    | Unit | fmt
    ------------------+-----+-------+-------+-------+-------+--------+------+----
    op.out            | No  |    -∞ |  (-∞) | 0.000 | 5.000 | +∞     | ˽    | .3f
    op.idd            | No  | 6.000 | 7.000 | 8.000 | 9.000 | 10.000 | ˽    | .3f
    </do_not_touch>

    '''

    def do(self):
        """Default implementation for test."""
        if hasattr(self.context, 'SemiCtrl_Control_instance'):
            self.context.SemiCtrl_Control_instance.init(self)      # call workaround for breakpoints and define the shortnames

        self.log_info('running first test')

        self.op.out.default()       # write the nominal value
        self.op.idd.write(8.0)      # write the measured value, if the value outside the Limits, than the test will faile
