from sqlalchemy import ForeignKey
from sqlalchemy import String,Integer,Float,Date
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from datetime import date

class Base(DeclarativeBase):
    pass





class User(Base):
   
   __tablename__ = "users"

   id:Mapped[int] = mapped_column(Integer,primary_key=True)
   full_name : Mapped[str] =mapped_column(String(100))
   email : Mapped[str] =mapped_column(String(100))
   password : Mapped[str]=mapped_column(String(200))


   
   
   




    

class Product(Base):
    __tablename__ =  "products"

    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_name: Mapped[str] = mapped_column(String(100))
    buying_price : Mapped[float] = mapped_column(Float)
    selling_price  : Mapped[float] = mapped_column(Float)



class Purchase(Base):
    __tablename__ = "purchases"

     
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    Product_id : Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity : Mapped[int] = mapped_column(Integer)
    purchase_date  : Mapped[date] = mapped_column(Date)
    supplier : Mapped[str] = mapped_column(String(100))


class Sale(Base):
    __tablename__ = "sales"

    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"))
    sales_date : Mapped[date] = mapped_column(Date)
    total_amount : Mapped[float] = mapped_column(Float)
  
    

     

class Sales_detail(Base):
    __tablename__ = "sales_details"

    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    Product_id : Mapped[int] = mapped_column(ForeignKey("products.id"))
    sales_id : Mapped[int] = mapped_column(ForeignKey("sales.id"))
    quantity  : Mapped[int] = mapped_column(Integer)
    buying_price : Mapped[float] = mapped_column(Float)
    total_amount : Mapped[float] = mapped_column(Float)

class Payment(Base):
    __tablename__ ="payments"

    id:Mapped[int] = mapped_column(Integer,primary_key=True)
    sales_id: Mapped[int ] =mapped_column(ForeignKey("sales.id"))
    payment_method: Mapped[str] = mapped_column(String(200))
    Payment_date: Mapped[date] = mapped_column(Date)