# Automata Theory

### Q1. Regular Expression to NFA

The input regular expression is first modified, by adding concatenation symbols where needed and enclosing paranthesis. It is then converted into its equivalent reverse Polish form so that we don't need to worry about deeply nested parantheses in the expression.

The expression is paresed left to right using a stack and an NFA is built stepwise using a slight modification to the Thompson Construction Algorithm:

1. **Union** of two NFAs A and B:
    1. Add two new states, one initial, one final.
    2. Add 4 new epsilon transitions:
        a. New initial to initial state of A
        b. New initial to initial state of B
        c. Final state of A to new final state
        c. Final state of B to new final state
    3. Mark the final states of A and B as non-final

2. **Concatenation** of two NFAs A and B:
    1. Add 1 new epsilont transitions:
        a. Final state of A to Initial state of B
    2. Mark the final state of A as non-final

3. **Kleen operation** on NFA A:
    1. Add two new states, one initial, one final.
    2. Add 4 new epsilon transitions:
        a. New initial to initial of A
        b. Final of A to new final
        c. New initial to new final
        d. Final of A to new initial
    3. Mark the final state of A as non-final

### Q2. NFA to DFA

First, the power set of the states of the NFA are generated using bit masking. Then the epsilon closure of every NFA state is computed using a Depth First Seach traversal into the NFA.

Using these two pieces, the DFA is constructed. Each state of the DFA is an element of the computed power set, i.e. a set of NFA states. Each transition in the DFA is computed as:

    For every d_state in dfa_states
      For every state in d_state
        For every input in dfa_letters
          For every ec1 in epsilon_closure(state)
              For every next_state in nfa_transition(ec1, input)
                For every ec2 in epislon_closure(next_state)
                  dfa_transition(state, action) = union(dfa_transition(state,action), ec2)

The above pseudocode is the implementation of the idea that for an NFA if the action is `a` at a given state, then the equivalent transition for any state in the DFA that contains the given state is `$* a $*`, where `$` is epsilon `*` is the kleen operator, together indicating epsilon closure, unioned across all the other NFA states in that DFA state.

### Q3. DFA to Regular Expression

The method used for this conversion was the **Brzozowski Alegbraic Method**. It is an algorithmic way of sovling the set of expressions, one for each state, in a way similar to how we solve them by hand. The key feature of Brzozowski is the order in which it solves the equations, reducing the number of extra computations it takes to get to the end result. It uses Areden's rule to simplify the given expressions. This method outputs a vector of regular expressions, one for each state. The regular expression for the initial state describes the entire NFA. 

### Q4. DFA to Minimal DFA

First, all states that are unreachable from the start state are removed from the DFA using a Depth First Search traversal from the initial state. Only the reachable states and their corresponding transitions are retained in the DFA.

We then use the Myhill-Nerode Table Filling method that detects which paris of states are redundant, adn merges those states. If paris are overlapping, they are also merged into a single state. The transitions are also updated and the state that contains the original initial state becomes the new initial state and the states that contain any of the original final states become the new final states.
