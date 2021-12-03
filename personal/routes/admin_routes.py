import os,random
from operator import mod
from flask import render_template,request,redirect,flash,make_response,session
from flask.helpers import url_for
from flask_sqlalchemy import model
from  personal import app,csrf,myforms,db,models

@app.route('/admin/dash')
def dash():
   tot= db.session.query(models.Guest).count()
   git=db.session.query(models.Gift).count()
   return render_template('admin/dashboard.html',tot=tot,git=git)


@app.route('/admin/guest') 
def adm_lay():
    all=db.session.query(models.Guest).all()
    data=db.session.query(models.Guest,models.State).join(models.State).all()
    return render_template('admin/admin.html',all=all,data=data)


@app.route('/admin/delete/<int:guestid>')
def delete(guestid):
    y=db.session.query(models.Guest).get(guestid)
    db.session.delete(y)
    db.session.commit()
    return  redirect ('/admin/guest')

@app.route('/admin/form',methods=['POST','GET'])    
def form():
    pos=myforms.InvitationForm()
    if request.method=='GET':
     return render_template('admin/adminform.html',pos=pos)
    else:
        #do validation here
        if pos.validate_on_submit:
            uploaded_file=request.files['ivcard']
            message=request.form.get('msg')
            #generate a random name and save with extension
            name,ext=os.path.splitext(uploaded_file.filename)
            #get ext
            #give it a newnwme conc atenated with extension
            newname=str(random.random() * 10000) + ext
            #new random name
            uploaded_file.save('personal/static/docs/' +newname)
            #insert into document table
            x=models.Document(doc_filename=newname,doc_msg=message)
            db.session.add(x)
            db.session.commit()
            flash('IV successfully uploaded')
            return redirect(url_for('dash')) 
        else:
            return render_template('admin/adminform.html',pos=pos)    