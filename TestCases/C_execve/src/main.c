#include<unistd.h>
int main()
{
    char* arg[]={
        "pwd"
    };
    execve("/usr/bin/pwd",arg,NULL);
    return 0;
}