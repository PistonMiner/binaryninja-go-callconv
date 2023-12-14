# Copyright 2021 Linus S. (PistonMiner)

# Go internal ABI changes over time so this may not be the most current, see:
# https://github.com/golang/go/blob/d20a0bfc8a7fd70537766990691d4c9e5841e086/src/cmd/compile/abi-internal.md

# Interactions with assembly functions use a different calling convention
# This is _not_ implemented here
# You can see this e.g. if xorps xmm15, xmm15 runs after calls
# https://go.dev/doc/asm#amd64

from binaryninja import *

BINJA_VERSION = 3

class GoCall_X86_64(CallingConvention):
    name = "gocall"

    caller_saved_regs = [
        "rax", "rbx", "rcx", "rdi", "rsi", "r8", "r9", "r10", "r11", # int
        "xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7", # float
        "xmm8", "xmm9", "xmm10", "xmm11", "xmm12", "xmm13", "xmm14",
    ] # todo: all
    callee_saved_regs = [
        #"rbp", # frame pointer
        "zmm15", "ymm15", "xmm15", # zero value (may be modified within)
    ]
    implicitly_defined_regs = [
        "zmm15", "ymm15", "xmm15", # zero value
        "r14" # current goroutine
    ]
    int_arg_regs = [
        "rax", "rbx", "rcx", "rdi", "rsi", "r8", "r9", "r10", "r11",
    ]
    float_arg_regs = [
        "xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7",
        "xmm8", "xmm9", "xmm10", "xmm11", "xmm12", "xmm13", "xmm14",
    ]

    #arg_regs_share_index = False
    #arg_regs_for_varargs = ?
    #stack_reserved_for_arg_regs

    # disable auto-assign
    eligible_for_heuristics = False

    # actually can return through all the arg regs but binja can only do finite
    int_return_reg = "rax"
    high_int_return_reg = "rbx"

cc = GoCall_X86_64(arch=Architecture["x86_64"], name="gocall")
Architecture["x86_64"].register_calling_convention(cc)

def setup_go_binary(bv):
    for f in bv.functions:
        f.calling_convention = bv.arch.calling_conventions["gocall"]
    bv.set_analysis_hold(False)
    bv.reanalyze()

def setup_go_binary_is_valid(bv):
    # We only support x86_64 right now
    if bv.arch and bv.arch.name != "x86_64":
        return False
    return True

PluginCommand.register(
    "Go\\Set Go calling convention",
    "Should load with analysis hold! Set gocall on all functions.",
    setup_go_binary,
    setup_go_binary_is_valid
)