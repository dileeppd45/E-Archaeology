import datetime
from django.shortcuts import render
from django.shortcuts import render, HttpResponse, redirect
from django.db import connection
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from django.http import JsonResponse
import uuid
from . import views
from datetime import date
cursor = connection.cursor()
# Create your views here.


def login(request):

    # request.session.clear()
    if request.method == "POST":
        userid = request.POST['userid']
        password = request.POST['password']
        cursor = connection.cursor()
        cursor.execute("select * from login where admin_id= '" + userid + "' AND password = '" + password + "'")
        admin = cursor.fetchone()
        if admin == None:
            cursor.execute("select * from museum where museum_id= '" + userid + "' AND password = '" + password + "'")
            museum = cursor.fetchone()
            if museum == None:
                cursor.execute("select * from user_register where user_id= '" + userid + "' AND password = '" + password + "'")
                user = cursor.fetchone()
                if user == None:
                    messages.error(request, 'Invalid Username Or Password!!')
                    return redirect("login")
                else:
                    request.session["uid"] = userid
                    return redirect('user_home')
            else:
                request.session["mid"] = userid
                return redirect('museum_home')
        else:
            request.session["aid"] = userid
            return redirect("admin_home")
    return render(request, "login.html")


def signup(request):
    if request.method == "POST":
        user_id = request.POST['uname']
        name = request.POST['name']
        address = request.POST['address']
        phone = request.POST['phone']
        email = request.POST['email']
        password = request.POST['password']
        cursor = connection.cursor()
        cursor.execute("select * from user_register where user_id ='" + user_id + "' ")
        data = cursor.fetchone()
        if data == None:
            cursor.execute("insert into user_register values('" + user_id + "','" + str(name) + "','" + str(address) + "','" + str(phone) + "','" + str(email) + "','" + str(password) + "')")
            return redirect("login")
        else:
            return HttpResponse("<script>alert('Usesrname already exixt Please enter a unique Username');window.location='../login';</script>")

    return render(request, "sign_up.html")


# ADMIN
def admin_home(request):
    try:
        if request.session["aid"] is None:
            return redirect(login)
    except KeyError:
        return redirect(login)
    return render(request, "admin_home.html")

def register_museum(request):
    try:
        if request.session["aid"] is None:
            return redirect(login)
    except KeyError:
        return redirect(login)
    success =False
    if request.method == "POST":
        cursor = connection.cursor()
        mid= request.POST['mid']
        cursor.execute("select * from museum where museum_id ='"+str(mid)+"' ")
        h = cursor.fetchone()
        if h == None:
            cursor.execute("select * from login where admin_id ='"+str(mid)+"'")
            h = cursor.fetchone()
            if h == None:
                cursor.execute("select * from user_register where user_id ='"+str(mid)+"' ")
                h = cursor.fetchone()
                if h == None:
                    name = request.POST['name']
                    cursor.execute("select * from museum where name ='"+str(name)+"'")
                    h = cursor.fetchone()
                    if h == None:
                        name= request.POST['name']
                        address = request.POST['address']
                        phone = request.POST['phone']
                        email = request.POST['email']
                        lat =request.POST['lat']
                        lon = request.POST['lon']
                        pas = request.POST['pas']
                        cursor.execute("insert into museum values('"+str(mid)+"','" + str(name) + "','" + str(address) + "', '" + str(phone) + "','"+ str(email) + "', '"+str(lat)+"','"+str(lon)+"','"+str(pas)+"') ")
                        success = True
                        return JsonResponse({'success': success})
                    else:
                        messages.error(request, "Error!! The museum name you entered is not available.. (" + str(name) + ") already taken.. ")
                        return redirect(register_museum)
        messages.error(request, "Error!! The museum id you entered is not available.. ("+str(mid)+") already taken.. ")
        return redirect(register_museum)
    return render(request, "admin_register_museum.html")

def view_museum(request):
    try:
        if request.session["aid"] is None:
            return redirect(login)
    except KeyError:
        return redirect(login)
    cursor = connection.cursor()
    cursor.execute("select * from museum")
    cdata = cursor.fetchone()
    if cdata ==None:
        return render (request, "admin_view_museum.html")
    cursor.execute("select * from museum")
    cdata = cursor.fetchall()
    return render (request, "admin_view_museum.html", {'data': cdata})

def edit_museum(request, id):
    try:
        if request.session["aid"] is None:
            return redirect(login)
    except KeyError:
        return redirect(login)
    cursor = connection.cursor()
    cursor.execute("select * from museum  where museum_id ='"+str(id)+"'")
    cdata = cursor.fetchone()
    return render(request, "admin_edit_museum.html", {'data': cdata})

def update_museum(request,id):
    try:
        if request.session["aid"] is None:
            return redirect(login)
    except KeyError:
        return redirect(login)
    if request.method == "POST":
        cursor = connection.cursor()
        name=request.POST['name']
        cursor.execute("select * from museum where name ='" + str(name) + "'and museum_id !='"+str(id)+"' ")
        h = cursor.fetchone()
        if h == None:
            address = request.POST['address']
            phone = request.POST['phone']
            email = request.POST['email']
            lat= request.POST['lat']
            lon= request.POST['lon']
            pas = request.POST['pas']
            cursor.execute("update museum set name ='"+str(name)+"' where museum_id='"+str(id)+"'")
            cursor.execute("update museum set address ='"+str(address)+"' where museum_id='"+str(id)+"'")
            cursor.execute("update museum set phone ='"+str(phone)+"' where museum_id='"+str(id)+"'")
            cursor.execute("update museum set email ='"+str(email)+"' where museum_id='"+str(id)+"'")
            cursor.execute("update museum set latitude ='"+str(lat)+"' where museum_id='"+str(id)+"' ")
            cursor.execute("update museum set longitude ='"+str(lon)+"' where museum_id='"+str(id)+"' ")
            cursor.execute("update museum set password ='"+str(pas)+"' where museum_id='"+str(id)+"' ")
            return redirect(view_museum)
        else:
            messages.error(request, "Error!! The museum name you entered is not available.. (" + str(name) + ") already taken.. ")
            return redirect("edit_museum",id=id)
def admin_museum_items(request,id):
    try:
        if request.session["aid"] is None:
            return redirect(login)
    except KeyError:
        return redirect(login)
    cursor = connection.cursor()
    cursor.execute("select * from item_details where seller_id ='"+str(id)+"' and status ='authorised'")
    mus_items=cursor.fetchall()
    cursor.execute("select * from item_details join bidding where item_details.seller_id ='"+str(id)+"' and item_details.item_id = bidding.item_id and bidding.status ='started' or item_details.seller_id ='"+str(id)+"' and item_details.item_id = bidding.item_id and bidding.status ='processing'")
    on_bidding =cursor.fetchall()
    cursor.execute("select * from item_details where seller_id ='"+str(id)+"' and status ='sold'")
    mus_sold = cursor.fetchall()
    cursor.execute("select * from item_details join bidding where item_details.buyer_id ='"+str(id)+"' and item_details.item_id = bidding.item_id and bidding.status ='sold'")
    mus_buyed =cursor.fetchall()
    cursor.execute("select * from museum where museum_id ='"+str(id)+"'")
    museum =cursor.fetchone()
    return render(request,'admin_museum_items.html',{'a':mus_items,'b':on_bidding,'c':mus_sold,'d':mus_buyed,'museum':museum})





def admin_location(request,id,jd):
    try:
        if request.session["aid"] is None:
            return redirect(login)
    except KeyError:
        return redirect(login)
    return render(request,"admin_location.html",{'lat':id,'lon':jd})


def admin_view_users(request):
    try:
        if request.session["aid"] is None:
            return redirect(login)
    except KeyError:
        return redirect(login)
    cursor = connection.cursor()
    cursor.execute("select * from user_register ")
    data = cursor.fetchall()
    return render(request,'admin_view_users.html',{'data':data})

def admin_user_items(request,id):
    try:
        if request.session["aid"] is None:
            return redirect(login)
    except KeyError:
        return redirect(login)
    cursor = connection.cursor()
    cursor.execute("select * from item_details where seller_id ='"+str(id)+"' and status ='approved'")
    mus_items=cursor.fetchall()
    cursor.execute("select * from item_details join bidding where item_details.seller_id ='"+str(id)+"' and item_details.item_id = bidding.item_id and bidding.status ='started' or item_details.seller_id ='"+str(id)+"' and item_details.item_id = bidding.item_id and bidding.status ='processing'")
    on_bidding =cursor.fetchall()
    cursor.execute("select * from item_details where seller_id ='"+str(id)+"' and status ='sold'")
    mus_sold = cursor.fetchall()
    cursor.execute("select * from item_details join bidding where item_details.buyer_id ='"+str(id)+"' and item_details.item_id = bidding.item_id and bidding.status ='sold'")
    mus_buyed =cursor.fetchall()
    cursor.execute("select * from user_register where user_id ='"+str(id)+"'")
    museum =cursor.fetchone()
    return render(request,'admin_user_items.html',{'a':mus_items,'b':on_bidding,'c':mus_sold,'d':mus_buyed,'museum':museum})




def item_details_pending(request):
    try:
        if request.session["aid"] is None:
            return redirect(login)
    except KeyError:
        return redirect(login)
    cursor = connection.cursor()
    cursor.execute("select * from item_details join user_register where item_details.status ='pending' and item_details.seller_id = user_register.user_id ")
    data = cursor.fetchall()
    return render(request,'admin_pending_item_details.html',{'data':data})

def approve_item(request,id):
    try:
        if request.session["aid"] is None:
            return redirect(login)
    except KeyError:
        return redirect(login)
    cursor = connection.cursor()
    cursor.execute("update item_details set status ='approved' where item_id='" + str(id) + "'")
    return redirect(item_details_pending)

def item_details_approved(request):
    try:
        if request.session["aid"] is None:
            return redirect(login)
    except KeyError:
        return redirect(login)
    cursor = connection.cursor()
    cursor.execute("select * from item_details where status ='approved' or status ='sold'")
    data = cursor.fetchall()
    return render(request,'admin_approved_item_details.html',{'data':data})


def view_bidding(request):
    try:
        if request.session["aid"] is None:
            return redirect(login)
    except KeyError:
        return redirect(login)
    cursor = connection.cursor()
    cursor.execute("select * from bidding join item_details where bidding.item_id = item_details.item_id and bidding.status ='started' or bidding.item_id = item_details.item_id and bidding.status ='processing' ")
    data = cursor.fetchall()
    return render(request,'admin_bidding.html',{'data':data})
def view_bidding_sold(request):
    try:
        if request.session["aid"] is None:
            return redirect(login)
    except KeyError:
        return redirect(login)
    cursor = connection.cursor()
    cursor.execute("select * from bidding join item_details where bidding.item_id = item_details.item_id and bidding.status = 'sold'")
    data = cursor.fetchall()
    return render(request,'admin_bidding_sold.html',{'data':data})


def place_request(request):
    try:
        if request.session["aid"] is None:
            return redirect(login)
    except KeyError:
        return redirect(login)
    cursor = connection.cursor()
    cursor.execute("select * from archaeological_place where status ='pending'")
    data = cursor.fetchall()
    return render(request,'admin_place_request.html',{'data':data})

def approve_place(request,id):
    try:
        if request.session["aid"] is None:
            return redirect(login)
    except KeyError:
        return redirect(login)
    cursor = connection.cursor()
    cursor.execute("update archaeological_place set status ='approved' where archaeological_place_id='" + str(id) + "'")
    return redirect(place_request)
def remove_place(request,id):
    try:
        if request.session["aid"] is None:
            return redirect(login)
    except KeyError:
        return redirect(login)
    cursor = connection.cursor()
    cursor.execute("delete from archaeological_place  where archaeological_place_id='" + str(id) + "'")
    return redirect(place_request)


def place_approved(request):
    try:
        if request.session["aid"] is None:
            return redirect(login)
    except KeyError:
        return redirect(login)
    cursor = connection.cursor()
    cursor.execute("select * from archaeological_place where status='approved'")
    data = cursor.fetchall()
    return render(request,'admin_place_approved.html',{'data':data})

def feedback(request):
    try:
        if request.session["aid"] is None:
            return redirect(login)
    except KeyError:
        return redirect(login)
    cursor = connection.cursor()
    cursor.execute("select * from feedback where reply ='pending'")
    data= cursor.fetchall()
    return render(request,'admin_feedback.html',{'data':data})
def reply_feedback(request,id):
    try:
        if request.session["aid"] is None:
            return redirect(login)
    except KeyError:
        return redirect(login)
    cursor = connection.cursor()
    if request.method == "POST":
        reply = request.POST['reply']
        cursor.execute("update feedback set reply ='"+str(reply)+"' where feedback_id='" + int(id) + "'")
        return redirect(feedback)
    cursor.execute("select * from feedback where feedback_id ='"+str(id)+"' ")
    data = cursor.fetchone()
    return render(request,'admin_reply_feedback.html',{'data':data})
def feedbacks_replied(request):
    try:
        if request.session["aid"] is None:
            return redirect(login)
    except KeyError:
        return redirect(login)
    cursor = connection.cursor()
    cursor.execute("select * from feedback where reply !='pending'")
    data = cursor.fetchall()
    return render(request, 'admin_feedback_replied.html', {'data': data})

def view_bookings_date(request,id):
    cursor = connection.cursor()
    cursor.execute("select * from bookings_date where museum_id ='"+str(id)+"' ")
    data = cursor.fetchall()
    cursor.execute("select * from museum where museum_id ='"+str(id)+"'")
    museum = cursor.fetchone()
    return render(request,'admin_view_bookings_date.html',{'data':data,'museum':museum})

# MUSEUM

def museum_home(request):
    return render(request,'museum_home.html')

def museum_user_bookings_date(request):
    mid = request.session["mid"]
    cursor = connection.cursor()
    cursor.execute("select * from bookings_date where museum_id ='" + str(mid) + "' ")
    data = cursor.fetchall()
    return render(request, 'museum_view_bookings_date.html', {'data': data})

def view_date_booking(request,id):
    mid = request.session["mid"]
    cursor = connection.cursor()
    cursor.execute("select * from bookings where museum_id ='" + str(mid) + "' and booking_date = '"+str(id)+"' ")
    data = cursor.fetchall()
    return render(request, 'museum_date_booking.html', {'data': data,'id':id})




def museums_artifacts(request):
    cursor = connection.cursor()
    mid = request.session["mid"]
    cursor.execute("select * from item_details where status ='authorised' and seller_id ='"+str(mid)+"'")
    data = cursor.fetchall()
    return render(request,'museum_my_artifacts.html',{'data':data})

def artifacts_sold(request):
    cursor = connection.cursor()
    mid = request.session["mid"]
    cursor.execute("select * from item_details where status ='sold' and seller_id ='" + str(mid) + "'")
    data = cursor.fetchall()
    return render(request, 'museum_sold_artifacts.html',{'data':data})

def artifacts_bought(request):
    cursor = connection.cursor()
    mid  = request.session["mid"]
    cursor.execute("select * from item_details where status ='sold' and buyer_id = '"+str(mid)+"'")
    data = cursor.fetchall()
    return render(request,'museum_bought_artifacts.html',{'data':data})

def add_artifacts(request):
    cursor = connection.cursor()
    if request.method == "POST" and request.FILES['upload']:
        name=request.POST['name']
        desc = request.POST['desc']
        price = request.POST['price']
        seller_id =request.session["mid"]
        upload = request.FILES['upload']
        fss = FileSystemStorage()
        file = fss.save(upload.name, upload)
        file_url = fss.url(file)
        last_date = "NULL"
        buyer_id= "NULL"
        last_price= "NULL"
        cursor.execute("insert into item_details values(null,'" + str(name) + "','" + str(desc) + "', '" + str(price) + "','" + str(seller_id) + "',curdate(),'"+str(file)+"','"+str(last_date)+"','"+str(buyer_id)+"','"+str(last_price)+"','authorised') ")
        return redirect(museums_artifacts)
    return render(request,'museum_add_artifacts.html')

def make_bidding(request,id):
    cursor = connection.cursor()
    cursor.execute("select * from bidding where item_id = '"+str(id)+"'")
    data = cursor.fetchone()
    if data == None:
        user_id = "NULL"
        item_id = id
        cursor.execute("select * from item_details where item_id='"+str(item_id)+"'")
        item = cursor.fetchone()
        basic_price = item[3]
        print(basic_price)
        user_bid_price = 'NULL'
        cursor.execute("insert into bidding values(null,'"+str(user_id)+"','"+str(item_id)+"','"+str(user_bid_price)+"',curdate(),'started')")
        return redirect(museums_artifacts)
    else:
        return HttpResponse("<script>alert('item already in bidding');window.location='../museum_artifacts';</script>")

def bidding_not_active(request):
    mid = request.session["mid"]
    cursor = connection.cursor()
    cursor.execute("select * from bidding join item_details where bidding.item_id = item_details.item_id and bidding.status ='started' and item_details.seller_id ='"+str(mid)+"'  ")
    data = cursor.fetchall()
    return render(request,'museum_bidding_not_active.html',{'data':data})

def delete_bid(request,id):
    cursor = connection.cursor()
    cursor.execute("select * from bidding where bidding_id ='"+str(id)+"' and status ='started'")
    data = cursor.fetchone()
    if data == None:
        return HttpResponse("<script>alert('someone just bid the item so unable remove the item ');window.location='../bidding_not_active';</script>")
    cursor.execute("delete from bidding where bidding_id='" + str(id) + "' ")
    return redirect(bidding_not_active)


def my_active_bidding(request):
    mid = request.session["mid"]
    cursor = connection.cursor()
    cursor.execute("select * from bidding join item_details where bidding.item_id = item_details.item_id and bidding.status ='processing' and item_details.seller_id ='"+str(mid)+"'")
    data = cursor.fetchall()
    return render(request,'museum_active_bidding.html',{'data':data})

def sell_bid_user(request,id):
    mid = request.session["mid"]
    cursor = connection.cursor()
    cursor.execute("select * from bidding where bidding_id = '"+str(id)+"' ")
    bid = cursor.fetchone()
    item_id = bid[2]
    cursor.execute("select * from item_details where item_id ='"+str(item_id)+"'")
    data = cursor.fetchone()
    seller_msge = "Congrats! You sold "+data[1]+" to "+data[8]+" for "+data[9]+"."
    buyer_msge = "Congrats! You owned "+data[1]+" from "+mid+" for "+data[9]+"."
    cursor.execute("update item_details set status ='sold' where item_id='" + str(item_id) + "'")
    cursor.execute("update bidding set status ='sold' where bidding_id = '"+str(id)+"'")
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    current_time = datetime.datetime.now().strftime('%H:%M:%S')
    cursor.execute("insert into notification values(null,'"+str(mid)+"','"+str(seller_msge)+"','"+current_date+"','"+current_time+"')")
    cursor.execute("insert into notification values(null,'"+str(data[8])+"','"+str(buyer_msge)+"','"+current_date+"','"+current_time+"')")
    return HttpResponse("<script>alert('"+seller_msge+"');window.location='../my_active_bidding';</script>")


def my_completed_bidding(request):
    mid = request.session["mid"]
    cursor = connection.cursor()
    cursor.execute("select * from bidding join item_details where bidding.item_id = item_details.item_id and bidding.status ='sold' and item_details.seller_id = '"+str(mid)+"'")
    data = cursor.fetchall()
    return render(request,'museum_my_completed_bidding.html',{'data':data})

def new_bidding(request):
    mid = request.session["mid"]
    cursor = connection.cursor()
    cursor.execute("select * from bidding join item_details where bidding.item_id = item_details.item_id and bidding.status ='started' and item_details.seller_id !='" + str(mid) + "'  ")
    data = cursor.fetchall()
    return render(request, 'museum_new_bidding.html', {'data': data})

def bid_new_item(request,id):
    cursor = connection.cursor()
    if request.method == "POST":
        amount = request.POST['total']
        card_num = request.POST['card_num']
        card_holder =request.POST['card_name']
        cvv= request.POST['cvv']
        exp = request.POST['card_expdate']
        cursor.execute("select * from account_table where card_number='"+str(card_num)+"' and card_holder ='"+str(card_holder)+"' and card_cvv ='"+str(cvv)+"' and exp_date='"+str(exp)+"' ")
        data = cursor.fetchone()
        if data == None:
            return HttpResponse("<script>alert('Invalid Card Details');window.location='../new_bidding';</script>")
        mid = request.session["mid"]
        cursor.execute("select * from bidding where bidding_id ='"+str(id)+"' and status ='started' ")
        data = cursor.fetchone()
        if data == None:
            return HttpResponse("<script>alert('the item was bidden by another user and your money is not debited from your account. and if you want to buy item  at any cost goahead and bid with the opponents with higher amount ');window.location='../bidding_running';</script>")
        cursor.execute("update item_details set buyer_id ='"+str(mid)+"' where item_id='" + str(data[2]) + "'")
        cursor.execute("update item_details set last_bid_date =curdate() where item_id='" + str(data[2]) + "'")
        cursor.execute("update item_details set last_price ='"+str(amount)+"' where item_id='" + str(data[2]) + "'")
        cursor.execute("update bidding set user_id ='"+str(mid)+"' where bidding_id ='" + str(id) + "'")
        cursor.execute("update bidding set user_bid_price ='"+str(amount)+"' where bidding_id='" + str(id) + "'")
        cursor.execute("update bidding set status ='processing' where bidding_id='" + str(id) + "'")
        cursor.execute("select * from item_details where item_id='"+str(data[2])+"' ")
        item = cursor.fetchone()
        sndr_msg=" You paid "+str(amount)+" to "+str(item[4])+" for  bidding "+str(item[1])+". "
        rcvr_msg=" You received amount "+str(amount)+" from "+str(mid)+" for bidding  "+str(item[1])+". "
        print(sndr_msg)
        print(rcvr_msg)
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        cursor.execute("insert into transactions values(null,'"+str(mid)+"','"+str(item[4])+"','"+str(amount)+"','"+str(sndr_msg)+"','"+str(rcvr_msg)+"','"+current_date+"','"+current_time+"')")
        cursor.execute("insert into notification values(null,'"+str(mid)+"','"+str(sndr_msg)+"','"+current_date+"','"+current_time+"')")
        cursor.execute("insert into notification values(null,'"+str(item[4])+"','"+str(rcvr_msg)+"','"+current_date+"','"+current_time+"')")
        return HttpResponse("<script>alert('"+sndr_msg+"');window.location='../bidding_running';</script>")

    cursor.execute("select item_details.basic_price, item_details.item_name,item_details.file_name from bidding join item_details where bidding.item_id = item_details.item_id and bidding.bidding_id ='"+str(id)+"' and bidding.status ='started'")
    data = cursor.fetchone()
    return render(request,'museum_new_bid_payment_page.html',{'data':data})

def bidding_running(request):
    mid = request.session["mid"]
    cursor = connection.cursor()
    cursor.execute("select * from bidding join item_details where bidding.item_id = item_details.item_id and bidding.status ='processing' and item_details.seller_id !='" + str(mid) + "'  ")
    data = cursor.fetchall()
    return render(request, 'museum_bidding_running.html', {'data': data})

def bid_running_item(request,id):
    cursor = connection.cursor()
    if request.method == "POST":
        amount = request.POST['total']
        card_num = request.POST['card_num']
        card_holder =request.POST['card_name']
        cvv= request.POST['cvv']
        exp = request.POST['card_expdate']
        cursor.execute("select * from account_table where card_number='" + str(card_num) + "' and card_holder ='" + str(card_holder) + "' and card_cvv ='" + str(cvv) + "' and exp_date='" + str(exp) + "' ")
        data = cursor.fetchone()
        if data == None:
            return HttpResponse("<script>alert('Invalid Card Details');window.location='../bidding_running';</script>")
        mid = request.session["mid"]
        cursor.execute("select * from bidding where bidding_id ='" + str(id) + "' and status ='processing' ")
        data = cursor.fetchone()
        if data == None:
            return HttpResponse("<script>alert('Sorry! The item is sold right now before you  bid. And your money is not debited from your account. Better luck next time.. ');window.location='../bidding_running';</script>")
        cursor.execute("select * from  item_details where item_id ='"+str(data[2])+"'")
        s = cursor.fetchone()
        old_buyer =s[8]
        old_price =s[9]
        cursor.execute("update item_details set buyer_id ='" + str(mid) + "' where item_id='" + str(data[2]) + "'")
        cursor.execute("update item_details set last_bid_date =curdate() where item_id='" + str(data[2]) + "'")
        cursor.execute("update item_details set last_price ='" + str(amount) + "' where item_id='" + str(data[2]) + "'")
        cursor.execute("update bidding set user_id ='" + str(mid) + "' where bidding_id ='" + str(id) + "'")
        cursor.execute("update bidding set user_bid_price ='" + str(amount) + "' where bidding_id='" + str(id) + "'")
        cursor.execute("update bidding set status ='processing' where bidding_id='" + str(id) + "'")
        cursor.execute("select * from item_details where item_id='" + str(data[2]) + "' ")
        item = cursor.fetchone()
        sndr_msg = " You paid " + str(amount) + " to " + str(item[4]) + " for  bidding " + str(item[1]) + ". "
        rcvr_msg = " You received amount " + str(amount) + " from " + str(mid) + " for bidding  " + str(item[1]) + ". "
        print(sndr_msg)
        print(rcvr_msg)
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        cursor.execute("insert into transactions values(null,'" + str(mid) + "','" + str(item[4]) + "','" + str(amount) + "','" + str(sndr_msg) + "','" + str(rcvr_msg) + "','" + current_date + "','" + current_time + "')")
        cursor.execute("insert into notification values(null,'" + str(mid) + "','" + str(sndr_msg) + "','" + current_date + "','" + current_time + "')")
        cursor.execute("insert into notification values(null,'" + str(item[4]) + "','" + str(rcvr_msg) + "','" + current_date + "','" + current_time + "')")
        osndr_msg ="Previous bid amount( "+old_price+" ) for the item( "+item[1]+" ) is returned to the previous bid User( "+old_buyer+" )."
        orcvr_msg ="Your bid amount( "+old_price+" ) for the item( "+item[1]+" ) is received from the seller( "+str(item[4])+" )."
        cursor.execute("insert into transactions values(null,'" + str(item[4]) + "','" + str(old_buyer) + "','" + str(old_price) + "','" + str(osndr_msg) + "','" + str(orcvr_msg) + "','" + current_date + "','" + current_time + "')")
        cursor.execute("insert into notification values(null,'" + str(item[4]) + "','" + str(osndr_msg) + "','" + current_date + "','" + current_time + "')")
        cursor.execute("insert into notification values(null,'" + str(old_buyer) + "','" + str(orcvr_msg) + "','" + current_date + "','" + current_time + "')")
        return HttpResponse("<script>alert('" + sndr_msg + "');window.location='../bidding_running';</script>")
    mid = request.session["mid"]
    cursor.execute("select * from bidding where bidding_id ='" + str(id) + "' and status ='processing' ")
    data = cursor.fetchone()
    if data == None:
        return HttpResponse(
            "<script>alert('Sorry! The item is sold right now before you  bid. And your money is not debited from your account. Better luck next time.. ');window.location='../bidding_running';</script>")
    if data[1] == str(mid):
        return HttpResponse("<script>alert('you already bid for this item ');window.location='../bidding_running';</script>")
    cursor.execute("select item_details.last_price, item_details.item_name,item_details.file_name from bidding join item_details where bidding.item_id = item_details.item_id and bidding.bidding_id ='"+str(id)+"' and bidding.status ='processing'")
    data = cursor.fetchone()
    data= list(data)
    data[0] = int(data[0]) + 1
    data= tuple(data)
    print(data)
    return render(request,'museum_running_bid_payment_page.html',{'data':data})


def museum_transactions(request):
    mid = request.session["mid"]
    cursor = connection.cursor()
    cursor.execute("select * from transactions where sender='"+str(mid)+"' or reciever ='"+str(mid)+"'")
    data = cursor.fetchone()
    if data ==None:# here we need to correct
        return redirect(museum_transactions)
    cursor.execute("select * from transactions where sender='"+str(mid)+"' or reciever ='"+str(mid)+"'")
    data = cursor.fetchall()
    ldata = list(data)
    len_of_ldata = len(ldata)
    a=[]
    b=[]
    for i in range(len_of_ldata):
        row = ldata[i]
        if row[1]==str(mid):
            c=[row[3],row[4],row[6],row[7]]
            c=tuple(c)
            d =[" "," "," "," "]
            d =tuple(d)
            a.append(c)
            b.append(d)
        else:
            c = [row[3], row[5], row[6], row[7]]
            c = tuple(c)
            d = [" ", " ", " ", " "]
            d = tuple(d)
            a.append(d)
            b.append(c)
    length_list =len(a)
    a = tuple(a)
    b = tuple(b)

    range_count = range(0, length_list)
    mata = zip(range_count, b, a)
    context = {
        'data': mata,
    }
    return render(request,'museum_transactions.html',{'data':mata})


def museum_notifications(request):
    mid = request.session["mid"]
    cursor = connection.cursor()
    cursor.execute("select * from notification where user_id ='"+str(mid)+"'")
    data = cursor.fetchall()
    return render(request,'museum_notifications.html',{'data':data})




# user
def user_home(request):

    return render(request,'user_home.html')

def user_pending_artifacts(request):
    uid = request.session["uid"]
    cursor= connection.cursor()
    cursor.execute("select * from item_details where status = 'pending' and seller_id ='"+str(uid)+"'")
    data = cursor.fetchall()
    return render(request,'user_pending_artifacts.html',{'data':data})

def user_artifacts(request):
    uid = request.session["uid"]
    cursor= connection.cursor()
    cursor.execute("select * from item_details where status = 'approved' and seller_id ='"+str(uid)+"'")
    data = cursor.fetchall()
    return render(request,'user_artifacts.html',{'data':data})
def user_make_bidding(request,id):
    cursor = connection.cursor()
    cursor.execute("select * from bidding where item_id = '"+str(id)+"'")
    data = cursor.fetchone()
    if data == None:
        user_id = "NULL"
        item_id = id
        cursor.execute("select * from item_details where item_id='"+str(item_id)+"'")
        item = cursor.fetchone()
        basic_price = item[3]
        print(basic_price)
        user_bid_price = 'NULL'
        cursor.execute("insert into bidding values(null,'"+str(user_id)+"','"+str(item_id)+"','"+str(user_bid_price)+"',curdate(),'started')")
        return redirect(user_artifacts)
    else:
        return HttpResponse("<script>alert('item already in bidding');window.location='../user_artifacts';</script>")

def user_add_artifacts(request):
    success = False
    cursor = connection.cursor()
    if request.method == "POST" and request.FILES['upload']:
        name=request.POST['name']
        desc = request.POST['desc']
        price = request.POST['price']
        seller_id =request.session["uid"]
        upload = request.FILES['upload']
        fss = FileSystemStorage()
        file = fss.save(upload.name, upload)
        file_url = fss.url(file)
        last_date = "NULL"
        buyer_id= "NULL"
        last_price= "NULL"
        cursor.execute("insert into item_details values(null,'" + str(name) + "','" + str(desc) + "', '" + str(price) + "','" + str(seller_id) + "',curdate(),'"+str(file)+"','"+str(last_date)+"','"+str(buyer_id)+"','"+str(last_price)+"','pending') ")
        success = True
        return JsonResponse({'success': success})
    return render(request,'user_add_artifacts.html')

def user_sold_artifacts(request):
    uid = request.session["uid"]
    cursor= connection.cursor()
    cursor.execute("select * from item_details where status = 'sold' and seller_id ='"+str(uid)+"'")
    data = cursor.fetchall()
    return render(request,'user_sold_artifacts.html',{'data':data})

def user_bought_artifacts(request):
    uid = request.session["uid"]
    cursor = connection.cursor()
    cursor.execute("select * from item_details where status ='sold' and buyer_id = '"+str(uid)+"'")
    data = cursor.fetchall()
    return render(request, 'user_bought_artifacts.html',{'data':data})

def user_bidding_not_active(request):
    mid = request.session["uid"]
    cursor = connection.cursor()
    cursor.execute("select * from bidding join item_details where bidding.item_id = item_details.item_id and bidding.status ='started' and item_details.seller_id ='"+str(mid)+"'  ")
    data = cursor.fetchall()
    return render(request,'user_bidding_not_active.html',{'data':data})


def user_delete_bid(request,id):
    cursor = connection.cursor()
    cursor.execute("select * from bidding where bidding_id ='"+str(id)+"' and status ='started'")
    data = cursor.fetchone()
    if data == None:
        return HttpResponse("<script>alert('someone just bid the item so unable remove the item ');window.location='../user_bidding_not_active';</script>")
    cursor.execute("delete from bidding where bidding_id='" + str(id) + "' ")
    return redirect(user_bidding_not_active)


def user_my_active_bidding(request):
    mid = request.session["uid"]
    cursor = connection.cursor()
    cursor.execute("select * from bidding join item_details where bidding.item_id = item_details.item_id and bidding.status ='processing' and item_details.seller_id ='"+str(mid)+"'")
    data = cursor.fetchall()
    return render(request,'user_active_bidding.html',{'data':data})

def user_sell_bid_user(request,id):
    mid = request.session["uid"]
    cursor = connection.cursor()
    cursor.execute("select * from bidding where bidding_id = '"+str(id)+"' ")
    bid = cursor.fetchone()
    item_id = bid[2]
    cursor.execute("select * from item_details where item_id ='"+str(item_id)+"'")
    data = cursor.fetchone()
    seller_msge = "Congrats! You sold "+data[1]+" to "+data[8]+" for "+data[9]+"."
    buyer_msge = "Congrats! You owned "+data[1]+" from "+mid+" for "+data[9]+"."
    cursor.execute("update item_details set status ='sold' where item_id='" + str(item_id) + "'")
    cursor.execute("update bidding set status ='sold' where bidding_id = '"+str(id)+"'")
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    current_time = datetime.datetime.now().strftime('%H:%M:%S')
    cursor.execute("insert into notification values(null,'"+str(mid)+"','"+str(seller_msge)+"','"+current_date+"','"+current_time+"')")
    cursor.execute("insert into notification values(null,'"+str(data[8])+"','"+str(buyer_msge)+"','"+current_date+"','"+current_time+"')")
    return HttpResponse("<script>alert('"+seller_msge+"');window.location='../user_my_active_bidding';</script>")


def user_my_completed_bidding(request):
    mid = request.session["uid"]
    cursor = connection.cursor()
    cursor.execute("select * from bidding join item_details where bidding.item_id = item_details.item_id and bidding.status ='sold' and item_details.seller_id = '"+str(mid)+"'")
    data = cursor.fetchall()
    return render(request,'user_my_completed_bidding.html',{'data':data})

def user_new_bidding(request):
    mid = request.session["uid"]
    cursor = connection.cursor()
    cursor.execute("select * from bidding join item_details where bidding.item_id = item_details.item_id and bidding.status ='started' and item_details.seller_id !='" + str(mid) + "'  ")
    data = cursor.fetchall()
    return render(request, 'user_new_bidding.html', {'data': data})

def user_bid_new_item(request,id):
    cursor = connection.cursor()
    if request.method == "POST":
        amount = request.POST['total']
        card_num = request.POST['card_num']
        card_holder =request.POST['card_name']
        cvv= request.POST['cvv']
        exp = request.POST['card_expdate']
        cursor.execute("select * from account_table where card_number='"+str(card_num)+"' and card_holder ='"+str(card_holder)+"' and card_cvv ='"+str(cvv)+"' and exp_date='"+str(exp)+"' ")
        data = cursor.fetchone()
        if data == None:
            return HttpResponse("<script>alert('Invalid Card Details');window.location='../user_new_bidding';</script>")
        mid = request.session["uid"]
        cursor.execute("select * from bidding where bidding_id ='"+str(id)+"' and status ='started' ")
        data = cursor.fetchone()
        if data == None:
            return HttpResponse("<script>alert('the item was bidden by another user and your money is not debited from your account. and if you want to buy item  at any cost goahead and bid with the opponents with higher amount ');window.location='../user_bidding_running';</script>")
        cursor.execute("update item_details set buyer_id ='"+str(mid)+"' where item_id='" + str(data[2]) + "'")
        cursor.execute("update item_details set last_bid_date =curdate() where item_id='" + str(data[2]) + "'")
        cursor.execute("update item_details set last_price ='"+str(amount)+"' where item_id='" + str(data[2]) + "'")
        cursor.execute("update bidding set user_id ='"+str(mid)+"' where bidding_id ='" + str(id) + "'")
        cursor.execute("update bidding set user_bid_price ='"+str(amount)+"' where bidding_id='" + str(id) + "'")
        cursor.execute("update bidding set status ='processing' where bidding_id='" + str(id) + "'")
        cursor.execute("select * from item_details where item_id='"+str(data[2])+"' ")
        item = cursor.fetchone()
        sndr_msg=" You paid "+str(amount)+" to "+str(item[4])+" for  bidding "+str(item[1])+". "
        rcvr_msg=" You received amount "+str(amount)+" from "+str(mid)+" for bidding  "+str(item[1])+". "
        print(sndr_msg)
        print(rcvr_msg)
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        cursor.execute("insert into transactions values(null,'"+str(mid)+"','"+str(item[4])+"','"+str(amount)+"','"+str(sndr_msg)+"','"+str(rcvr_msg)+"','"+current_date+"','"+current_time+"')")
        cursor.execute("insert into notification values(null,'"+str(mid)+"','"+str(sndr_msg)+"','"+current_date+"','"+current_time+"')")
        cursor.execute("insert into notification values(null,'"+str(item[4])+"','"+str(rcvr_msg)+"','"+current_date+"','"+current_time+"')")
        return HttpResponse("<script>alert('"+sndr_msg+"');window.location='../user_bidding_running';</script>")

    cursor.execute("select item_details.basic_price, item_details.item_name,item_details.file_name from bidding join item_details where bidding.item_id = item_details.item_id and bidding.bidding_id ='"+str(id)+"' and bidding.status ='started'")
    data = cursor.fetchone()
    return render(request,'user_new_bid_payment_page.html',{'data':data})

def user_bidding_running(request):
    mid = request.session["uid"]
    cursor = connection.cursor()
    cursor.execute("select * from bidding join item_details where bidding.item_id = item_details.item_id and bidding.status ='processing' and item_details.seller_id !='" + str(mid) + "'  ")
    data = cursor.fetchall()
    return render(request, 'user_bidding_running.html', {'data': data})

def user_bid_running_item(request,id):
    cursor = connection.cursor()
    if request.method == "POST":
        amount = request.POST['total']
        card_num = request.POST['card_num']
        card_holder =request.POST['card_name']
        cvv= request.POST['cvv']
        exp = request.POST['card_expdate']
        cursor.execute("select * from account_table where card_number='" + str(card_num) + "' and card_holder ='" + str(card_holder) + "' and card_cvv ='" + str(cvv) + "' and exp_date='" + str(exp) + "' ")
        data = cursor.fetchone()
        if data == None:
            return HttpResponse("<script>alert('Invalid Card Details');window.location='../user_bidding_running';</script>")
        mid = request.session["uid"]
        cursor.execute("select * from bidding where bidding_id ='" + str(id) + "' and status ='processing' ")
        data = cursor.fetchone()
        if data == None:
            return HttpResponse("<script>alert('Sorry! The item is sold right now before you  bid. And your money is not debited from your account. Better luck next time.. ');window.location='../user_bidding_running';</script>")
        cursor.execute("select * from  item_details where item_id ='"+str(data[2])+"'")
        s = cursor.fetchone()
        old_buyer =s[8]
        old_price =s[9]
        cursor.execute("update item_details set buyer_id ='" + str(mid) + "' where item_id='" + str(data[2]) + "'")
        cursor.execute("update item_details set last_bid_date =curdate() where item_id='" + str(data[2]) + "'")
        cursor.execute("update item_details set last_price ='" + str(amount) + "' where item_id='" + str(data[2]) + "'")
        cursor.execute("update bidding set user_id ='" + str(mid) + "' where bidding_id ='" + str(id) + "'")
        cursor.execute("update bidding set user_bid_price ='" + str(amount) + "' where bidding_id='" + str(id) + "'")
        cursor.execute("update bidding set status ='processing' where bidding_id='" + str(id) + "'")
        cursor.execute("select * from item_details where item_id='" + str(data[2]) + "' ")
        item = cursor.fetchone()
        sndr_msg = " You paid " + str(amount) + " to " + str(item[4]) + " for  bidding " + str(item[1]) + ". "
        rcvr_msg = " You received amount " + str(amount) + " from " + str(mid) + " for bidding  " + str(item[1]) + ". "
        print(sndr_msg)
        print(rcvr_msg)
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        cursor.execute("insert into transactions values(null,'" + str(mid) + "','" + str(item[4]) + "','" + str(amount) + "','" + str(sndr_msg) + "','" + str(rcvr_msg) + "','" + current_date + "','" + current_time + "')")
        cursor.execute("insert into notification values(null,'" + str(mid) + "','" + str(sndr_msg) + "','" + current_date + "','" + current_time + "')")
        cursor.execute("insert into notification values(null,'" + str(item[4]) + "','" + str(rcvr_msg) + "','" + current_date + "','" + current_time + "')")
        osndr_msg ="Previous bid amount( "+old_price+" ) for the item( "+item[1]+" ) is returned to the previous bid User( "+old_buyer+" )."
        orcvr_msg ="Your bid amount( "+old_price+" ) for the item( "+item[1]+" ) is received from the seller( "+str(item[4])+" )."
        cursor.execute("insert into transactions values(null,'" + str(item[4]) + "','" + str(old_buyer) + "','" + str(old_price) + "','" + str(osndr_msg) + "','" + str(orcvr_msg) + "','" + current_date + "','" + current_time + "')")
        cursor.execute("insert into notification values(null,'" + str(item[4]) + "','" + str(osndr_msg) + "','" + current_date + "','" + current_time + "')")
        cursor.execute("insert into notification values(null,'" + str(old_buyer) + "','" + str(orcvr_msg) + "','" + current_date + "','" + current_time + "')")
        return HttpResponse("<script>alert('" + sndr_msg + "');window.location='../user_bidding_running';</script>")
    mid = request.session["uid"]
    cursor.execute("select * from bidding where bidding_id ='" + str(id) + "' and status ='processing' ")
    data = cursor.fetchone()
    if data == None:
        return HttpResponse(
            "<script>alert('Sorry! The item is sold right now before you  bid. And your money is not debited from your account. Better luck next time.. ');window.location='../user_bidding_running';</script>")
    if data[1] == str(mid):
        return HttpResponse("<script>alert('you already bid for this item ');window.location='../user_bidding_running';</script>")
    cursor.execute("select item_details.last_price, item_details.item_name,item_details.file_name from bidding join item_details where bidding.item_id = item_details.item_id and bidding.bidding_id ='"+str(id)+"' and bidding.status ='processing'")
    data = cursor.fetchone()
    data= list(data)
    data[0] = int(data[0]) + 1
    data= tuple(data)
    print(data)
    return render(request,'user_running_bid_payment_page.html',{'data':data})


def user_transactions(request):
    mid = request.session["uid"]
    cursor = connection.cursor()
    cursor.execute("select * from transactions where sender='"+str(mid)+"' or reciever ='"+str(mid)+"'")
    data = cursor.fetchone()
    if data ==None:# here we need to correct
        return render(request,'user_transactions.html')
    cursor.execute("select * from transactions where sender='"+str(mid)+"' or reciever ='"+str(mid)+"'")
    data = cursor.fetchall()
    ldata = list(data)
    len_of_ldata = len(ldata)
    a=[]
    b=[]
    for i in range(len_of_ldata):
        row = ldata[i]
        if row[1]==str(mid):
            c=[row[3],row[4],row[6],row[7]]
            c=tuple(c)
            d =[" "," "," "," "]
            d =tuple(d)
            a.append(c)
            b.append(d)
        else:
            c = [row[3], row[5], row[6], row[7]]
            c = tuple(c)
            d = [" ", " ", " ", " "]
            d = tuple(d)
            a.append(d)
            b.append(c)
    length_list =len(a)
    a = tuple(a)
    b = tuple(b)

    range_count = range(0, length_list)
    mata = zip(range_count, b, a)
    context = {
        'data': mata,
    }
    return render(request,'user_transactions.html',{'data':mata})


def user_notifications(request):
    mid = request.session["uid"]
    cursor = connection.cursor()
    cursor.execute("select * from notification where user_id ='"+str(mid)+"'")
    data = cursor.fetchall()
    return render(request,'user_notifications.html',{'data':data})

def add_place(request):
    if 'uid' in request.session:  # Check if 'uid' is in session
        uid = request.session['uid']
    else:

        return redirect(reverse('user_home'))
    success =False
    cursor = connection.cursor()
    if request.method == "POST":
            name = request.POST['place_name']
            address = request.POST['address']
            district = request.POST['district']
            cursor.execute("insert into archaeological_place values(null,'" + str(name) + "','" + str(address) + "','" + district + "','pending' )")
            success =True
            return JsonResponse({'success': success})

    return render(request,'user_add_place.html')

def user_view_place(request):
    uid = request.session["uid"]
    cursor = connection.cursor()
    cursor.execute("select * from archaeological_place where status ='approved'")
    data = cursor.fetchall()
    return render(request,'user_view_place.html',{'data':data})

def user_view_museum(request):
    cursor= connection.cursor()
    cursor.execute("select * from museum ")
    data = cursor.fetchall()
    return render(request,'user_view_museum.html',{'data':data})

def user_make_booking(request,id):
    uid = request.session["uid"]
    cursor = connection.cursor()
    cursor.execute("select * from museum where museum_id='" + str(id) + "'")
    museum = cursor.fetchone()
    museum = museum[1]
    if request.method == "POST":
            date = request.POST['book_date']
            count = request.POST['count']
            cursor.execute("select * from bookings_date where booking_date ='"+str(date)+"' and museum_id ='"+str(id)+"'")
            data = cursor.fetchone()
            if data ==None:
                cursor.execute("insert into bookings values(Null,'"+str(id)+"','"+str(uid)+"', '"+str(count)+"','"+str(date)+"')")
                cursor.execute("insert into bookings_date values(Null,'"+str(id)+"','"+str(date)+"','"+str(count)+"')")
                return HttpResponse("<script>alert('Booked Tickets');window.location='../user_view_museum';</script>")

            else:
                total_bookings= int(data[3]) + int(count)
                if int(total_bookings) <= 100:
                    cursor.execute("insert into bookings values(Null,'"+str(id)+"','"+str(uid)+"', '"+str(count)+"','"+str(date)+"')")
                    cursor.execute("update bookings_date set booking_count ='"+str(total_bookings)+"' where booking_date='" + str(date) + "' and museum_id='"+str(id)+"'")
                    return HttpResponse("<script>alert('Booked Tickets');window.location='../user_view_museum';</script>")
                else:
                    s = str(100-int(data[3]))
                    if s == "0":
                        avail = "there is no bookings available on: "+date+"."
                    else:
                        avail ="there is only "+s+" bookings available on: "+date+"."
                    return render(request,'user_make_booking.html',{'museum':museum,'avail':avail,'id':id})

    return render(request,'user_make_booking.html',{'museum':museum,'id':id})

def user_view_booking(request,id):
    uid = request.session["uid"]
    cursor = connection.cursor()
    cursor.execute("select * from bookings where user_id = '"+str(uid)+"' and museum_id ='"+str(id)+"'")
    data =cursor.fetchall()
    cursor = connection.cursor()
    cursor.execute("select * from museum where museum_id='" + str(id) + "'")
    museum = cursor.fetchone()
    museum = museum[1]
    return render(request,'user_view_booking.html',{'data':data,'museum':museum})


def user_location(request,id,jd):
    try:
        if request.session["uid"] is None:
            return redirect(login)
    except KeyError:
        return redirect(login)
    return render(request,"user_location.html",{'lat':id,'lon':jd})

def user_museum_items(request,id):
    try:
        if request.session["uid"] is None:
            return redirect(login)
    except KeyError:
        return redirect(login)
    cursor = connection.cursor()
    cursor.execute("select * from item_details where seller_id ='"+str(id)+"' and status ='authorised'")
    mus_items=cursor.fetchall()
    cursor.execute("select * from item_details join bidding where item_details.seller_id ='"+str(id)+"' and item_details.item_id = bidding.item_id and bidding.status ='started' or item_details.seller_id ='"+str(id)+"' and item_details.item_id = bidding.item_id and bidding.status ='processing'")
    on_bidding =cursor.fetchall()
    cursor.execute("select * from item_details where seller_id ='"+str(id)+"' and status ='sold'")
    mus_sold = cursor.fetchall()
    cursor.execute("select * from item_details join bidding where item_details.buyer_id ='"+str(id)+"' and item_details.item_id = bidding.item_id and bidding.status ='sold'")
    mus_buyed =cursor.fetchall()
    cursor.execute("select * from museum where museum_id ='"+str(id)+"'")
    museum =cursor.fetchone()
    return render(request,'user_museum_items.html',{'a':mus_items,'b':on_bidding,'c':mus_sold,'d':mus_buyed,'museum':museum})














