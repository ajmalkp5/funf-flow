from django.shortcuts import render,redirect

from django.views.generic import View

from budget.models import Transaction
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.utils import timezone
from django.db.models import Sum
from django.utils.decorators import method_decorator



def sign_required(fn):
    def wrapper(request,*args,**kwargs):
        if not request.user.is_authenticated:
            return redirect("signin")
        else:
            return fn(request,*args,**kwargs)
    return wrapper




# localhost:8000/transactions/all/
# view for listing all transactions


@method_decorator(sign_required,name="dispatch")
class Transactionlistview(View):
    def get(self,request,*args,**kwargs):
        qs=Transaction.objects.filter(user_object=request.user)
        cur_month=timezone.now().month
        cur_year=timezone.now().year
        print(cur_month,cur_year)
        data=Transaction.objects.filter(
            created_date__month=cur_month,
            created_date__year=cur_year,
            user_object=request.user
        ).values("type").annotate(type_sum=Sum("amount"))
        print(data)
        cat_qs=Transaction.objects.filter(
            created_date__month=cur_month,
            created_date__year=cur_year,
            user_object=request.user
        ).values("category").annotate(cat_sum=Sum("amount"))
        print(cat_qs)
        
        
        return render(request,"transaction_list.html",{"data":qs,"type_total":data,"cat_data":cat_qs})




class Registrationform(forms.ModelForm):
    class Meta:
        model=User
        fields=["username","email","password"]
        widgets={
            "username":forms.TextInput(attrs={"class":"form-control"}),
            "email":forms.EmailInput(attrs={"class":"form-control"}),
            "password":forms.PasswordInput(attrs={"class":"form-control"})

        }




class LoginForm(forms.Form):
    username=forms.CharField()
    password=forms.CharField()




class Transactionform(forms.ModelForm):

    class Meta:
        model=Transaction
        exclude=("created_date","user_object")
        # fields="__all__"
        # fields[]=["title","amount","field1","field2"etc....]
        widgets={
            "title":forms.TextInput(attrs={"class":"form-control"}),
            "amount":forms.NumberInput(attrs={"class":"form-control"}),
            "type":forms.Select(attrs={"class":"form-control form-select"}),
            "category":forms.Select(attrs={"class":"form-control form-select"})
        }


# view for creating transaction
# localhost:8000/transactions/add/
@method_decorator(sign_required,name="dispatch")   
class Transactioncreateview(View):
    def get(self,request,*args,**kwargs):
        form=Transactionform()
        return render(request,"transaction_add.html",{"form":form})
    
    def post(self,request,*args,**kwargs):
        form=Transactionform(request.POST)
        if form.is_valid():
            data=form.cleaned_data
            Transaction.objects.create(**data,user_object=request.user)
            return redirect("transaction-list")
        else:
            return render(request,"transaction_add.html",{"form":form})


# transaction detailview
# localhost:8000/transaction/{id}/
# method get
@method_decorator(sign_required,name="dispatch")        
class Transactiondetailview(View):
    def get(self,request,*args,**kwargs):
        
        id=kwargs.get("pk")
        qs=Transaction.objects.get(id=id)
        return render(request,"transaction_detail.html",{"data":qs})

    
# transaction delete
#url: localhost:8000/transactions/{id}
# method get 
@method_decorator(sign_required,name="dispatch")   
class Transactiondeleteview(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        Transaction.objects.filter(id=id).delete()
        return redirect("transaction-list")
    

# transaction update
# url localhost:8000/transactions/{id}/change/ 
# method:get;post
@method_decorator(sign_required,name="dispatch")   
class TransactionUpdateview(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        transaction_object=Transaction.objects.get(id=id)
        form=Transactionform(instance=transaction_object)
        return render(request,"transaction_edit.html",{"form":form})
    
    def post(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        transaction_object=Transaction.objects.get(id=id)
        form=Transactionform(request.POST,instance=transaction_object)
        if form.is_valid():
            form.save()
            return redirect("transaction-list")
        else:
            return render(request,"transaction_edit.html",{"form":form})


@method_decorator(sign_required,name="dispatch")
class Signupview(View):
    def get(self,request,*args,**kwargs):
        form=Registrationform()
        return render(request,"register.html",{"form":form})
    
    def post(self,request,*args,**kwargs):
        form=Registrationform(request.POST)
        if form.is_valid():
            User.objects.create_user(**form.cleaned_data)
            print("created")
            return redirect("signin")
        else:
            print("failed")
            return render(request,"register.html",{"form":form})
        



# signin
# url:localhost:8000/signin/
# method get post
        

class Signinview(View):
    def get(self,request,*args,**kwargs):
        form=LoginForm()
        return render(request,"login.html",{"form":form})
    
    def post(self,request,*args,**kwargs):
        form=LoginForm(request.POST)
        if form.is_valid():
            u_name=form.cleaned_data.get("username")
            pwd=form.cleaned_data.get("password")
            user_object=authenticate(request,username=u_name,password=pwd)
            if user_object:
                login(request,user_object)
                return redirect("transaction-list")
        
        return render(request,"login.html",{"form":form})

        




# signout
# url:localhost:8000/logout/
# method get   

    
class Signgnoutview(View):
    def get(self,request,*args,**kwargs):
        logout(request)
        return redirect("signin")