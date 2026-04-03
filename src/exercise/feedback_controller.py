class FeedbackController:
    """Controls timing and display of form feedback to prevent noise."""
    """
    Controls WHEN feedback should be shown.
    Prevents noisy real-time feedback.
    """

    def __init__(self):
        """Initialize feedback controller with display duration of ~3 seconds."""
        self.pending_feedback = None
        self.frames_since_feedback = 0
        self.MAX_WAIT_FRAMES = 45  # ~1.5 sec @30fps

        # ✅ NEW — display duration system
        self.display_feedback = None
        self.display_timer = 0
        self.DISPLAY_FRAMES = 90  # show feedback ~3 seconds

    def update(self, exercise, state_name, raw_feedback):
        """Process and display feedback based on state and exercise.
        
        Args:
            exercise: Current exercise object.
            state_name: Current exercise state.
            raw_feedback: Raw feedback from validator.
        
        Returns:
            Feedback message or None if not in valid state.
        """
        """
        exercise -> current exercise object
        state_name -> current state
        raw_feedback -> validator output
        """

        # -------------------------------------------------
        # ✅ STEP 1 — keep showing existing feedback
        # -------------------------------------------------
        if self.display_timer > 0:
            self.display_timer -= 1
            return self.display_feedback

        # -------------------------------------------------
        # ORIGINAL LOGIC (UNCHANGED)
        # -------------------------------------------------

        # No feedback generated
        if raw_feedback is None:
            self.frames_since_feedback += 1
            return None

        # ✅ Show only in valid state
        if exercise.allow_feedback(state_name):
            self.pending_feedback = None
            self.frames_since_feedback = 0

            # ✅ NEW: lock feedback for display duration
            self.display_feedback = raw_feedback
            self.display_timer = self.DISPLAY_FRAMES

            return self.display_feedback

        # Otherwise store temporarily
        self.pending_feedback = raw_feedback
        self.frames_since_feedback += 1

        # ✅ Safety: user never reached correct state
        if self.frames_since_feedback > self.MAX_WAIT_FRAMES:
            fb = self.pending_feedback
            self.pending_feedback = None
            self.frames_since_feedback = 0

            # ✅ NEW: lock feedback display
            self.display_feedback = fb
            self.display_timer = self.DISPLAY_FRAMES

            return self.display_feedback

        return None
