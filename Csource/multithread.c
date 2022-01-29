#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <pthread.h>
int global;
char string[20];
void *counter(void *arg)
{
    int i;
    pid_t pid;
    pthread_t thread_id;

    pid = getpid();
    thread_id = pthread_self();

    for (i = 0; i < 10; i++)
    {
        global++;
        printf("[%d][%d]%d\n", pid, thread_id, i);
    }
    return (arg);
}

void main()
{
    pid_t p_pid;
    int number, status;
    pthread_t thread_id1, thread_id2;
    void *result;

    p_pid = getpid();
    printf("[%d]start\n", p_pid);
    status = pthread_create(&thread_id1, NULL, counter, &number);
    printf("[%d]thread_id1=%d\n", p_pid, thread_id1);

    status = pthread_create(&thread_id2, NULL, counter, (void *)NULL);
    printf("[%d]thread_id2=%d\n", p_pid, thread_id2);

    pthread_join(thread_id1, &result);
    printf("[%d]thread_id1 = %d end\n", p_pid, thread_id1);

    pthread_join(thread_id2, &result);
    printf("[%d]thread_id2 = %d end\n", p_pid, thread_id2);

    printf("[%d]end\n", p_pid);
}
