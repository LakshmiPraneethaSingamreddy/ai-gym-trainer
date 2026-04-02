import pytest

from src.exercise.pushup.pushup_rep_counter import PushupRepCounter
from src.exercise.pushup.pushup_state_machine import PushupState, PushupStateMachine


def _landmark(x=0.0, y=0.0, visibility=0.0):
    return {"x": x, "y": y, "visibility": visibility}


def _build_landmarks(elbow_angle, knee_angle, visible_side="left"):
    landmarks = [_landmark() for _ in range(33)]

    if visible_side == "left":
        side_indexes = {
            "shoulder": 11,
            "elbow": 13,
            "wrist": 15,
            "hip": 23,
            "knee": 25,
            "ankle": 27,
        }
        hidden_indexes = [12, 14, 16, 24, 26, 28]
    else:
        side_indexes = {
            "shoulder": 12,
            "elbow": 14,
            "wrist": 16,
            "hip": 24,
            "knee": 26,
            "ankle": 28,
        }
        hidden_indexes = [11, 13, 15, 23, 25, 27]

    for index in hidden_indexes:
        landmarks[index] = _landmark(visibility=0.05)

    landmarks[side_indexes["shoulder"]] = _landmark(1.0, 0.0, 0.95)
    landmarks[side_indexes["elbow"]] = _landmark(0.0, 0.0, 0.95)
    elbow_points = {
        180: (-1.0, 0.0),
        170: (-0.9848077530, 0.1736481777),
        150: (-0.8660254038, 0.5),
        140: (-0.7660444431, 0.6427876097),
        120: (-0.5, 0.8660254038),
        90: (0.0, 1.0),
        60: (0.5, 0.8660254038),
    }
    landmarks[side_indexes["wrist"]] = _landmark(
        *elbow_points[elbow_angle], visibility=0.95
    )

    landmarks[side_indexes["hip"]] = _landmark(0.0, 0.0, 0.95)
    landmarks[side_indexes["knee"]] = _landmark(0.0, 0.0, 0.95)
    knee_points = {
        180: (-1.0, 0.0),
        170: (-0.9848077530, 0.1736481777),
        150: (-0.8660254038, 0.5),
        140: (-0.7660444431, 0.6427876097),
        120: (-0.5, 0.8660254038),
        90: (0.0, 1.0),
        60: (0.5, 0.8660254038),
    }
    landmarks[side_indexes["ankle"]] = _landmark(
        *knee_points[knee_angle], visibility=0.95
    )

    return landmarks


def _build_sitting_landmarks(elbow_angle, visible_side="left"):
    landmarks = _build_landmarks(elbow_angle, 180, visible_side)

    if visible_side == "left":
        landmarks[11] = _landmark(0.0, 0.0, 0.95)
        landmarks[23] = _landmark(0.0, 1.0, 0.95)
    else:
        landmarks[12] = _landmark(0.0, 0.0, 0.95)
        landmarks[24] = _landmark(0.0, 1.0, 0.95)

    return landmarks


@pytest.mark.parametrize("knee_angle, expected_mode", [(180, False), (90, True)])
def test_pushup_state_machine_counts_regular_and_knee_pushups(
    knee_angle, expected_mode
):
    machine = PushupStateMachine()
    counter = PushupRepCounter()

    sequence = [180, 120, 90, 170]
    reps = 0

    for elbow_angle in sequence:
        state = machine.update(_build_landmarks(elbow_angle, knee_angle))
        reps = counter.update(state.name, machine.reached_bottom)

    assert machine.is_knee_pushup is expected_mode
    assert machine.state == PushupState.UP
    assert reps == 1


def test_pushup_state_machine_ignores_shallow_motion():
    machine = PushupStateMachine()
    counter = PushupRepCounter()

    sequence = [180, 150, 140, 150, 170]
    reps = 0

    for elbow_angle in sequence:
        state = machine.update(_build_landmarks(elbow_angle, 180))
        reps = counter.update(state.name, machine.reached_bottom)

    assert machine.state == PushupState.UP
    assert reps == 0


def test_pushup_state_machine_counts_regular_pushup_with_standard_depth():
    machine = PushupStateMachine()
    counter = PushupRepCounter()

    sequence = [180, 140, 120, 170]
    reps = 0

    for elbow_angle in sequence:
        state = machine.update(_build_landmarks(elbow_angle, 180))
        reps = counter.update(state.name, machine.reached_bottom)

    assert machine.is_knee_pushup is False
    assert machine.state == PushupState.UP
    assert reps == 1


def test_pushup_state_machine_ignores_sitting_elbow_motion():
    machine = PushupStateMachine()
    counter = PushupRepCounter()

    sequence = [180, 120, 90, 170]
    reps = 0

    for elbow_angle in sequence:
        state = machine.update(_build_sitting_landmarks(elbow_angle))
        reps = counter.update(state.name, machine.reached_bottom)

    assert machine.state == PushupState.UP
    assert reps == 0
