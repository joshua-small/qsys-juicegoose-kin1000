from pathlib import Path
import copy, hashlib, importlib.util, itertools, json, re
from lupa.lua53 import LuaRuntime

root=Path(__file__).parent
old=(root/'baseline.qplug').read_text(encoding='utf-8-sig')
new=(root.parent/'content/JuiceGooseKin1000ApRmUps.qplug').read_text()
spec=importlib.util.spec_from_file_location('layout_check',root/'check_layout.py')
checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
contract=json.loads((root/'layout-contract.json').read_text())
checks=[checker.validate(new,contract)]

def design(source,debug='None',poll=5):
    l=LuaRuntime(unpack_returned_tuples=True,encoding='latin-1');l.execute(source.encode())
    g=l.globals();p=l.table()
    for d in g.GetProperties().values():p[d.Name]=l.table(Value=d.Value)
    p['Debug Print'].Value=debug;p['Poll Interval (s)'].Value=poll
    p.plugin_show_debug=l.table(Value=True)
    return l,g,p

_,a,ap=design(old);_,b,bp=design(new)
plain=checker.plain
assert plain(a.GetControls(ap))==plain(b.GetControls(bp))
assert plain(a.GetPins(ap))==plain(b.GetPins(bp))
assert a.PluginInfo.Id==b.PluginInfo.Id and a.PluginInfo.Name==b.PluginInfo.Name
assert a.GetPrettyName(ap)==b.GetPrettyName(bp)
assert plain(a.GetColor(ap))==plain(b.GetColor(bp))
pa,pb=plain(a.GetProperties()),plain(b.GetProperties())
assert pa[0]==pb[0] and pa[1]['Value']==pb[1]['Value']
assert pb[1]['Choices']==['None','Tx','Rx','Tx/Rx','Function Calls','All']
runtime_start='if Controls then'
assert old.split(runtime_start,1)[1].replace('DebugFunctions = debugPrint == "All"','DebugFunctions = debugPrint == "Function Calls" or debugPrint == "All"')==new.split(runtime_start,1)[1]
checks.append('Identity, all 29 control declarations, serial pin, PrettyNames and poll property preserved; runtime source identical except Function Calls debug selection')

# Mutation checks must reject the same missing-caption and stacking regressions
# that previously passed informal source reviews.
mutations=[new.replace('Text = "Commands",','Text = "Missing",',1),new.replace('ZOrder = 2,','ZOrder = 1,',1)]
for broken in mutations:
    try:checker.validate(broken,contract)
    except checker.LayoutError:pass
    else:raise AssertionError('layout mutation accepted')
checks.append('Negative fixtures reject missing Commands caption and duplicate shared ZOrder')

mock='''
print=function() end
Timer={}
function Timer.New()
  return {Start=function(self,seconds) self.Running=true;self.Seconds=seconds end,
          Stop=function(self) self.Running=false end}
end
SerialPorts={{IsOpen=false,BufferLength=0,
  Open=function(self,...) self.Settings={...};self.IsOpen=true end,
  Close=function(self) self.IsOpen=false end,
  Write=function(self,data) end,
  Read=function(self,count) return "" end}}
'''
def runtime(source,debug='None',poll=5):
    l,g,p=design(source,debug,poll);g.Properties=p;l.execute(mock)
    g.Controls=l.table()
    for d in g.GetControls(p).values():
        g.Controls[d.Name]=l.table(Value=d.DefaultValue or 0,Boolean=False,String='')
    l.execute(source.encode())
    return l,g

for poll in [2,5,60]:
    for debug in contract['variants'][0]['Debug Print'], 'Tx','Rx','Tx/Rx','All':
        _,a=runtime(old,debug,poll);_,b=runtime(new,debug,poll)
        assert (a.DebugTx,a.DebugRx,a.DebugFunctions)==(b.DebugTx,b.DebugRx,b.DebugFunctions)
        a.StartupTimer.EventHandler();b.StartupTimer.EventHandler()
        assert plain(a.SerialPort.Settings)==plain(b.SerialPort.Settings)==[1200,8,'N',1]
        for vals in [(0,0,0),(60,1,0),(1440,255,59)]:
            emitted=[]
            for g in [a,b]:
                messages=[];g.Send=lambda message,expected=None:messages.append((message,expected))
                g.Controls.WakeUpMinutes.Value,g.Controls.PreSDMinutes.Value,g.Controls.PreSDSeconds.Value=vals
                for name in ['SelfTestBtn','EnableACRestartBtn','DisableACRestartBtn','SetWakeUpBtn','SetPreSDBtn']:
                    ctl=g.Controls[name];ctl.Value=1;ctl.EventHandler(ctl)
                    before=len(messages);ctl.Value=0;ctl.EventHandler(ctl);assert len(messages)==before
                emitted.append(messages)
            assert emitted[0]==emitted[1]
_,g=runtime(new,'Function Calls');assert g.DebugFunctions and not g.DebugTx and not g.DebugRx
checks.append('Full-runtime startup and command callbacks preserve serial settings, outgoing bytes and release behavior across poll/debug/value variants; Function Calls traces independently')

_,g=runtime(new)
for fault,bad,over,low,on,avr,test in itertools.product([False,True],repeat=7):
    data=[0]*16;data[5]=255;data[9]=(1 if on else 0)+(2 if low else 0)+(8 if avr else 0)+(32 if over else 0);data[10]=128+(1 if fault else 0)+(2 if bad else 0)+(4 if test else 0)
    assert g.ParsePollResponse(bytes(data))
    assert g.Status.Value==(2 if fault or bad or over else 1 if low or on else 0)
    assert g.Controls.SystemFault.Boolean==(fault or bad or over or low)
    assert g.Controls.SystemFault.Color==('#E6AB38' if low and not(fault or bad or over) else '#DF0024')
checks.append('128 UPS flag combinations retain fault precedence, severity, recovery and aggregate LED truth table')

for layout,graphics,defs,page,version in checker.snapshots(new,{},contract['pages']):
    for name,o in layout.items():
        if o['Style']=='None':continue
        assert not any(k in o for k in ['TextColor','OffColor','UnlinkOffColor'])
        if defs[name].get('ButtonType')=='Momentary':
            assert o['ButtonStyle']=='Momentary' and o['Size']==[45,20] and o['Margin']==2 and o['Color']==[255,255,255]
    if page['name']=='Controls':
        for name in ['OnBattery','LowBattery']:assert layout[name]['Color']==[230,171,56]
        for name in ['SystemFault','Fault','BatteryBad','Overload']:assert layout[name]['Color']==[223,0,36]
        for name in ['AVRActive','TestMode','PreSDCountActive','ScheduleCountActive','NoLoadShutdownDisabled']:assert layout[name]['Color']==[128,128,128]
checks.append('Momentary native button styling, semantic LED palette and absent optional color overrides checked on both pages')
report=dict(sha256=hashlib.sha256((root.parent/'content/JuiceGooseKin1000ApRmUps.qplug').read_bytes()).hexdigest(),checks=checks,limits='Offline mocks and coordinates only; Designer rendering/save-reopen/Core/device/Library acceptance deferred.')
print(json.dumps(report,indent=2))
