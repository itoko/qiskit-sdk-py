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

# pylint: disable=missing-function-docstring

"""Test delay instruction for quantum circuits."""

import numpy as np
from qiskit.circuit import Delay
from qiskit.circuit import QuantumCircuit
from qiskit.circuit.exceptions import CircuitError
from qiskit.test.base import QiskitTestCase


class TestDelayClass(QiskitTestCase):
    """Test delay instruction for quantum circuits."""

    def test_keep_units_after_adding_delays_to_circuit(self):
        qc = QuantumCircuit(1)
        qc.h(0)
        qc.delay(100, 0)
        qc.delay(200, 0, unit='s')
        qc.delay(300, 0, unit='ns')
        qc.delay(400, 0, unit='dt')
        self.assertEqual(qc.data[1][0].unit, 'dt')
        self.assertEqual(qc.data[2][0].unit, 's')
        self.assertEqual(qc.data[3][0].unit, 'ns')
        self.assertEqual(qc.data[4][0].unit, 'dt')

    def test_fail_if_non_integer_duration_with_dt_unit_is_supplied(self):
        qc = QuantumCircuit(1)
        with self.assertRaises(CircuitError):
            qc.delay(0.5, 0, unit='dt')

    def test_fail_if_unknown_unit_is_supplied(self):
        qc = QuantumCircuit(1)
        with self.assertRaises(CircuitError):
            qc.delay(100, 0, unit='my_unit')

    def test_add_delay_on_single_qubit_to_circuit(self):
        qc = QuantumCircuit(1)
        qc.h(0)
        qc.delay(100, 0)
        qc.delay(200, qc.qubits[0])
        self.assertEqual(qc.data[1], (Delay(duration=100), qc.qubits, []))
        self.assertEqual(qc.data[2], (Delay(duration=200), qc.qubits, []))

    def test_to_matrix_return_identity_matrix(self):
        actual = Delay(100).to_matrix()
        expected = np.array([[1, 0],
                             [0, 1]], dtype=complex)
        self.assertTrue(np.array_equal(actual, expected))
