#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

#define N 1000000
#define A 2.0

double X[N], Y[N];

void* daxpy_thread(void* arg) {
    int thread_id = *(int*)arg;
    int chunk_size = N / 4;
    int start_idx = thread_id * chunk_size;
    int end_idx = (thread_id + 1) * chunk_size;

    for (int i = start_idx; i < end_idx; i++) {
        Y[i] = A * X[i] + Y[i];
    }

    return NULL;
}

int main() {
    for (int i = 0; i < N; i++) {
        X[i] = i * 1.0;
        Y[i] = i * 2.0;
    }

    pthread_t threads[4];
    int thread_ids[4];

    // Create threads
    for (int i = 0; i < 4; i++) {
        thread_ids[i] = i;
        pthread_create(&threads[i], NULL, daxpy_thread, &thread_ids[i]);
    }

    // Join threads
    for (int i = 0; i < 4; i++) {
        pthread_join(threads[i], NULL);
    }

    for (int i = 0; i < 10; i++) {
        printf("Y[%d] = %f\n", i, Y[i]);
    }

    return 0;
}