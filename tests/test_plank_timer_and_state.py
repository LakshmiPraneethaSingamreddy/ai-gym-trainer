from src.exercise.plank.plank_rep_counter import PlankTimer
from src.exercise.plank.plank_state_machine import PlankState, PlankStateMachine


def _landmark(x=0.0, y=0.0, visibility=0.0):
    return {"x": x, "y": y, "visibility": visibility}


def _blank_landmarks():
    return [_landmark() for _ in range(33)]


def _set_side_landmarks(
    landmarks,
    side,
    shoulder,
    hip,
    knee,
    ankle,
    elbow,
    wrist,
    visibility=0.95,
):
    if side == "left":
        s_i, e_i, w_i, h_i, k_i, a_i = 11, 13, 15, 23, 25, 27
        hidden = [12, 14, 16, 24, 26, 28]
    else:
        s_i, e_i, w_i, h_i, k_i, a_i = 12, 14, 16, 24, 26, 28
        hidden = [11, 13, 15, 23, 25, 27]

    landmarks[s_i] = _landmark(*shoulder, visibility)
    landmarks[e_i] = _landmark(*elbow, visibility)
    landmarks[w_i] = _landmark(*wrist, visibility)
    landmarks[h_i] = _landmark(*hip, visibility)
    landmarks[k_i] = _landmark(*knee, visibility)
    landmarks[a_i] = _landmark(*ankle, visibility)

    for idx in hidden:
        landmarks[idx] = _landmark(0.0, 0.0, 0.05)


def test_plank_timer_pauses_on_broken_and_resumes(monkeypatch):
    timer = PlankTimer()

    timeline = iter([0.0, 0.5, 1.0, 2.0, 2.5, 3.0])
    monkeypatch.setattr(
        "src.exercise.plank.plank_rep_counter.time.time", lambda: next(timeline)
    )

    assert timer.update("HOLDING") == 0.0
    assert timer.update("HOLDING") == 0.5
    assert timer.update("BROKEN") == 1.0
    assert timer.update("BROKEN") == 1.0
    assert timer.update("HOLDING") == 1.0
    assert timer.update("HOLDING") == 1.5


def test_plank_state_machine_requires_horizontalish_posture():
    machine = PlankStateMachine()

    # Upright straight line (would be false HOLDING previously)
    upright = _blank_landmarks()
    _set_side_landmarks(
        upright,
        "left",
        shoulder=(0.0, 0.0),
        hip=(0.0, 1.0),
        knee=(0.0, 1.5),
        ankle=(0.0, 2.0),
        elbow=(-0.2, 0.1),
        wrist=(-0.2, 0.4),
    )

    # Horizontal straight line (valid plank posture)
    horizontal = _blank_landmarks()
    _set_side_landmarks(
        horizontal,
        "left",
        shoulder=(0.0, 0.0),
        hip=(1.0, 0.02),
        knee=(1.5, 0.02),
        ankle=(2.0, 0.0),
        elbow=(-0.2, 0.12),
        wrist=(-0.2, 0.35),
    )

    assert machine.update(upright) == PlankState.BROKEN
    assert machine.update(horizontal) == PlankState.HOLDING


def test_plank_state_machine_rejects_lying_flat_with_straight_arm():
    machine = PlankStateMachine()

    lying_flat = _blank_landmarks()
    _set_side_landmarks(
        lying_flat,
        "left",
        shoulder=(0.0, 0.0),
        hip=(1.0, 0.0),
        knee=(1.5, 0.0),
        ankle=(2.0, 0.0),
        elbow=(-0.2, 0.0),
        wrist=(-0.4, 0.0),
    )

    assert machine.update(lying_flat) == PlankState.BROKEN


def test_plank_state_machine_hold_break_hold_floor_sequence():
    machine = PlankStateMachine()

    holding = _blank_landmarks()
    _set_side_landmarks(
        holding,
        "left",
        shoulder=(0.0, 0.0),
        hip=(1.0, 0.02),
        knee=(1.5, 0.02),
        ankle=(2.0, 0.0),
        elbow=(-0.2, 0.12),
        wrist=(-0.2, 0.35),
    )

    broken_hip_up = _blank_landmarks()
    _set_side_landmarks(
        broken_hip_up,
        "left",
        shoulder=(0.0, 0.0),
        hip=(1.0, -0.22),
        knee=(1.5, -0.22),
        ankle=(2.0, 0.0),
        elbow=(-0.2, 0.12),
        wrist=(-0.2, 0.35),
    )

    lying_flat_bent_arm = _blank_landmarks()
    _set_side_landmarks(
        lying_flat_bent_arm,
        "left",
        shoulder=(0.0, 0.0),
        hip=(1.0, 0.0),
        knee=(1.5, 0.0),
        ankle=(2.0, 0.0),
        elbow=(-0.2, 0.0),
        wrist=(-0.2, 0.3),
    )

    assert machine.update(holding) == PlankState.HOLDING
    assert machine.update(broken_hip_up) == PlankState.BROKEN
    assert machine.update(holding) == PlankState.HOLDING
    assert machine.update(lying_flat_bent_arm) == PlankState.BROKEN


def test_plank_state_machine_rejects_shoulder_hip_misalignment():
    machine = PlankStateMachine()

    misaligned = _blank_landmarks()
    _set_side_landmarks(
        misaligned,
        "left",
        shoulder=(0.0, 0.0),
        hip=(1.0, 0.2),
        knee=(1.5, 0.02),
        ankle=(2.0, 0.0),
        elbow=(-0.2, 0.12),
        wrist=(-0.2, 0.35),
    )

    assert machine.update(misaligned) == PlankState.BROKEN
