import json
import sys


class DFA:
    def __init__(self, states, alphabet, transitions, start_states, accept_states):
        self.states = states
        self.alphabet = sorted(alphabet)

        self.transitions = {}
        for state in self.states:
            self.transitions[state] = {}

        for transition in transitions:
            self.transitions[transition[0]][transition[1]] = transition[2]

        self.init_states = start_states

        self.accept_states = sorted(accept_states)

    def gen_regex(self):

        A = [['' for _ in range(len(self.states))]
             for _ in range(len(self.states))]
        B = ['' for _ in range(len(self.states))]

        for i in range(len(self.states)):
            s = self.states[i]
            if s in self.accept_states:
                B[i] = '$'

            for a in self.transitions[s]:
                ns = self.transitions[s][a]
                j = self.states.index(ns)
                A[i][j] = a if A[i][j] == '' else self.union(A[i][j], a)

        for n in range(len(self.states) - 1, -1, -1):
            if A[n][n] != '':
                B[n] = self.concat(self.kleen(A[n][n]), B[n])
                for j in range(n):
                    A[n][j] = self.concat(self.kleen(A[n][n]), A[n][j])

            for i in range(n):
                if A[i][n] != '':
                    B[i] = self.union(B[i], self.concat(A[i][n], B[n]))
                    for j in range(n):
                        A[i][j] = self.union(
                            A[i][j], self.concat(A[i][n], A[n][j]))

        self.regex = B[0]

    def kleen(self, r):
        if r in ['', '$']:
            return '$'
        elif r in self.alphabet:
            return f'{r}*'
        elif r[0] == '(' and r[-1] == ')':
            return f'{r}*'
        else:
            return f'({r})*'

    def union(self, r1, r2):
        if r1 == '' or r2 == '':
            return r1 + r2
        else:
            return f'({r1}+{r2})'

    def concat(self, r1, r2):
        if r1 == '' or r2 == '':
            return ''
        elif r1 == '$' and r2 != '$':
            return r2
        elif r1 != '$' and r2 == '$':
            return r1
        elif r1 == '$' and r2 == '$':
            return '$'
        else:
            return f'{r1}{r2}'

    def print_data(self):
        print("==STATES==")
        for state in self.states:
            print(state)
        print("==ALPHABET==")
        for letter in self.alphabet:
            print(letter)
        print("==TRANSITIONS==")
        for state in self.states:
            for letter in self.transitions[state].keys():
                ns = self.transitions[str(state)][letter]
                print(
                    f"{state if state != set() else '{}'}:{letter}>{ns if ns != set() else '{}' }")
        print("==INITIAL STATE==")
        for state in self.init_states:
            print(state)
        print("==ACCEPT STATES==")
        for state in self.accept_states:
            print(state)

    def write_to_file(self):
        regex_data = {'regex': self.regex}
        with open(sys.argv[2], 'w+') as f:
            json.dump(regex_data, f, indent=4)


def read_DFA_from_file():
    with open(sys.argv[1]) as f:
        dfa_data = json.load(f)

    # Put the init_state at the start of the list of states
    init_state = dfa_data['start_states'][0]
    dfa_data['states'] = list(
        filter(lambda s: s != init_state, dfa_data['states']))
    dfa_data['states'] = [init_state] + dfa_data['states']

    dfa = DFA(dfa_data['states'], dfa_data['letters'], dfa_data['transition_function'],
              dfa_data['start_states'], dfa_data['final_states'])

    return dfa


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 q3.py infile outfile")
        exit()

    dfa = read_DFA_from_file()
    dfa.gen_regex()
    dfa.write_to_file()


if __name__ == "__main__":
    main()
