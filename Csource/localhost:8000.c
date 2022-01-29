
#include<stdio.h>
#include<string.h>
void foo(void){
    char a[3]={0,0,0};
    char *p;
    long int r;
                          
    p = a;
    r = 0x00007fffffffdf68 - (long int)p;
    p = p + r;
    *p = *p + 8;
    printf("aaa\n");
    fflush(stdout);
    return;
}
int main(int argc, char ** argv) {
    char x;
    x=0;
    foo();
    x=100;
    printf ("x=%d\n", x);
    return 0;
}
                        
                