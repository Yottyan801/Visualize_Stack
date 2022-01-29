#include <stdio.h>
#include <pthread.h>

void f1(void);
void f2(void);
int counter = 0;
pthread_mutex_t mutex;

int main(void)
{
    pthread_t thread1, thread2;
    pthread_mutex_init(&mutex, NULL);
    pthread_create(&thread1, NULL, (void *)f1, NULL);
    pthread_create(&thread2, NULL, (void *)f2, NULL);

    pthread_join(thread1, NULL);
    pthread_join(thread2, NULL);
    printf("counter = %d\n", counter);

    pthread_mutex_destroy(&mutex);

    return 0;
}

void f1(void)
{
    int i;
    for (i = 0; i < 3; i++)
    {
        pthread_mutex_lock(&mutex);
        counter++;
        pthread_mutex_unlock(&mutex);
    }
}

void f2(void)
{
    int i;
    for (i = 0; i < 3; i++)
    {
        pthread_mutex_lock(&mutex);
        counter++;
        pthread_mutex_unlock(&mutex);
    }
}

//このソースコードには変数counterの宣言文がない。
//「counter = 12」が出力されるように宣言文を追加しなさい。
//解答例　11行目に int sample = 10;

//6行目 int counter;