import json
import sys


class NFA:
    def __init__(self, alphabet_set, init_states, accept_states):
        self.states = []
        self.alphabet = list(set(alphabet_set + ['$']))
        self.transitions = {}
        self.init_states = init_states
        self.accept_states = accept_states

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
        print("=INITIAL STATES=")
        for state in self.init_states:
            print(state)
        print("=ACCEPT STATES=")
        for state in self.accept_states:
            print(state)
        print("=TRANSITIONS=")
        for state in self.transitions.keys():
            for action in self.transitions[state].keys():
                for next_state in self.transitions[state][action]:
                    print(f"{state}:{action}>{next_state}")


class DFA:
    def __init__(self, states, alphabet_set, transitions, init_states, accept_states):
        self.states = states
        self.alphabet = alphabet_set
        self.transitions = transitions
        self.init_states = init_states
        self.accept_states = accept_states

    def write_to_file(self):
        out_dfa = {}
        out_dfa['states'] = self.states
        out_dfa['letters'] = [letter for letter in self.alphabet]
        out_dfa['transition_function'] = self.transitions
        out_dfa['start_states'] = [self.init_states]
        out_dfa['final_states'] = self.accept_states

        with open(sys.argv[2], 'w+') as f:
            json.dump(out_dfa, f, indent=4)


def load_NFA_from_file():
    with open(sys.argv[1]) as f:
        nfa_data = json.load(f)

    nfa = NFA(nfa_data['letters'], nfa_data['start_states'],
              nfa_data['final_states'])

    for state in nfa_data['states']:
        nfa.add_state(state)

    for transition in nfa_data['transition_function']:
        s = transition[0]
        i = transition[1]
        ns = transition[2]
        nfa.add_transition(s, i, ns)

    return nfa


def gen_DFA_states(nfa_states):

    state_count = 2**(len(nfa_states))
    dfa_states = []

    for i in range(state_count):
        state = []
        mask = 1
        idx = 0
        while mask <= i:
            if i & mask:
                state.append(nfa_states[idx])
            mask <<= 1
            idx += 1

        dfa_states.append(sorted(state))

    return dfa_states


def epsilon_traverse(curr_state, ec_set, transition, visited):

    if visited[curr_state]:
        return

    visited[curr_state] = True

    if '$' not in transition[curr_state].keys():
        return

    for next_state in transition[curr_state]['$']:
        ec_set.append(next_state)
        epsilon_traverse(next_state, ec_set, transition, visited)


def compute_ec(nfa):

    ec = {}

    for state in nfa.states:
        ec[state] = [state]
        visited = {}
        for s in nfa.states:
            visited[s] = False
        epsilon_traverse(state, ec[state], nfa.transitions, visited)
        ec[state] = sorted(ec[state])

    return ec


def construct_DFA(nfa, dfa_states, epislon_closure):

    alphabet = [letter for letter in nfa.alphabet if letter != '$']

    dfa_transition = {}
    for dfa_state in dfa_states:

        state_name = str(dfa_state)
        dfa_transition[state_name] = {}

        for action in alphabet:

            dfa_transition[state_name][action] = []

            for state in dfa_state:

                for ec1_state in epislon_closure[state]:
                    if action in nfa.transitions[ec1_state].keys():
                        for next_state in nfa.transitions[ec1_state][action]:
                            for ec2_state in epislon_closure[next_state]:
                                dfa_transition[state_name][action].append(
                                    ec2_state)

            dfa_transition[state_name][action] = sorted(
                list(set(dfa_transition[state_name][action])))

    transition_table = []
    for dfa_state in dfa_states:
        state = dfa_state
        for action in alphabet:
            next_state = dfa_transition[str(dfa_state)][action]
            transition_table.append([state, action, next_state])

    init_state = []
    for state in nfa.init_states:
        init_state += epislon_closure[state]

    init_state = sorted(list(set(init_state)))

    accept_states = []
    for nfa_accept_state in nfa.accept_states:
        for state in dfa_states:
            if nfa_accept_state in state:
                accept_states.append(state)

    dfa = DFA(dfa_states, alphabet, transition_table,
              init_state, accept_states)

    return dfa


def main():

    if(len(sys.argv) != 3):
        print("Usage: q1.py infile outfile")
        exit()
    try:
        nfa = load_NFA_from_file()
    except:
        print(
            "Error reading input file. Please ensure it is present and correctly formatted")
        exit()

    dfa_states = gen_DFA_states(nfa.states)
    epislon_closure = compute_ec(nfa)
    dfa = construct_DFA(nfa, dfa_states, epislon_closure)

    dfa.write_to_file()


if __name__ == "__main__":
    main()
