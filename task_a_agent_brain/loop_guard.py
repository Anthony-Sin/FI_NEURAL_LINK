class LoopGuard:
    """
    Maintains an in-memory list of recent actions to detect repetitive loops.
    """

    def __init__(self, n: int = 5):
        """
        Initializes the LoopGuard.

        Args:
            n (int): The number of recent actions to track. Defaults to 5.
        """
        self.max_n = n
        self.actions = []

    def record_action(self, action: str):
        """
        Appends an action to the history and trims it to maintain the window size N.

        Args:
            action (str): The action string to record.
        """
        self.actions.append(action)
        if len(self.actions) > self.max_n:
            self.actions.pop(0)

    def check_loop(self, action: str) -> bool:
        """
        Returns True if the given action has appeared 3 or more times in the
        current history window.

        Args:
            action (str): The action string to check for looping.

        Returns:
            bool: True if a loop is detected, False otherwise.
        """
        # Count occurrences in the existing window.
        # If we add the action, will it be there 3 or more times?
        count = self.actions.count(action)
        return count >= 2

    def reset(self):
        """
        Clears the recorded action history.
        """
        self.actions = []
