CXX ?= c++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra -pedantic

.PHONY: all check clean

all: check_dictionary

check_dictionary: src/check_dictionary.cpp
	$(CXX) $(CXXFLAGS) -o $@ $<

check: check_dictionary
	./check_dictionary

clean:
	rm -f check_dictionary
