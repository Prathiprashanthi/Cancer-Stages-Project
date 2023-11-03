from django.shortcuts import render, redirect
from adminapp.models import  All_users_model, Upload_dataset_model
from userapp.models import User_details, Predict_details
from django.contrib import messages
from django.core.paginator import Paginator
import pandas as pd
from adminapp.models import *
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble  import GradientBoostingClassifier
from sklearn.svm  import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble  import AdaBoostClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split

from xgboost import XGBClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from sklearn.metrics import accuracy_score,f1_score, recall_score, precision_score, auc, roc_auc_score, roc_curve

from sklearn.metrics import classification_report,confusion_matrix
from sklearn.model_selection import cross_val_score

from sklearn import metrics
from sklearn.naive_bayes import BernoulliNB,MultinomialNB
from sklearn.multiclass import OneVsRestClassifier
# import os
# import socket
import tensorflow as tf
import keras
from keras.models import Sequential
ann = Sequential()
from keras.layers import Dense


# Admin logout
def adminlogout(req):
    messages.info(req, 'You are logged out..!')
    return redirect('admin')

#Admin Dashboard index.html
def admindashboard(req):
    all_users_count =  User_details.objects.all().count()
    pending_users_count = User_details.objects.filter(User_Status = 'Pending').count()
    rejected_users_count = User_details.objects.filter(User_Status = 'removed').count()
    accepted_users_count = User_details.objects.filter(User_Status = 'accepted').count()
    datasets_count = Upload_dataset_model.objects.all().count()
    no_of_predicts = Predict_details.objects.all().count()
    return render(req, 'admin/admin-dashboard.html',{'a' : pending_users_count, 'b' : all_users_count, 'c' : rejected_users_count, 'd' : accepted_users_count, 'e' : datasets_count, 'f' : no_of_predicts})

# Admin pending users
def pendingusers(req):
    pending = User_details.objects.filter(User_Status = 'Pending')
    paginator = Paginator(pending, 5) 
    page_number = req.GET.get('page')
    post = paginator.get_page(page_number)
    return render(req, 'admin/admin-pending-users.html', { 'user' : post})

# Admin all users
def allusers(req):
    all_users = User_details.objects.all()
    paginator = Paginator(all_users, 5)
    page_number = req.GET.get('page')
    post = paginator.get_page(page_number)
    return render(req, 'admin/admin-all-users.html', {"allu" : all_users, 'user' : post})

#Deleet user button in allusers
def delete_user(req, id):
    User_details.objects.get(User_id = id).delete()
    messages.warning(req, 'User was Deleted..!')
    return redirect('allusers')

# Acept users button
def accept_user(req, id):
    status_update = User_details.objects.get(User_id = id)
    status_update.User_Status = 'accepted'
    status_update.save()
    messages.success(req, 'User was accepted..!')
    return redirect('pendingusers')

# Remove user button
def reject_user(req, id):
    status_update2 = User_details.objects.get(User_id = id)
    status_update2.User_Status = 'removed'
    status_update2.save()
    messages.warning(req, 'User was Rejected..!')
    return redirect('pendingusers')

# change status
# def change_status(req, id):
#     status_update = User_details.objects.get(User_id = id)
#     if (status_update.User_Status == 'accepted'):
#         status_update.User_Status = 'rejected'
#     else:
#         status_update.User_Status = 'accepted'

#     status_update.save()
#     return redirect('allusers')

# Admin upload dataset
def uploaddataset(req):
    if req.method == 'POST':
        file = req.FILES['data_file']
        # print(file)
        file_size = str((file.size)/1024) +' kb'
        # print(file_size)
        Upload_dataset_model.objects.create(File_size = file_size, Dataset = file)
        messages.success(req, 'Your dataset was uploaded..')
    return render(req, 'admin/admin-upload-dataset.html')

# Admin view dataset
def viewdataset(req):
    dataset = Upload_dataset_model.objects.all()
    paginator = Paginator(dataset, 5)
    page_number = req.GET.get('page')
    post = paginator.get_page(page_number)
    return render(req, 'admin/admin-view-dataset.html', {'data' : dataset, 'user' : post})

# Admin delete dataset button
def delete_dataset(req, id):
    dataset = Upload_dataset_model.objects.get(User_id = id).delete()
    messages.warning(req, 'Dataset was deleted..!')
    return redirect('viewdataset')

# Admin ANM Alogorithm
def anmalgm(req):
    
    return render(req, 'admin/admin-anm-algorithm.html')
def annalgm(req):
    return render(req,'admin/admin_ann_algoritham.html')

def logistc(req):
    return render(req, 'admin/admin_logistic.html')
  
def random(req):
    return render(req, 'admin/admin_randomforest.html')
  


# logistic_btn
def logistic_btn(req):
    dataset = Upload_dataset_model.objects.last()
    # print(dataset.Dataset)
    df=pd.read_csv(dataset.Dataset.path)

    X = df.drop('Level', axis = 1)
    y = df['Level']
    from sklearn.model_selection import train_test_split
    X_train,X_test,y_train,y_test = train_test_split(X,y,random_state=1,test_size=0.2)
    from sklearn.linear_model import LogisticRegression
    ANN = LogisticRegression()
    ANN.fit(X_train, y_train)

    # prediction
    train_prediction= ANN.predict(X_train)
    test_prediction= ANN.predict(X_test)
    print('*'*20)

    # evaluation
    from sklearn.metrics import accuracy_score
    accuracy = round(accuracy_score(y_test,test_prediction)*100, 2)
    precession = round(precision_score(test_prediction,y_test,average = 'macro')*100, 2)
    recall = round(recall_score(test_prediction,y_test,average = 'macro')*100, 2)
    f1_score = round(recall_score(test_prediction,y_test,average = 'macro')*100, 2)
    # Accuracy_train(accuracy_score(prediction_train,y_train))
    name = "Logistic Regression Algorithm"
    Logistic.objects.create(Accuracy=accuracy,Precession=precession,F1_Score=f1_score,Recall=recall,Name=name)
    data = Logistic.objects.last()
    messages.success(req, 'Algorithm executed Successfully')
    return render(req, 'admin/admin_logistic.html',{'i': data})
    
# random_btn
def randomforest_btn(req):
    dataset = Upload_dataset_model.objects.last()
    # print(dataset.Dataset)
    df=pd.read_csv(dataset.Dataset.path)
    

    
    X = df.drop('Level', axis = 1)
    y = df['Level']

    from sklearn.model_selection import train_test_split
    X_train,X_test,y_train,y_test = train_test_split(X,y,random_state=1,test_size=0.2)
    from sklearn.ensemble import RandomForestClassifier
    RDF = RandomForestClassifier()
    RDF.fit(X_train, y_train)

    # prediction
    train_prediction= RDF.predict(X_train)
    test_prediction= RDF.predict(X_test)
    print('*'*20)

    # evaluation
    from sklearn.metrics import accuracy_score
    accuracy = round(accuracy_score(y_test,test_prediction)*100, 2)
    precession = round(precision_score(test_prediction,y_test,average = 'macro')*100, 2)
    recall = round(recall_score(test_prediction,y_test,average = 'macro')*100, 2)
    f1_score = round(recall_score(test_prediction,y_test,average = 'macro')*100, 2)
    # Accuracy_train(accuracy_score(prediction_train,y_train))
    name = "Random Forest"
    RandomForest.objects.create(Accuracy=accuracy,Precession=precession,F1_Score=f1_score,Recall=recall,Name=name)
    data = RandomForest.objects.last()
    messages.success(req, 'Algorithm executed Successfully')
    return render(req, 'admin/admin_randomforest.html',{'i': data})
    

# Admin XGBOOST Algorithm
def xgbalgm(req):
    return render(req, 'admin/admin-xgboost-algorithm.html')

# XGBOOST_btn


# Admin ADA Boost Algorithm
def adabalgm(req):
    return render(req, 'admin/admin-adaboost-algorithm.html')


# Admin KNN Algorithm
def knnalgm(req):
    return render(req, 'admin/admin-knn-algorithm.html')

# KNN_btn
def KNN_btn(req):
    dataset = Upload_dataset_model.objects.last()
    # print(dataset.Dataset)
    df=pd.read_csv(dataset.Dataset.path)
   
    X = df.drop('Level', axis = 1)
    y = df['Level']
    
    from sklearn.model_selection import train_test_split
    X_train,X_test,y_train,y_test = train_test_split(X,y,random_state=1,test_size=0.2)
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X_train=scaler.fit_transform(X_train)
    X_test= scaler.transform(X_test)
    from sklearn.neighbors import KNeighborsClassifier
    KNN = KNeighborsClassifier()
    KNN.fit(X_train, y_train)

    # prediction
    train_prediction= KNN.predict(X_train)
    test_prediction= KNN.predict(X_test)
    print('*'*20)

    # evaluation
    from sklearn.metrics import accuracy_score
    accuracy = round(accuracy_score(y_test,test_prediction)*100, 2)
    precession = round(precision_score(test_prediction,y_test,average = 'macro')*100, 2)
    recall = round(recall_score(test_prediction,y_test,average = 'macro')*100, 2)
    f1_score = round(recall_score(test_prediction,y_test,average = 'macro')*100, 2)
    # Accuracy_train(accuracy_score(prediction_train,y_train))
    name = "KNN Algorithm"
    KNN_ALGO.objects.create(Accuracy=accuracy,Precession=precession,F1_Score=f1_score,Recall=recall,Name=name)
    data = KNN_ALGO.objects.last()
    messages.success(req, 'Algorithm executed Successfully')
    return render(req, 'admin/admin-knn-algorithm.html',{'i': data})

# Admin SXM Algorithm
def sxmalgm(req):
    return render(req, 'admin/admin-sxm-algorithm.html')

# SXM_btn
def SXM_btn(req):
    dataset = Upload_dataset_model.objects.last()
    # print(dataset.Dataset)
    df=pd.read_csv(dataset.Dataset.path)
    
    X = df.drop('Level', axis = 1)
    y = df['Level']
    
    from sklearn.model_selection import train_test_split
    X_train,X_test,y_train,y_test = train_test_split(X,y,random_state=1,test_size=0.2)
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X_train=scaler.fit_transform(X_train)
    X_test= scaler.transform(X_test)


    SXM = SVC()
    SXM.fit(X_train, y_train)

    # prediction
    train_prediction= SXM.predict(X_train)
    test_prediction= SXM.predict(X_test)
    print('*'*20)

    # evaluation
    from sklearn.metrics import accuracy_score
    accuracy = round(accuracy_score(y_test,test_prediction)*100, 2)
    precession = round(precision_score(test_prediction,y_test,average = 'macro')*100, 2)
    recall = round(recall_score(test_prediction,y_test,average = 'macro')*100, 2)
    f1_score = round(recall_score(test_prediction,y_test,average = 'macro')*100, 2)
    # Accuracy_train(accuracy_score(prediction_train,y_train))
    name = "SVC Algorithm"
    SXM_ALGO.objects.create(Accuracy=accuracy,Precession=precession,F1_Score=f1_score,Recall=recall,Name=name)
    data = SXM_ALGO.objects.last()
    messages.success(req, 'Algorithm executed Successfully')
    return render(req, 'admin/admin-sxm-algorithm.html',{'i':data})

# Admin Decission tree Algorithm
def dtalgm(req):
    return render(req, 'admin/admin-decission-algorithm.html')

# Decissiontree_btn 
def Decisiontree_btn(req):
    dataset = Upload_dataset_model.objects.last()
    # print(dataset.Dataset)
    df=pd.read_csv(dataset.Dataset.path)
   

    X = df.drop('Level', axis = 1)
    y = df['Level']

    from sklearn.model_selection import train_test_split
    X_train,X_test,y_train,y_test = train_test_split(X,y,random_state=1,test_size=0.2)
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X_train=scaler.fit_transform(X_train)
    X_test= scaler.transform(X_test)


   #  XGBoost
    from sklearn.tree import DecisionTreeClassifier
    DEC = DecisionTreeClassifier()
    DEC.fit(X_train, y_train)

    # prediction
    train_prediction= DEC.predict(X_train)
    test_prediction= DEC.predict(X_test)
    print('*'*20)

    # evaluation
    from sklearn.metrics import accuracy_score
    accuracy = round(accuracy_score(y_test,test_prediction)*100, 2)
    precession = round(precision_score(test_prediction,y_test,average = 'macro')*100, 2)
    recall = round(recall_score(test_prediction,y_test,average = 'macro')*100, 2)
    f1_score = round(recall_score(test_prediction,y_test,average = 'macro')*100, 2)
    name = "Decision Tree Algorithm"
    DT_ALGO.objects.create(Accuracy=accuracy,Precession=precession,F1_Score=f1_score,Recall=recall,Name=name)
    data = DT_ALGO.objects.last()
    messages.success(req, 'Algorithm executed Successfully')
    return render(req, 'admin/admin-decission-algorithm.html',{'i':data})

# Admin Comparison graph
def cgraph(req):

    details2 = KNN_ALGO.objects.last()
    c = details2.Accuracy
    print(c,'cccccccccccccccccccccccccccccccc')
    deatails3 = SXM_ALGO.objects.last()
    d = deatails3.Accuracy
    details4 = DT_ALGO.objects.last()
    e = details4.Accuracy
    details6 = Logistic.objects.last()
    g = details6.Accuracy
    details7 = RandomForest.objects.last()
    h = details7.Accuracy
    return render(req, 'admin/admin-graph-analysis.html', {'knn':c,'sxm':d,'dt':e,'log':g, 'ran':h})

def view_view(request):
    # df=pd.read_csv('heart.csv')
    data = Upload_dataset_model.objects.last()
    print(data,type(data),'sssss')
    file = str(data.Dataset)
    df = pd.read_csv(f'./media/{file}')
    table = df.to_html(table_id='data_table')
    return render(request,'admin/admin-view-view.html', {'t':table})



