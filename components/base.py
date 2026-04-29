class BaseComponent:
    """
    Abstract base class for all hardware components.

    Every component must define:
        - name        : str  — uppercase identifier e.g. "LED"
        - interfaces  : list — list of {"label": ..., "signal_type": ...}
        - generate_setup(pin_assignments, action) -> str
        - generate_loop(pin_assignments, action)  -> str

    pin_assignments is a dict like {"SIGNAL": 2} or {"TRIG": 4, "ECHO": 5}
    action is the action dict from logic_planner e.g. {"type": "blink", "times": 5}
    """

    name: str = "BASE"
    interfaces: list = []

    def generate_setup(self, pin_assignments: dict, action: dict) -> str:
        raise NotImplementedError(f"{self.__class__.__name__} must implement generate_setup()")

    def generate_loop(self, pin_assignments: dict, action: dict) -> str:
        raise NotImplementedError(f"{self.__class__.__name__} must implement generate_loop()")