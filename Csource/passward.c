#include<stdio.h>
#include<stdlib.h>
#include<string.h>
 
int check_passwd(char *passwd){
  char buf[16];
  int auth_flag = 0;
  
  strcpy(buf, passwd);
  if(strcmp(buf, "iloveyou")==0)
    auth_flag = 1;
 
  return auth_flag;
}
 
int main(){
    char pass[8];
    scanf("%s",pass);
    printf("[-]How to use: %s <password>\n", pass);
 
  if(check_passwd(pass))
    printf("[+]Access Sucsess\n");
  else printf("[-]Access Denied\n");
 
  return 0;
}