
import lldb
import threading
import subprocess
import platform
import Cparse


class lldbapi:
    StopReason = ['invalid', 'None', 'Trace',
                  'BP', 'WP', 'Signal', 'Exception', 'Exec', 'PlanComplete', 'ThreadExiting']

    def __init__(self):
        self.procState = -1
        self.stackinfo = []
        self.exit = True
        self.thread = threading.Thread()
        lldb.SBDebugger.Initialize()
        self.arch = platform.machine()
        self.parser = Cparse.CParse()

    def compile(self, fpath="sample/sample.c", lib="", bin_path="bin/target"):

        com = (
            "gcc %s -l%s -g -o %s" % (fpath, lib, bin_path)
            if lib
            else "gcc %s -g -o %s" % (fpath, bin_path)
        )
        print("COM:" + com)

        if subprocess.call(com, shell=True):
            print("Compile Error")
            return False
        else:
            self.file = lldb.SBFileSpec(fpath)
            self.parser.__init__()
            self.parser.SetFilePath(fpath)
            self.parser.Parse()
            self.func = self.parser.parse_data["func"]
            if not self.file.IsValid():
                print("File Error")
            self.module = lldb.SBFileSpec(bin_path)
            if not self.module.IsValid():
                print("Module Error")
            return True

    def __del__(self):
        self.exit = False

    def Create(self):
        self.debugger = lldb.SBDebugger.Create()
        if not self.debugger.IsValid():
            print("Debugger Error")
            return
        self.debugger.SetAsync(False)
        modulepath = self.module.GetDirectory()+'/'+self.module.GetFilename()
        self.target = self.debugger.CreateTargetWithFileAndArch(
            modulepath, self.arch)
        if not self.target.IsValid():
            print("Target Error")
            return

    def Launch(self):
        self.process = self.target.LaunchSimple(None, None, ".")
        self.StoreProcessInfo()

    def Continue(self):
        self.process.Continue()
        self.StoreProcessInfo()

    def AllThreadStepOver(self):
        thread = self.process.GetThreadAtIndex(0)
        thread.StepOver(lldb.eAllThreads)
        self.StoreProcessInfo()

    def OnlyThreadStepOver(self, thread_id):
        thread = self.process.GetThreadByID(thread_id)
        thread.StepOver(lldb.eOnlyThisThread)
        self.StoreProcessInfo()

    def Input(self, input):
        input += "\n"
        self.process.PutSTDIN(input)

    def Output(self):
        out = self.process.GetSTDOUT(2048)
        return out if out else ""

    def info_free(self):
        for t_idx in range(len(self.stackinfo)):
            try:
                del self.stackinfo[t_idx]
            except IndexError:
                pass
        self.stackinfo.__init__()

    def CreateBPAtFunc(self):
        print(self.func)
        for func in self.func:
            bp = self.target.BreakpointCreateByName(func)
            if not bp.IsValid():
                print("Can not Create BP at main()")
    def CreateBPAtDesignatedLine(self,line):
        filepath = self.file.GetDirectory()+'/'+self.file.GetFilename()
        for l in line:
            print("line number :" + str(l))
            bp = self.target.BreakpointCreateByLocation(filepath, l)
            if not bp.IsValid():
                print("Can not Create BP(line:%s)" % str(l))
                return False
        return True

    def StoreProcessInfo(self):
        if not self.process.IsValid():
            print("Process Error")
            return
        self.info_free()
        self.procState = self.process.GetState()
        self.thread_num = self.process.GetNumThreads()
        for idx in range(self.thread_num):
            thread = self.process.GetThreadAtIndex(idx)
            self.stackinfo.append(self.StoreThreadInfo(thread))

    def StoreThreadInfo(self, thread):
        if not thread.IsValid():
            print("Thread Error")
            return
        t_dict = dict()
        t_dict["ID"] = thread.GetThreadID()
        t_dict["IndexID"] = thread.GetIndexID()
        t_dict["flist"] = []
        t_dict["StopReason"] = self.StopReason[thread.GetStopReason()]
        for idx in range(thread.GetNumFrames()):
            frame = thread.GetFrameAtIndex(idx)
            f_dict = self.StoreFrameInfo(frame)
            if f_dict is not None:
                t_dict['flist'].append(f_dict)
        return t_dict

    def StoreFrameInfo(self, frame):
        if not frame.IsValid():
            print("Frame Error")
            return
        f_dict = dict()
        f_dict['ID'] = frame.GetFrameID()
        f_dict['name'] = frame.GetDisplayFunctionName()
        if frame.GetLineEntry().IsValid():
            f_dict['line'] = frame.GetLineEntry().GetLine()
            # return f_dict

        f_dict['module'] = frame.GetModule().GetFileSpec().GetFilename()
        error =lldb.SBError()
        contents = self.process.ReadMemory(frame.GetFP()+8,8,error)
        if contents is None:
            f_dict['retrun_ad'] = 'None'
        else :
            f_dict['retrun_ad'] = hex(int.from_bytes(contents,'little'))
        f_dict['SP'] = hex(frame.GetSP())
        f_dict['PC'] = hex(frame.GetPC())
        f_dict['FP'] = hex(frame.GetFP())
        f_dict['CFA'] = hex(frame.GetCFA())

        f_dict['slist'] = []
        
        symbol = frame.GetSymbol()

        if symbol.GetType() == lldb.eSymbolTypeCode:
            instructions = symbol.GetInstructions(self.target)
            for inst in instructions:               
                f_dict['slist'].append(self.StoreStackInfo(inst))
        return f_dict
                            
    def StoreStackInfo(self,inst):
        s_dict = dict()

        address = inst.GetAddress()
        s_dict['address'] = hex(address.GetLoadAddress(self.target))
        s_dict['mnemonic'] = inst.GetMnemonic(self.target)
        s_dict['operands'] = inst.GetOperands(self.target)
        return s_dict
