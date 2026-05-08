# -*- coding: utf-8 -*-
"""
  Environment for DT2207031
  Labor QDB-Messplatz

  smu reset:
     self calibration and SINGLE_POINT is default
     settings for all channels: current_limit_autorange=True, voltage_limit_autorange=True,
     power_line_frequency = 50.0, aperture_time_units=POWER_LINE_CYCLES, aperture_time=2,
     auto_zero=OFF, dc_noise_rejection=SECOND_ORDER
"""
import os
from pylab_ml.misc.project_info import Project_Info
from pylab_ml.collate_instrument import Interface
from pylab_ml.base_instrument import mqttclose, logger
from pylab_ml.smu.natinst.pxie41xx import PXIe41xx
from pylab_ml.dmm.natinst.pxie40xx import PXIe40xx
from pylab_ml.scope.natinst.pxie51xx import PXIe51xx
from pylab_ml.matrix.pickering.pickering_40_5xx import Pickering_40_5xx
from pylab_ml.thermostreamer.mpi_ta5k import MPI_TA5K
from pylab_ml.base_instrument import createDummyifInvalid

# TDK-Micronas library
from labml_instruments.boards.micronas.teensy_loadmatrix import LoadMatrix
from labml_instruments.coil.dcs6k import DCS6k
from labml_instruments.coil.coil_3a import Coil
from labml_instruments.matrix.qdbmatrix import QDBMatrix
from labml_instruments.boards.micronas.communication.apbboard import HALAPBBoard
from labml_instruments.boards.micronas.communication.stiboard import STIBoard
from labml_instruments.others.rc_motor import Motor

name = 'PXIe System'
stilload = False
run_pattern = -1
project_info = Project_Info(__file__)

# createDummyifInvalid(True)               # create Dummy-instance if instrument not found -> no exception will occure
logger.info("Config Instruments with file {}".format(__file__))

interface = HALAPBBoard(addr=12, instName="interface")

matrix = QDBMatrix(addr=18, instName='matrix')

smu = PXIe41xx(addr="PXI1Slot2", instName="smu")  # PXie-4138
smu1 = PXIe41xx(addr='PXI1Slot3', instName='smu1')                        # PXie-4138
# smu2 = PXIe41xx(addr='PXI2Slot2', instName='smu2', channels='0,1,2,3')  # PXie-4141
dmm = PXIe40xx(addr="PXI1Slot5", instName="dmm")  # PXie-4081
# scope = PXIe51xx(addr="PXI1Slot4", instName="scope")

# loadmat = LoadMatrix(instName='loadmat')
thermo = MPI_TA5K(addr=2, interface=Interface.gpib, instName='thermo')   # if not avaiable use instead dummy thermostreamer

# coilsupply = DCS6k("521B18340004", maxCurrent=3.0, maxVoltage=50.0, instName="coilsupply")
# coil = Coil(coilsupply, CalPoly=(0.015473, 0.009612, 20.642873, 0.070134), instName="coil")  # ask Mario Morantz for the latest Polynom
# coilm = Motor(addr=20, debug=True, instName='coilm')
# if coilm.id == 'no instance':
#     logger.warning('no revolution speed manipulator found!')

logger.info(f"Instrument Device {os.environ.get('Computername')} configuration done")
