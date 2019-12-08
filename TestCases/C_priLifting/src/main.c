#include<unistd.h>
#include <sys/types.h>
#include<stdlib.h>
#include<stdio.h>
int main()
{
    int i=seteuid(0);
    if(i==-1)
        printf("can not set effective uid\n");
    i=setuid(0);
    if(i==-1)
        printf("can not set uid\n");
    return 0;
}