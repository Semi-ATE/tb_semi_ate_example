"""
Do **NOT** change anything in this module, as it is automatically generated thus your changes **WILL** be lost in time!
"""

from math import inf, nan
from ate_test_app.sequencers.SequencerBase import SequencerBase
from ate_test_app.sequencers.CommandLineParser import CommandLineParser
from ate_test_app.sequencers.binning.BinStrategyFactory import create_bin_strategy
from ate_test_app.stages_sequence_generator.stages_sequence_generator import StagesSequenceGenerator
from ate_test_app.sequencers.mqtt.MqttConnection import MqttConnection
from ate_test_app.sequencers.harness.HarnessFactory import create_harness

from ate_common.pattern.tool_factory import get_stil_tool

import os
import sys
from pathlib import Path

# setup the include path manually as the project is not a package
parent_path = str(Path(__file__).joinpath('..', '..', '..').resolve())
sys.path.append(parent_path)

from HW0.PR import common
from HW0.HW0_auto_script import AutoScript

if __name__ == '__main__':
    params = CommandLineParser(sys.argv)
    test_program_name = Path(__file__).stem
    bin_table_name = f'{test_program_name}_binning.json'
    bin_table_path = Path(__file__).parent.joinpath(bin_table_name)

    execution_strategy_name = f'{test_program_name}_execution_strategy.json'
    execution_strategy_path = Path(__file__).parent.joinpath(execution_strategy_name)

    execution_strategy = StagesSequenceGenerator(execution_strategy_path)
    bin_strategy = create_bin_strategy(params.bin_strategytype, bin_table_path, test_program_name)

    program_name = os.path.basename(__file__).replace(".py", "")
    sequencer = SequencerBase(program_name, bin_strategy)

    auto_script = AutoScript()
    source = f"TestApp{params.site_id}"

    mqtt = MqttConnection(params)
    output_path = Path(parent_path).parent.joinpath('output')
    output_path.mkdir(exist_ok=True)
    harness_strategy = create_harness(params.harness_strategytype, mqtt.get_mqtt_client(), str(output_path.joinpath(program_name)))
    context = common.make_context(source, params, sequencer, auto_script, execution_strategy, mqtt, harness_strategy)
    auto_script.set_context(context)
    auto_script.set_logger(context.get_logger())
    auto_script.before_start_setup()

    stil_tool = get_stil_tool()
    if hasattr(context.tester, 'stilload') and context.tester.stilload is False:
        pass
    else:
        stil_tool._load_patterns({})

    from HW0.PR.first_bench.first_bench import first_bench
    _ate_var_first_bench_1 = first_bench("first_bench_1", 60000, 100, context, stil_tool)
    _ate_var_first_bench_1.ip.set_parameter('Temperature', 'static', 25, -40.0, 170.0, 0, context, True)
    _ate_var_first_bench_1.op.set_parameter('out', 101, nan, 5.0, 11, 2, 'first_bench_1')
    _ate_var_first_bench_1.op.set_parameter('idd', 102, 7.0, 9.0, 11, 2, 'first_bench_1')
    sequencer.register_test(_ate_var_first_bench_1)
    from HW0.PR.bench_with_inputparameter.bench_with_inputparameter import bench_with_inputparameter
    _ate_var_bench_with_inputparameter_1 = bench_with_inputparameter("bench_with_inputparameter_1", 60001, 200, context, stil_tool)
    _ate_var_bench_with_inputparameter_1.ip.set_parameter('Temperature', 'static', 25, -40.0, 170.0, 0, context, True)
    _ate_var_bench_with_inputparameter_1.ip.set_parameter('vdd', 'static', 0.800, 0.0, 1.0, 0, context, True)
    _ate_var_bench_with_inputparameter_1.op.set_parameter('Vout', 201, nan, nan, 11, 2, 'bench_with_inputparameter_1')
    sequencer.register_test(_ate_var_bench_with_inputparameter_1)

    # Start MQTT using the sequencer.
    # Note that "run()" will
    # only return when the program should terminate.
    context.harness.run()
    context.get_logger().cleanup()