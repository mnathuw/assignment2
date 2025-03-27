from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
import datetime
import matplotlib.pyplot as plt

# initialize database
Base = declarative_base()
engine = create_engine('sqlite:///ecommerce.db')
Session = sessionmaker(bind=engine)
session = Session()

# order-product table
order_product_table = Table(
    'order_product', Base.metadata,
    Column('order_id', Integer, ForeignKey('orders.order_id')),
    Column('product_id', Integer, ForeignKey('products.product_id')),
    Column('quantity', Integer, default=1)
)

# customer
class Customer(Base):
    __tablename__ = 'customers'
    customer_id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    shipping_address = Column(String)  # New field added
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    orders = relationship('Order', back_populates='customer')

# order
class Order(Base):
    __tablename__ = 'orders'
    order_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.customer_id'))
    order_date = Column(DateTime, default=datetime.datetime.utcnow)
    customer = relationship('Customer', back_populates='orders')
    products = relationship('Product', secondary=order_product_table, back_populates='orders')

# product
class Product(Base):
    __tablename__ = 'products'
    product_id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)
    orders = relationship('Order', secondary=order_product_table, back_populates='products')

# database table
Base.metadata.create_all(engine)

# insert customers
customer1 = Customer(name="Claire Smith", email="csmith@example.com")
customer2 = Customer(name="John Brown", email="jbrown@example.com")
customer3 = Customer(name="Olivia Pearson", email="opearson@example.com")
session.add_all([customer1, customer2, customer3])
session.commit()

# insert products
product1 = Product(name="Laptop", price=1200.00)
product2 = Product(name="Smartphone", price=800.00)
product3 = Product(name="Headphones", price=150.00)
product4 = Product(name="Monitor", price=300.00)
product5 = Product(name="Keyboard", price=50.00)
product6 = Product(name="Printer", price=200.00)
session.add_all([product1, product2, product3, product4, product5, product6])
session.commit()

# insert orders, commit orders first
order1 = Order(customer_id=customer1.customer_id)
order2 = Order(customer_id=customer1.customer_id)
order3 = Order(customer_id=customer2.customer_id)
order4 = Order(customer_id=customer3.customer_id)
order5 = Order(customer_id=customer2.customer_id)
order6 = Order(customer_id=customer3.customer_id)
session.add_all([order1, order2, order3, order4, order5, order6])
session.commit()

# associate products with orders
order1.products.extend([product1, product3])
order2.products.extend([product2, product5])
order3.products.extend([product4])
order4.products.extend([product2, product3, product5])
order5.products.extend([product5, product6])
order6.products.extend([product1, product3, product5])
session.commit()

# most purchased product
def most_purchased_product():
    results = session.query(Product.name, order_product_table.c.quantity).join(order_product_table).all()
    product_sales = {}
    for product_name, quantity in results:
        if quantity is not None:
            product_sales[product_name] = product_sales.get(product_name, 0) + quantity
    if product_sales:
        most_purchased = max(product_sales, key=product_sales.get)
        print(f"Most purchased product: {most_purchased} ({product_sales[most_purchased]} units)")
    else:
        print("No product purchases found.")

most_purchased_product()

# data visualization: pie chart for product sales
def plot_product_sales():
    results = session.query(Product.name, order_product_table.c.quantity).join(order_product_table).all()
    product_sales = {}
    for product_name, quantity in results:
        if quantity is not None:
            product_sales[product_name] = product_sales.get(product_name, 0) + quantity

    if product_sales:
        plt.figure(figsize=(8, 6))
        plt.pie(product_sales.values(), labels=product_sales.keys(), autopct='%1.1f%%', startangle=140)
        plt.title("Product Sales Distribution")
        plt.show()
    else:
        print("No sales data available for visualization.")

plot_product_sales()