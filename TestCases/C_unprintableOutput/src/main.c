#include<stdio.h>
int main()
{
    char mal[100]={0};
    for(int u=0;u!=31;++u)
        mal[u]=u+1;
    printf("%s",mal);
}