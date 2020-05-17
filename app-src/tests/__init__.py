class DummyLogger:

    def __init__(self):
        self.log_lines = list()

    def info(self, message: str):
        self.log_lines.append(message)

    def debug(self, message: str):
        self.log_lines.append(message)

    def warning(self, message: str):
        self.log_lines.append(message)

    def error(self, message: str):
        self.log_lines.append(message)

