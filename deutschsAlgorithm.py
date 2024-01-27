'''
Deutsch's Algorithm solves the parity problem for 1 bit

The parity problem involves queries to a function f
- a string of n bits is passed to f which returns 0 or 1
- the solution to the problem is 1 if the number of n-bit strings that cause f to produce 1 is odd
- in the case where n=1, there are 4 possible functions:
    a:    0, 1 
    f(a): 0, 0 (constant 0)

    a:    0, 1
    f(a): 0, 1 (balanced)

    a:    0, 1
    f(a): 1, 0 (balanced)

    a:    0, 1
    f(a): 1, 1 (constant 1)

The Deutsch problem takes a random one of the above functions and produces:
- 0 if constant
- 1 if balanced

Any classical algorithm requires 2 queries to f to produce an answer
The Deutsch quantum algorithm only requires 1
'''

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


def deutsch_function(case: int):
    # generate a valid Deutsch function as a `QuantumCircuit`.
    if case not in [1, 2, 3, 4]:
        raise ValueError("`case` must be 1, 2, 3, or 4.")

    f = QuantumCircuit(2)

    # case 1: f always produces 0, so XORing it to the second qubit state does nothing
    if case == 1:
        print('case 1, generating a constant function...')

    # case 2: f produces input, so XORing to second qubit is equivalent to cx gate
    if case == 2:
        print('case 2, generating a balanced function...')
        f.cx(0, 1)

    # case 3: f negates input, so XORing to second qubit is equivalent to cx followed by x
    elif case == 3:
        print('case 3, generating a balanced function...')
        f.cx(0, 1)
        f.x(1)

    # case 4: f produces 1, so XORing it to the second qubit flips it
    elif case == 4:
        print('case 4, generating a constant function...')
        f.x(1)

    return f

def compile_circuit(function: QuantumCircuit):
    # compiles a circuit for use in Deutsch's algorithm.
    
    n = function.num_qubits - 1
    qc = QuantumCircuit(n + 1, n)

    qc.x(n) # prepare the bottom qubit in the |1> state
    qc.h(range(n + 1)) # put the qubits in superposition

    qc.barrier()
    qc.compose(function, inplace=True) # make the single query to f
    qc.barrier()

    qc.h(range(n))
    qc.measure(range(n), range(n)) # measure to get answer to problem

    return qc

# simulate and solve the problem

def deutsch_algorithm(function: QuantumCircuit):
    # determine if a Deutsch function is constant or balanced.

    qc = compile_circuit(function)

    result = AerSimulator().run(qc, shots=1, memory=True).result()
    measurements = result.get_memory()
    if measurements[0] == "0":
        return "constant"
    return "balanced"

# try all 4 possible functions:
f = deutsch_function(1)
#display(f.draw())
print(f'Deutsch\'s algorithm predicted function 1 is {deutsch_algorithm(f)}\n')

f = deutsch_function(2)
print(f.draw())
print(f'Deutsch\'s algorithm predicted function 2 is {deutsch_algorithm(f)}\n')

f = deutsch_function(3)
print(f.draw())
print(f'Deutsch\'s algorithm predicted function 3 is {deutsch_algorithm(f)}\n')

f = deutsch_function(4)
print(f.draw())
print(f'Deutsch\'s algorithm predicted function 4 is {deutsch_algorithm(f)}\n')