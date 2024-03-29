from WebApp import app
from flask import render_template,request,redirect,url_for,flash,session,jsonify,g,session,make_response,send_file
from flask_sqlalchemy import SQLAlchemy
import base64
# import pdfkit
# from reportlab.pdfgen import canvas
# import os
# from PyPDF2 import PdfFileWriter, PdfFileReader
import io
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import letter
from PIL import Image
import pickle
import pymysql
pymysql.install_as_MySQLdb()


db = SQLAlchemy(app)


class User:
    def __init__(self, id, username, password, user_type):
        self.id = id
        self.username = username
        self.password = password
        self.type = user_type

    def __repr__(self):
        return f'<User: {self.username}>'


#Creating model table for our CRUD database
class Data(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(100))


    def __init__(self, name, email, phone):

        self.name = name
        self.email = email
        self.phone = phone


users = []
users.append(User(id=1, username='Shreyas', password='password', user_type='Doctor'))
users.append(User(id=2, username='Becca', password='secret', user_type='Nurse'))
users.append(User(id=3, username='Carlos', password='somethingsimple', user_type='Receptionist'))



@app.before_request
def before_request():
    g.user = False

    try:
        if 'user_id' in session:
            user = [x for x in users if x.id == session['user_id']][0]
            g.user = user
    except:
        flash("User Not Found!")
        return render_template('login.html')



# Default Route
@app.route('/')
def index():
	return render_template('login.html')




#User Logs In
@app.route('/login',methods = ["GET","POST"])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']
        
        try:
            user = [x for x in users if x.username == username][0]
            if user and user.password == password:
                session['user_id'] = user.id
                session['user_type'] = user.type
                return redirect(url_for('managepatients'))
            else:
                flash("Incorrect Password!")
                return render_template('login.html')

        except:
            flash("User Not Found!")
            return render_template('login.html')


        return redirect(url_for('login'))

    return render_template('login.html')


#User Logs Out
@app.route('/logout',methods = ["GET","POST"])
def logout():
	session.clear()
	return redirect('/')



# Manage Services WebPage
@app.route('/managepatients')
def managepatients():

    if not g.user:
        return redirect(url_for('login'))

    all_data = Data.query.all()

    return render_template("managepatients.html", services = all_data, stype=1,utype=1)


#this route is for inserting data to mysql database via html forms
@app.route('/insert', methods = ['POST'])
def insert():

    if not g.user:
        return redirect(url_for('login'))

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']


        my_data = Data(name, email, phone)
        db.session.add(my_data)
        db.session.commit()

        flash("Patient Inserted Successfully")

        return redirect(url_for('managepatients'))


#this is our update route where we are going to update our employee
@app.route('/update', methods = ['GET', 'POST'])
def update():

    if not g.user:
        return redirect(url_for('login'))

    if request.method == 'POST':
        my_data = Data.query.get(request.form.get('id'))

        my_data.name = request.form['name']
        my_data.email = request.form['email']
        my_data.phone = request.form['phone']

        db.session.commit()
        flash("Patient Updated Successfully")

        return redirect(url_for('managepatients'))




#This route is for deleting our employee
@app.route('/delete/<id>/', methods = ['GET', 'POST'])
def delete(id):
    my_data = Data.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash("Patient Deleted Successfully")

    return redirect(url_for('managepatients'))


#This route is for treating a patient
@app.route('/treatment/<id>/', methods = ['GET', 'POST'])
def treatment(id):
    my_data = Data.query.get(id)
    # db.session.delete(my_data)
    # db.session.commit()
    # flash("Patient Deleted Successfully")

    return render_template('treatment.html')


#This route is for New Appointment
@app.route('/newappointment/<id>/', methods = ['GET', 'POST'])
def newappointment(id):
    my_data = Data.query.get(id)

    # db.session.delete(my_data)
    # db.session.commit()
    # flash("Patient Deleted Successfully")

    return render_template('newappointment.html')


#This route is for Prescription
@app.route('/prescription/<id>/', methods = ['GET', 'POST'])
def prescription(id):
    
    if request.method=="POST":

            my_data = Data.query.get(id)
			# uid = session['uid']
			# sname = request.form['sname']
			
			
            return render_template('prescription.html')
    else:
			#session['sid'] = str(sid)
            # sname = session['sname']
            return render_template('prescription.html')
    
    # db.session.delete(my_data)
    # db.session.commit()
    # flash("Patient Deleted Successfully")

    return render_template('prescription.html')


#This route is for Download
@app.route('/downloadPDF', methods = ['GET', 'POST'])
def downloadPDF():

        #medicine = request.form['medicine']
        # my_data = Data.query.get(id)
        img = Image.open("WebApp/static/images/prescription.png")
	#img = Image.open("/Users/shreyas_rl/Desktop/git/Flask-SqlAlchemy/Rheumatoid/WebApp/static/images/prescription.png")

        img_p = pickle.dumps(img)



        image_p = pickle.loads(img_p)

        print(image_p)

        img_byte_arr = io.BytesIO()
        image_p.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
    #img_byte_arr = img_byte_arr.getvalue()

        return send_file(img_byte_arr, mimetype='image/png',attachment_filename='output.png',
	                     as_attachment=True)


@app.route('/download', methods = ['GET', 'POST'])
def download():

    if request.method=="POST":
        medicine = request.form['medicine']
        # my_data = Data.query.get(id)
        img = Image.open("WebApp/static/images/prescription.png")
	#img = Image.open("/Users/shreyas_rl/Desktop/git/Flask-SqlAlchemy/Rheumatoid/WebApp/static/images/prescription.png")

        img_p = pickle.dumps(img)

# print(img_p)

        image_p = pickle.loads(img_p)

        print(image_p)

        img_byte_arr = io.BytesIO()
        image_p.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        #img_base64 = base64.b64encode(img_byte_arr.read())
        img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")
		#return jsonify({'status':str(img_base64)})

        return render_template('download.html', prescription=1, presPNG = img_base64)

    else:
    	
    	return render_template('prescription.html')



@app.route('/test')
def test():

    from PyPDF2 import PdfFileWriter, PdfFileReader
    import io
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    packet = io.BytesIO()
    # create a new PDF with Reportlab
    can = canvas.Canvas(packet, pagesize=letter)
    can.drawString(10, 100, "Hello There")
    can.save()

    #move to the beginning of the StringIO buffer
    packet.seek(0)
    new_pdf = PdfFileReader(packet)
    # read your existing PDF
    existing_pdf = PdfFileReader(open("WebApp/static/pdf/samplePrescription.pdf", "rb"))
    output = PdfFileWriter()
    # add the "watermark" (which is the new pdf) on the existing page
    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)
    # finally, write "output" to a real file
    outputStream = open("WebApp/static/pdf/prescription.pdf", "wb")
    output.write(outputStream)
    outputStream.close()

    return send_file("static/pdf/prescription.pdf",
	                     attachment_filename='output.pdf',
	                     as_attachment=True)

	#return render_template('prescriptionPDF.html')


@app.route('/test2')
def test2():
    img = Image.open("WebApp/static/images/prescription.png")
	#img = Image.open("/Users/shreyas_rl/Desktop/git/Flask-SqlAlchemy/Rheumatoid/WebApp/static/images/prescription.png")

    img_p = pickle.dumps(img)

# print(img_p)

    image_p = pickle.loads(img_p)

    print(image_p)

    img_byte_arr = io.BytesIO()
    image_p.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    #img_byte_arr = img_byte_arr.getvalue()

    return send_file(img_byte_arr, mimetype='image/png',attachment_filename='output.png',
	                     as_attachment=True)

@app.route('/savepatienttreatment/<id>/', methods = ['GET', 'POST'])
def savepatienttreatment(id):
    
    os.remove("WebApp/static/pdf/prescription.pdf")

    return redirect(url_for('managepatients'))



#Edit a given Service SID
@app.route('/sess/<seid>')
def sess(seid):
	try:
		if not 'uid' in session:
			return redirect('/')

		cur = con.cursor()
		name = session['name']

		try:
			session['sid'] = str(seid)
		except:
			seid = session['sid']

		cur.execute("SELECT * FROM services WHERE serviceid = %s",(seid,))
		data = cur.fetchall()[0]

		sname = data[1]
		session['sname'] = sname
		return render_template('addnew.html',sname=sname,name=name)

	except Exception as e:
		con.rollback()
		cur.close()

		return redirect('/')






#Create a New Service : Initialisation of Services Table with status = 'inactive'
@app.route('/sinsert',methods = ['GET','POST'])
def sinsert():
	
	try:

		if not 'uid' in session:
			return redirect('/')

		if request.method=="POST":
			
			uid = session['uid']
			sname = request.form['sname']
			
			cur = con.cursor()
			timstamp = datetime.datetime.now().date()
			cur.execute("INSERT INTO services(servicename,status,dateofcreation) VALUES(%s,%s,%s)",(sname,'inactive',timstamp))
			con.commit()
			cur.execute("SELECT serviceid FROM services WHERE servicename = %s AND status = %s AND dateofcreation = %s",(sname,'inactive',timstamp))
			sid = cur.fetchone()[0]
			cur.execute("INSERT INTO userservices(uid,sid) VALUES(%s,%s)",(uid,sid))
			con.commit()
			session['sid'] = str(sid)
			session['sname'] = sname
			cur.close()
			return render_template('addnew.html',sname=sname)
		else:
			#session['sid'] = str(sid)
			sname = session['sname']
			return render_template('addnew.html',sname=sname)

	except Exception as e:
		con.rollback()
		cur.close()

		return redirect('/')



@app.route('/updatesname',methods = ["GET","POST"])
def updatesname():
	try:
		if not 'uid' in session:
				return redirect('/')

		if request.method=="POST":
				
			uid = session['uid']
			sid = session['sid']

			sname = request.form['sname']
			name = session['name']
				
			cur = con.cursor()
			cur.execute("UPDATE services SET servicename = %s WHERE serviceid = %s",(sname,sid))
			con.commit()
			cur.close()

			session['sname'] = sname
			return render_template('addnew.html',sname=sname)
		else:
			return render_template('addnew.html',sname=session['sname'],name=name)

	except Exception as e:
		con.rollback()
		cur.close()

		return redirect('/')



# Step 1 WebPage
@app.route('/step1',methods=['GET','POST'])
def step1():
		
	try:
		if not 'uid' in session:
			return redirect('/')

		cur = con.cursor()
		sid = session['sid']
		cur.execute("SELECT * FROM servicedetails WHERE sid = %s",(sid,))
		try:
			urlp = cur.fetchall()
		except TypeError:
			urlp = False

		cur.close()
		name = session['name']
		return render_template('step1.html',urls=urlp,sname=session['sname'],name = name)

	except Exception as e:
		con.rollback()
		cur.close()

		return redirect('/')





# Add New URL Prefix Stage 1 
@app.route('/addurl',methods=['GET','POST'])
def addurl():
		
	try:
		if not 'uid' in session:
			return redirect('/')

		if request.method=="POST":
			
			sid = session['sid']
			cur = con.cursor()
			url  = request.form['urlprefix']
			cur.execute("INSERT INTO servicedetails(sid,urlp) VALUES(%s,%s)",(sid,url))
			con.commit()
			cur.close()
			return redirect(url_for('step1'))

	except Exception as e:
		con.rollback()
		cur.close()

		return redirect('/')





#Edit added URL Prefix Stage 1
@app.route('/urledit',methods = ['GET','POST'])
def urledit():
		
	try:
		if not 'uid' in session:
			return redirect('/')

		if request.method == 'POST':
			urlid = request.form['urlid']
			urlp = request.form['urlpre']
			sid = session['sid']
			cur = con.cursor()
			cur.execute("UPDATE servicedetails SET urlp = %s WHERE sid = %s AND urlid = %s",(urlp,sid,urlid))
			con.commit()
			cur.close()
			return redirect(url_for('step1'))

	except Exception as e:
		con.rollback()
		cur.close()

		return redirect('/')





#Delete added URL Stage 1
@app.route('/deleterow/<row>')
def deleterow(row):
		
	try:
		if not 'uid' in session:
			return redirect('/')

		#print("DELETE FUNCTION INVOKED!")
		sid = session['sid']
		cur = con.cursor()
		cur.execute("DELETE FROM servicedetails WHERE sid = %s AND urlp = %s ",(sid,row))
		con.commit()
		cur.close()
		return redirect(url_for('step1'))

	except Exception as e:
		con.rollback()
		cur.close()

		return redirect('/')





# Step 2 WebPage
@app.route('/step2',methods=['GET','POST'])
def step2():
		
	try:
		if not 'uid' in session:
			return redirect('/')

		cur = con.cursor()
		sid = session['sid']

		#Fetching Default Filters
		cur.execute("SELECT * FROM filters WHERE ftype = %s ORDER BY fid ASC ",(0,))
		filters = list(cur.fetchall())
		flist = []
		for filter in filters:
			filter = list(filter)
			mid = filter[6]
			cur.execute("SELECT * FROM masks WHERE mid = %s",(mid,))
			filter[6] = cur.fetchall()[0][1]
			flist.append(filter)

		#Fetching Selected Filters
		cur.execute("SELECT * FROM fsets WHERE fsetid = %s ",(sid,))
		fids = cur.fetchall()
		selfils = []
		for fid in fids:
			cur.execute("SELECT * FROM filters WHERE fid = %s",(fid[1],))
			selfils.append(list(cur.fetchall()[0]))

		for selfil in selfils:
			mid = selfil[6]
			cur.execute("SELECT * FROM masks WHERE mid = %s",(mid,))
			selfil[6] = cur.fetchall()[0][1]

		cur.execute("SELECT * FROM prefixes ORDER BY pid")
		prefixes = cur.fetchall()

		pnames = []
		for prefix in prefixes:
			pnames.append(prefix[1])

		cur.execute("SELECT * FROM suffixes ORDER BY sufid")
		suffixes = cur.fetchall()

		snames = []
		for suffix in suffixes:
			snames.append(suffix[1])

		name = session['name']
		cur.close()
		status = 2
		return render_template('step2.html',filters=flist,selfils = selfils,status = status,prefixes=pnames,suffixes=snames,sname=session['sname'],name = name)

	except Exception as e:
		con.rollback()
		cur.close()

		return redirect('/')






# Selecting from Default Filters Stage 2 
@app.route('/selfilter/<fid>',methods = ['GET','POST'])
def selfilter(fid):
		
	try:
		if not 'uid' in session:
			return redirect('/')

		cur = con.cursor()
		sid = session['sid']

		cur.execute("SELECT * FROM filters WHERE fid = %s",(fid,))
		f = cur.fetchall()[0]

		fname = f[2]
		farea = f[3]
		fprefix = f[4]
		fsuffix = f[5]
		maskid = f[6]

		cur.execute("INSERT INTO filters(ftype,fname,farea,fprefix,fsuffix,maskid,unmask) VALUES(%s,%s,%s,%s,%s,%s,%s)",(1,fname,farea,fprefix,fsuffix,maskid,0))
		con.commit()
		cur.execute("SELECT fid FROM filters WHERE ftype = %s AND fname = %s AND farea = %s AND fprefix = %s AND fsuffix = %s AND maskid = %s AND unmask = %s ORDER BY fid DESC",(1,fname,farea,fprefix,fsuffix,maskid,0))
		fid = cur.fetchone()[0]
		cur.execute("INSERT INTO fsets(fsetid,filterid) VALUES(%s,%s)",(sid,fid))
		con.commit()
		cur.close()
		return redirect(url_for('step2'))

	except Exception as e:
		con.rollback()
		cur.close()

		return redirect('/')






# Edit a Selected Filter : Add a new filter into Filters Table, link to Fsets Table
@app.route('/updatefil',methods = ["GET","POST"])
def updatefil():
		
	try:
		if not 'uid' in session:
			return redirect('/')

		if request.method == 'POST':
			fid = request.form['fid']
			fname = request.form['name']
			farea = request.form['area']
			fprefix = request.form['prefix']
			fsuffix = request.form['suffix']
			maskid = request.form['mask']
			cur = con.cursor()
			sid = session['sid']
			cur.execute("SELECT mid FROM masks WHERE mname = %s",(maskid,))
			mid = cur.fetchall()[0]
			#Check corresponding to fid is there a row with type = 0
			cur.execute("SELECT * FROM filters WHERE fid = %s",(fid,))
			f = cur.fetchall()[0]
			if f[1] == 1:
				cur.execute("UPDATE filters SET fname = %s , farea = %s , fprefix = %s , fsuffix = %s , maskid = %s , unmask = %s WHERE fid = %s",(fname,farea,fprefix,fsuffix,mid,0,fid))
				con.commit()
			cur.close()
			return redirect(url_for('step2'))

	except Exception as e:
		con.rollback()
		cur.close()

		return redirect('/')




# Delete Selected Filter FID
@app.route('/deleteselfil/<fid>')
def deleteselfil(fid):
		
	try:
		if not 'uid' in session:
			return redirect('/')

		cur = con.cursor()
		sid = session['sid']
		cur.execute("DELETE FROM filters WHERE fid = %s",(fid,))
		con.commit()
		cur.execute("DELETE FROM fsets WHERE fsetid = %s AND filterid = %s ",(sid,fid))
		con.commit()
		cur.close()
		return redirect(url_for('step2'))

	except Exception as e:
		con.rollback()
		cur.close()

		return redirect('/')






# Step 3 WebPage
@app.route('/step3',methods = ['GET','POST'])
def step3():
	
	try:
		if not 'uid' in session:
			return redirect('/')

		cur = con.cursor()
		sid = session['sid']
		cur.execute("SELECT * FROM fsets WHERE fsetid = %s ",(sid,))
		fids = cur.fetchall()
		selfils = []
		for fid in fids:
			cur.execute("SELECT * FROM filters WHERE fid = %s",(fid[1],))
			selfils.append(list(cur.fetchall()[0]))

		for selfil in selfils:
			mid = selfil[6]
			cur.execute("SELECT * FROM masks WHERE mid = %s",(mid,))
			selfil[6] = cur.fetchall()[0][1]
		cur.close()
		name = session['name']
		return render_template('step3.html',selfils = selfils,sname=session['sname'],name = name)

	except Exception as e:
		con.rollback()
		cur.close()

		return redirect('/')



# Save a New Service, make Status = Active
@app.route('/saveservice',methods = ['GET','POST'])
def saveservice():

	try:
		if not 'uid' in session:
			return redirect('/')

		else:
			cur = con.cursor()
			sid = session['sid']

			cur.execute("SELECT * FROM fsets WHERE fsetid = %s ",(sid,))
			fids = cur.fetchall()
			for fid in fids:
				cur.execute("UPDATE filters SET unmask = %s WHERE fid = %s",(0,fid[1]))
				con.commit()

			try:
				unmask = request.form.getlist('unmask')
				unmask = tuple(int(x) for x in unmask)
				cur.execute("UPDATE filters SET unmask = %s WHERE fid IN %s",(1,unmask))
				con.commit()
			except Exception as e:
				con.rollback()
				cur.close()


			cur = con.cursor()
			cur.execute("UPDATE services SET status = %s WHERE serviceid = %s",('active',sid))
			con.commit()
			cur.close()

			red.activeServices()

			return redirect(url_for('manageservices'))


	except Exception as e:
		con.rollback()
		cur.close()

		return redirect('/')




# Stop Service
@app.route('/Stop/<sid>',methods = ['GET','POST'])
def stop(sid):

	# try:
		if not 'uid' in session:
			return redirect('/')

		cur = con.cursor()
		#sid = session['sid']
		cur.execute("UPDATE services SET status = %s WHERE serviceid = %s",('inactive',sid))
		con.commit()
		cur.close()

		red.activeServices()

		return redirect(url_for('manageservices'))

	# except:
	# 	con.rollback()
	# 	cur.close()

	# 	return redirect('/')



#Start Service
@app.route('/Start/<sid>',methods = ['GET','POST'])
def start(sid):

	try:
		if not 'uid' in session:
			return redirect('/')

		cur = con.cursor()
		#sid = session['sid']
		cur.execute("UPDATE services SET status = %s WHERE serviceid = %s",('active',sid))
		con.commit()
		cur.close()

		red.activeServices()

		return redirect(url_for('manageservices'))

	except:
		con.rollback()
		cur.close()

		return redirect('/')





@app.route('/logs',methods=["GET","POST"])
def logs():
	try:
		if not 'uid' in session:
			return redirect('/')

		utype = session['utype']

		if request.method=="POST":
			cur = con.cursor()
			startdate = request.form['startdate']
			enddate = request.form['enddate']
			#date = request.form['date']
			wholedata = []
			cur.execute("SELECT * FROM services WHERE dateofcreation BETWEEN %s AND %s",(startdate,enddate))
			data = cur.fetchall()
			for s in data:
				sid = str(s[0])
				#print(sid)
				cur.execute("SELECT * FROM userservices WHERE sid = %s",(sid,))
				user = cur.fetchall()[0]
				uid = str(user[0])
				cur.execute("SELECT * FROM users WHERE uid = %s",(uid,))
				userdata = cur.fetchall()[0]
				username = str(userdata[2]) + " " + str(userdata[3])
				print(username)
				wholedata.append([s[0],s[1],s[2],s[3],username])
			name = session['name']


			return render_template('dashboard.html',data = wholedata,name=name,utype=utype,startdate=startdate,enddate=enddate)
		else:
			'''cur = con.cursor()
												cur.execute("SELECT * FROM services ORDER BY status")
												data = cur.fetchall()'''
			name = session['name']
			return render_template('dashboard.html',name=name,utype=utype)
			
	except Exception as e:
		con.rollback()
		cur.close()

		return redirect('/')



@app.route('/view_report',methods=["GET","POST"])
def view_report():
	try:
		if not 'uid' in session:
			return redirect('/')

		if request.method=="POST":
			cur = con.cursor()
			sid = request.form['logid']
			date = request.form['date']
			uname = request.form['name']
			sname = request.form['sname']
			status = request.form['status']

			startdate = request.form['startdate']
			enddate = request.form['enddate']

			data = [[sid,sname,status,date,uname,]]
			#date = request.form['date']

			utype = session['utype']

			cur.execute("SELECT * FROM logs WHERE logid = %s",(sid,))
			logdata = cur.fetchall()
			try:
				print(logdata[0])
				name = session['name']
				alldata = []
				for row in logdata:
					masks = pickle.loads(row[3])
					#print(masks)
					alldata.append([row[0],row[1],row[2],masks])

				return render_template('dashboard.html',name=name,data=data,logdata=alldata,utype=utype,startdate=startdate,enddate=enddate)
			except:
				flash("No Logs Found!","info")
				name = session['name']
				return render_template('dashboard.html',name=name,data=data,logdata=logdata,utype=utype,startdate=startdate,enddate=enddate)
		else:
			return redirect('/logs')

	except Exception as e:
		con.rollback()
		cur.close()

		return redirect('/')




@app.route('/settings',methods=["GET","POST"])
def settings():
	try:
		if not 'uid' in session:
			return redirect('/')
		elif session['utype'] != 1:
			return redirect('/')

		if request.method=="POST":
			cur = con.cursor()
			email = request.form['email']
			cur.execute("SELECT * FROM users WHERE email = %s",(email,))
			
		else:
			cur = con.cursor()
			cur.execute("SELECT * FROM users ORDER BY timstamp DESC")

		users = cur.fetchall()
		alldata = []
		for user in users:
			ustatus = user[6]
			if ustatus == 0:
				ustatus = "Waiting"
			elif ustatus == 1:
				ustatus = "Approved"
			elif ustatus == -1:
				ustatus = "Rejected"
			alldata.append([user[0],user[1],user[2],user[3],user[4],user[5],ustatus,user[7]])

		name = session['name']
		return render_template('settings.html',name=name,users=alldata, pagename="")


	except Exception as e:
		con.rollback()
		cur.close()

		return redirect('/')



@app.route('/user_approval')
def user_approval():
	try:
		if not 'uid' in session:
				return redirect('/')

		cur = con.cursor()
		name = session['name']

		cur.execute("SELECT * FROM users WHERE approve = 1")
		users = cur.fetchall()
		alldata = []
		for user in users:
			ustatus = user[6]
			if ustatus == 0:
				ustatus = "Waiting"
			elif ustatus == 1:
				ustatus = "Approved"
			elif ustatus == -1:
				ustatus = "Rejected"
			alldata.append([user[0],user[1],user[2],user[3],user[4],user[5],ustatus,user[7]])

		pagename = "Approved"
		return render_template('settings.html',name=name,users=alldata,pagename=pagename)
	except Exception as e:
		con.rollback()
		cur.close()

		return redirect('/')




@app.route('/user_waiting')
def user_waiting():
	try:
		if not 'uid' in session:
				return redirect('/')

		cur = con.cursor()
		name = session['name']

		cur.execute("SELECT * FROM users WHERE approve = 0")
		users = cur.fetchall()
		alldata = []
		for user in users:
			ustatus = user[6]
			if ustatus == 0:
				ustatus = "Waiting"
			elif ustatus == 1:
				ustatus = "Approved"
			elif ustatus == -1:
				ustatus = "Rejected"
			alldata.append([user[0],user[1],user[2],user[3],user[4],user[5],ustatus,user[7]])

		pagename = "Waiting For Approval"
		return render_template('settings.html',name=name,users=alldata,pagename=pagename)
	except Exception as e:
		con.rollback()
		cur.close()

		return redirect('/')



@app.route('/user_rejection')
def user_rejection():
	try:
		if not 'uid' in session:
				return redirect('/')

		cur = con.cursor()
		name = session['name']

		cur.execute("SELECT * FROM users WHERE approve = -1")
		users = cur.fetchall()
		alldata = []
		for user in users:
			ustatus = user[6]
			if ustatus == 0:
				ustatus = "Waiting"
			elif ustatus == 1:
				ustatus = "Approved"
			elif ustatus == -1:
				ustatus = "Rejected"
			alldata.append([user[0],user[1],user[2],user[3],user[4],user[5],ustatus,user[7]])
		pagename = "Unapproved"
		return render_template('settings.html',name=name,users=alldata,pagename=pagename)
	except Exception as e:
		con.rollback()
		cur.close()

		return redirect('/')



@app.route('/help')
def help():
	try:
		name = session['name']
		utype = session['utype']
		return render_template('help.html',name=name,utype=utype)
	except Exception as e:
		con.rollback()
		cur.close()
		return redirect('/')

@app.route('/filtertypes')
def filtertypes():
	try:
		name = session['name']
		utype = session['utype']
		return render_template('filtertypes.html',name=name,utype=utype)
	except Exception as e:
		con.rollback()
		cur.close()

		return redirect('/')





@app.route('/userlogs',methods=["GET","POST"])
def userlogs():
	try:
		if not 'uid' in session:
			return redirect('/')

		utype = session['utype']

		if request.method=="POST":
			cur = con.cursor()
			startdate = request.form['startdate']
			enddate = request.form['enddate']
			#date = request.form['date']
			wholedata = []
			cur.execute("SELECT * FROM userlogs WHERE logdate BETWEEN %s AND %s",(startdate,enddate))
			data = cur.fetchall()
			name = session['name']
			return render_template('userDashboard.html',data = data,name=name,utype=utype)
		else:
			'''cur = con.cursor()
												cur.execute("SELECT * FROM services ORDER BY status")
												data = cur.fetchall()'''
			name = session['name']
			return render_template('userDashboard.html',name=name,utype=utype)
			
	except Exception as e:
		con.rollback()
		cur.close()

		return redirect('/')



@app.route('/view_user_report',methods=["GET","POST"])
def view_user_report():
	try:
		if not 'uid' in session:
			return redirect('/')

		if request.method=="POST":
			cur = con.cursor()
			sid = request.form['logid']
			date = request.form['date']
			uname = request.form['name']
			sname = request.form['sname']
			status = request.form['status']
			data = [[sid,sname,status,date,uname,]]
			#date = request.form['date']

			utype = session['utype']

			cur.execute("SELECT * FROM userlogs WHERE logid = %s",(sid,))
			logdata = cur.fetchall()
			try:
				print(logdata[0])
				name = session['name']
				# alldata = []
				# for row in logdata:
				# 	masks = pickle.loads(row[3])
				# 	#print(masks)
				# 	alldata.append([row[0],row[1],row[2],masks])

				return render_template('dashboard.html',name=name,data=data,logdata=alldata,utype=utype)
			except:
				flash("No Logs Found!","info")
				name = session['name']
				return render_template('dashboard.html',name=name,data=data,logdata=logdata,utype=utype)
		else:
			return redirect('/logs')

	except Exception as e:
		con.rollback()
		cur.close()

		return redirect('/')


