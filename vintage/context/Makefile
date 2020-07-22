all : test_ctx

test_ctx : contextu.c test_ctx.cpp
	gcc -g -Wall -o $@ $^

test_swap : contextu.c test_swap.cpp
	gcc -g -Wall -o $@ $^

clean :
	rm test_ctx
	rm test_swap
