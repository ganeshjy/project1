import os
import random
import shutil
import smtplib
import string
import bcrypt
import uvicorn
import jwt
import pymongo
from datetime import datetime 
from bson import ObjectId
from fastapi import FastAPI, HTTPException, Path, Request, Form, File, UploadFile
from fastapi import Depends
from secrets import token_hex
from pathlib import Path
from fastapi.encoders import jsonable_encoder
from gridfs import GridFS
from jose import JWTError,jwt
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
c = pymongo.MongoClient('mongodb+srv://kganeshjyothi:ganesh8450@cluster0.gxet2oh.mongodb.net/')
db = "sample"
if db not in c.list_database_names():
    db = c[db]
db= c.get_database(db) 
col ="student" 
if col not in db.list_collection_names():
    db.create_collection(col)
col=db.col
app = FastAPI()
app.add_middleware(SessionMiddleware,secret_key="gane")

templates = Jinja2Templates(directory="templates")
app.mount("/static",StaticFiles(directory="static"),name="static")

@app.get("/login",response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse("Signup.html",{"request":request})


@app.get("/signin",response_class=HTMLResponse)
def signin(request: Request):
    return templates.TemplateResponse("Signin.html",{"request":request})

@app.get("/logout",response_class=HTMLResponse)
def logout(request:Request):
    request.session.clear()
    return RedirectResponse(url="/signin", status_code=303)

@app.post("/newuser")
def newuser(request: Request,username:str = Form(),email: str = Form(),password: str = Form(),conformpassword: str = Form()):
     # check wheather the username or email existing
    # existing_user=col.find_one({"$or": [{"Username": username}]})
    existing_user=col.find_one({"$or": [{"Username": username}, {"Email": email}]})

    if existing_user:
        return templates.TemplateResponse("Signup.html",{"request":request, "error_username":"Username or Email already exists"})
    # checking password=conformpassword
    if password!=conformpassword:
        # return {"Info":"password and retyped password are not same"}
        return templates.TemplateResponse("Signup.html",{"request":request, "error_conpassword":"password and conformpassword is incorrect"})
     # Hash the password before storing it in the database
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    rec ={"Username":username,
            "Email":email,
            "password":hashed_password.decode('utf-8'),
            "path":"../static/images/user.jpg" ,
            "account":"user"      
            }
    col.insert_one(rec)
    return home(email,request)
    

def home(username,request):
    payload={"Email":username}
    entoken=jwt.encode(payload, key="jyothi", algorithm="HS256")
    return templates.TemplateResponse("dashboard.html",{"request": request,"token":entoken})


@app.post("/token")
async def token(request: Request, data: dict):
    # print("hello")
    # print(data)
    try:
        decode_token = jwt.decode(data.get('token'), "jyothi", algorithms=["HS256"])
        # print('Decoded Token:', decode_token)
        user_data = col.find_one({"Email": decode_token["Email"]}, {"_id": 0})
        
        request.session["_email"]=decode_token["Email"]
        # print('User Data:', user_data)
        return jsonable_encoder(user_data)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@app.post("/logincheck")
def logincheck(request: Request, email: str = Form(), password: str = Form()):
    rec = col.find_one({"Email": email})    
    if rec == None:
         return templates.TemplateResponse("Signin.html", {"request": request, "error_email": "User not found in db"})
    hashed_password = rec.get('password')

    if hashed_password is None:
        return templates.TemplateResponse("Signin.html",{"request": request, "error_password": "Password not available for the user" })

      # Verify the hashed password
    if bcrypt.checkpw(password.encode('utf-8'), rec['password'].encode('utf-8')):
        return home(email, request)
    else:
        return templates.TemplateResponse("Signin.html", {"request":request,"error_password":"Invalid Password"}) 


@app.get("/sendotp",response_class=HTMLResponse)
def sendotp(request: Request):
    return templates.TemplateResponse("otp.html",{"request":request})


@app.post("/otp")
async def otp(request: Request, email:str=Form()):
    user=col.find_one({"Email":email})
    global eemail
    eemail=email
    if not user : 
        return templates.TemplateResponse("otp.html",{"request":request,"error_email":"user not found"})
        # raise HTTPException(status_code=400, detail="user not found")
    otp = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    user["otp"]=otp
    # a = col.update_one({"Email":email},{"$set":user})
    col.update_one({"_id":ObjectId(user["_id"])}, {"$set":user})
    server= smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("kganeshjyothi@gmail.com","xpym nuvl vgtj sfap")
    message = 'Subject:{}\n\n{}'.format('OTP for Password Reset', 'your otp is:' +otp )
    server.sendmail("kganeshjyothi@gmail.com", user["Email"], message)
    server.quit()
    return templates.TemplateResponse("otp1.html",{"request":request})


@app.post("/verifyotp")
async def verifyotp(request: Request, OTP:str=Form(), Password:str=Form(),Con_Password:str=Form()):
    # user=col.find_one({"Email":email})
    email=eemail
    data={"Email":email}
    user=col.find_one({"Email":email})
    if OTP==user["otp"]:
        if Password==Con_Password:
            update=col.update_one(data,{"$set":{"password":Password}})
            return  templates.TemplateResponse("dashboard.html",{"request":request})
        else:
            return templates.TemplateResponse("otp1.html",{"request":request,"error_conformpassword":"new password and conform password is incorrect"})
            # return{"msg":"your password is incorrect"}
    else:
        return templates.TemplateResponse("otp1.html",{"request":request, "error_otp":"your OTP is incorrect"})
        # return{"msg":"your OTP is incorrect"}



# updating password
@app.get("/newpassword",response_class=HTMLResponse)
def newpassword(request: Request):
    return templates.TemplateResponse("udtpwd.html",{"request":request})



# Check if the username and old password match
@app.post("/update_password")
async def update_password(request: Request,username: str = Form(),oldPassword: str = Form(),newPassword: str = Form(),confirmPassword: str = Form()):
   
    # Check if the username and old password match
    
    user = col.find_one({"Username": username})
    if user is None:
        return templates.TemplateResponse("udtpwd.html",{"request":request, "error_username":"Invalid username"})
        # return {"msg": "Invalid username or old password"}

    if bcrypt.checkpw(oldPassword.encode('utf-8'), user['password'].encode('utf-8')):        
        if oldPassword==newPassword:
            return templates.TemplateResponse("udtpwd.html",{"request":request, "error_oldpassword":" old password and new password is same"})
           
        else:
            # Check if the new password and confirm password match
            if newPassword != confirmPassword:
                return templates.TemplateResponse("udtpwd.html",{"request":request,"error_conformpassword":"New password and conform password is incorrect"})
            hashed_password = bcrypt.hashpw(newPassword.encode('utf-8'), bcrypt.gensalt())   
            update = col.update_one({"_id": ObjectId(user["_id"])}, {"$set": {"password": hashed_password.decode('utf-8')}})
            return templates.TemplateResponse("dashboard.html", {"request": request})

    else:
        return templates.TemplateResponse("udtpwd.html",{"request":request, "error_oldpassword":"old password is incorrect"})
   

# dashboard
@app.get("/dashboard",response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html",{"request":request})


# myaccount
@app.get("/details",response_class=HTMLResponse)
def Myaccount(request: Request):
    return templates.TemplateResponse("myaccount.html",{"request":request})


# upload img
@app.post("/upload_image",response_class=HTMLResponse)
async  def upload_img(request: Request, username:str=Form(),profilePic: UploadFile = File(...)):
    recc=col.find_one({"Username":username})
    file_path=recc['path']
    path= os.path.join('static/images/',f"{username}_{profilePic.filename}")
    if(path!=file_path):
        with open(path,"wb") as images:
            shutil.copyfileobj(profilePic.file,images)
        col.update_one({"Username":username},{'$set':{'path':path}})
    # return templates.TemplateResponse("dashboard.html",{"request":request})
     # Redirect to the dashboard page after uploading image
    return RedirectResponse(url="/dashboard", status_code=303)


# displaying img
@app.get("/display_image", response_class=HTMLResponse)  
def my_account(request: Request):
    username = request.headers.get("Authorization").split(" ")[1] 
    user_data = col.find_one({"Username": username})
    return templates.TemplateResponse("myaccount.html", {"request": request, "image_path": user_data['path']})


@app.post("/upload_image",response_class=HTMLResponse)
async  def upload_img(request: Request, username:str=Form(),profilePic: UploadFile = File(...)):
    photo=col.find_one({"Username": username})
    return{photo}
   

# deleting img
@app.post("/del_img", response_class=HTMLResponse)
def deleteimg(request: Request, username:str=Form()):
    user_data=col.find_one({"Username":username},{"_id": 0})
    img_path=user_data['path']
    if(img_path!='../static/images/user.jpg'):
        os.remove(img_path)
        col.update_one({"Username":username},{'$set':{'path':'../static/images/user.jpg'}})
    return templates.TemplateResponse("dashboard.html",{"request":request})
    

# Create Shipment
@app.get("/createshipment",response_class=HTMLResponse)
def createshipment(request: Request):
    return templates.TemplateResponse("createshipment.html",{"request":request})


# inserting the create shipment details in database
@app.post("/cre_ship")
async def cre_ship(request: Request,
                   username:str=Form(),
                   ShipmentNumber: int = Form(),
                    RouteDetails: str = Form(),
                    Device: str = Form(),
                    PONumber: int = Form(),
                    NDCNumber: int = Form(),
                    SlnoofGoods: str = Form(),
                    Conno: str = Form(),
                    GoodsType: str = Form(),
                    ExpectedDeliveryDate: str = Form(),
                    DeliveryNumber: int = Form(),
                    BatchId: str = Form(),
                    ShipmentDescription: str = Form(),
):
    
    shipment_col="shipment_data"
    if shipment_col not in db.list_collection_names():
        db.create_collection(shipment_col)
    shipment_col1=db[shipment_col]    
    existing_shipment=shipment_col1.find_one({"ShipmentNumber":ShipmentNumber})
    if existing_shipment:
        return{"Info" :"ShipmentNumber already exists"}    
      # Convert ExpectedDeliveryDate to a datetime object
    # formatted_delivery_date = datetime.strptime(ExpectedDeliveryDate, "%Y-%m-%d")
    _email_=request.session.get("_email",None)
    shipment_data ={
        "ShipmentNumber":ShipmentNumber,
        "RouteDetails":RouteDetails,
         "Device": Device,
        "PONumber": PONumber,
        "NDCNumber": NDCNumber,
        "SlnoofGoods": SlnoofGoods,
        "Conno": Conno,
        "GoodsType":GoodsType,
        "ExpectedDeliveryDate": ExpectedDeliveryDate,
        "DeliveryNumber": DeliveryNumber,
        "BatchId": BatchId,
        "ShipmentDescription": ShipmentDescription,
        "email":_email_
    }
    shipment_col1.insert_one(shipment_data)
    # return{"Successfully Inserted into database"}
    return templates.TemplateResponse("dashboard.html", {"request": request})


# geting the details of create shipment
@app.get("/myshipment_details",response_class=HTMLResponse)
def myshipment_details(request: Request):    
    _email_=request.session.get("_email",None)
    # print(ship_ment_)
    shipment_col="shipment_data"
    shipment_col1=db[shipment_col]
    shipments = shipment_col1.find({"email":_email_})#based on the email it display the shipment details
    return templates.TemplateResponse("myshipment.html",{"request":request, "shipments":shipments})

# device data
@app.get("/deviceDetails",response_class=HTMLResponse)
def deviceDetails(request:Request):
    device_col="device_data"
    device_collection=db[device_col]
    device_data=device_collection.find()
    return templates.TemplateResponse("device.html",{"request":request, "device_data":device_data})


