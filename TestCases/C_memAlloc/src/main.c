#include<stdlib.h> 
#include<stdio.h>
int main()
{
    size_t num=-1;
    num=(num<<1)>>1;
    printf("try to alloc %ld bytes for 1000 times.\n",num);
    unsigned char *trash[1000];
    for(int u=0;u!=1000;++u)
        trash[u]=malloc(num);
    printf("fool :p\n");
    return 0;
}