puts "Test IDA"
#-memories
ida_probe -log -wave -wave_probe_args="${::env(TOPLEVEL)} -all -depth all"TOPLEVEL
run