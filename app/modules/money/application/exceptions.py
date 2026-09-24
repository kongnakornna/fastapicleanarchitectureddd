"""Money application exceptions — ข้อยกเว้นแอปพลิเคชันเงิน"""


class StandardException(Exception):
    """StandardException — ข้อผิดพลาดมาตรฐาน"""


class MoneyException(StandardException):
    """MoneyException — ข้อผิดพลาดโมดูลเงิน"""

    def __init__(self, message: str = "Money operation failed"):
        self.message = message
        super().__init__(message)
