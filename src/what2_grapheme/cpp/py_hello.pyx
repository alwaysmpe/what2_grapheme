# distutils: language = c++

cdef extern from "hello.cpp":
    void Helloworld()

def C_Helloworld():
    Helloworld()

#c_helloworld()