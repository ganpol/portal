from django.db import models
from datetime import datetime
from resources import POSITIONS, cashier


class Order(models.Model):
    time_in = models.DateTimeField(auto_now_add=True)
    time_out = models.DateTimeField(null=True)
    cost = models.FloatField(default=0.0)
    take_away = models.BooleanField(default=False)
    complete = models.BooleanField(default=False)
    staff = models.ForeignKey('Staff', on_delete=models.CASCADE)
    products = models.ManyToManyField('Product', through='ProductOrder')

    # В модели Order мы можем получить время, которое было затрачено на выполнение заказа.
    def finish_order(self):
        self.time_out = datetime.now()
        self.complete = True
        self.save()

    # Возвращающий время выполнения заказа в минутах (округлить до целого). Если заказ ещё не выполнен, то вернуть количество минут с начала выполнения заказа.
    def get_duration(self):
        if self.complete:  # если завершён, возвращаем разность объектов
            return (self.time_out - self.time_in).total_seconds() // 60
        else:  # если ещё нет, то сколько длится выполнение
            return (datetime.now() - self.time_in).total_seconds() // 60


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.FloatField(default=0.0)

    # fries_stand = Product(name="Картофель фри (станд.)", price=93.0)
    # fries_stand.save()

    # fries_big = Product.objects.create(name="Картофель фри (бол.)", price=106.0)


director = 'DI'
admin = 'AD'
cook = 'CO'
cashier = 'CA'
cleaner = 'CL'

POSITIONS = [
    (director, 'Директор'),
    (admin, 'Администратор'),
    (cook, 'Повар'),
    (cashier, 'Кассир'),
    (cleaner, 'Уборщик')
]


class Staff(models.Model):
    full_name = models.CharField(max_length=255)
    position = models.CharField(max_length=2, choices=POSITIONS, default=cashier)
    labor_contract = models.IntegerField(default=0)

    def get_last_name(self):
        return self.full_name.split()[0]


class ProductOrder(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    _amount = models.IntegerField(default=1, db_column='amount')

    def product_sum(self):
        product_price = self.product.price
        return product_price * self.amount

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value):
        self._amount = int(value) if value >= 0 else 0
        self.save()
