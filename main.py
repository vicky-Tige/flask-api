# it has to have to have a ruote
# it has to have a method (get/put/post/delete)
# it has to have a status code(200,201,403)
# it has to return data as Json(key :value pair)
import sentry_sdk
from flask import Flask,request,jsonify
from flask_jwt_extended import JWTManager,jwt_required,create_access_token,get_jwt_identity
from sqlalchemy import create_engine,select
from sqlalchemy.orm import Session
from model import Base,Product,User,Purchase,Sale,Sales_detail,Payment
from datetime import datetime
from flask_bcrypt import Bcrypt


# import json
sentry_sdk.init(
    dsn="https://0ae45aac38007871a7f2fc2ca694a475@o4512046022524928.ingest.us.sentry.io/4512046231322624",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)

app = Flask(__name__)
app.config["JWT_SECRET_KEY"]="PPDR123"
jwt=JWTManager(app)
bcrypt=Bcrypt(app)

# create a connection to the db using sqlalchemy engine
engine = create_engine("sqlite:///./flask_duka_api.db",echo=True)

# create  talbes into the db using sqlalchemy
Base.metadata.create_all(engine) 

#create a session to do sql transaction
session= Session(engine)

allowed_methods=["get","post","put","delete","patch","head","options"]

@app.before_request
def before_request():
    try:
        pass

    except:
        pass

@app.route("/",methods=allowed_methods)
def home():
    if request.method == "GET":
        data = {"flask Api": "Version 1"}
        return jsonify (data),200
    else:
        error={"Error":"Method not allowed"}
        return jsonify(error),405

@app.route("/register",methods=["POST"])
def register():
    if request.method=="POST":
        try:
            data = request._get_file_stream()
            if data["full_name"]=="" or data["email"] == "" or data["password"] == "":
                error={"All fields should me filled"}
                return jsonify(error),403
            query=select(User).filter_by(email=data["email"])
            user=session.scalars(query).first()
            if user:
                return jsonify({"message":"email arleady exist"}),403

            hashed_password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
            new_user=User(
                full_name=data["full_name"],
                email=data["email"],
                password=hashed_password
            )
            session.add(new_user)
            session.commit()

            token=create_access_token(identity=data["email"])
            message=({"success":"user added succesfully","token":token}) 

            return jsonify(message),201
        except:
            error={"Error":"sorry try again later"}
            return jsonify(error),500
    else:
        error={"Error":"method not allowed"}
        return jsonify(error),405
    
@app.route("/login",methods=allowed_methods)
def login():
    if request.method=="POST":
        data=dict(request.get_json())
        if "email" not in data.keys()  or "passsword" not in data.keys():
            error={"Error":"All fields should me filled"}
            return jsonify(error),403
        
        query=select(User).filter_by(email=data["email"])
        user=session.scalars(query).first()
        if not user or not bcrypt.check_password_hash(user.password,data["password"]):
            return jsonify({"message":"invalid email or password"}),401  
        else:
            token = create_access_token(identity=data["email"])
            message=({"success":"login successful","token":token})

        return jsonify(message),200
    else:
        error={"Error":"method not allowed"}
        return jsonify(error),405

@app.route("/products", methods=["GET","POST"])
@jwt_required()
def products():
    email = get_jwt_identity()
    query = select(User).filter_by(email=email)
    user=session.scalars(query).first()
    
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

        return jsonify(results),201
        
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

@app.route("/purchase")
@jwt_required
def purchase():
    email = get_jwt_identity()
    query = select(User).filter_by(email=email)
    user=session.scalars(query).first()
    if request.method=="GET":

        query = select(Purchase)
        purchases = session.scalars(query).all()

        results = []
        for purchase in purchases:

            p = {"id":purchase.id,
                "product_id":purchase.product_id,
                "quantity":purchase.quantity,
                "purchase_date":purchase.purchase_date,
                "supplier":purchase.supplier
            }
            
            results.append(p)
        return jsonify(results)
        
    elif request.method=="POST":
        data = request.get_json()

        if data["product_id"] == "" or data["quantity"] == "" or data["purchase_date"] == "" or data["supplier"] == "":
            error={"Missing requured fields"}
            return jsonify(error),405
        else:
            new_purchases=Purchase(
                product_id=data["product_id"],
                quantity=data["quantity"],
                purchase_date=datetime.strptime(data["purchase_date"],"%Y-%m-%d"),
                supplier=data["supplier"]
            )
            session.add(new_purchases)
            session.commit()
            return jsonify({"message":"purchase added successfully"}),201
    else:
        error={"Error":"method not allowed"}
        return jsonify(error),405

@app.route("/sale",methods=["GET","POST"])
@jwt_required()
def sale():
    email = get_jwt_identity()
    query = select(User).filter_by(email=email)
    user=session.scalars(query).first()
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

@app.route("/sales-detail",methods=["GET","POST"])
@jwt_required()
def sales_detail():

    email = get_jwt_identity()
    query = select(User).filter_by(email=email)
    user=session.scalars(query).first()
    if request.method=="GET":
        query=select(Sales_detail)
        sales_detail=session.scalars(query).all()

        results=[]
        for s in sales_detail:
            d={"id":s.id,
               
               "product_id":s.product_id,
               "sales_id":s.sales_id,
               "quantity":s.quantity,
               
            }
            results.append(d)
        return jsonify(results),200

    elif request.method =="POST":
        data=request.get_json()
        if data["product_id"] == "" or data["sales_id"] == "" or data["quantity"]=="":
            error={"Error":"missing fields required"}
            return jsonify(error),405
        else:
            new_sales_details=Sales_detail(
                product_id=data["product_id"],
                sales_id=data["sales_id"],
                quantity=data["quantity"],
               
            )   

            session.add(new_sales_details)     
            session.commit()

            return jsonify({"message":"sales_details added successfully"}),201

    else:
        error={"Error":"Method not allowed"}
        return jsonify(error),405

@app.route("/payment", methods=["GET","POST"])
@jwt_required()
def payments():
    email = get_jwt_identity()
    query = select(User).filter_by(email=email)
    user=session.scalars(query).first()
    if request.method=="GET":
        query=select(Payment)
        payments=session.scalars(query).all()

        results=[]
        for payment in payments:
            p={"id":payment.id,
               "sales_id":payment.sales_id,
               "payment_method":payment.payment_method,
               "payment_date":payment.payment_date
            }

            results.append(p)
        return jsonify(results),200

    elif request.method =="POST":
            data=request.get_json()
           
            if  data["sales_id"] == "" or data["payment_method"]=="" or data["payment_date"] =="" :
                error={"Error":"missing fields required"}
                return jsonify(error),405
            else:
                new_payments=Payment(
                    
                    sales_id=data["sales_id"],
                    payment_method=data["payment_method"],
                    payment_date=datetime.strptime(data["payment_date"],"%Y-%m-%d"),
                    
                )   
    
                session.add(new_payments)     
                session.commit()
                return jsonify({"Message":"payments added successfully"}),201

    else:
        error={"Error":"method not allowed"}
        return jsonify(error),405


app.run(debug=True)