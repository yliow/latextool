#include <iostream>
#include <ctime>

int f(int n)
{
    if (n <= 1)
        return 1;
    else
        return f(n - 1) + f(n - 2);
}

int main()
{
    std::cout << '(';
    double start, end;
    for (int n = 0; n < 50; n += 2)
    {
        start = double(clock()) / CLOCKS_PER_SEC;
        f(n);
        end = double(clock()) / CLOCKS_PER_SEC;
        double difftime = end - start;
        std::cout << '(' << n << ',' << difftime << "), ";
        std::cout.flush();
    }
    std::cout << ')';
    std::cout << std::endl;
    return 0;
}
