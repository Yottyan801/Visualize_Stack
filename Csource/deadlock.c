/*
 *  sample program
 *  Deadlock test program
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <pthread.h>

#define MAX_THREADS 3
#define MAX_CNT 10000
int grobal_cnt;
pthread_mutex_t mutex;
void *thread(void *);
static void countup(void);

int main(void)
{
    int i = 0;
    pthread_t thread_id[MAX_THREADS];
    void *thread_return;

    printf("sample program(%s) start\n", __FILE__);
    pthread_mutex_init(&mutex, NULL);
    /* create new threads */
    for (i = 0; i < MAX_THREADS; i++)
    {
        if (pthread_create(&thread_id[i], NULL, thread, NULL) < 0)
        {
            perror("pthread_create error");
            exit(1);
        }
    }

    /* wait for the end of threads */
    for (i = 0; i < MAX_THREADS; i++)
    {
        if (pthread_join(thread_id[i], &thread_return) < 0)
        {
            perror("pthread_join error");
            exit(1);
        }
    }
    printf("grobal_cnt = %d\n", grobal_cnt);
    return 0;
}
void *thread(void *arg)
{
    int i = 0;
    pthread_t thread_id = pthread_self();

    printf("thread[%lx] start\n", thread_id);
    /* counter increment */
    for (i = 0; i < MAX_CNT; i++)
    {
        pthread_mutex_lock(&mutex);
        countup();
        pthread_mutex_unlock(&mutex);
    }
    printf("thread[%lx] end\n", pthread_self());
    pthread_exit(0);
}
static void countup(void)
{
    int cnt = 0;
    pthread_mutex_lock(&mutex);
    cnt = grobal_cnt;
    cnt++;
    grobal_cnt = cnt;
    pthread_mutex_unlock(&mutex);
    return;
}