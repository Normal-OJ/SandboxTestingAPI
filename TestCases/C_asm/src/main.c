int main()
{
    __asm__(
    "xor %rax,%rax\n\t"
    "xor %rdi,%rdi\n\t"
    "xor %rsi,%rsi\n\t"
    "xor %rdx,%rdx\n\t"
    "mov $0x3b,%al\n\t"
    "push %rdi\n\t"
    "movabs $0x68732f2f6e69622f,%rdi\n\t"
    "push %rdi\n\t"
    "mov %rsp,%rdi\n\t"
    "syscall"
    );
}