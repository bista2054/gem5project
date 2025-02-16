import m5
from m5.objects import *
from caches import *


system = System()


system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()


system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MiB')]


num_threads = 4

# Create a list of CPUs
system.cpu = [X86MinorCPU() for _ in range(num_threads)]

for i in range(num_threads):
    system.cpu[i].icache = L1_ICache()
    system.cpu[i].dcache = L1_DCache()


system.l2bus = L2XBar()
for i in range(num_threads):
    system.cpu[i].icache.connectCPU(system.cpu[i])
    system.cpu[i].dcache.connectCPU(system.cpu[i])
    system.cpu[i].icache.connectBus(system.l2bus)
    system.cpu[i].dcache.connectBus(system.l2bus)


system.l2cache = L2Cache()
system.l2cache.connectCPUSideBus(system.l2bus)
system.membus = SystemXBar()
system.l2cache.connectMemSideBus(system.membus)


for i in range(num_threads):
    system.cpu[i].createInterruptController()
    system.cpu[i].interrupts[0].pio = system.membus.mem_side_ports
    system.cpu[i].interrupts[0].int_requestor = system.membus.cpu_side_ports
    system.cpu[i].interrupts[0].int_responder = system.membus.mem_side_ports


system.system_port = system.membus.cpu_side_ports


system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports


binary = 'tests/test-progs/hello/bin/x86/linux/daxpy'  # Path to the compiled daxpy binary


system.workload = SEWorkload.init_compatible(binary)

processes = []
for i in range(num_threads):
    process = Process()
    process.cmd = [binary]  # Same binary for all threads
    process.pid = 100 + i  # Assign unique PIDs
    processes.append(process)

for i in range(num_threads):
    system.cpu[i].workload = processes[i]
    system.cpu[i].createThreads()


root = Root(full_system=False, system=system)

# Initialize the simulation
m5.instantiate()

# Start the simulation
print("Beginning simulation!")
exit_event = m5.simulate()

# Print simulation exit reason
print('Exiting @ tick {} because {}'
      .format(m5.curTick(), exit_event.getCause()))