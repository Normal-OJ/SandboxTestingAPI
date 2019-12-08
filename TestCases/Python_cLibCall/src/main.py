import ctypes

command = "pwd"

libc = ctypes.CDLL('libc.so.6')
Cexecve=libc.execl
arg0 = ctypes.create_string_buffer(10)
arg1 = ctypes.create_string_buffer(10)
arg2 = ctypes.create_string_buffer(10)
arg3 = ctypes.create_string_buffer(len(command)+1)

arg0.value = b"/bin/sh"
arg1.value = b"sh"
arg2.value = b"-c"
arg3.value = command.encode()
Cexecve(arg0,arg1,arg2,arg3,0)