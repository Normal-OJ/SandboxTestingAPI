#include<stdlib.h>
#include<stdio.h>
int main()
{
    FILE* f=fopen("/etc/passwd","r");
    char str[1000]={0};
    printf("try to reach flag.txt\n");
    fgets(str,1000,f);
    printf("final reach:%s\n",str);
}