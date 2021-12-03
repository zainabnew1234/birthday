import random,os,string,json,requests
from flask_mail import Message
from flask import render_template,request,redirect,flash,make_response,session,abort
from werkzeug.security import generate_password_hash,check_password_hash
from flask.helpers import url_for
from  personal import app,csrf,myforms,db,models,mail,Message

def refno():
    sample_xters=random.sample(string.digits,10)
    newname=''.join(sample_xters)
    return newname

@app.route('/user/testmail')
def testmail():
    Message()
    msg=Message(subject="Testing Mail",sender="oyindaadesewa@gmail.com",
    recipients=['oyindaadesewa@gmail.com'],body="Test Mail")
    f=open('requirement.txt')
    msg.html="<div><h1>WELCOME ON BOARD</h1></div>"
    msg.attach("Requirement.txt","application/text",f.read())
    mail.send(msg)
    return 'Mail was sent'
   

@app.route('/user/donatecash',methods=['GET','POST'])
def donatecash():
    logggedin=session.get('user')
    if logggedin:
        if request.method=='GET':
         return render_template('user/donate.html')
        else:
            received=request.form.get('don')
            return 'Form submitted'
    else:
        abort(403)      

@app.route('/user/paycash',methods=['GET','POST'])
def paycash():
    if session.get('user') != None:
     if request.method=='GET':
      return render_template('user/cash.html')     
     else:
        guestid=session.get('user')
        amt=request.form.get('don',0)
        ref=refno()
        session['trxref']=ref
        t=models.Transaction(trx_guestid=guestid,trx_amt=amt,trx_ref=ref,trx_status='Pending')
        db.session.add(t)
        db.session.commit()
        return redirect(url_for('confirmpay'))   
    else:
        return redirect(url_for('gin'))  

@app.route('/user/confirmpay',methods=['GET','POST'])
def confirmpay():
    if session.get('user') != None and session.get('trxref') != None:
        ref = session.get('trxref')
        deets = db.session.query(models.Transaction).filter(models.Transaction.trx_ref==ref).first()

        if request.method=='GET':
            return render_template('user/confirm.html',deets=deets)  
        else:
            #connect to paystack endpoint
            amount = deets.trx_amt * 100
            email=deets.guest.email
            headers = {"Content-Type": "application/json","Authorization":"Bearer sk_test_74d86d020b298241c12bfe692d12f383e4c405c7"}            
            data = {"reference": ref, "amount": amount, "email": email}
            
            response = requests.post('https://api.paystack.co/transaction/initialize', headers=headers, data=json.dumps(data))

            rsp = json.loads(response.text) 
            if rsp.get('status')==True:	
                payurl=rsp['data']['authorization_url']
                return redirect (payurl)
            else:
                return redirect(url_for('paycash'))    
    else:     
        return redirect(url_for('login'))

@app.route('/user/paystack')
def paystack():
    loggedin=session.get('user')
    refsession = session.get('trxref')
    if loggedin and refsession:
         #receive response from Payment Company and inform user of the transaction status
        ref=request.args.get('reference')
        headers={'Authorization':'Bearer sk_test_74d86d020b298241c12bfe692d12f383e4c405c7'}
        #urlverify = "https://api.paystack.co/transaction/verify/"+ref
        response = requests.get(f"https://api.paystack.co/transaction/verify/{ref}", headers=headers)
        rsp =response.json()#in json format
        #return render_template('user/test.html',rsp=rsp)

        if rsp['data']['status'] =='success':
            amt = rsp['data']['amount']
            ipaddress = rsp['data']['ip_address']
            t = models.Transaction.query.filter(models.Transaction.trx_ref==refsession).first()
            t.trx_status = 'Paid'
            db.session.commit()
            return "Payment Was Successful"
            #return 'update database and redirect them to the feedback page'
        else:
            t = models.Transaction.query.filter(models.Transaction.trx_ref==refsession).first()
            t.trx_status = 'Failed'
            db.session.commit()
            return "Payment Failed"     
    else:
        abort(403)





@app.route('/user/lay2',methods=['GET','POST'])
def lay():
    if request.method=='GET':
          response=requests.get('http://127.0.0.1:8082/hostel/api/v1.0/listall/')
          hostels=json.loads(response.text)
          allstates=db.session.query(models.State).all()
          return render_template('user/home.html',allstates=allstates,hostels=hostels)
    else:
        #retrieve form data
        fname=request.form.get('fname')  
        lname=request.form.get('lname')
        email=request.form.get('email')
        password=request.form.get('password')  
        state=request.form.get('state')
        #save into database using ORM insert
        converted=generate_password_hash(password)
        g=models.Guest(fname=fname,lname=lname,email=email,pwd=converted,stateid=state)
        db.session.add(g)
        db.session.commit()
        #keep details in session
        session['user']=g.id
        #save feedback in a flash and redirecct to '/user/profile2'
        flash('Registration was successful')
        return redirect('/user/profile2')

@app.route('/user/gift',methods=['POST','GET'])
def gift():
    loggedin_user=session.get('user')
    if loggedin_user:
     if request.method =='GET':
      allgifts=models.Gift.query.all()
      return render_template('user/gift.html',allgifts=allgifts)   

     else:
        selected=request.form.getlist('item')
        if selected:
            for t in selected:
                quantity='quantity_'+str(t)
                total=request.form.get(quantity,1)
                statement=models.guest_gift.insert().values(gift_id=t,guest_id=loggedin_user,qty=total)
                db.session.execute(statement)
            db.session.commit()
            flash('Thanks for your donation')    
            return redirect('/user/profile2')
        else:
            flash('Please select a gift')
            return redirect('/user/gift')
    else:
     return redirect('/user/in')

 

@app.route('/user/in',methods=['POST','GET'])  
def gin():
    if request.method =='GET':
        #1. display login form
        return render_template('user/login.html')

    else:
        #2.retrieve form data
        data1=request.form.get('text')
        data2=request.form.get('password')

        #3. query to fetch from guesttable where username=email amd password=pwd
        rec=db.session.query(models.Guest).filter(models.Guest.email==data1).first()

        #4.if data is fetched,keep the id in session and redirect to profile page
        if rec:
            loggedin_user =rec.id
            hashedpass =rec.pwd
            check=check_password_hash(hashedpass,data2)
            if check:
             session['user']=loggedin_user
             return redirect ('/user/profile2')

            else:
                flash('Invalid credentials') 
                return redirect(url_for('gin'))

        #5. if data is empty,keep feedback in a flash and redirect to homepage/loginpage
        else:
         flash('Invalid Credientials')
         return   redirect('/user/in')
     

@app.route('/user/profile2')
def profile2():
    loggedin_user =session.get('user')
    if loggedin_user != None:
        data =db.session.query(models.Guest).get(loggedin_user)
        iv=db.session.query(models.Document).get(1)
        return render_template('user/profile3.html',data=data,iv=iv)  
    else:
        return 'Display'     

@app.route('/user/quest')      
def quest():
    if session.get('user') != None:
     return render_template ('user/quest.html')    
    else: 
        return redirect ('/user/in') 




@app.route('/user/questajax',methods=['GET','POST'])      
def quest_ajax():
    if session.get('user') != None:
     return render_template ('user/questajax.html')    
    else: 
        return redirect ('/user/in') 

@app.route('/user/submitajax',methods=['POST','GET'])
def submitajax():
    loggedin=session.get('user')
    if loggedin != None:
        quest=request.form.get('quest')
        firstn=request.form.get('fname')
        lastn=request.form.get('lname')
        csrf_token=request.form.get('csrf_token')
        pixobj=request.files['pix']
        filename=pixobj.filename
        v=models.Question(guest_id=loggedin,question=quest)
        db.session.add(v)
        db.session.commit()
        return f'Thank you {firstn} {lastn}, your question has been asked....,you token is {csrf_token} and your file is {filename}'
    else: 
        return "You need to login to ask a question"


@app.route('/user/demajax',methods=['GET','POST'])
@csrf.exempt
def demajax():
    if request.method=='GET':
     records=db.session.query(models.State).all()
     return render_template('user/test.html',records=records)
    else:
        user=request.form.get('user')
        deets=db.session.query(models.Guest).filter(models.Guest.email==user).all()
        if deets:
            rsp={"msg":"You have registered with this email","status":"failed"}
            return json.dumps(rsp)
   
        else:
            rsp={"msg":"Username available","status":"passed"}
            return json.dumps(rsp) 

@app.route('/user/lga')   
def lga():
    state=request.args.get('stateid')
    data=db.session.query(models.Lga).filter(models.Lga.state_id==state).all()
    tosend="<select class='form-control' name='' >"
    for t in data:
        tosend=tosend+f"<option>{t.lga_name}</option>"
    tosend=tosend+"</select>"
    return tosend         
       


@app.route('/user/submitquest',methods=['POST'])
def submitquest():
    loggedin=session.get('user')
    if loggedin != None:
        quest=request.form.get('quest')
        v=models.Question(guest_id=loggedin,question=quest)
        db.session.add(v)
        db.session.commit()
        return 'Thank you for asking...'

    else:
        return redirect('/user/in')    




@app.route('/user/out')  
def log():
    session.pop('user',None) 
    return redirect('/user/in')


@app.route('/user/addpics', methods=['GET','POST'])
def addpics():
    if session.get('user') != None:
        if request.method=='GET':
            return render_template('user/form2.html')
        else: #form is submitted
            fileobj = request.files['pics']       

            if fileobj.filename == '':
                flash('Please select a file')
                return redirect(url_for('addpics'))
            else:
                 #get the file extension,  #splits file into 2 parts on the extension
                name, ext = os.path.splitext(fileobj.filename)
                allowed_extensions=['.jpg','.jpeg','.png','.gif']

                if ext not in allowed_extensions:
                    flash(f'Extension {ext}is not allowed')
                    return redirect(url_for('addpics'))
                else:
                    sample_xters = random.sample(string.ascii_lowercase,10) 
                    newname = ''.join(sample_xters) + ext

                    destination = 'personal/static/images/guest/'+newname
                    fileobj.save(destination)
                    ##save the details in the db
                    id = session.get('user')
                    guest = db.session.query(models.Guest).get(id)
                    guest.profilepix=newname
                    db.session.commit() 
                    return redirect('/user/profile2')
    else:
        return redirect(url_for('gin'))        




@app.route('/hello',methods=['POST','GET'])
def hel():
    # db.session.execute("INSERT INTO posts SET post_title='Testlost',post_content='What a loss'")
    # db.session.commit()
    pos = myforms.PostForm()
    if request.method =='GET':
     return render_template('user/post.html',pos=pos)
    else:
        if pos.validate_on_submit():
            tit=request.form.get('title')
            des=pos.data['desc']
            cont=request.values.get('mssg')
            #inserting into database using raw method
            # db.session.execute(f"INSERT INTO posts SET post_title='{tit}',post_content='{cont}' ")
            # db.session.commit()

            #inserting into database using orm/sqlalchemy
            p = models.Post(post_title=tit,post_content=cont)
            db.session.add(p)
            db.session.commit()
            #TO GET THE ID OF THE LAST ROW INSERTED
            id_lastrecord_insert=p.id
            flash(f'Blog post number {id_lastrecord_insert} has been submitted')
            return  redirect('/hello')

        else:
             return render_template('user/post.html',pos=pos)



@app.route('/fetch')
def collect():
    # using raw method to fetch
    tab=db.session.execute('select * from posts ' )
    retrieve=tab.fetchall()
    return render_template('user/index.html',retrieve=retrieve)


@app.route('/orm')    
def orm():
 record=models.Post.query.add_columns(models.Post.post_title,models.Post.post_content).all()
 record=models.Post.query.first()
#  record=models.Post.query.get(12)
#  record=models.Post.query.get(12)
 #this is counting from orm
#  rec=models.Post.query.count()
 return render_template('user/orm.html',record=record)

#method 2
#    rec=db.session.query(models.Post.post_title,models.Post.post_content).all()
#    return render_template('user/orm.html',rec=rec)

@app.route('/logout')
def logout():
    session.pop('use',None)
    return redirect('/')


@app.route('/about/',methods=['GET', 'POST'])
@csrf.exempt   #this is to exempt a particular route for protection from cdrf
def about():
    if request.method == 'GET':
     list=['Adebola','Muyiwa','Debola','Sola']
     return render_template('user/about.html',list=list)
    else:
           te = request.form.get('rate') 
           flash(f"Thank u for rating us {te}")
           return redirect('/about')


                       
@app.route('/')
def home():
    #obj = myforms.SubscriptionForm()
    return render_template('user/index.html')




@app.route('/contact/')
def contact():
    usercountry = request.cookies.get('country')
    return render_template('user/contact.html',usercountry=usercountry,myconfig=app.config)  


@app.route('/visitor/africa')  
def africa():
    resp = make_response(redirect('/store'))
    resp.set_cookie('country','africa')
    return resp

@app.route('/visitor/europe')   
def europe():
    resp = make_response(redirect('/store'))
    resp.set_cookie('country','europe')
    return resp


@app.route('/store')    
def store():
    mycookies=request.cookies.get('country')
    return render_template('user/store.html',mycookies=mycookies)


@app.route('/cookie')
def opt():
    resp = make_response(redirect('/'))    
    resp.set_cookie('country',max_age=-10*24*60*60)
    return resp


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method =='GET':
        return render_template('user/login.html')
    else:    
        user=request.form.get('text')
        word=request.form.get('password')
        if user =='zainab' and word =='1234':
         session['use']=user
         return redirect('/profi')
         
        else:
            flash('The username/password is incorrect')
            return redirect('/login') 


@app.route('/subscribe',methods=['POST'])
def sub():
    subform = myforms.SubscriptionForm()
    if request.method == 'POST' and subform.validate_on_submit():
        fullname = request.form.get('fullname')
        return f"Thank you {fullname},form was submitted"

    else:
        return  render_template('user/index.html',obj=subform)      



@app.route('/success')
def success():
    return render_template('user/submit.html')

@app.route('/submit',methods=['GET','POST'])
def submit():
    # #this is when u r using method (get) in ur form method 
    # fname=request.args.get('fullname')      
    # msg=request.args.get('message')
    # name=open('submit.txt','a')
    # name.write(msg)
    # return render_template('submit.html',fname=fname,msg=msg)

    #this is when u r using method (post) in ur form method
    if request.method =='POST':
        fname=request.form.get('fullname')  
        msg=request.form.get('message')  
        gender=request.form.get('gen')  
        name=open('submit.txt','a')
        name.write('msg')  
        flash(f"Here is your message:{msg}")
        flash(f'Thank you {fname} for contacting us',category="feedback")
        # return redirect('/success')
        # return f"Thanks for contacting us {fname}"
        return render_template('user/submit.html',fname=fname,msg=msg,gender=gender)

    else:
        return 'You have to fill the form first'  





@app.route('/profile/<int:userid>')
def profile(userid):
    return render_template('profile.html',user=userid)
   # {{user}} u can use it this way 

@app.route('/update',methods=['GET','POST'])    
def update():
    return ' Sucessfully updated!'

@app.route('/blog/')  
def blog():
    return 'This is the content of my blog'  

@app.errorhandler(404)
def my404(error):
    return render_template('user/error404.html',error=error),404   




@app.route('/profi')    
def prof():
    if session.get('use') != None:
     return render_template('user/profilepage.html')    
    else:
        return redirect('/login') 

  
           