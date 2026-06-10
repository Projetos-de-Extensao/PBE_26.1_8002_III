class gradeHorariaIncompativelException(Exception):
    def __init__(self, message="Grade horária incompatível com o contrato!"):
        self.message = message
        super().__init__(self.message)