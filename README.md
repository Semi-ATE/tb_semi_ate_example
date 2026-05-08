# CURA

This directory contains the test benches and test flows for the CURA project that run under Semi-ATE.
The following projects are supported.
- CURA:
	- CURA 0103		-> HW_ID_BASE = 0x??

<br>
<br>
If a test bench runs stably and is suitable for measurements, it should be included in the flow.

To do this, add the test bench to the ‘production’ group and place it in the correct location in flows/production/CURA_HW0_FT_DummyDevice_production_qdb_flow.

The test must then be described accordingly in the description of the respective test bench. For correct graphical representation later on, [#tags](https://semi-ate.github.io/Semi-ATE/buildtool/scripts.html) must be used as described in [Semi-ATE](https://semi-ate.github.io/Semi-ATE/buildtool/scripts.html).

Current flow for QDB returns as [pdf](./CURA/doc/CURA_HW0_FT_Device1_production_qdb_flow.pdf)

![Aktueller Flow](./CURA/doc/H_HW0_FT_Device1_production_qdb_flow.png)

<br>
<br>

# If you encounter problems, check the following:
- Does the pinout of your device match the load board?
- Is the correct interface board connected?
- Is the relay matrix switching correctly?
- Are the signals reaching the device? Check [protocol](./docu/protocols/readme.md).