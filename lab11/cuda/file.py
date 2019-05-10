# ppds-labs: cuda
# Copyright (c) 2019, Milten Plescott. All rights reserved.
# SPDX-License-Identifier: MIT

import math
import numpy
from numba import cuda
from random import randint


@cuda.jit
def my_kernel(io_array):
    """
    Code for kernel.
    """
    # Thread id in a 1D block
    tx = cuda.threadIdx.x
    # Block id in a 1D grid
    ty = cuda.blockIdx.x
    # Block width, i.e. number of threads per block
    bw = cuda.blockDim.x
    # Compute index inside the array
    pos = tx + ty * bw
    # Check array boundaries
    if pos < io_array.size:
        # do the computation
        io_array[pos] *= 2


@cuda.jit
def my_kernel2(io_array):
    pos = cuda.grid(1)
    if pos < io_array.size:
        io_array[pos] *= 2


@cuda.jit
def my_kernel_2D(io_array):
    x, y = cuda.grid(2)
    if x < io_array.shape[0] and y < io_array.shape[1]:
        io_array[x, y] *= 2


@cuda.jit
def matmul(A, B, C):
    """
    Perform matrix multiplication of C = A * B
    """
    row, col = cuda.grid(2)
    if row < C.shape[0] and col < C.shape[1]:
        sum = 0.0
        for i in range(A.shape[0]):
            sum += A[row, i] * B[i, col]
        C[row, col] = sum


def fun1():
    print(cuda.gpus)

    # Create the data array - usually initialized some other way
    data = numpy.ones(256)

    # Set the number of threads in a block
    threadsperblock = 32

    # Calculate the number of thread blocks in the grid
    blockspergrid = (data.size + (threadsperblock - 1)) // threadsperblock

    print("Data shape: " + str(data.shape))
    print("Threads per block: " + str(threadsperblock))
    print("Blocks per grid: " + str(blockspergrid))

    # Now start the kernel
    my_kernel2[blockspergrid, threadsperblock](data)

    # Print the result
    print(data)


def fun2():
    data = numpy.ones((16, 16))
    threadsperblock = (16, 16)
    blockspergrid_x = math.ceil(data.shape[0] / threadsperblock[0])
    blockspergrid_y = math.ceil(data.shape[1] / threadsperblock[1])
    blockspergrid = (blockspergrid_x, blockspergrid_y)
    my_kernel_2D[blockspergrid, threadsperblock](data)
    print(data)


def fun3():
    A_rows = randint(1, 50)
    A_cols = randint(50, 100)
    B_rows = A_cols
    B_cols = randint(1, 100)
    C_rows = A_rows
    C_cols = B_cols
    A_data = numpy.random.randint(low=-100, high=100, size=(A_rows, A_cols))
    B_data = numpy.random.randint(low=-100, high=100, size=(B_rows, B_cols))
    print("A rows: " + str(A_rows))
    print("A cols: " + str(A_cols))
    print("B rows: " + str(B_rows))
    print("B cols: " + str(B_cols))
    print("C rows: " + str(C_rows))
    print("C cols: " + str(C_cols))
    # print("A data: " + str(A_data))
    # print("B data: " + str(B_data))

    A_global_mem = cuda.to_device(A_data)
    B_global_mem = cuda.to_device(B_data)
    C_global_mem = cuda.device_array((C_rows, C_cols))

    threadsperblock = (32, 32)
    blockspergrid_x = math.ceil(C_rows / threadsperblock[0])
    blockspergrid_y = math.ceil(C_cols / threadsperblock[1])
    blockspergrid = (blockspergrid_x, blockspergrid_y)

    matmul[blockspergrid, threadsperblock](A_global_mem, B_global_mem, C_global_mem)

    result = C_global_mem.copy_to_host()
    print(result)


def main():
    fun1()
    fun2()
    fun3()


if __name__ == '__main__':
    main()
