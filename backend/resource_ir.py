class ResourceIR:
    def __init__(self, ir_dict):
        self.components = ir_dict.get("components", [])
        self.logic = ir_dict.get("logic", [])
