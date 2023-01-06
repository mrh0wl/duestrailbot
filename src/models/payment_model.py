# imports from default libs
from typing import Any, Iterable, List, Mapping, TypeVar

Number = Iterable[TypeVar('Number', int, float)]


class Plan:
    def __init__(self, name: str, price: Number):
        self.name = name
        self.price = price

    def toJson(self) -> Mapping[str, Any]:
        return {'name': self.name, 'price': self.price}

    @staticmethod
    def fromJson(json: Mapping[str, Any]):
        name, price = list(dict(json).items())[0]
        return Plan(name=name, price=price)


class TotalPay:
    def __init__(self, total_pay: List[Number]):
        self.months = total_pay[0]
        self.paid = total_pay[1]

    def toJson(self) -> Mapping[str, Any]:
        return {str(self.months): self.paid}

    @staticmethod
    def fromJson(json: Mapping[str, Any]):
        lista = [[int(k), v] for k, v in json.items()][0]
        return TotalPay(lista)

    def __format__(self, formatter):
        return format(self.paid, formatter)


class Payment:
    def __init__(self,
                 discounts: Number,
                 extra_fees: Number,
                 total_pay: List[TotalPay],
                 plan: Plan = None,
                 ):
        self.plan = plan
        self.discounts = discounts
        self.extra_fees = extra_fees
        self.total_pay = total_pay

        if len(self.extra_fees) != 0:
            for extra_fee in self.extra_fees:
                self.total_pay += extra_fee
        if len(self.discounts) != 0:
            for discount in self.discounts:
                self.total_pay -= discount

    def tojson(self) -> Mapping[str, Any]:
        return {
            'plan': self.plan.toJson(),
            'discounts': self.discounts,
            'extra_fees': self.extra_fees,
            'total_pay': [item.toJson() for item in self.total_pay] if self.total_pay else []
        }

    @staticmethod
    def fromJson(json: Mapping[str, Any]):
        sorted_list = list(
            dict(sorted(json['plan'].items())).values()) if 'plan' in json and json['plan'] is not None else None
        return Payment(
            plan=Plan.fromJson(
                {sorted_list[0]: sorted_list[1]}) if sorted_list else None,
            discounts=json['discounts'],
            extra_fees=json['extra_fees'],
            total_pay=[TotalPay.fromJson(item)
                       for item in json['total_pay']] if json['total_pay'] else []
        )

    def update(
        self,
        plan: Plan = None,
    ):
        self.plan = plan or self.plan
        self.discounts = self.discounts
        self.extra_fees = self.extra_fees
        self.total_pay = plan.price if plan is not None else self.total_pay

        if len(self.extra_fees) != 0:
            for extra_fee in self.extra_fees:
                self.total_pay += extra_fee
        if len(self.discounts) != 0:
            for discount in self.discounts:
                self.total_pay -= discount
