# it has to have to have a ruote
# it has to have a method (get/put/post/delete)
# it has to have a status code(200,201,403)
# it has to return data as Json(key :value pair)
import sentry_sdk
from flask import Flask,request,jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager,jwt_required,create_access_token,get_jwt_identity
from sqlalchemy import create_engine,select
from sqlalchemy.orm import Session
from model import Base,Product,User,Purchase,Sale,Sales_detail,Payment
from datetime import datetime
from flask_bcrypt import Bcrypt
from mpesa import make_stk_push
from generate_receipts import create_pdf


# import json
sentry_sdk.init(
    dsn="https://0ae45aac38007871a7f2fc2ca694a475@o4512046022524928.ingest.us.sentry.io/4512046231322624",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)

app = Flask(__name__)
CORS(app,resources={ r"/*":{
    "origins":"*",
    "allowed_headers":["Content-Type","Authorization"]
}})
# 
# CORS(app)
app.config["JWT_SECRET_KEY"]="PPDR123"
jwt=JWTManager(app)
bcrypt=Bcrypt(app)

# create a connection to the db using sqlalchemy engine
engine = create_engine("sqlite:///./flask_duka_api.db",echo=True)

# create  talbes into the db using sqlalchemy
Base.metadata.create_all(engine) 

#create a session to do sql transaction
session= Session(engine)

allowed_methods=["GET","POST","PUT","DELETE","PATCH","HEAD"]

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

@app.route("/register",methods=allowed_methods)
def register():

    if request.method=="POST":
        try:
            data = request.get_json()
            print("REGISTER DATA:",data)
            if "full_name" not in data.keys() or "email" not in data.keys()  or "password" not in data.keys():
                error={"Error":"All fields should me filled"}
                return jsonify(error),403
            query=select(User).filter_by(email=data["email"])
            user=session.scalars(query).first()
            if user:
                print("USER ALREADY FOUND",user.email)
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
            return jsonify(
                 
                {"user":{"id":new_user.id,
                         "full_name":new_user.full_name,
                         "email": new_user.email},
                         "success":"user added succesfully",
                         "token":token
            }),201
        except:
            error={"Error":"sorry try again later"}
            return jsonify(error),500
    else:
        error={"Error":"method not allowed"}
        return jsonify(error),405
@app.route("/login",methods=allowed_methods)
def login():
    if request.method=="POST":
        try: 
            data=dict(request.get_json())
            print("LOGIN DATA:",data)
            if "email" not in data.keys()  or "password" not in data.keys():
                error={"Error":"All fields should me filled"}
                return jsonify(error),403
            
            query=select(User).filter_by(email=data["email"])
            user=session.scalars(query).first()
            print("FOUND USER:",user)
            if not user:
                 return jsonify({"message":"user not found"})
            if not bcrypt.check_password_hash(user.password,data["password"]):
                return jsonify({"message":"invalid password"}),401

            token = create_access_token(identity=data["email"])
            
            return jsonify({
                
                 "user":{
                      "id":user.id,
                      "email":user.email,
                      "full_name":user.full_name},

                      "success":"login successful",
                      "token":token
            }),200

        except Exception as e:
            sentry_sdk.capture_exception(e)
        return jsonify({"Error":"try again later"}),500
    else:
        error={"Error":"method not allowed"}
        return jsonify(error),405

@app.route("/products", methods=allowed_methods)
@jwt_required()
def products():
    email = get_jwt_identity()
    query = select(User).filter_by(email=email)
    user=session.scalars(query).first()

    if request.method == "GET":
        try:

            query=select(Product)
            products=session.scalars(query).all()

            results=[]

            for product in products:
                        
                        s={"id":product.id,
                        "user_id":product.user_id,
                        "product_name":product.product_name,
                        "buying_price":product.buying_price,
                        "selling_price":product.selling_price,
                        "created_at":product.created_at
                        }

                        results.append(s)
            return jsonify(results),200
        except Exception as e:
            sentry_sdk.capture_exception(e)
        return jsonify({"Error":"sorry try again later"})
            
    elif request.method=="POST":
        try:
            data = request.get_json()
            if data["product_name"] == "" or data["buying_price"] ==""or data["selling_price"]=="":
                error ={"Error":"Ensure all fields are set"}
                return jsonify(error), 403
            else:
                #store in the db
                new_product = Product(
                    user_id = user.id,
                    product_name = data["product_name"],
                    buying_price = float(data["buying_price"]),
                    selling_price = float(data["selling_price"]),
                    created_at=datetime.utcnow()
                )
            
                session.add(new_product)
                session.commit()

            return jsonify({"Message":"new products added"}),201
        except Exception as e:
            sentry_sdk.capture_exception(e)
        return jsonify({"Error":"sorry,try again later"}),500

    else:
            error ={"Error":"Method not allowed"}
            return jsonify(error),405

@app.route("/purchase",methods=allowed_methods)
@jwt_required
def purchase():
    email = get_jwt_identity()
    query = select(User).filter_by(email=email)
    user=session.scalars(query).first()
    if request.method=="GET":
        try:

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
        except Exception as e:
            sentry_sdk.capture_exception(e)
        return jsonify({"Error":"try again later"}),500
            
    elif request.method=="POST":
            try:
                data = request.get_json()

                if data["product_id"] == "" or data["quantity"] == "" or data["purchase_date"]=="" or data["supplier"]=="":
                            error={"Error":"missing fields required"}
                            return jsonify(error),403
                else:
                            new_purchase=Purchase(
                                product_id=data["product_id"],
                                quantity=data["quantity"],
                                purchase_date=datetime.strptime(data["sales_date"],"%Y-%m-%d"),
                           
                            )   
                
                            session.add(new_purchase)     
                            session.commit()
                
                            return jsonify({"message":"sales added successfully"})
            except Exception as e:
                sentry_sdk.capture_exception(e)
            return jsonify({"Error":"try again later"}),500
    else:
                error={"Error":"methhod not allowed"}
                return jsonify(error),405

@app.route("/sale",methods=allowed_methods)
@jwt_required()
def sale():
    email = get_jwt_identity()
    query = select(User).filter_by(email=email)
    user=session.scalars(query).first()
    if request.method=="GET":
        try:
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
        except Exception as e:
            sentry_sdk.capture_exception(e)
        return jsonify({"Error":"try again later"}),500

    elif request.method =="POST":
        try:
            data=request.get_json()

            if data["sales_date"] == "" or data["total_amount"]=="":
                error={"Error":"missing fields required"}
                return jsonify(error),403
            else:
                new_sales=Sale(
                    user_id=user.id,
                    sales_date=datetime.strptime(data["sales_date"],"%Y-%m-%d"),
                    total_amount=data["total_amount"]
                )   

                session.add(new_sales)     
                session.commit()

                return jsonify({"message":"sales added successfully"})
        except Exception as e:
            print(e)
            sentry_sdk.capture_exception(e)
        return jsonify({"Error":"try again later"}),500
    else:
        error={"Error":"method not allowed"}
        return jsonify(error),405

@app.route("/sales-detail",methods=allowed_methods)
@jwt_required()
def sales_detail():

    email = get_jwt_identity()
    query = select(User).filter_by(email=email)
    user=session.scalars(query).first()
    if request.method=="GET":
        try:
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
        
        except Exception as e:
            sentry_sdk.capture_exception(e)
        return jsonify({"Error":"try again later"})

    elif request.method =="POST":
        try:
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
        except Exception as e:
            sentry_sdk.capture_exception(e)
        return jsonify({"Error":"try again later"}),500

    else:
        error={"Error":"Method not allowed"}
        return jsonify(error),405

@app.route("/payment", methods=allowed_methods)
@jwt_required()
def payments():
    email = get_jwt_identity()
    query = select(User).filter_by(email=email)
    user=session.scalars(query).first()
    if request.method=="GET":
        try:
            query=select(Payment)
            payments=session.scalars(query).all()

            results=[]
            for payment in payments:
                p={"id":payment.id,
                "sales_id":payment.sales_id,
                "amount":payment.amount
                }

                results.append(p)
            return jsonify(results),200
        except Exception as e:
            sentry_sdk.capture_exception(e)
        return jsonify({"Error":"try again later"}),500

    elif request.method =="POST":
                try:
                    data=request.get_json()
                
                    if  data["sales_id"] == "" or data["amount"]=="":
                        error={"Error":"missing fields required"}
                        return jsonify(error),405
                    else:
                        new_payments=Payment(
                            
                            sales_id=data["sales_id"],
                            # payment_method=data["payment_method"],
                            # payment_date=datetime.strptime(data["payment_date"],"%Y-%m-%d"),
                            amount=data["amount"]
                            
                        )   
            
                        session.add(new_payments)     
                        session.commit()
                        return jsonify({"Message":"payments added successfully"}),201
                except Exception as e:
                    sentry_sdk.capture_exception(e)
                return jsonify({'Error':"try again later"}),500
    else:
        error={"Error":"method not allowed"}
        return jsonify(error),405
    
@app.route("/stk_push",methods=allowed_methods)
def stk_push():
     
     try:
                payload=request.get_json()
                print(payload)
                response=make_stk_push(payload)
                new_payment=Payment(sales_id=payload["sales_id"],
                                    amount=payload["amount"],
                                    phone_number=payload["phone_number"],
                                    mrid=response.get("MerchantRequestID"),
                                    crid=response.get("CheckoutRequestID"),
                                    status="pending")
                session.add(new_payment)
                session.commit()
                return {"Message":"stk push initiator"}
     except Exception as e:
              print(f"stk push error: {e}")
              session.rollback()
              return{"message":"stk push failed"}

@app.route("/saf-callback",methods=allowed_methods)
def saf_callback():
     try:
          payload=request.get_json() 
          body=payload.get(
          'Body',{}
          )
          stkCallback=body.get('stkCallback',{})
          result_code=stkCallback.get('ResultCode')
          mrid=stkCallback.get('MerchantRequestID')
          crid=stkCallback.get('CheckoutRequestID')
          payment=session.scalars(select(Payment).where(Payment.mrid == mrid,Payment.crid==crid)).first()
          if payment:
               
               if result_code ==0:
                    # print("result code-------",result_code)
                    callback_metadata=stkCallback.get('CallbackMetadata',{}).get('Item',[])
                    for item in callback_metadata:
                        if item.get('Name') == 'MpesaReceiptNumber':
                            payment.transaction_code=item.get('Value')
                            payment.status = "completed"
                            session.commit()
                            text=f"Transaction code:{payment.transaction_code},Amount : {payment.amount}"
                            print("before pdf----")
                            create_pdf(text,payment.transaction_code)
                            print("after pdf---")
                            return{"message":"callback processed successfully"}
                    else:
                          return{"message":"receipt number not found"}

               else:
                    #  payment.status="failed"
                    #  session.commit()
                             # Commit payment status FIRST — this is critical
                     return{"message":"payment failed"}
          else:
                # payment.status="failed"
                # session.commit()
                print("payment not found")
                return{"message":"payment not foud"}
               
     except Exception as e:
                            import traceback
                            traceback.print_exc()

                            print(f"Error Processing Callback {e}")
                            session.rollback()
                            return{"Message":"callback received"}

app.run(debug=True)