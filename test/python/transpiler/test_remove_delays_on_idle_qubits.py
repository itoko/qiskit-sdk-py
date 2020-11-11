# This code is part of Qiskit.
#
# (C) Copyright IBM 2020.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""Test RemoveDelaysOnIdleQubits pass"""

import unittest

from qiskit import QuantumCircuit
from qiskit.converters import circuit_to_dag, dag_to_circuit
from qiskit.transpiler.passes.utils import RemoveDelaysOnIdleQubits

from qiskit.test import QiskitTestCase


class TestRemoveDelaysOnIdleQubits(QiskitTestCase):
    """ Test RemoveDelaysOnIdleQubits pass. """

    def test_simple_circuit(self):
        """ Remove delays on ancilla qubits.
        """
        qc = QuantumCircuit(3)
        qc.delay(100, 0)
        qc.h(0)
        qc.data[1][0].duration = 200
        qc.delay(300, 1)
        qc.delay(300, 2)
        qc.duration = 300  # scheduled circuit
        dag = circuit_to_dag(qc)

        expected = QuantumCircuit(3)
        expected.delay(100, 0)
        expected.h(0)
        expected.data[1][0].duration = 200
        expected.duration = 300

        pass_ = RemoveDelaysOnIdleQubits()
        after = pass_.run(dag)

        self.assertEqual(dag_to_circuit(after), expected)
        self.assertEqual(after.duration, expected.duration)

    def test_circuits_with_only_delays(self):
        """ Remove all delays in circuit with only delays.
        """
        qc = QuantumCircuit(2)
        qc.delay(100, 0)
        qc.delay(100, 0)
        qc.delay(200, 1)
        qc.duration = 200  # scheduled circuit
        dag = circuit_to_dag(qc)

        expected = QuantumCircuit(2)
        expected.duration = 0  # empty scheduled circuit

        pass_ = RemoveDelaysOnIdleQubits()
        after = pass_.run(dag)

        self.assertEqual(after, circuit_to_dag(expected))
        self.assertEqual(after.duration, expected.duration)


if __name__ == '__main__':
    unittest.main()
