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

"""Pass to remove delays on idle qubits."""

from qiskit.circuit.delay import Delay
from qiskit.transpiler.basepasses import TransformationPass
from qiskit.transpiler.exceptions import TranspilerError


class RemoveDelaysOnIdleQubits(TransformationPass):
    """Pass to remove delays on idle qubits."""

    def run(self, dag):
        """Remove delays on idle qubits.

        Args:
            dag (DAGCircuit): DAG to be transformed.

        Returns:
            DAGCircuit: A transformed DAG.

        Raises:
            TranspilerError: if the circuit is not mapped on physical qubits.
        """
        if dag.duration is None:
            raise TranspilerError('RemoveDelaysOnIdleQubits runs on scheduled circuits only')

        removed = False
        for q in dag.qubits:
            idling = True
            for node in dag.nodes_on_wire(q, only_ops=True):
                if not isinstance(node.op, Delay):
                    idling = False
                    break
            if idling:
                removed = True
                for node in list(dag.nodes_on_wire(q, only_ops=True)):
                    dag.remove_op_node(node)

        # need to update dag.duration when any delay is removed
        if removed:
            circuit_duration = 0
            for q in dag.qubits:
                per_qubit = sum([node.op.duration for node in dag.nodes_on_wire(q, only_ops=True)])
                circuit_duration = max(per_qubit, circuit_duration)
            dag.duration = circuit_duration

        return dag
