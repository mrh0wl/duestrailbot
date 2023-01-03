# imports from default libs
from collections.abc import Iterable, Mapping
from typing import Any, TypeVar

Number = Iterable[TypeVar('Number', int, float)] | None


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


class Payment:
    def __init__(self,
                 discounts: Number,
                 extra_fees: Number,
                 total_pay: Number,
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
            'total_pay': self.total_pay
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
            total_pay=json['total_pay']
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
