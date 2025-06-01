from IPython.display import clear_output
clear_output()

def InitializeQubits(circuit, n, m):

    circuit.h(range(n))
    circuit.x(n+m-1)

from qiskit import QuantumCircuit

def CircuitMod15(a, power):

    if a not in [2,4,7,8,11,13]:
        raise ValueError("Broj a mora biti jednak 2,4,7,8,11 ili 13!")
    U = QuantumCircuit(4)        
    for iteration in range(power):
        if a in [2,13]:
            U.swap(2,3)
            U.swap(1,2)
            U.swap(0,1)
        if a in [7,8]:
            U.swap(0,1)
            U.swap(1,2)
            U.swap(2,3)
        if a in [4, 11]:
            U.swap(1,3)
            U.swap(0,2)
        if a in [7,11,13]:
            for q in range(4):
                U.x(q)
    U = U.to_gate()
    U.name = "%i^%i mod 15" % (a, power)
    c_U = U.control()
    return c_U

def ModularExponentiation(circuit, n, m, a):
    
    for x in range(n):
        exponent = 2**x
        circuit.append(CircuitMod15(a, exponent), 
                     [x] + list(range(n, n+m)))

from qiskit.circuit.library import QFT

def QFTInverse(circuit, qubits):
    
    circuit.append(QFT(len(qubits), do_swaps=True).inverse(), qubits)

def ExecuteQPE(n, m, a):

    shor = QuantumCircuit(n+m, n)

    # Hadamard i negacija
    InitializeQubits(shor, n, m)
    shor.barrier()

    # modularni operator
    ModularExponentiation(shor, n, m, a)
    shor.barrier()

    # transponirana kvantna Fourierova transformacija
    QFTInverse(shor, range(n))

    # mjerimo izlaz
    shor.measure(range(n), range(n))
    
    return shor

# pokretanje kvantnog algoritma
n = 4; m = 4; a = 7
mycircuit = ExecuteQPE(n, m, a)
print("\nKvantni sklop:")
print(mycircuit)

# pokretanje simulatora
from qiskit import Aer, execute
simulator = Aer.get_backend('qasm_simulator')
counts = execute(mycircuit, backend=simulator, shots=1000).result().get_counts(mycircuit)

# klasicni post-proces
from math import gcd

print(f"Rezultati:\n")
for i in counts:
    r = int(i, 2)
    print(f"Mjerenje: {r}")
    
    if r % 2 != 0:
        print("Neuspjeh. Izmjerena vrijednost je neparna.")
        continue
    x = int((a ** (r/2)) % 15)
    if (x + 1) % 15 == 0:
        print("Neuspjeh. Vrijedi: x + 1 = 0 (mod N) za x = a^(r/2) (mod N).")
        continue
    guesses = gcd(x + 1, 15), gcd(x - 1, 15)
    print(f"Uspjeh! Potencijalni faktori: {guesses}")