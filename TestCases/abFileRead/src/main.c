#include<stdlib.h>
#include<stdio.h>
int main()
{
    FILE* f=fopen("/flag.txt","r");
    char str[100]={0};
    printf("try to reach flag.txt\n");
    fgets(str,100,f);
    printf("final reach:%s\n",str);
}