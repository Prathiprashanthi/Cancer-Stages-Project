from django.shortcuts import render, redirect
from userapp.models import *
from django.contrib import messages
import urllib.request
import urllib.parse
import random 
import time
from adminapp.models import *
import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm  import SVC
from sklearn.metrics import accuracy_score,f1_score, recall_score, precision_score, auc, roc_auc_score, roc_curve
import ssl
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime



#Create your views here.

# SMS send
def sendSMS(user, otp, mobile):
    data = urllib.parse.urlencode({
        'username': 'Codebook',
        'apikey': '56dbbdc9cea86b276f6c',
        'mobile': mobile,
        'message': f'Hello {user}, your OTP for account activation is {otp}. This message is generated from https://www.codebook.in server. Thank you',
        'senderid': 'CODEBK'
    })
    data = data.encode('utf-8')
    # Disable SSL certificate verification
    context = ssl._create_unverified_context()
    request = urllib.request.Request("https://smslogin.co/v3/api.php?")
    f = urllib.request.urlopen(request, data,context=context)
    return f.read()



# User Register details
def register(req):
    if req.method == 'POST' :
        name = req.POST.get('myName')
        age = req.POST.get('myAge')
        password = req.POST.get('myPwd')
        phone = req.POST.get('myPhone')
        email = req.POST.get('myEmail')
        address = req.POST.get("address")
        image = req.FILES['image']
        number = random.randint(1000,9999)
        
        print(number)
        try:
            user_data = User_details.objects.get(Email = email)
            messages.warning(req, 'Email was already registered, choose another email..!')
            return redirect("register")
        except:
            sendSMS(name,number,phone)
            User_details.objects.create(Full_name = name, Image = image, Age = age, Password = password, Address = address, Email = email, Phone_Number = phone, Otp_Num = number)
            mail_message = f'Registration Successfully\n Your 4 digit Pin is below\n {number}'
            print(mail_message)
            send_mail("Student Password", mail_message , settings.EMAIL_HOST_USER, [email])
            req.session['Email'] = email
            messages.success(req, 'Your account was created..')
            return redirect('otpverify')
    return render(req, 'user/user-register.html')

# User Login 
def login(req):
    if req.method == 'POST':
        user_email = req.POST.get('uemail')
        user_password = req.POST.get('upwd')
        print( user_email,user_password)
        
        # try:
        user_data = User_details.objects.get(Email = user_email)
        print(user_data)
        if user_data.Password == user_password:
            if user_data.Otp_Status == 'verified' and user_data.User_Status=='accepted':
                req.session['User_id'] = user_data.User_id
                messages.success(req, 'You are logged in..')
                user_data.No_Of_Times_Login += 1
                user_data.save()
                return redirect('userdashboard')
            elif user_data.Otp_Status == 'verified' and user_data.User_Status=='pending':
                messages.info(req, 'Your Status is in pending')
                return redirect('login')
            else:
                messages.warning(req, 'verifyOTP...!')
                req.session['Email'] = user_data.Email
                return redirect('otpverify')
        else:
            messages.error(req, 'incorrect credentials...!')
            return redirect('login')
            
        # except:
        #     if user_data.Email == user_email and user_data.Password != user_password:
        #         messages.info(req, 'Password was incorrect..!')
        #         return redirect('login')
        #     messages.warning(req, 'Pending Account  Admin needs to be Accept your request')
            # return redirect('login')
    return render(req, 'main/main-user.html')



# def login(req):
#     if req.method == 'POST':
#         user_email = req.POST.get('uemail')
#         user_password = req.POST.get('upwd')

#         try:
#             user_data = User_details.objects.get(Email = user_email)
#             if user_data.Password == user_password:
#                 if user_data.Otp_Status == 'verified' and user_data.User_Status == 'accepted':
#                     req.session['User_id'] = user_data.User_id
#                     user_data.No_Of_Times_Login += 1
#                     user_data.save()
#                     # print(user_data.No_Of_Times_Login,'no of logins')
#                     messages.success(req, 'You are logged in..')
#                     return redirect('userdashboard')
#                 elif user_data.Otp_Status == 'pending':
#                     req.session['User_id'] = user_data.User_id
#                     return redirect('login')
#                 elif  user_data.Otp_Status == 'verified' and user_data.User_Status == 'pending':
#                     req.session['User_id'] = user_data.User_id
#                     messages.warning(req, 'Your Request was in pending. Please Try after some time. Thank You..!')
#                     return redirect('login')
#             else:
#                 messages.warning(req, 'Password was incorrect..!')
#                 return redirect('login')
#         except:
#             if user_data.Email == user_email and user_data.Password != user_password:
#                 messages.info(req, 'Password was incorrect..!')
#                 return redirect('login')
#             messages.warning(req, 'Once Check your passowrd and mail id, or you did not have an account please register..!')
#             return redirect('login')
#     return render(req, 'main/main-user.html')

# OTP Verification 
def otpverify(req):
    user_id = req.session['Email']
    user_o = User_details.objects.get(Email = user_id)
    print(user_o.Otp_Num,'data otp')
    if req.method == 'POST':
        user_otp = req.POST.get('otp')
        u_otp = int(user_otp)
        if u_otp == user_o.Otp_Num:
            user_o.Otp_Status = 'verified'
            user_o.save()
            messages.success(req, 'OTP verification was Success. Now you can continue to login..!')
            return redirect('home')
        else:
            messages.error(req, 'OTP verification was Faild. You entered invalid OTP..!')
            return redirect('otpverify')
    return render(req, 'user/user-otpverify.html')

# user-dashboard Function
def userdashboard(req):
    prediction_count =  User_details.objects.all().count()
    user_id = req.session["User_id"]
    user = User_details.objects.get(User_id = user_id)
    return render(req, 'user/user-dashboard.html', {'predictions' : prediction_count, 'la' : user})


# user-profile Function
def profile(req):
    user_id = req.session["User_id"]
    user = User_details.objects.get(User_id = user_id)
    if req.method == 'POST':
        user_name = req.POST.get('userName')
        user_age = req.POST.get('userAge')
        user_phone = req.POST.get('userPhNum')
        user_email = req.POST.get('userEmail')
        user_address = req.POST.get("userAddress")
        # user_img = request.POST.get("userimg")

        user.Full_name = user_name
        user.Age = user_age
        user.Address = user_address
        user.Phone_Number = user_phone
        user.Email=user_email
       

        if len(req.FILES) != 0:
            image = req.FILES['profilepic']
            user.Image = image
            user.Full_name = user_name
            user.Age = user_age
            user.Address = user_address
            user.Phone_Number = user_phone
            user.Email=user_email
            user.Address=user_address
            
            user.save()
            messages.success(req, 'Updated SUccessfully...!')
        else:
            user.Full_name = user_name
            user.Age = user_age
            user.save()
            messages.success(req, 'Updated SUccessfully...!')
            
    context = {"i":user}
    return render(req, 'user/user-profile.html',context)

from sklearn.ensemble import RandomForestClassifier
# predictdiabetes form Function
def predict(req):
    if req.method == 'POST':
        Smoking = req.POST.get('field1')
        Shortness_of_Breath = req.POST.get('field2')
        Balanced_Diet = req.POST.get('field3')
        Dust_Allergy = req.POST.get('field4')
        Alcohol_use = req.POST.get('field5')
        Fatigue = req.POST.get('field6')
        Wheezing = req.POST.get('field7')
        Obesity = req.POST.get('field8')
        Passive_Smoker = req.POST.get('field9')
        Coughing_of_Blood =req.POST.get('field10')
        print(Smoking,Shortness_of_Breath,Balanced_Diet,Dust_Allergy,Alcohol_use,Fatigue,Wheezing,Obesity, Passive_Smoker, Coughing_of_Blood)
        import pickle
        file_path = 'rf_level.pkl'  # Path to the saved model file

        with open(file_path, 'rb') as file:
            loaded_model = pickle.load(file)
            res =loaded_model.predict([[Smoking,Shortness_of_Breath,Balanced_Diet,Dust_Allergy,Alcohol_use,Fatigue,Wheezing,Obesity, Passive_Smoker, Coughing_of_Blood]])
            #res=loaded_model.predict([[1,2,5,4,7,8,7,6,4,3]])
            print(res,'hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh')

            dataset = Upload_dataset_model.objects.last()
            # print(dataset.Dataset)
            df=pd.read_csv(dataset.Dataset.path)
            X = df.drop('Level', axis = 1)
            y = df['Level']
          

            from sklearn.model_selection import train_test_split
            X_train,X_test,y_train,y_test = train_test_split(X,y,random_state=1,test_size=0.2)


            from sklearn.ensemble import RandomForestClassifier
            XGB = RandomForestClassifier()
            XGB.fit(X_train, y_train)

            # prediction
            train_prediction= XGB.predict(X_train)
            test_prediction= XGB.predict(X_test)
            print('*'*20)

            # evaluation
            from sklearn.metrics import accuracy_score
            accuracy = round(accuracy_score(y_test,test_prediction)*100, 2)
            precession = round(precision_score(test_prediction,y_test,average = 'macro')*100, 2)
            recall = round(recall_score(test_prediction,y_test,average = 'macro')*100, 2)
            f1_score = round(recall_score(test_prediction,y_test,average = 'macro')*100, 2)
            print(precession, accuracy,recall, f1_score,'uuuuuuuuuuuuuuuuuuuuuuuuuuu')
            
            if res == 1:
                messages.success(req,"Cancer Level is Low")
            elif res ==2:
                messages.success(req,"cancer Level is medium")
            else:
                messages.warning(req,"Cancer Level is High")
            print(res,'rerererererererereeererere')
            context = {'accc': accuracy,'pre': precession,'f1':f1_score,'call':recall,'res':res}
            res = int(res)
            print(type(res), 'ttttttttttttttttttttttttt')
            return render(req, 'user/user-result.html',context)
    return render(req, 'user/user-predict.html')


# Result function
def result(req):
    return render(req, 'user/user-result.html')

# User Logout
def userlogout(req):
    user_id = req.session["User_id"]
    user = User_details.objects.get(User_id = user_id) 
    t = time.localtime()
    user.Last_Login_Time = t
    current_time = time.strftime('%H:%M:%S', t)
    user.Last_Login_Time = current_time
    current_date = time.strftime('%Y-%m-%d')
    user.Last_Login_Date = current_date
    user.save()
    messages.info(req, 'You are logged out..')
    print(user.Last_Login_Time)
    # print(user.Last_Login_Date)
    return redirect('login')
