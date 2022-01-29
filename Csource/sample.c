typedef struct
{
    char name[10];
    int number;
} Yoshizuka;

int global;
int main()
{
    int a = 30;
    static int b = 40;
    char *d;
    int c[10];
    Yoshizuka yoshi;
    yoshi.name[0] = "Y";
    yoshi.number = 20;
    a = 20;
    global = 40;
    return 0;
}