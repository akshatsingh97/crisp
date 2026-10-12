"""Gate evaluation for the Crisp evaluation suite. Pure functions, no I/O."""
import operator

OPS = {"<=": operator.le, ">=": operator.ge, "<": operator.lt, ">": operator.gt, "==": operator.eq}


def evaluate(gates, metrics, suites):
    """Return one result per gate: {"id", "name", "value", "target", "status"}.

    status is PASS, FAIL, INCOMPLETE, or SKIP.
    - SKIP: the gate's suite did not run, or the metric does not apply (None).
    - INCOMPLETE: the suite ran but some of its data is missing (for example, a
      model call failed). INCOMPLETE counts as a failure: a gate never passes on
      partial data.
    A gate with suite "all" runs whenever any suite ran. It reads only the generated answers,
    so it is incomplete only when an answer is missing (incomplete_generation).
    """
    incomplete = set(metrics.get("incomplete_suites", []))
    results = []
    for gate in gates:
        value = metrics.get(gate["metric"])
        ran = gate["suite"] == "all" or gate["suite"] in suites
        if not ran:
            status = "SKIP"
        elif gate["suite"] in incomplete or (gate["suite"] == "all" and metrics.get("incomplete_generation")):
            status = "INCOMPLETE"
        elif value is None:
            status = "SKIP"  # not applicable, for example no code scenario in a quick run
        else:
            status = "PASS" if OPS[gate["op"]](value, gate["value"]) else "FAIL"
        results.append({"id": gate["id"], "name": gate["name"], "value": value,
                        "target": f"{gate['op']} {gate['value']}", "status": status})
    return results
