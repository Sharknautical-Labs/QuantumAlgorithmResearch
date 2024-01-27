'''
The goal of the Deutsch-Jozsa problem is to determine if a function is balanced or constant
The function in this problem can have an arbitrary number of bits as input
- functions that are neither balanced nor constant are not considered
- n measurements will be made, and if any one of them are 1, the output is 1
- output: 0 if f is constant, 1 if f is balanced

Just as with Deutsch's algorithm, this algorithm can solve the problem with only 1 query
A classical algorithm to solve the problem will take 2^(n-1)+1 queries in the worst case
'''

from qiskit import QuantumCircuit
import numpy as np
from qiskit_aer import AerSimulator


def add_cx(qc, bit_string):
    for qubit, bit in enumerate(reversed(bit_string)):
        if bit == "1":
            qc.x(qubit)
    return qc

# create a random Deutsch-Jozsa function, with a 50% chance of being balanced and 50% change of being constant
def dj_function(num_qubits):
    qc = QuantumCircuit(num_qubits + 1)

    if np.random.randint(0, 2):
        # flip output qubit with 50% chance
        # if the function is constant it will always output 1 if this is run, and always 0 if not 
        qc.x(num_qubits)
    if np.random.randint(0, 2):
        # return constant circuit with 50% chance, ie input does not affect output
        print('generating a constant function...')
        return qc
    else:
        # balanced function
        print('generating a random balanced function...')

        # randomly select the 50% of inputs that will flip the input
        on_states = np.random.choice(
            range(2**num_qubits),  # numbers to sample from
            2**num_qubits // 2,  # number of samples
            replace=False,  # makes sure states are only sampled once
        )

        for state in on_states:
            qc.barrier()
            # use x gates to flip the output if the inputs match one of the strings in on_states
            qc = add_cx(qc, f"{state:0b}")
            qc.mcx(list(range(num_qubits)), num_qubits)
            qc = add_cx(qc, f"{state:0b}")

        qc.barrier()

        return qc
    
def compile_circuit(function: QuantumCircuit):
    # generate a circuit for use in the Deutsch-Jozsa algorithm
    n = function.num_qubits - 1
    qc = QuantumCircuit(n + 1, n) # n+1 qubits, n measurements
    qc.x(n) # the last qubit must be prepared in the |1> state
    qc.h(range(n + 1))
    qc.compose(function, inplace=True) # apply 1 query gate
    qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc

def dj_algorithm(function: QuantumCircuit):
    # determine if a Deutsch-Jozsa function is constant or balanced using the Deutsch-Jozsa algorithm
    qc = compile_circuit(function)

    result = AerSimulator().run(qc, shots=1, memory=True).result()
    measurements = result.get_memory()
    if "1" in measurements[0]: # if any one of the outputs are 1, the function is balanced
        return "balanced"
    else:
        return "constant"
    
def dj_classical_algorithm(function: QuantumCircuit):
    # determine if a Deutsch-Jozsa function is constant or balanced using a classical deterministic algorithm
    # generate the first 2^(n-1)+1 inputs to try
    n = function.num_qubits - 1
    try_states = range(2**(n-1)+1)

    # iterate over the try_states and check if they all produce the same output or not
    num_queries = 0
    outputs = []
    for state in try_states:
        c = QuantumCircuit(n+1, 1) # n+1 bits, 1 measurement
        c = add_cx(c, f"{state:0b}") # prepare the circuit in state

        c.compose(function, inplace=True) # apply 1 query gate
        num_queries += 1

        # get the output of the function
        c.measure(n, 0)
        result = AerSimulator().run(c, shots=1, memory=True).result().get_memory()[0]

        # check to see if this output is different from previous outputs
        if outputs and not result in outputs:
            return ("balanced", num_queries)
        else:
            outputs.append(result)
    else:
        return ("constant", num_queries)
    
# show that the quantum algorithm can get the correct result with fewer queries than a deterministic classical algorithm
f = dj_function(3)
print(f.draw())
print(f'The Deutsch-Jozsa algorithm predicted the function is {dj_algorithm(f)} in 1 query')
classical_result = dj_classical_algorithm(f)
print(f'The classical algorithm determined the function is {classical_result[0]} in {classical_result[1]} queries')