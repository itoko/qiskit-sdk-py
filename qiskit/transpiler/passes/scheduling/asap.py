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

"""ASAP Scheduling."""
from collections import defaultdict
from typing import List

from qiskit.circuit import Qubit, Clbit
from qiskit.circuit.bit import Bit
from qiskit.circuit.delay import Delay
from qiskit.dagcircuit import DAGCircuit
from qiskit.transpiler.basepasses import TransformationPass
from qiskit.transpiler.exceptions import TranspilerError


class ASAPSchedule(TransformationPass):
    """ASAP Scheduling."""

    def __init__(self, durations):
        """ASAPSchedule initializer.

        Args:
            durations (InstructionDurations): Durations of instructions to be used in scheduling
        """
        super().__init__()
        self.durations = durations

    def run(self, dag, time_unit=None):  # pylint: disable=arguments-differ
        """Run the ASAPSchedule pass on `dag`.

        Args:
            dag (DAGCircuit): DAG to schedule.
            time_unit (str): Time unit to be used in scheduling: 'dt' or 's'.

        Returns:
            DAGCircuit: A scheduled DAG.

        Raises:
            TranspilerError: if the circuit is not mapped on physical qubits.
        """
        if len(dag.qregs) != 1 or dag.qregs.get('q', None) is None:
            raise TranspilerError('ASAP schedule runs on physical circuits only')

        if not time_unit:
            time_unit = self.property_set['time_unit']

        new_dag = DAGCircuit()
        for qreg in dag.qregs.values():
            new_dag.add_qreg(qreg)
        for creg in dag.cregs.values():
            new_dag.add_creg(creg)

        bit_time_available = defaultdict(int)

        def pad_with_delays(bits: List[Bit], until, unit) -> None:
            """Pad idle time-slots in ``bits`` with delays in ``unit`` until ``until``."""
            for b in bits:
                if bit_time_available[b] < until:
                    idle_duration = until - bit_time_available[b]
                    new_dag.apply_operation_back(Delay(idle_duration, unit, isinstance(b, Qubit)),
                                                 [b] if isinstance(b, Qubit) else [],
                                                 [b] if isinstance(b, Clbit) else [])

        for node in dag.topological_op_nodes():
            node_bits = node.qargs + node.cargs
            start_time = max(bit_time_available[b] for b in node_bits)
            pad_with_delays(node_bits, until=start_time, unit=time_unit)

            new_node = new_dag.apply_operation_back(node.op, node.qargs, node.cargs, node.condition)
            duration = self.durations.get(node.op, node.qargs, unit=time_unit)
            # set duration for each instruction (tricky but necessary)
            new_node.op.duration = duration
            new_node.op.unit = time_unit

            stop_time = start_time + duration
            # update time table
            for b in node_bits:
                bit_time_available[b] = stop_time

        working_bits = bit_time_available.keys()
        circuit_duration = max(bit_time_available[b] for b in working_bits)
        pad_with_delays(new_dag.qubits, until=circuit_duration, unit=time_unit)
        pad_with_delays(new_dag.clbits, until=circuit_duration, unit=time_unit)

        new_dag.name = dag.name
        new_dag.duration = circuit_duration
        new_dag.unit = time_unit
        return new_dag
