# it has to have to have a ruote
# it has to have a method (get/put/post/delete)
# it has to have a status code(200,201,403)
# it has to return data as Json(key :value pair)

from flask import Flask,request,jsonify
from sqlalchemy import create_engine,select
from sqlalchemy.orm import Session
from model import Base,Product,User,Purchase,Sale,Sales_detail,Payment
from datetime import datetime

# import json

app = Flask(__name__)

# create a connection to the db using sqlalchemy engine
engine = create_engine("sqlite:///./flask_duka_api.db",echo=True)

# create  talbes into the db using sqlalchemy
Base.metadata.create_all(engine) 

#create a session to do sql transaction
session= Session(engine)
user ={"id":"1",
    "full_name":"victoria",
    "email":  "vicky@gmail.com",
    "password":"7811",
    "phone_number":"0112021910"
}
@app.before_request
def before_request():
    
    try:
        print("A request is coming in!")
        new_user=(user)
        session.add(new_user)
        session.commit

        return jsonify({"Message":"User added successfully"}),201
    except:
        print("Error found")

@app.route("/")
def home():
    if request.method == "GET":
        data = {"flask Api": "Version 1"}
        return jsonify (data),200
    else:
        error={"Error":"Method not allowed"}

        return jsonify(error),405

@app.route("/products", methods=["GET","POST"])
def products():
    if request.method == "GET":
        #fetch data from db
        query = select(Product)
        products=session.scalars(query)

        results =[]
        for prod in products:
            p = {"id":prod.id,
                 "Product_name":prod.product_name,
                 "buying_price":prod.buying_price,
                 "selling_price":prod.selling_price

                 }
            results.append(p)
        



        
        return jsonify(results),200
        
    elif request.method=="POST":
        data = request.get_json()
        if data["product_name"] == "" or data["buying_price"] ==""or data["selling_price"]=="":
            error ={"Error":"Ensure all fields are set"}
            return jsonify(error), 403
        else:
            #store in the db
            new_product = Product(
                user_id = user ["id"],
                product_name = data["product_name"],
                buying_price = float(data["buying_price"]),
                selling_price = float(data["selling_price"])
            )
        
        session.add(new_product)
        session.commit()
        return jsonify({"Message":"new products added"}),201

    else:
        error ={"Error":"Method not allowed"}
        return jsonify(error),405

    
       
@app.route("/purchase",methods=["GET","POST"])
def purchase():
    if request.method=="GET":

        query = select(Purchase)
        purchases = session.scalars(query).all()

        results = []
        for purchase in purchases:

            p = {"id":purchase.id,
                "product_id":purchase.product_id,
                "quantity":purchase.quantity,
                "purchase_date":purchase.purchase_date.isoformat(),
                "supplier":purchase.supplier
            }
            

            results.append(p)
            return jsonify(results),200
        
    elif request.method=="POST":
        data = request.get_json()

        if data["product_id"] == "" or data["quantity"] == "" or data["purchase_date"] == "" or data["supplier"]:
            error={"Missing requured fields"}
            return jsonify(error),405
        else:
            new_purchases=Purchase(
                product_id=data["product_id"],
                quantity=data["quantity"],
                purchase_date=datetime.strptime(data["purchase_date"],"%Y-%m-%d").date(),
                supplier=data["supplier"]
            )
            session.add(new_purchases)
            session.commit()
            return jsonify({"message":"purchase added successfully"}),201
    else:
        error={"Error":"method not allowed"}
        return jsonify(error),405

@app.route("/sale",methods=["GET","POST"])
def sale():
    if request.method=="GET":
        query=select(Sale)
        sales=session.scalars(query).all()

        results=[]
        for sale in sales:
            s={"id":sale.id,
               "user_id":sale.user_id,
               "sales_date":sale.sales_date,
               "total_amount":sale.total_amount,
            }
            results.append(s)
        return jsonify(results),200

    elif request.method =="POST":
        data=request.get_json()

        if data["user_id"] == "" or data["sales_date"] == "" or data["total_amount"]=="":
            error={"Error":"missing fields required"}
            return jsonify(error),403
        else:
            new_sales=Sale(
                user_id=user["id"],
                sales_date=datetime.strptime(data["sales_date"],"%Y-%m-%d"),
                total_amount=data["total_amount"]
            )   

            session.add(new_sales)     
            session.commit()

            return jsonify({"message":"sales added successfully"})
    else:
        error={"Error":"methhod not allowed"}
        return jsonify(error),405

@app.route("/sales_detail",methods=["GET","POST"])
def sales_detail():
    if request.method=="GET":
        query=select(Sales_detail)
        sales=session.scalar(query)

        results=[]
        for s in sales_detail:
            d={"id":d.id,
               "product_id":d.product_id,
               "sales_id":d.sales_id,
               "quantity":d.quantity,
               "buying_price":d.buying_price,
               "total_amount":d.total_amount
            }
            results.append(d)
            return jsonify(results),200

  
    
    elif request.method =="POST":
        data=request.get_json
        if data["product_id"] == "" or data["sales_id"] == "" or data["quantity"] or data["buying_price"] =="" or data["total_amount"]=="":
            error={"Error":"missing fields required"}
        else:
            new_sales_details=Sales_detail(
                product_id=["product_id"],
                sales_id=["sales_id"],
                quantity=["quantity"],
                buying_price=["buying_price"],
                total_amount=["total_amount"]
            )   

            session.add(new_sales_details)     
            session.commit()

            return jsonify({"message":"sales_details added successfully"})

    else:
        error={"Error":"Method not allowed"}
        return jsonify(error),405

@app.route("/payment", methods=["GET","POST"])
def payments():
    if request.method=="GET":
        query=select(Payment)
        payments=session.scalars(query).all()

        results=[]
        for payment in payments:
            p={"id":payment.id,
               "sales_id":payment.sales_id,
               "payment_method":payment.payment_method,
               "payment_date":payment.Payment_date
            }

            results.append(p)
        return jsonify(results),200

    elif request.method =="POST":
            data=request.get_json()
           
            if  data["sales_id"] == "" or data["payment_method"]=="" or data["Payment_date"] =="" :
                error={"Error":"missing fields required"}
                return jsonify(error),405
            else:
                new_payments=Payment(
                    
                    sales_id=data["sales_id"],
                    payment_method=data["payment_method"],
                    Payment_date=datetime.strptime(data["Payment_date"],"%Y-%m-%d"),
                    
                )   
    
                session.add(new_payments)     
                session.commit()
                return jsonify({"Message":"payments added successfully"}),201

    else:
        error={"Error":"method not allowed"}
        return jsonify(error),405
    

    


               
               
            

           



        
    
        

            
               

            



    


            






     

   















app.run(debug=True)

