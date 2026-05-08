"""General functions for the project cura."""

from pylab_ml.base_instrument import logger
from pylab_ml.common.common import str2num
from time import sleep

# das muss noch angepasst werden, bisher ist das nur ein copy von HANA

def unsigned_data(f):
    """
    Convert to 16-bit unsigned_data

    Parameters
    -------
    f : 16-bit value

    Returns
    -------
    unsigned 16-bit value

    """
    if f < 0.0:
        f += 65536.0
    return int(f)


def signed_data(f):
    """
    Convert to 16-bit signed_data

    Parameters
    -------
    f : 16-bit value

    Returns
    -------
    signed 16-bit value

    """
    if f > 32767:
        f -= 65536
    return int(f)


class TP_tasks():
    """General functions for the project hana."""

    def __init__(self, parent, instName=None):
        self.parent = parent
        self.instName = instName

    def micid(self, typ):
        micid = self.parent.setup.lastresult
        if typ == 'hal':
            value = ((micid[0] << 16)) + micid[1]
            self.parent.log_info(f'MicID == {hex(value)}')
            self.parent.setup.write(self.parent.setup.lastmacro, 'Y', value & 0x7f)  # Y = Bit 6-0
            self.parent.log_info(f'      Y == {value & 0x7f}')
            self.parent.setup.write(self.parent.setup.lastmacro, 'X', (value >> 7) & 0x7f)        # X = Bit 13-7
            self.parent.log_info(f'      X == {(value >> 7) & 0x7f}')
            self.parent.setup.write(self.parent.setup.lastmacro, 'WNR', (value >> 14) & 0x1f)      # WNR = Bit 18-14
            self.parent.log_info(f' WNR == {(value >> 14) & 0x1f}')
            self.parent.setup.write(self.parent.setup.lastmacro, 'PLNR', (value >> 19) & 0x1fff)   # PLNR = Bit31-19
            self.parent.log_info(f' PLNR == {(value >> 19) & 0x1fff}')
        return value

    def unlock(self):
        logger.info(f'Try {self.instName}.unlock')
        quiet = self.parent.tester.interface.quiet
        self.parent.tester.interface.quiet = True
        forcebank = self.parent.regs._forcebank
        self.parent.regs._forcebank = False
        self.parent.regs._bank = -1
        for unlock in self.parent.setup.regs.unlock:
            try:
                self.parent.regs.register[unlock[0]].write(unlock[1])
            except KeyError:
                logger.error(f"{self.instName}.unlock  register {unlock[0]} doesn't exist in registermaster")
        NVPROGM = self.parent.regs.NVPROGM.read()     # self.parent.regs.register[self.setup.reg_progm].read()
        self.parent.regs._forcebank = forcebank
        if NVPROGM == 0xffff or self.parent.regs.NVPROGM.UNLCK == 0:         # self.parent.regs.__dict__[self.parent.setup.reg_progm].UNLCK==0:
            logger.error("      -> could't unlock...... NVPROGM = 0x{:04x}".format(NVPROGM))
            result = -1
        else:
            logger.info("      -> ok, unlocked,  0x{:04x}".format(NVPROGM))
            result = 0
        self.parent.tester.interface.quiet = quiet
        return (NVPROGM, result)

    def datfilter(self, start, data, myfilter, withoutmic=True):
        """
        filter data from start-address with myfilter.

        Parameters
        ----------
        start : integer
            start-address.
        data : array of integers
        myfilter : string
            use only the regnames which start with the myfilter-string
        withoutmic : boolean, optional
            the result is without the EE_MIC_ID.
            if you want the EE_MIC_ID, you have to set False
            The default is True.

        Returns
        -------
        result

        """
        result = data.copy()
        for index in range(0, len(data)):               # use only myfilter address
            regname = self.parent.regs.find(start+index)
            if regname is None or regname.find(myfilter) < 0 or (regname.find('EE_MIC_ID') >= 0 and withoutmic):
                result[index] = None
            if regname is not None and regname == myfilter:
                return  data[index]
        return result

    def readDatalogDump(self, fileName):
        """
        reads a QDB Datalog EEPROM Dump file from Quality.

        Parameters
        ----------
        fileName : string
            DESCRIPTION.

        Returns
        -------

         data : memory data integer list, None entries for
             not used/initialized values

        """
        try:
            file = open(fileName)
        except OSError:
            logger.error("   readDatalogDump: couln't read {fileName}")
            return -1, None
        base_adr = 10
        base_dat = 16

        data = []
        state = ''
        base = 0
        for line in file:
            parts = line.split()
            for index in range(0, len(parts)):
                value = parts[index]
                if value == '//':
                    break
                value = str2num(value, base_adr if state == 'address' else base_dat)
                if type(value) == str:
                    if value == 'base':
                        state = 'base'
                    elif value == 'address' and index == 0:
                        state = 'address'
                    elif value == 'data' and index == 0:
                        state = 'data'
                    continue
                elif state == 'base':
                    base = value * 32
                    continue
                elif state == 'address':
                    adr = base + value
                    continue
                data.append((adr, value))
                break
        file.close()
        minadr = min(data)[0]
        maxadr = max(data)[0]+1
        array = [None]*(maxadr-minadr)
        adr = minadr
        for index in range(0, len(data)):
            array[data[index][0]] = data[index][1]
        return minadr, array

    def EEPROMwrite(self, data, startadr=0):
        error = 0
        count = 0
        # TODO: use self.parent.setup.regs.progm
        nvprogm = self.parent.regs.NVPROGM
        nvprogm.read()
        nvprogm.EE5V = 1
        if nvprogm.UNLCK == 0:
            logger.error("EEPROMwrite: EPPROM is locked, couldn't write eeprom")
            return 1
        nvprogm.write()
        for adr, dat in enumerate(data):
            if dat is not None:
                self.parent.regs.writereg(startadr + adr, dat)
                count += 1
                newdat = self.parent.regs.readreg(startadr + adr)
                if newdat != dat:
                    logger.error(f"EEPROMwrite: 0x{adr:04x}: with 0x{dat:04x}, read 0x{newdat:04x}")
                    error +=1
        logger.info(f"EEPROM write with {error} errors/{count} values")
        return error

    def NVRamwrite(self, liste, mode='AUTO'):
        ''' mode=='AUTO' Program/Erase with statemachine
            mode=='MANU' Program/Erase manuell        -> only available in STI-mode , not tested yet!!!!!
            mode=='SHADOW' write only shadowram
        '''
        if mode == "MANU":
            logger.error("NVRAMwrite mode='MANU' not tested, check the results!!!")
        self.unlock()
        progm = self.parent.setup.regs.progm
        self.parent.regs.register[progm].write(0x2002)   # enable Latch hw outputs, ram layer active
        if mode == 'MANU' and self.parent.regs.use == 'sti':
            logger.measure('NVRamwrite:  1. Stop Fima')
            self.parent.regs.TEST3._write(0x0120)                  # konstanten Stromverbrauch einstellen
            self.parent.regs.TEST1._write(0x003e)                  # stop Fima
            self.parent.regs.NV_MIC_SETUP_2._write(0xc3f0)         # set Startadresse of Fima                          altes Datum sichern????!!!!!!!
            self.parent.regs.TEST1._write(0x003e)                  # stop Fima
            self.parent.regs.TEST4._write(0x0cc0)
        error = 0
        progerror = False
        for nvram in liste:
            olddat = self.parent.regs.register[nvram[0]].read()
            newdat = str2num(nvram[1])
            if olddat < 0:
                logger.error(f'NVRAMwrite not possible {nvram[0]} = olddat')
                return 1
            self.parent.regs.register[nvram[0]].write(newdat)
            err = self.parent.regs.register[nvram[0]].read(compare=newdat)
            error += err
        if mode == 'AUTO':
            self.parent.regs.register[progm].read(compare='0bxxxx_x000_1000_0010')
            self.parent.regs.register[progm].write(0x0006)     # enable EE5V   TODO: check if necessary or if not in Automode
            self.parent.regs.register[progm].read(compare=0x0086, mask=0x07ff)
            self.parent.regs.register[progm].write(0x0026)     # start automatic programming and clear error flags
            sleep(0.2)
            self.parent.regs.register[progm].read()
            if self.parent.regs.register[progm].PER == 1:
                logger.error('NVRamwrite Pump error during program/erase')
                progerror = True
            if self.parent.regs.register[progm].VER == 1:
                logger.error('NVRamwrite Voltage error during program/erase')
                progerror = True
        elif mode == 'MANU':
            self.parent.regs.TEST7.write(0x0300)      # switch off Decimationfilter (Reset,input=Test6.testdac)
            self.parent.regs.TEST2.write(0x0000)
            self.parent.regs.register[progm].write(0x2086)   # clear NVRam cells,vdd=5v,enable Latch, Ram Layer active
            sleep(0.1)
            self.parent.regs.register[progm].write(0x2096)   # enable Voltage pump ->start state machine
            err = self.parent.regs.register[progm].read(compare=0xc986)
            error += err
            self.parent.regs.register[progm].write(0x2082)
            err = self.parent.regs.register[progm].read(compare=0xc982)
            error += err
            self.parent.regs.TEST2.write(0x0000)                   # reset vddhtol
            self.parent.regs.TEST2.write(0x0000)                   # set vddhtol
            self.parent.regs.register[progm].write(0x208e)                 # set NVRam cells,vdd=5v,enable Latch, Ram Layer active
            sleep(0.1)
            self.parent.regs.register[progm].write(0x209e)
            err = self.parent.regs.register[progm].read(compare=0xc98e)
            error += err
            self.parent.regs.register[progm].write(0x208a)                 #
            err = self.parent.regs.register[progm].read(compare=0xc98a)
            error += err
            self.parent.regs.TEST2.write(0x0000)                   # reset vddhtol
            self.parent.regs.TEST4.write(0x0c00)                   # read Margincells and NVE
            err = self.parent.regs.register[progm].read(compare=0x208a)
            error += err
            self.parent.regs.register[progm].write(0x208b)                 # force RAM-Layer of NVRAM
            for nvram in liste:
                err = self.parent.regs.register[nvram[0]].read(compare=nvram[1])
                error += 1
            self.parent.regs.register[progm].write(0x0001)
        elif mode == 'SHADOW':
            # switch HW outputs from latching to transparent mode
            self.parent.regs.register[progm].LTCH = 0
            self.parent.regs.register[progm].write()
            self.parent.regs.register[progm].read()
        if not progerror and error == 0:
            logger.info(f'NVRamwrite({mode}) wrote {liste} successful')
        elif error != 0:
            logger.error(f'NVRamwrite({mode}) wrote done, but {error} error occur')
        else:
            logger.error(f'NVRamwrite({mode}) wrote done, but Voltage or Pump error occur')
            error += 1
        return error

    # def NVRAM_compare(self,CUST0=None,MIC1=None,MIC2=None,TRIM=None):
    #      logger.error("NVRAM_compare in work, dont use it !!!!!!!!!!!!!!!!!!!!!!!!!")
    #      nCUST0 = self.regs.__dict__[self.setup.nv_register[0]]._read()
    #      nMIC1 = self.regs.__dict__[self.setup.nv_register[1]]._read()
    #      nMIC2 = self.regs.__dict__[self.setup.nv_register[2]]._read()
    #      nTRIM = self.regs.__dict__[self.setup.nv_register[3]]._read()
    #      result=True
    #      if CUST0!=None and nCUST0!=CUST0:
    #          print("!! Error: {}=0x{:04x}, target=0x{:04x}".format(self.setup.nv_register[0],nCUST0,CUST0))
    #          result=False
    #      if MIC1!=None and nMIC1!=MIC1:
    #          print("!! Error: {}=0x{:04x}, target=0x{:04x}".format(self.setup.nv_register[1],nMIC1,MIC1))
    #          result=False
    #      if MIC2!=None and nMIC2!=MIC2:
    #          print("!! Error: {}=0x{:04x}, target=0x{:04x}".format(self.setup.nv_register[2],nMIC2,MIC2))
    #          result=False
    #      if TRIM!=None and nTRIM!=TRIM:
    #          print("!! Error: {}=0x{:04x}, target=0x{:04x}".format(self.setup.nv_register[3],nTRIM,TRIM))
    #          result=False
    #      if result==True: print('    -> done, compare ok    :-)')
    #      return (result)

# ---------------------------------------------------------------------

    def __repr__(self):
        return f"{self.__class__}"
