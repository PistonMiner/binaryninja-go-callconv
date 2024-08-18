# Copyright 2021 Linus S. (PistonMiner)

# Go internal ABI changes over time so this may not be the most current, see:
# https://github.com/golang/go/blob/d20a0bfc8a7fd70537766990691d4c9e5841e086/src/cmd/compile/abi-internal.md

# Interactions with assembly functions use a different calling convention
# This is _not_ implemented here
# You can see this e.g. if xorps xmm15, xmm15 runs after calls
# https://go.dev/doc/asm#amd64

from binaryninja import *
import os

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

    def perform_get_incoming_reg_value(self, reg: RegisterName, _: Function) -> RegisterValue:
        if reg in ["zmm15", "ymm15", "xmm15"]:
            return variable.ConstantRegisterValue(0)
        return variable.Undetermined()

cc = GoCall_X86_64(arch=Architecture["x86_64"], name="gocall")
Architecture["x86_64"].register_calling_convention(cc)

class GoPlatform_Linux_X86_64(Platform):
    name = "go-linux-x86_64"
    global_regs = ["r14"]
    os_list = ["linux"]

    # Load 'g' struct
    type_file_path = os.path.dirname(os.path.realpath(__file__)) + "/go-linux-x86_64.c"

    def __init__(self, arch: Architecture, handle=None):
        super().__init__(arch, handle)
        self.register_calling_convention(cc)
        self.default_calling_convention = cc
        self.cdecl_calling_convention = cc
        self.fastcall_calling_convention = cc
        self.stdcall_calling_convention = cc
        named_g = Type.named_type_from_type('g', self.types['g'])
        self.global_reg_types["r14"] = Type.pointer(arch, named_g)

plat = GoPlatform_Linux_X86_64(arch=Architecture["x86_64"])
plat.register("linux")

# The BV is not yet fully parsed, so we can't check bv.sections
def golang_recognizer(bv: BinaryView, metadata: Metadata):
    if b'\x00.gopclntab\x00' in bv.read(0, 0x99999999):
        return plat

BinaryViewType["ELF"].register_platform_recognizer(
    62,  # EM_X86_64
    Endianness.LittleEndian,
    golang_recognizer
)
