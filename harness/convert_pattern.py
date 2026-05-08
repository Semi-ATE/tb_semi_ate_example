# -*- coding: utf-8 -*-
"""
Created on Fri Aug  2 11:28:41 2024

@author: jung
"""

import sys
import os
import subprocess
import shutil
from time import sleep


class ConvertPattern():

    def __init__(self, filename):
        print(f'ConvertPattern: {filename}')
        self.harness = os.path.dirname(__file__)
        self.stildir = '\\STIL'
        self.error = 0

        options = '-l -status -alltoio -repeat -repinout 0 1 -repbreak_lc -pingrp allsigs -comment_ls -stil'
        options = options + f' -scr {self.harness}{self.stildir}\\miniSCT_pin8_scramble.scr'
        # options += f' -pync {self.harness}\\{self.stildir}\\miniSCT_pin8_pync_template.py'
        # options += ' -post miniSCT_modify.py'
        self.options = options
        self.run(filename)

    def run(self, filename):
        version = '_0x0x' if os.environ.get('VERSION') is None else '_' + os.environ.get('VERSION')

        patternpath = os.path.dirname(filename)
        pattype = os.path.splitext(filename)[1]
        patref = os.path.basename(filename)
        outname = patref[:patref.find('__')+4] + version
        patref = patref[:patref.find('__')]

        self.options = self.options + f' -outname {outname} -patref {patref}'

        if pattype == '.tp':
            cmd = f'C:\\home\\vericonv\\vericonv_12_2_0\\Win64\\vericonv {self.options} {filename}'
            output = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE).stdout.read()
            self.error = -1 if output == '' else self.error
            # print(output)
            stil_filename = f'{os.getenv("PROJECT_PATH")}{self.stildir}\\{outname}.stil'
        elif pattype == '.stil':
            stil_filename = filename

        print(stil_filename)
        print(outname)
        print(patref)
        self.pync_workaround(stil_filename, outname, patref)

        shutil.move(stil_filename + '.pync', patternpath+f'\\{outname}.stil')

        if pattype == '.tp':
            sleep(1)
            os.remove(filename)
            os.remove(stil_filename)

    def remove_mid_pattern(self):
        pass

    def pync_workaround(self, filename, outname, patref):
        with open(filename, 'r') as f_in:
            lines = f_in.readlines()
        condition = 0
        with open(filename + '.pync', 'w') as pyncfile:
            for line in lines:
                pyncfile.write(line)
                if line.find('//') == 0 and condition == 0:
                    condition = 1
                if line.find('include') > 0 and condition == 1:
                    pyncfile.write('\nSTIL 1.0;\n\n')
                    pyncfile.write('Include \"../../../gen/gen_signals.stil";\n')
                    pyncfile.write('Include \"../../../gen/gen_timing.stil";\n')
                    # pyncfile.write(", "//__VDSM__Include \"../../../gen/gen_DSM_{patref}.stil";\n')
                    pyncfile.write("\n")
                    pyncfile.write(f"PatternBurst pbu_{outname} " + "{\n")
                    pyncfile.write("   PatList {\n")
                    pyncfile.write(f"      {patref};\n")
                    pyncfile.write("   }\n")
                    pyncfile.write("}\n\n")
                    pyncfile.write(f"PatternExec pex_{patref} " + "{\n\n")
                    pyncfile.write("   Selector selGenTiming;\n")
                    pyncfile.write("   Category catGenTiming;\n")
                    pyncfile.write("   Timing   timGenTiming;\n\n")
                    pyncfile.write(f"   PatternBurst pbu_{outname};\n")
                    pyncfile.write("}\n\n")
                    condition = -1


if __name__ == '__main__':
    index = 0
    for arg in sys.argv:
        if arg == '-h':
            print('helptext')
        elif index > 0:
            filename = arg
        index += 1

    # pattern = ConvertPattern(r"C:\Users\jung\ATE\packages\HATC\HATC23\pattern\HW0\FT\DummyDevice\uart__40_hepting.tp")
    pattern = ConvertPattern(filename)
    sys.stdout.write(f"{pattern.error}\n")
