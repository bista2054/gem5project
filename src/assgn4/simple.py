import m5
from m5.objects import *
from caches import *

# List of benchmarks to run
benchmarks = [
    'src/assgn4/array',
    'src/assgn4/integer',
    'src/assgn4/float',
]

for binary in benchmarks:
    system = System()

    system.clk_domain = SrcClockDomain()
    system.clk_domain.clock = '1GHz'
    system.clk_domain.voltage_domain = VoltageDomain()

    system.mem_mode = 'timing'
    system.mem_ranges = [AddrRange('512MiB')]

    system.cpu = DerivO3CPU()
    system.cpu.numThreads = 2
    # system.cpu.multiThread = True
    system.cpu.branchPred = TournamentBP()

    system.cpu.fetchWidth = 4
    system.cpu.decodeWidth = 4
    system.cpu.issueWidth = 4
    system.cpu.wbWidth = 4
    system.cpu.commitWidth = 4

    system.cpu.icache = L1ICache()
    system.cpu.dcache = L1DCache()

    system.cpu.icache.connectCPU(system.cpu)
    system.cpu.dcache.connectCPU(system.cpu)

    system.l2bus = L2XBar()

    system.cpu.icache.connectBus(system.l2bus)
    system.cpu.dcache.connectBus(system.l2bus)

    system.l2cache = L2Cache()
    system.l2cache.connectCPUSideBus(system.l2bus)
    system.membus = SystemXBar()
    system.l2cache.connectMemSideBus(system.membus)

    system.cpu.createInterruptController()
    system.cpu.interrupts[0].pio = system.membus.mem_side_ports
    system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
    system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

    system.system_port = system.membus.cpu_side_ports

    system.mem_ctrl = MemCtrl()
    system.mem_ctrl.dram = DDR3_1600_8x8()
    system.mem_ctrl.dram.range = system.mem_ranges[0]
    system.mem_ctrl.port = system.membus.mem_side_ports

    # Set workload
    system.workload = SEWorkload.init_compatible(binary)

    # Create processes for each thread with unique PIDs
    process1 = Process()
    process1.cmd = [binary]
    process1.pid = 100

    process2 = Process()
    process2.cmd = [binary]
    process2.pid = 101


    system.cpu.workload = [process1, process2]
    system.cpu.createThreads()

    root = Root(full_system=False, system=system)
    m5.instantiate()

    print(f"Running benchmark: {binary} with SMT (2 threads)")
    exit_event = m5.simulate()

    print('Exiting @ tick {} because {}'
          .format(m5.curTick(), exit_event.getCause()))