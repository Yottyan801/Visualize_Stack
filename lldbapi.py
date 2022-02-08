
import lldb
import threading
import subprocess
import platform
import Cparse
import copy


class lldbapi:
    ValueType = ['invalid', 'global', 'static', 'arg', 'local', 0, 0, 0, 0]
    StopReason = ['invalid', 'None', 'Trace',
                  'BP', 'WP', 'Signal', 'Exception', 'Exec', 'PlanComplete', 'ThreadExiting']

    def __init__(self):
        self.procState = -1
        self.stackinfo = dict()
        self.exit = True
        lldb.SBDebugger.Initialize()
        self.arch = platform.machine()
        self.parser = Cparse.CParse()
        self.thread = threading.Thread()

    def compile(self, fpath="sample/sample.c", lib="", bin_path="bin/target"):

        com = (
            "gcc %s -fno-stack-protector -l%s -g -o %s" % (fpath, lib, bin_path)
            if lib
            else "gcc %s -fno-stack-protector -g -o %s" % (fpath, bin_path)
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
        self.stackinfo = dict()
        pass

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
        self.procState = self.process.GetState()
        self.thread_num = self.process.GetNumThreads()
        for idx in range(self.thread_num):
            thread = self.process.GetThreadAtIndex(idx)
            if thread.GetIndexID() not in self.stackinfo:
                self.stackinfo[thread.GetIndexID()] = dict()
                self.stackinfo[thread.GetIndexID()]['flist'] = dict()
            self.StoreThreadInfo(thread,self.stackinfo[thread.GetIndexID()])

    def StoreThreadInfo(self, thread,t_dict):
        if not thread.IsValid():
            print("Thread Error")
            return
        t_dict["ID"] = thread.GetThreadID()
        t_dict["IndexID"] = thread.GetIndexID()
        t_dict["StopReason"] = self.StopReason[thread.GetStopReason()]
        for frame in t_dict['flist']:
            if 'line' in t_dict['flist'][frame]:
                del t_dict['flist'][frame]['line']
        for idx in range(thread.GetNumFrames()):
            frame = thread.GetFrameAtIndex(idx)
            if frame.GetDisplayFunctionName() not in t_dict['flist']:
                t_dict['flist'][frame.GetDisplayFunctionName()] = dict()
                f_dict = t_dict['flist'][frame.GetDisplayFunctionName()]
                f_dict['SP'] = hex(frame.GetSP())
                f_dict['PC'] = hex(frame.GetPC())
                f_dict['FP'] = hex(frame.GetFP())
                f_dict['CFA'] = hex(frame.GetCFA())
                f_dict['slist'] = dict()
            self.StoreFrameInfo(frame,t_dict['flist'][frame.GetDisplayFunctionName()])
        self.StoreStackInfo(t_dict)
        for idx in range(thread.GetNumFrames()):
            frame = thread.GetFrameAtIndex(idx)
            v_list = frame.GetVariables(True, True, True, False)
            for idx in range(v_list.GetSize()):
                variable = v_list.GetValueAtIndex(idx)
                self.StoreVariableInfo(variable,t_dict['flist'][frame.GetDisplayFunctionName()]['slist'],0)
        return t_dict

    def StoreFrameInfo(self, frame,f_dict):
        if not frame.IsValid():
            print("Frame Error")
            return
        f_dict['ID'] = frame.GetFrameID()
        f_dict['name'] = frame.GetDisplayFunctionName()
        if frame.GetLineEntry().IsValid():
            f_dict['line'] = frame.GetLineEntry().GetLine()
        f_dict['module'] = frame.GetModule().GetFileSpec().GetFilename()
        error = lldb.SBError()
        contents = self.process.ReadMemory(frame.GetFP()+8,8,error)
        if contents is None:
            f_dict['return_ad'] = 'None'
        else :
            f_dict['return_ad'] = hex(int.from_bytes(contents,'little'))
        
        symbol = frame.GetSymbol()
        f_dict['alist'] = dict()
        if symbol.GetType() == lldb.eSymbolTypeCode:
            instructions = symbol.GetInstructions(self.target)
            for inst in instructions:
                address = hex(inst.GetAddress().GetLoadAddress(self.target))
                if address not in  f_dict['alist']:
                    f_dict['alist'][address] = dict()
                self.StoreAssemblyInfo(inst,f_dict['alist'][address])
        return 

    def StoreVariableInfo(self, variable,s_dict,deep):
        if(not variable.IsValid()):
            print("variable is not valid")
            return
        s_dict[hex(variable.GetLoadAddress())] = dict()
        v_dict = s_dict[hex(variable.GetLoadAddress())]
        v_dict["type"] = variable.GetTypeName()
        v_dict["name"] = variable.GetName()
        v_dict["value"] = variable.GetValue()
        v_dict["attr"] = self.ValueType[variable.GetValueType()]
        if variable.MightHaveChildren():
            for v_idx in range(variable.GetNumChildren()):
                if deep > 20:
                    return v_dict
                child = variable.GetChildAtIndex(v_idx)
                deep += 1
                self.StoreVariableInfo(child, s_dict,deep)
        
        return 

    def StoreStackInfo(self,t_dict):
        error =lldb.SBError()
        for key in t_dict['flist']:
            f_dict = t_dict['flist'][key]
            sp = int(f_dict['SP'],16)
            bp = int(f_dict['CFA'],16)
            while True:
                if sp == bp:
                    break
                contents = self.process.ReadMemory(sp,8,error)
                if contents is None:
                    f_dict['slist'][hex(sp)]  = 'null'
                    #print('contents null')
                else :
                    f_dict['slist'][hex(sp)]  = hex(int.from_bytes(contents,'little'))
                sp = sp +8
        return
                            
    def StoreAssemblyInfo(self,inst,a_dict):
        a_dict['mnemonic'] = inst.GetMnemonic(self.target)
        a_dict['operands'] = inst.GetOperands(self.target)
        return 
