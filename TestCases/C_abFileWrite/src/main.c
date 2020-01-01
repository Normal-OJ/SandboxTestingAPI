#include<stdio.h>
#include<stdlib.h>
int main()
{
    FILE* f=fopen("crack.txt","w");
    char* str="hacked :p";
    printf("try to writing file...\n");
    int num=fwrite(str,1,9,f);
    printf("Done,write %d char to file.\n",num);
    return 0;
}