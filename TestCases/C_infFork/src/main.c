#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

int main(){
    for(int u=0;u!=500;++u)
    {
        int PID = fork();
        if(PID==0)
        {
            printf("Child's PID is %d\n", getpid());
            while (1);
        }
        else
            printf("Parent's PID is %d\n", getpid());
            
    }
    return 0;
}