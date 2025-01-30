database -open -default waves
probe -create -name all ${::env(TOPLEVEL)} -depth all -tasks -functions -uvm -database waves -packed 9280
run