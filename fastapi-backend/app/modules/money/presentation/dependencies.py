"""Money presentation dependencies — dependencies สำหรับเงิน"""

from ..application.use_cases import MoneyUseCases


def get_money_use_cases() -> MoneyUseCases:
    """สร้าง MoneyUseCases — Get MoneyUseCases instance"""
    return MoneyUseCases()
