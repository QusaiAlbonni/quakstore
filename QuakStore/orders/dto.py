from dataclasses import dataclass

from cart.models import CartItem

from collections.abc import Sequence

from .models import Order, User, OrderItem, Product


@dataclass(frozen=True)
class OrderItemDTO:
    product: int
    quantity: int


@dataclass(frozen=True)
class OrderDTO:
    total: int
    state: str
    owner: int
    items: list[OrderItemDTO]
    provider: str = 'stripe'
    payment_intent: str | None= None

    @classmethod
    def from_cart(cls, cart_items: Sequence[CartItem], provider: str = 'stripe'):
        if not len(cart_items):
            raise ValueError()
        items = []
        total = 0
        state = 'pending'
        owner = cart_items[0].user.pk
        for item in cart_items:
            product = Product.objects.get(pk= item.product.pk)
            if item.quantity > product.stock:
                raise ValueError()
            items.append(OrderItemDTO(item.product.pk, item.quantity))
            total += item.quantity * item.product.discounted_price
        return OrderDTO(
            total=total,
            state=state,
            owner=owner,
            items=items,
            provider=provider
        )


class OrderAssembler:
    def __init__(self, DTO: OrderDTO) -> None:
        self.dto = DTO
        
    def create(self) -> Order:
        order = Order()
        order.owner = User.objects.get(pk=self.dto.owner)
        order.total = self.dto.total
        order.state = self.dto.state
        order.provider = self.dto.provider
        order.save()
        self.create_items(order)
        return order
    
    def create_items(self, order: Order):
        items: list[OrderItem] = []
        products: list[Product] = []
        for dto in self.dto.items:
            item=OrderItem(order=order, quantity=dto.quantity, product_id=dto.product)
            items.append(item)
            product= item.product
            product.stock -= item.quantity
            products.append(product)
        
        Product.objects.bulk_update(products, ["stock"])
        return OrderItem.objects.bulk_create(items)