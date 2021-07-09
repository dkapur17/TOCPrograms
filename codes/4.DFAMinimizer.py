import json
import sys


class DFA:
    def __init__(self, states, alphabet, transitions, start_states, accept_states):
        self.states = sorted(states)
        self.alphabet = sorted(alphabet)

        self.transitions = {}
        for state in self.states:
            self.transitions[state] = {}

        for transition in transitions:
            self.transitions[transition[0]][transition[1]] = transition[2]

        self.init_states = start_states

        self.accept_states = sorted(accept_states)

    def print_data(self):
        print("==STATES==")
        for state in self.states:
            print(state)
        print("==ALPHABET==")
        for letter in self.alphabet:
            print(letter)
        print("==TRANSITIONS==")
        for state in self.states:
            for letter in self.alphabet:
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
        out_dfa = {}
        out_dfa['states'] = self.states
        out_dfa['letters'] = self.alphabet
        out_dfa['transition_function'] = []
        for state in self.states:
            for action in self.alphabet:
                next_state = self.transitions[str(state)][action]
                out_dfa['transition_function'].append(
                    [state, action, next_state])
        out_dfa['start_states'] = self.init_states
        out_dfa['final_states'] = self.accept_states

        with open(sys.argv[2], 'w+') as f:
            json.dump(out_dfa, f, indent=4)


def traverse(curr_state, transitions, reachable_states, visited):
    if visited[curr_state]:
        return

    visited[curr_state] = True
    reachable_states.append(curr_state)

    for action in transitions[curr_state].keys():
        next_state = transitions[curr_state][action]
        traverse(next_state, transitions, reachable_states, visited)


def read_DFA_from_file_and_clean():
    with open(sys.argv[1]) as f:
        dfa_data = json.load(f)

    all_states = [state for state in dfa_data['states']]

    reachable_states = []

    visited = {}
    all_transitions = {}

    for state in all_states:
        all_transitions[state] = {}
        visited[state] = False

    for transition in dfa_data['transition_function']:
        all_transitions[transition[0]][transition[1]] = transition[2]

    for start_state in dfa_data['start_states']:
        traverse(start_state, all_transitions, reachable_states, visited)

    req_transitions = []
    for transition in dfa_data['transition_function']:
        s = transition[0]
        a = transition[1]
        ns = transition[2]
        if s in reachable_states and ns in reachable_states:
            req_transitions.append(transition)

    req_final_states = []
    for final_state in dfa_data['final_states']:
        if final_state in reachable_states:
            req_final_states.append(final_state)

    dfa = DFA(reachable_states, dfa_data['letters'],
              req_transitions, dfa_data['start_states'], req_final_states)

    return dfa


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 q4.py infile outfile")
        exit()

    dfa = read_DFA_from_file_and_clean()

    n = len(dfa.states)
    filling_table = [['' for _ in range(n)] for _ in range(n)]

    for i in range(n):
        for j in range(i):
            p = dfa.states[i]
            q = dfa.states[j]
            if (p in dfa.accept_states and q not in dfa.accept_states) or (p not in dfa.accept_states and q in dfa.accept_states):
                filling_table[i][j] = True
            else:
                filling_table[i][j] = False

    while True:
        changed = False
        for i in range(n):
            for j in range(i):
                if not filling_table[i][j]:
                    p = dfa.states[i]
                    q = dfa.states[j]
                    for letter in dfa.alphabet:
                        np = dfa.transitions[p][letter]
                        nq = dfa.transitions[q][letter]
                        x = dfa.states.index(np)
                        y = dfa.states.index(nq)
                        if filling_table[x][y] or filling_table[y][x]:
                            filling_table[i][j] = True
                            changed = True
        if not changed:
            break

    merged_states = []

    for i in range(n):
        for j in range(i):
            if not filling_table[i][j]:
                p = dfa.states[i]
                q = dfa.states[j]

                p_index = -1
                q_index = -1
                for k in range(len(merged_states)):
                    if p in merged_states[k]:
                        p_index = k
                    if q in merged_states[k]:
                        q_index = k

                if p_index == - 1 and q_index == -1:
                    merged_states.append([p, q])
                elif p_index == -1 and q_index != -1:
                    merged_states[q_index].append(p)
                elif p_index != -1 and q_index == -1:
                    merged_states[p_index].append(q)

    for i in range(len(merged_states)):
        merged_states[i] = sorted(merged_states[i])

    merged_aliases = {}

    for merged_state in merged_states:
        for state in merged_state:
            merged_aliases[state] = merged_state

    for state in dfa.states:
        if state not in merged_aliases.keys():
            merged_aliases[state] = [state]

    new_state_list = []
    for state in merged_aliases.values():
        if state not in new_state_list:
            new_state_list.append(state)

    dfa.states = new_state_list

    new_transitions = {}

    for state in dfa.transitions.keys():
        new_transitions[str(merged_aliases[state])] = {}

        for action in dfa.alphabet:
            next_state = dfa.transitions[state][action]
            new_transitions[str(merged_aliases[state])
                            ][action] = merged_aliases[str(next_state)]

    dfa.transitions = new_transitions

    new_init_states = []
    for init_state in dfa.init_states:
        for state in dfa.states:
            if init_state in state and state not in new_init_states:
                new_init_states.append(state)

    dfa.init_states = new_init_states

    new_accept_states = []

    for s1 in dfa.accept_states:
        for s2 in dfa.states:
            if s1 in s2 and s2 not in new_accept_states:
                new_accept_states.append(s2)

    dfa.accept_states = new_accept_states

    dfa.write_to_file()


if __name__ == "__main__":
    main()
