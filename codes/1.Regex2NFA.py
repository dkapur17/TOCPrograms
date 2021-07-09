import re
import json
import sys
from uuid import uuid4

precedence = {
    '*': 3,
    '.': 2,
    '+': 1
}


class PopException(Exception):
    pass


class Stack:
    def __init__(self):
        self.__data__ = []
        self.__size__ = 0

    def push(self, val):
        self.__data__ = [val] + self.__data__
        self.__size__ += 1

    def top(self):
        return self.__data__[0]

    def pop(self):
        if self.__size__:
            self.__data__ = self.__data__[1:]
            self.__size__ -= 1
        else:
            raise PopException

    def size(self):
        return self.__size__

    def empty(self):
        return self.__size__ == 0


def match_parentheses(regex):
    tracker = 0
    for c in regex:
        if c == '(':
            tracker += 1
        elif c == ')':
            tracker -= 1
        if tracker < 0:
            return False
    return tracker == 0


def add_concat_symbol(regex):
    concat_regex = '('
    for i in range(len(regex) - 1):
        concat_regex += regex[i]
        if regex[i] not in '()*+' and regex[i + 1] not in '()*+':
            concat_regex += '.'
        elif regex[i] == ')' and regex[i + 1] == '(':
            concat_regex += '.'
        elif regex[i] not in '()*+' and regex[i + 1] == '(':
            concat_regex += '.'
        elif regex[i] == ')' and regex[i + 1] not in '()*+':
            concat_regex += '.'
        elif regex[i] == '*' and regex[i + 1] not in ')*+':
            concat_regex += '.'
    concat_regex += regex[-1] + ')'
    return concat_regex


def convert_to_postfix(regex):
    postfix = ''
    s = Stack()

    for c in regex:
        if c not in '()+.':
            postfix += c
        elif c == '(':
            s.push(c)
        elif c == ')':
            while(s.top() != '('):
                postfix += s.top()
                s.pop()
            s.pop()
        else:
            if s.empty():
                s.push(c)
            else:
                if s.top() == '(':
                    s.push(c)
                elif precedence[c] > precedence[s.top()]:
                    s.push(c)
                elif precedence[c] == precedence[s.top()]:
                    postfix += c
                else:
                    while not s.empty() and s.top() != '(' and precedence[c] < precedence[s.top()]:
                        postfix += s.top()
                        s.pop()
                    s.push(c)
    while not s.empty():
        postfix += s.top()
        s.pop()

    return postfix


class NFA:
    def __init__(self, alphabet_set, init_state, accept_state):
        self.states = []
        self.alphabet = list(set(alphabet_set + ['$']))
        self.transitions = {}
        self.init_state = init_state
        self.accept_state = accept_state

    def add_state(self, s):
        self.states.append(s)
        self.transitions[s] = {}
        for input in self.alphabet:
            self.transitions[s][input] = []

    def add_transition(self, s, a, ns):
        self.transitions[s][a].append(ns)

    def print_data(self):
        print("=STATES=")
        for state in self.states:
            print(state)
        print("=ALPHABET=")
        for c in self.alphabet:
            if c != '$':
                print(c)
        print("=INITIAL STATE=")
        print(self.init_state)
        print("=ACCEPT STATES=")
        print(self.accept_state)
        print("=TRANSITIONS=")
        for state in self.transitions.keys():
            for action in self.transitions[state].keys():
                for next_state in self.transitions[state][action]:
                    print(f"{state}:{action}>{next_state}")

    def write_to_file(self):
        out_nfa = {}
        out_nfa['states'] = [state for state in self.states]
        out_nfa['letters'] = [
            letter for letter in self.alphabet if letter != '$']
        out_nfa['transition_function'] = []
        for state in self.transitions.keys():
            for action in self.transitions[state].keys():
                for next_state in self.transitions[state][action]:
                    out_nfa['transition_function'].append(
                        [state, action, next_state])
        out_nfa['start_states'] = [self.init_state]
        out_nfa['final_states'] = [self.accept_state]

        with open(sys.argv[2], 'w+') as f:
            json.dump(out_nfa, f, indent=4)

    def clean(self):

        state_alias = {}

        for i, state in enumerate(self.states):
            state_alias[state] = f"q{i}"

        self.states = [state_alias[state] for state in self.states]

        aliased_transitions = {}

        for state in self.transitions.keys():
            aliased_transitions[state_alias[state]
                                ] = {}
            for action in self.transitions[state]:
                if len(self.transitions[state][action]):
                    aliased_transitions[state_alias[state]][action] = [
                        state_alias[s] for s in self.transitions[state][action]]

        self.transitions = aliased_transitions

        self.init_state = state_alias[self.init_state]
        self.accept_state = state_alias[self.accept_state]


def concat(N1, N2):
    alphabet = (N1.alphabet + N2.alphabet)
    init_state = N1.init_state
    accept_state = N2.accept_state
    N = NFA(alphabet, init_state, accept_state)
    for state in N1.states + N2.states:
        N.add_state(state)

    N.transitions = {**(N1.transitions), **(N2.transitions)}
    # Add transition based on Thompson construction
    N.add_transition(N1.accept_state, '$', N2.init_state)

    return N


def union(N1, N2):
    alphabet = (N1.alphabet + N2.alphabet)
    init_state = str(uuid4())
    accept_state = str(uuid4())
    N = NFA(alphabet, init_state, accept_state)
    for state in N1.states + N2.states:
        N.add_state(state)

    N.transitions = {**(N1.transitions), **(N2.transitions)}

    N.add_state(init_state)
    N.add_state(accept_state)

    # Add transitions based on Thompson Construction
    N.add_transition(init_state, '$', N1.init_state)
    N.add_transition(init_state, '$', N2.init_state)
    N.add_transition(N1.accept_state, '$', accept_state)
    N.add_transition(N2.accept_state, '$', accept_state)

    return N


def kleen(N1):
    alphabet = N1.alphabet
    init_state = str(uuid4())
    accept_state = str(uuid4())
    N = NFA(alphabet, init_state, accept_state)
    for state in N1.states:
        N.add_state(state)
    N.transitions = {**(N1.transitions)}

    N.add_state(init_state)
    N.add_state(accept_state)

    # Add transitions based on Thompson Construction
    N.add_transition(init_state, '$', N1.init_state)
    N.add_transition(N1.accept_state, '$', accept_state)
    N.add_transition(init_state, '$', accept_state)
    N.add_transition(N1.accept_state, '$', N1.init_state)

    return N


def readInputFile():
    with open(sys.argv[1]) as f:
        ip = json.load(f)
    return ip['regex']


def main():

    if(len(sys.argv) != 3):
        print("Usage: q1.py infile outfile")
        exit()
    try:
        regex = readInputFile()
    except:
        print(
            "Error reading input file. Please ensure it is present and correctly formatted.")
        exit()

    if len(re.findall(r'[^\w\+\*\(\)\$]', regex)):
        print("ERROR: Malformed Regular Expression")
        exit()
    elif not match_parentheses(regex):
        print("ERROR: Malformed Regular Expression")
        exit()
    regex = add_concat_symbol(regex)
    try:
        regex = convert_to_postfix(regex)
    except PopException:
        print("ERROR: Malformed Regular Expression")
        exit()
    NFA_Stack = Stack()
    for c in regex:
        if c not in '+*.':
            state1 = str(uuid4())
            state2 = str(uuid4())
            new_NFA = NFA([c], state1, state2)
            new_NFA.add_state(state1)
            new_NFA.add_state(state2)
            new_NFA.add_transition(state1, c, state2)
            NFA_Stack.push(new_NFA)
        # Concatenate
        elif c == '.':
            N2 = NFA_Stack.top()
            NFA_Stack.pop()
            N1 = NFA_Stack.top()
            NFA_Stack.pop()
            N = concat(N1, N2)
            NFA_Stack.push(N)
        # Union
        elif c == '+':
            N2 = NFA_Stack.top()
            NFA_Stack.pop()
            N1 = NFA_Stack.top()
            NFA_Stack.pop()
            N = union(N1, N2)
            NFA_Stack.push(N)
        # Kleen
        elif c == '*':
            N1 = NFA_Stack.top()
            NFA_Stack.pop()
            N = kleen(N1)
            NFA_Stack.push(N)

    N = NFA_Stack.top()
    N.clean()
    N.write_to_file()


if __name__ == "__main__":
    main()
