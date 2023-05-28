import csv
from flask import Flask, render_template, redirect, url_for,request
from flask import *
from flask_bootstrap import Bootstrap
import PIL.Image
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from array import *
from io import BytesIO
from PIL import Image
import logging
from base64 import b64decode
import cv2
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pytz
import _thread
import pandas as pd
import shutil # save img locally
import numpy as np
from flask import Flask, render_template, url_for, request,send_file
from flask_sqlalchemy import SQLAlchemy
from flask import *
from pylab import array, plot, show, axis, arange, figure, uint8 
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from scrapy.selector import Selector
import wget
import mysql.connector
from twocaptcha import TwoCaptcha
api_key = os.getenv('APIKEY_2CAPTCHA', 'cfccb208aa0b7829cc84c634fd6aa314')
solver = TwoCaptcha(api_key)


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SECRET_KEY'] = 'Myones..OK?!'
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
browse_params=False
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'



try:
    shutil.rmtree("Generated_PDF")
except:
    pass

record_hub_search_iter=0

user_list=[
           'fonehi8344@hrisland.com',
            'hotorin730@fitzola.com',
            'pekevob464@hrisland.com',
            'mojov17607@gam1fy.com',
            'xivatan270@ippals.com',
            'nifikot541@hrisland.com',
            'niyay78655@fitzola.com',
            'feveke2994@gam1fy.com',
            'heparan541@ippals.com',
            'xipayo5251@ippals.com',
            'nikobed421@fitzola.com',
            'seyiv48476@hrisland.com',
            'cinewe7879@ippals.com',
            'cecom19022@fitzola.com',
            'hixiv42699@hrisland.com']


df=pd.read_csv('All_Counties_Updated.csv')
counties=df.values.tolist()

# west_virginia_type=pd.read_csv('West_Virginia_Type_Search.csv')
# west_virginia_type=west_virginia_type.values.tolist()


def array_list(array_num):
    num_list = array_num.tolist() # list
    
# Get the unique values of 'State' column
states=df.State.unique()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    
class Orders(db.Model):
    o_id=db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    order_id_remark = db.Column(db.String(80))
    time_created = db.Column(db.String(80))
    state = db.Column(db.String(80))
    county = db.Column(db.String(80))
    document_number = db.Column(db.String(80))
    book_page = db.Column(db.String(80))
    no_of_pages = db.Column(db.String(80))
    site = db.Column(db.String(80))
    status = db.Column(db.String(80))
    time_completed = db.Column(db.String(80))
    pdf = db.Column(db.PickleType)
    total_sec = db.Column(db.String(80))
    remark = db.Column(db.String(80))
    
def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData

def writeTofile(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
    with open(filename, 'wb') as file:
        file.write(data)
    print("Stored blob data into: ", filename, "\n")
    

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    
    
    


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))
        message='Invalid username or password'
        return render_template('login.html', form=form,message=message)
        #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            message='Username Already Exists..'
        else:
            hashed_password = generate_password_hash(form.password.data, method='sha256')
            new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            dict={'username':form.username.data, 'email':form.email.data, 'password':hashed_password,'subscribe':'FALSE','subscribe_date':'','subscribe_end':''}
            mydb = mysql.connector.connect(
            host='82.180.142.1',
            database='u658764133_login',
            user='u658764133_main_data',
            password='Devops1234$'
            )
            mycursor = mydb.cursor()
            sql = "INSERT INTO login (username, email,password) VALUES (%s, %s, %s)"
            val = (form.username.data, form.email.data, form.password.data)
            mycursor.execute(sql, val)
            mydb.commit()
            print(mycursor.rowcount, "record inserted.")
            message='New user has been created!'
            print(message)
        return render_template('signup.html', form=form,message=message)
        #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'
    return render_template('signup.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    print(current_user.username)
    return render_template('index.html', name=current_user.username)

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    state=''
    county=''
    order_id_remark=''
    if request.method == 'POST':
        order_id_remark=request.form['order_id_remark']
        print(order_id_remark)
        state=request.form['state']
        print("State : ",state)
        county=request.form['county']
        print("County : ",county) 
        page_upto=''
        type_search=''
        west_virginia_type_search=''
        if state=='':
            return render_template('search.html', name=current_user.username,states=states,county=county,order_id_remark=order_id_remark)
        elif state !="" and county =="":
            countys = df.loc[df['State'] == state]
            countys=countys.County.unique()
            return render_template('search.html', name=current_user.username,states=states,state=state,counties=countys,county=county,order_id_remark=order_id_remark)
        elif county!="":
            countys = df.loc[df['State'] == state]
            countys=countys.County.unique()
            if county in countys:
                if state=='Georgia':
                    page_upto=request.form['page_upto']
                    type_search=request.form['type_search']
                elif state=='West Virginia':
                    west_virginia_type_search=request.form['west_virginia_type_search']
                    print(west_virginia_type_search)
                site = df.loc[df['County'] == county]
                site=site.loc[site['State'] == state]
                is_login=site.Login.unique()
                link=site.Link.unique()
                link=link[0]
                print("Link : ",link)
                
                site=site.Site.unique()
                print(site)
                print("Site : ",site[0])
                site=site[0]
                document_type=request.form['document_type']
                print("Document Type : ",document_type)
                book=''
                page=''
                DocumentNumber=''
                
                if document_type=="Document Number":
                    DocumentNumber=request.form['DocumentNumber']
                    print("Document Number : ",DocumentNumber)
                    if is_login[0]=="no":
                        new_order=Orders(username=current_user.username,order_id_remark=order_id_remark,time_created=datetime.now(pytz.timezone('US/Pacific')).strftime("%m-%d-%Y, %H:%M:%S"),state=state,county=county,document_number=DocumentNumber,site=site,status='Order Created')
                        db.session.add(new_order)
                        db.session.commit()
                        o_id=new_order.o_id
                elif document_type=="Book, Page":
                    book=request.form['book']
                    page=request.form['page']
                    print("Book Page : ",book,page)
                    if is_login[0]=="no":
                        book_page=str(book)+'-'+str(page)
                        new_order=Orders(username=current_user.username,order_id_remark=order_id_remark,time_created=datetime.now(pytz.timezone('US/Pacific')).strftime("%m-%d-%Y, %H:%M:%S"),state=state,county=county,book_page=book_page,site=site,status='Order Created')
                        db.session.add(new_order)
                        db.session.commit()
                        o_id=new_order.o_id
                if is_login[0]=="no":
                    print("No Login Required")
                    if site=='SearchIQ':
                        try:
                            print(o_id)
                            _thread.start_new_thread(SQ_WOL,(link,document_type,book,page,DocumentNumber,o_id,))
                            # threading.Thread(target=SQ_WOL,args=(link,document_type,book,page,DocumentNumber,o_id)).start()
                            return redirect('/account')
                            # browser = searchiq('/Applications/Google Chrome')
                            # browser.open_page(link)
                            # print(link)
                            # pdf_name=browser.search_results(document_type,book,page,DocumentNumber)
                            # browser.close_browser()
                            # if pdf_name[-4:]=='.pdf':
                            #     new_order.pdf=convertToBinaryData(pdf_name)
                            #     new_order.status='Completed'
                            #     db.session.commit()
                            # else:
                            #     new_order.status='Problem Occurred'
                            #     db.session.commit()
                                
                            # return send_file(pdf_name, as_attachment=True)
                        except:
                            browser.close_browser()
                            return 'Failed to Get'
                    elif site=='UslandRecords':
                        try:
                            _thread.start_new_thread(US_WOL,(link,document_type,book,page,DocumentNumber,o_id,))
                            # threading.Thread(target=SQ_WOL,args=(link,document_type,book,page,DocumentNumber,o_id)).start()
                            return redirect('/account')
                        
                            # browser = Uslandrecord('/Applications/Google Chrome')
                            # browser.open_page(link)
                            # pdf_name=browser.search_results(document_type,DocumentNumber,book,page)
                            # return send_file(pdf_name, as_attachment=True)
                        except:
                            # browser.close_browser()
                            return 'Failed to Get'
                    elif site=='Kofile':
                        try:
                            _thread.start_new_thread(KF_WOL,(link,document_type,book,page,DocumentNumber,o_id,))
                            return redirect('/account')
                            # browser = kofiletech('/Applications/Google Chrome')
                            # links='https://countyfusion1.kofiletech.us/'
                            # browser.open_page(links)
                            # print(links)
                            # pdf_name=browser.search_results(link,document_type,book,page,DocumentNumber)
                            # browser.close_browser()
                            # return send_file(pdf_name, as_attachment=True)
                        except:
                            browser.close_browser()
                            return 'Failed to Get'
                    elif site=='West_Virginia':
                        try:
                            _thread.start_new_thread(WV_WOL,(link,document_type,book,page,DocumentNumber,o_id,west_virginia_type_search,))
                            return redirect('/account')
                            # browser = kofiletech('/Applications/Google Chrome')
                            # links='https://countyfusion1.kofiletech.us/'
                            # browser.open_page(links)
                            # print(links)
                            # pdf_name=browser.search_results(link,document_type,book,page,DocumentNumber)
                            # browser.close_browser()
                            # return send_file(pdf_name, as_attachment=True)
                        except:
                            browser.close_browser()
                            return 'Failed to Get'
                    elif site=='Record Search Hub':
                        try:
                            _thread.start_new_thread(RSH_WOL,(link,document_type,book,page,DocumentNumber,o_id,county,))
                            return redirect('/account')
                        except:
                            browser.close_browser()
                            return 'Failed to Get'
                        
                    elif site=='Landmark':
                        try:
                            _thread.start_new_thread(LM_WOL,(link,document_type,book,page,DocumentNumber,o_id,county,))
                            return redirect('/account')
                        except:
                            browser.close_browser()
                            return 'Failed to Get'
                        
                        
                elif is_login[0]=="yes":
                    try:
                        username=request.form['username']
                        print("Login Success")
                        password=request.form['password']
                
                        if document_type=="Document Number":
                            new_order=Orders(username=current_user.username,order_id_remark=order_id_remark,time_created=datetime.now(pytz.timezone('US/Pacific')).strftime("%m-%d-%Y, %H:%M:%S"),state=state,county=county,document_number=DocumentNumber,site=site,status='Order Created')
                            db.session.add(new_order)
                            db.session.commit()
                            o_id=new_order.o_id
                        elif document_type=="Book, Page":
                            book_page=str(book)+'-'+str(page)
                            new_order=Orders(username=current_user.username,order_id_remark=order_id_remark,time_created=datetime.now(pytz.timezone('US/Pacific')).strftime("%m-%d-%Y, %H:%M:%S"),state=state,county=county,book_page=book_page,site=site,status='Order Created')
                            db.session.add(new_order)
                            db.session.commit()
                            o_id=new_order.o_id
                        print("Username : ",username)
                        print("Password : ",password)
                        if site=='SearchIQ':
                            try:
                                _thread.start_new_thread(SQ_WL,(link,document_type,book,page,DocumentNumber,o_id,username,password,))
                                return redirect('/account')
                                # browser = searchiq('/Applications/Google Chrome')
                                # browser.open_page(link)
                                # print(link)
                                # pdf_name=browser.search_results(document_type,book,page,DocumentNumber,Username=username,Password=password)
                                # browser.close_browser()
                                # return send_file(pdf_name, as_attachment=True)
                            except:
                                # browser.close_browser()
                                return 'Failed to Get'
                        elif site=='DoxPopIN':
                            try:
                                print(o_id)
                                _thread.start_new_thread(DP_WL,(username,password,document_type,county,DocumentNumber,book,page,o_id,))
                                # threading.Thread(target=DP_WL,args=(username,password,document_type,county,DocumentNumber,book,page,o_id)).start()
                                return redirect('/account')
                                # pdf_name=doxpopsaveimages(username,password,document_type,county,DocumentNumber,book,page,county)
                                # if pdf_name[0:16]=='You have entered':
                                #     print(pdf_name)
                                #     return render_template('search.html', name=current_user.username,states=states,state=state,counties=countys,county=county,message=pdf_name)
                                # else:    
                                #     return send_file(pdf_name, as_attachment=True)
                            except:
                                # browser.close_browser()
                                return 'Failed to get'
                        elif site=='GSCCA':
                            print("GEORGIA")
                            print(page_upto,page)
                            a=int(int(page_upto)-int(page))
                            type_search=request.form['type_search']
                            print(type_search)
                            if (a)<0:
                                print("Invalid page number")
                                return 'Invalid Page Number Entered'
                            else:
                                print("HERE")
                                new_order.book_page=str(book)+'-'+str(page)+'-'+str(page_upto)
                                db.session.commit()
                                try:
                                    print(o_id)
                                    _thread.start_new_thread(GS_WL,(username,password,document_type,county,DocumentNumber,book,page,o_id,a,type_search,link,))
                                    return redirect('/account')
                                    # browser = GSCCCA('/Applications/Google Chrome')
                                    # lik='https://www.gsccca.org'
                                    # browser.open_page(lik)
                                    # browser.login(username,password)
                                    # pdf_name=browser.search_results(link,book,page,a,type_search)
                                    # return send_file(pdf_name, as_attachment=True)
                                except:
                                    # browser.close_browser()
                                    return 'Failed to Get'
                        elif site=='Kofile':
                            try:
                                browser = kofiletech('/Applications/Google Chrome')
                                links='https://countyfusion1.kofiletech.us/'
                                browser.open_page(links)
                                print(links)
                                pdf_name=browser.search_results(link,document_type,book,page,DocumentNumber,Username=username,Password=password)
                                return send_file(pdf_name, as_attachment=True)
                            except:
                                browser.close_browser() 
                                return 'Failed to Get'
                    except:
                        print("Login Required")
                        return render_template('search.html',name=current_user.username,states=states,state=state,counties=countys,county=county,document_type=document_type,DocumentNumber=DocumentNumber,book=book,page=page,login="TRUE",page_upto=page_upto,type_search=type_search,order_id_remark=order_id_remark)
            else:
                county=""
            return render_template('search.html', name=current_user.username,states=states,state=state,counties=countys,county=county,west_virginia_type_search=west_virginia_type_search,order_id_remark=order_id_remark)
    return render_template('search.html', name=current_user.username,states=states,county=county,order_id_remark=order_id_remark)

        

@app.route('/account')
@login_required
def account():
    
    # view_all =login_mongodb.find_one({'username':current_user.username})
    # view_all={'subscribe':'TRUE'}
    user=str(current_user.username)
    view_all=Orders.query.filter_by(username=user)
    return render_template('account.html', name=current_user.username,view_all=view_all)

@app.route('/order_details/<o_id>')
@login_required
def order_details(o_id):
    user=str(current_user.username)
    d=Orders.query.filter_by(o_id=o_id).first()
    if d.username==current_user.username:
        return render_template('order_details.html', name=current_user.username,view_all=d)
    else:
        return 'Unauthorized Request'

@app.route('/download_pdf/<o_id>')
@login_required
def download_pdf(o_id):
    d=Orders.query.filter_by(o_id=o_id).first()
    if d.username==current_user.username:
        path='.pdf'
        if d.document_number!=None:
            path=str(d.document_number)+path
        else:
            path=str(d.book_page)+path
        writeTofile(d.pdf, path)
        _thread.start_new_thread(remove_file_pdf,(path,))
        # threading.Thread(target=remove_file_pdf,args=(str(path))).start()
        return send_file(path, as_attachment=True)
    else:
        return 'Unauthorized Request'
    
@app.route('/remove_order/<o_id>')
@login_required
def remove_order(o_id):
    d=Orders.query.filter_by(o_id=o_id).first()
    if d.username==current_user.username:
        db.session.delete(d)
        db.session.commit()
        return redirect('/account')
    else:
        return 'Unauthorized Request'
    

@app.route('/get_report')
@login_required
def get_report():
    try:
        user=str(current_user.username)
        d=Orders.query.filter_by(username=user)
        path=user+'_Report.csv'
        with open(path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter =',')
            csv_writer.writerow(['Order ID','Time Created','State','County','Document Number','Book/Page','Total Pages','Site','Status','Time Completed','Total Seconds','Remark'])
            for p in d:
                csv_writer.writerow([p.order_id_remark,p.time_created,p.state,p.county,p.document_number,p.book_page,p.no_of_pages,p.site,p.status,p.time_completed,p.total_sec,p.remark])
        _thread.start_new_thread(remove_file_pdf,(path,))
        return send_file(path,mimetype= 'text/csv', as_attachment=True)
    except:
        return 'Unauthorized Request'


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/tapestry_start_order/<current_user>&<username>&<password>&<type>&<NET_SessionId>&<__zlcmid>&<doc>&<county>&<state>')
def tapestry_start_order(current_user,username,password,type,NET_SessionId,__zlcmid,doc,county,state):
    try:
        new_order=Orders(username=current_user,order_id_remark="Tapestry",time_created=datetime.now(pytz.timezone('US/Pacific')).strftime("%m-%d-%Y, %H:%M:%S"),state=state,county=county,document_number=doc,site="Tapestry",status='Order Created')
        db.session.add(new_order)
        db.session.commit()
        o_id=new_order.o_id
        _thread.start_new_thread(TAP,(username,password,type,NET_SessionId,__zlcmid,doc,county,state,o_id,))
        return str(o_id)
    except:
        return 'Failed to Get'
    

@app.route('/tapestry_order_check/<o_id>')
def tapestry_order_check(o_id):
    d=Orders.query.filter_by(o_id=o_id).first()
    return str(d.status)


#USLANDRECORS
class Uslandrecord:
    browser, service = None, None

    # Initialise the webdriver with the path to chromedriver.exe
    def __init__(self, driver: str):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('window-size=1920x1080')
        options.add_argument('--disable-dev-shm-usage')
        self.service = Service(driver)
        if browse_params:
            self.browser=webdriver.Chrome()
            # self.browser = webdriver.Chrome(service=self.service)
        else:
            self.browser= webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.browser.maximize_window()

    def open_page(self, url: str):
        self.browser.get(url)

    def close_browser(self):
        self.browser.close()
        
    def add_input(self, by: By, value: str, text: str):
        field = self.browser.find_element(by=by, value=value)
        field.send_keys(text)

    def click_button(self, by: By, value: str):
        button = self.browser.find_element(by=by, value=value)
        button.click()

            
    def search_results(self,document_type:str,DocumentNumber:str,book:str,page:str,o_id):
        print("Entered1")
        a=0
        while(1):
            a=a+1
            # self.browser.get_screenshot_as_file("s/screenshot"+str(a)+".png")
            if a>=1000:
                return "Problem in Getting the Document Server"
            try:
                select = Select(self.browser.find_element(by=By.ID,value='SearchCriteriaName1_DDL_SearchName'))
                break
            except:
                # delete_cache(self.browser)
                print(a)
        time.sleep(1)
        if document_type=="Document Number":
            # select by visible text
            select.select_by_visible_text('Document Search')
            # select.select_by_value('Recorded Land Document Search')
        elif document_type=="Book, Page":
            select.select_by_visible_text('Book Search')
            # select.select_by_value('Recorded Land Book Search')
        a=1
        time.sleep(3)
        if document_type=="Document Number":
            self.add_input(by=By.ID,value='SearchFormEx1_ACSTextBox_Document',text=DocumentNumber)
        elif document_type=="Book, Page":
            print(book,page)
            self.add_input(by=By.ID,value='SearchFormEx1_ACSTextBox_Volume',text=book)
            b=self.browser.find_element(by=By.ID,value='SearchFormEx1_ACSTextBox_Volume').text
            print("STR B",str(b))
            time.sleep(3)
            print("here")
            # pageSource = self.browser.page_source
            # fileToWrite = open("page_source.html", "w")
            # fileToWrite.write(pageSource)
            # fileToWrite.close()
            self.add_input(by=By.ID,value='SearchFormEx1_ACSTextBox_PageNumber',text=page)
        self.click_button(by=By.ID,value='SearchFormEx1_btnSearch')

        try:
            while(1):
                try:
                    self.click_button(by=By.XPATH,value='/html/body/form/div[5]/div[39]/div[1]/div[2]/table/tbody/tr[1]/td/div/div[2]/table/tbody/tr[1]/td[4]/a')
                    break
                except:
                    pass
            time.sleep(2)
            self.click_button(by=By.XPATH,value='/html/body/form/div[5]/div[29]/div/div/table/tbody/tr/td[2]/div/table[1]/tbody/tr/td[3]/table/tbody/tr[2]/td[2]/a')
            time.sleep(2)
        except:
            print('No document Found')
            return False
        
        main_page = self.browser.current_window_handle
        #get instance of first pop up  window
        whandle = self.browser.window_handles[1]

        #switch to pop up window
        self.browser.switch_to.window(whandle)
        self.browser.maximize_window()
        
        
        no_of_pages=self.browser.find_element(by=By.XPATH,value='/html/body/form/div[2]/div[2]/div[2]/table/tbody/tr[1]/td/div/table/tbody/tr/td[2]/table/tbody/tr/td[3]/span')
        no_of_pages=no_of_pages.text.split(sep=' of ')
        no_of_pages=int(no_of_pages[1])
        order=Orders.query.filter_by(o_id=o_id).first() 
        order.no_of_pages=no_of_pages
        db.session.commit()
        # pdf_name=self.browser.find_element(by=By.XPATH,value='/html/body/form/div[6]/table/tbody/tr/td[1]/table/tbody/tr[2]/td/div/span/table/tbody/tr/td/font[1]')
        # pdf_name=pdf_name.text
        # print(no_of_pages,pdf_name)
        #creating a directory to save images
        folder_name = 'images'
        if not os.path.isdir(folder_name):
            os.makedirs(folder_name)
        pdf_images=[]
        folderName = datetime.now().strftime("%d%m%Y%H%M%S")
        imageFolderPath = os.path.join(folder_name, folderName)
        os.makedirs(imageFolderPath)
        
        pdf_path='pdf'
        if not os.path.isdir(pdf_path):
            os.makedirs(pdf_path)
        # imgs=[]
        
        src=[]
        # Image Id ImageViewer1_docImage
        for i in range(0,no_of_pages):
            self.add_input(by=By.XPATH,value='//*[@id="ImageViewer1_TextBox_GoTo"]',text=str(i+1))
            self.click_button(by=By.XPATH,value='//*[@id="ImageViewer1_BtnGoTo"]')
            time.sleep(2)
            self.click_button(by=By.ID,value='ImageViewer1_BtnFitToBest')
            time.sleep(2)
            
            while(1):
                try:
                    img_source=self.browser.find_element(by=By.ID, value='ImageViewer1_docImage')
                    imageURL= img_source.get_attribute('src')
                    # print('Success')
                    # print(imageURL)
                    if 'ZOOM' in imageURL:
                        print(imageURL)
                        break
                except:
                    print('Getting')
                    pass
            try:
                self.download_image(imageURL, imageFolderPath, i)
                print("Downloaded element")
                # print("Here")
                time.sleep(0.05)
            except:
                print("Failed to download")
            # try:    
            #     self.click_button(by=By.ID,value='ImageViewer1_BtnNext')
            # except:
            #     print("Only 1 Page")
        self.close_browser()
        print("Here2")
        #switch to pop up window
        self.browser.switch_to.window(main_page)
        print("Here2")
        
        pdf_name=image_Export_to_PDF(folder_name,imageFolderPath,folderName,pdf_path)
        print("Here2")
        print(pdf_name)
        print(folder_name,imageFolderPath,folderName,pdf_path)
        shutil.rmtree(imageFolderPath)
        return pdf_name
       
    def download_image(self,url, folder_name, num):
        self.browser.get(url)    
        time.sleep(2)
        self.click_button(by=By.XPATH,value='/html/body/img')
        # path=str(num)+".png"
        path=os.path.join(folder_name, str(num)+".png")
        # path1=os.path.join(folder_name, str(num)+"12.png")
        img= self.browser.find_element(by=By.XPATH,value='/html/body/img')
        # img.screenshot(path)
        b64img = self.browser.execute_script(r'''
        var img = document.getElementsByTagName("img")[0];
        var canvas = document.createElement("canvas");
        canvas.width = img.width;
        canvas.height = img.height;
        var ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0);
        var dataURL = canvas.toDataURL("image/png");
        return dataURL.replace(/^data:image\/(png|jpg);base64,/, "");
        ''')

        # Decode from base64, translate to bytes and write to PIL image
        img_png = Image.open(BytesIO(b64decode(b64img)))
        img=self.remove_watermark_usland(img=img_png)
        im_pil = Image.fromarray(img)
        cv2.imwrite(path,img)
        self.browser.back()

    def remove_watermark_usland(self,img):
        img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
        for i in range(len(img)):
            for j in range(len(img[0])):
                if img[i,j] >200:
                    # if img[i,(j-1)]>10 and img[(i-1),j]>10 and img[i,(j+1)]>10 and img[(i+1),j]>10:
                    img[i,j] =255
        maxIntensity = 255.0 # depends on dtype of image data
        # Parameters for manipulating image data
        phi = 1
        theta = 1
        newImage = (maxIntensity/phi)*(img/(maxIntensity/theta))**2
        newImage = array(newImage,dtype=uint8)
        # cv2.imwrite('newImage123.jpg',newImage)
        return newImage
    
    def image_Export_to_PDF(self,dir_name,images_path, pdf_Name,pdf_path):
        print("image_Export_to_PDF")
        imgs=[]
        pdffilename = pdf_path + "/" + pdf_Name + '.pdf'
        list_of_files = filter(lambda x: os.path.isfile(os.path.join(dir_name, x)),
                            os.listdir(dir_name))
        # Sort list of files based on last modification time in ascending order
        list_of_files = sorted(list_of_files, key=lambda x: os.path.getmtime(os.path.join(dir_name, x)))
        for filename in list_of_files:
            print(filename)
        # for filename in list_of_files:
        #     try:
        #         img=Image.open(filename,mode="r")
        #         imgs.append(img)
        #     except:
        #         print("ohh noo")
        #         pass
        for filename in os.listdir(images_path):
            f = os.path.join(images_path, filename)
            img=Image.open(f,mode="r")
            imgs.append(img)
        if len(imgs)==1:
            im=imgs[0]
            im.save(pdffilename)
        else:
            im=imgs[0]
            imgs.pop(0)
            im.save(pdffilename, save_all=True, append_images=imgs)
        return pdffilename

#DOXPOPIN
def doxpopsaveimages(inputUsername,inputPassword, inputDocumentType, inputcounty_name, inputDocumentNumber, inputBook,inputPage,inputSelectRegion,o_id):
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        print("HERE")
        def watermarkRemoval(imagePath):
            img = cv2.imread(imagePath, 0)
            for i in range(len(img)):
                # print(type(i))
                for j in range(len(img[0])):
                    # print(type(img[j]),img[j],j)
                    if img[i, j] == 0:
                        if img[i, (j - 1)] >= 55 and img[(i - 1), j] >= 55 and img[i, (j + 1)] >= 55 and img[
                            (i + 1), j] >= 55:
                            img[i, j] = 255
            maxIntensity = 255.0  # depends on dtype of image data

            # Parameters for manipulating image data
            phi = 1
            theta = 1

            newImage = (maxIntensity / phi) * (img / (maxIntensity / theta)) ** 2
            newImage = array(newImage, dtype=uint8)
            cv2.imwrite(imagePath, newImage)
            return newImage

        def joiningimages(pageimagePaths, pageNumber):
            # print("joiningimages")
            images = [PIL.Image.open(x) for x in pageimagePaths]
            widths = 0
            size = []
            heights = 0
            for i in images:
                w, h = i.size
                size.append(i.size)
                heights += h
                widths += w

            widths = int(widths / 2)
            heights = int(heights / 2)
            # print("before "+str(heights) + "......." + str(widths))
            output_Image = PIL.Image.new('RGB', (widths, heights))

            x_offset = 0
            y_offset = 0

            for num in range(0, 4):
                # checking condition
                if num % 2 != 0:  # odd number 1,3
                    output_Image.paste(images[num], (y_offset, 700))
                    y_offset += images[num].size[0]
                    # print("y offeet  " + str(y_offset))

                else:  # even number 0,2
                    output_Image.paste(images[num], (x_offset, 0))
                    x_offset += images[num].size[0]
                    # print("x offeet  " + str(x_offset))
            # print(joinedImagePath)

            output_Image.save(joinedImagePath + '\\' + str(pageNumber) + '.png')
            output_Image = PIL.Image.fromarray(watermarkRemoval(joinedImagePath + '\\' + str(pageNumber) + '.png'))
            pdf_image.append(output_Image)

        def image_Export_to_PDF(dir_name, pdf_Name):
            print("image_Export_to_PDF")
            # dir_name = r"F:\poc\folderTest"
            # Get list of all files only in the given directory
            list_of_files = filter(lambda x: os.path.isfile(os.path.join(dir_name, x)),
                                os.listdir(dir_name))
            # Sort list of files based on last modification time in ascending order
            list_of_files = sorted(list_of_files, key=lambda x: os.path.getmtime(os.path.join(dir_name, x)))
            # Iterate over sorted list of files and print file path
            # along with last modification time of file

            imagePaths = []

            for file_name in list_of_files:
                file_path = os.path.join(dir_name, file_name)
                imagePaths.append(file_path)
            pageNumber = 1
            separate_image = []

            pdffilename = parent_dir + "/" + pdf_Name + '.pdf'

            if len(imagePaths) % 4 == 0:
                for num in range(0, len(imagePaths)):
                    separate_image.append(imagePaths[num])
                    # print(imagePaths[num])
                    if (num + 1) % 4 == 0:
                        joiningimages(separate_image, pageNumber)
                        separate_image = []
                        pageNumber += 1
                pdf_image_firtPage = pdf_image[0]
                pdf_image.pop(0)

                pdf_image_firtPage.save(pdffilename, save_all=True, append_images=pdf_image)
                # print("Exported to PDF: " + pdffilename)
                # Label(r, text= "Exported to PDF: " + pdffilename, font=('Poppins bold', 25)).pack(pady=20)
            else:
                print("Error: Number of files are not in correct count. Please change and try agains")
            return pdffilename
        
        
        # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        # driver = webdriver.Chrome("/Applications/Google Chrome")
        
        if browse_params:
            driver=webdriver.Chrome()
            # self.browser = webdriver.Chrome(service=self.service)
        else:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        # driver = webdriver.Chrome(executable_path=r"F:\Webdriver\chromedriver.exe")
        # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get("https://www.doxpop.com/prod/in/")
        print("HEREEE")
        documentNumber=None
        username = driver.find_element(By.ID, "header-username-input")
        password = driver.find_element(By.ID, "header-password-input")
        # doxpopUsername = 'dinesshapp@gmail.com'
        # doxpopPassword = 'Mision1!'

        username.send_keys(inputUsername)  # add username here
        password.send_keys(inputPassword)  # add password here

        driver.find_element(By.NAME, "login_button").click()
        time.sleep(2)
        try:
            # selecting dropdown
            select = Select(driver.find_element(By.ID, 'recorder-search-by'))
            select.select_by_visible_text(inputDocumentType)
        except:
            message_final='Incorrect Username or Password'
            print(message_final)
            return message_final
        
        try:
            time.sleep(1)

            # selecting dropdown
            select = Select(driver.find_element(By.ID, 'recorder-search-by'))
            select.select_by_visible_text(inputDocumentType)
            print("Hello")
            
            

            # # county_name
            # if inputDocumentType=="Document Party":
            #     county_name = driver.find_element(By.ID, "app_input_uid_7")
            #     county_name.send_keys(inputcounty_name)
            #     exportpdfname = inputcounty_name

            #documentNumber
            if inputDocumentType == "Document Number":
                documentNumber = driver.find_element(By.ID, "v-input-wrapper__input-uid_7")
                documentNumber.send_keys(inputDocumentNumber)
                exportpdfname = inputDocumentNumber

            if inputDocumentType == "Book, Page":
                #Book
                bookName = driver.find_element(By.ID, "v-input-wrapper__input-uid_16")
                bookName.send_keys(inputBook)
                #Page
                pageName = driver.find_element(By.ID, "v-input-wrapper__input-uid_17")
                pageName.send_keys(inputPage)
                exportpdfname = "Book-"+inputBook+",Page-"+inputPage


            select = Select(driver.find_element(By.ID, 'recorder-search-region'))
            select.select_by_visible_text(inputSelectRegion)
            # type="submit"
            # driver.find_element_by_xpath('(.//button[@type="submit"])[5]').click()
            print("Hello")
            driver.find_element(By.XPATH, '//*[@id="page__body__main"]/div[1]/div[2]/section/div/div/div[1]/form/div[5]/div[2]/button').click()
            time.sleep(3)
            try:
                try:
                    driver.find_element(By.XPATH, './/a[@title="preview and purchase document pages"]')
                except:
                    message_final='You have entered incorrect Document Number or Book/Page Number'
                    print(message_final)
                    return message_final
                print("Hello")
                county_name1= driver.find_element(By.XPATH, '//*[@id="page__body__main"]/div[4]/table/tbody/tr/td[2]')
                county_name1=county_name1.text
                print(county_name1)
                doc_number= driver.find_element(By.XPATH, '//*[@id="page__body__main"]/div[4]/table/tbody/tr/td[1]/a')
                doc_number=doc_number.text
                print("Hello")
                global document_number
                document_number=doc_number
                date_mor= driver.find_element(By.XPATH, '//*[@id="page__body__main"]/div[4]/table/tbody/tr/td[3]')
                date_mor=date_mor.text
                type_mor=driver.find_element(By.XPATH, '//*[@id="page__body__main"]/div[4]/table/tbody/tr/td[4]')
                type_mor=type_mor.text
                partyName= driver.find_element(By.XPATH, '//*[@id="page__body__main"]/div[4]/table/tbody/tr/td[5]/ul/li[1]/span')
                partyName=partyName.text
                
                driver.find_element(By.XPATH, './/a[@title="preview and purchase document pages"]').click()

                time.sleep(5)

                # d = driver.find_element(By.XPATH,'(.//*[@class="document-image-chunk"])[2]').get_attribute("style")

                # print(d)
                response = Selector(text=driver.page_source)

                s = response.xpath('.//*[@class="document-image-chunk"]/@style').re(r'url\("([\S]+)"\)')
                webPageNumber = driver.find_element(By.ID, "document-image-stats").text.split('/')[1].split('(')[0].strip()
                # webPageNumber = int(webPageNumber)
                print("page", webPageNumber)
                order=Orders.query.filter_by(o_id=o_id).first() 
                order.no_of_pages=str(webPageNumber)
                db.session.commit()
                print(s)

                time.sleep(2)
                driver.close()
                
                pdf_image = []
                folderName = datetime.now().strftime("%d%m%Y%H%M%S")
                parent_dir = "Generated_PDF" 
                imageFolderPath = os.path.join(parent_dir, folderName)
                joinedImagePath = os.path.join(imageFolderPath, 'Output')
                os.makedirs(imageFolderPath)
                os.makedirs(joinedImagePath)
                images_Path = imageFolderPath + "/DisplayImage"

                document_url = s[0]
                documentId = ((document_url.split("?")[1]).split("&")[0]).split("=")[1]
                userID = ((document_url.split("?")[1]).split("&")[1]).split("=")[1]
                # totalPages = int(input("Enter Page No. : "))
                print(documentId)
                # userID="707057"
                page = ""
                x = ""
                y = ""
                # accessCode="qxiGoR%2BsAErPnMrpg34d%2FVkPjTsvWwHr%2FIcIRt35PGkxG1%2Bf9t2SNYtHu87wj%2FIa"
                if ("getThumbnail") in document_url:
                    accessCode = ((document_url.split("?")[1]).split("&")[4]).split("=")[1]
                else:
                    accessCode = ((document_url.split("?")[1]).split("&")[6]).split("=")[1]

                mainURL1 = "https://www.doxpop.com/images/prod/DisplayImage?"

                mainURL2 = "documentId="

                mainURL3 = "userId="

                mainURL4 = "action=getTile&"

                mainURL5 = "page="

                mainURL6 = "x="

                mainURL7 = "y="

                mainURL8 = "accessCode="
                for pagenumber in range(1, int(webPageNumber) + 1):
                    # print("page="+str(i))
                    for num in range(0, 4):
                        # checking condition

                        x = str(int(num / 2))
                        y = str(num % 2)
                        genrated_URL = mainURL1 + mainURL2 + documentId + "&" + mainURL3 + userID + "&" + mainURL4 + mainURL5 + str(
                            pagenumber) + "&" + mainURL6 + x + "&" + mainURL7 + y + "&" + mainURL8 + accessCode
                        print(genrated_URL)
                        # filename = images_Path + str(pagenumber) + str(num) + ".png"
                        filename = images_Path + str(pagenumber) + x + y + ".png"
                        # print(URL)
                        response = wget.download(genrated_URL, filename)
                        # savImages(genrated_URL, filename)

                # for url in s:
                #     # print(url,type(s))
                #     URL = f"https://www.doxpop.com/{url}"
                #     print(URL)
                #     pagenumber = ((url.split("page=")[1]).split("&")[0])
                #     x = ((url.split("x=")[1]).split("&")[0])
                #     y = ((url.split("y=")[1]).split("&")[0])
                #
                #     filename = images_Path + pagenumber + x +y+ ".png"
                #     # print(URL)
                #     response = wget.download(URL, filename)
                # print("saved")
                #exportpdfname
                print("OK")
                pdfName = image_Export_to_PDF(imageFolderPath, exportpdfname)
                print("Here")
                file = open(pdfName, "rb")
                # upload=data_pdf(email=user_me,pages=webPageNumber,county_name=county_name1,date=date_mor,type=type_mor,document_number=doc_number,party_name=partyName,pdf=file.read(),date_created=datetime.utcnow(),user_status='FALSE')
                # db.session.add(upload)
                # db.session.commit ()
                # print(imageFolderPath)
                # shutil.rmtree(parent_dir)
                shutil.rmtree(joinedImagePath)
                shutil.rmtree(imageFolderPath)
                
                return pdfName
            except:
                print("No Book_found")
                return 'No Book found'
        except:
            print("Username and password are incorrect")
            return 'No Search Tokens for this Username'
    except:
        driver.close()
        return 'Technical Error Occurred'


#Land Mark
class Land_mark:
    browser, service = None, None

    # Initialise the webdriver with the path to chromedriver.exe
    def __init__(self, driver: str):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('window-size=1920x1080')
        options.add_argument('--disable-dev-shm-usage')
        self.service = Service(driver)
        if browse_params:
            self.browser=webdriver.Chrome()
            # self.browser = webdriver.Chrome(service=self.service)
        else:
            self.browser= webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.browser.maximize_window()
        

    def open_page(self, url: str):
        self.browser.get(url)

    def close_browser(self):
        self.browser.close()
        
    def add_input(self, by: By, value: str, text: str):
        field = self.browser.find_element(by=by, value=value)
        field.send_keys(text)

    def click_button(self, by: By, value: str):
        button = self.browser.find_element(by=by, value=value)
        button.click()
        
    def search_results(self,book: str,page: str,DocumentNumber: str,document_type: str,o_id):
        #Document Number
        if document_type=="Document Number":
            try:
                self.click_button(by=By.XPATH,value='//*[@id="bodySection"]/div/div/div[3]/div[3]/div[2]/a/img')
            except:
                self.click_button(by=By.XPATH,value='/html/body/div[6]/div/div/div[3]/div/div[7]/a/img')

        #Book and Page
        elif document_type=="Book, Page":
            try:
                self.click_button(by=By.XPATH,value='//*[@id="bodySection"]/div/div/div[3]/div[2]/div[1]/a/img')
            except:
                self.click_button(by=By.XPATH,value='/html/body/div[6]/div/div/div[3]/div/div[3]/a/img')


        a=0
        while(1):
            a=a+1
            if a>100:
                break
            try:
                #Accept Button
                self.click_button(by=By.XPATH,value='//*[@id="idAcceptYes"]')
                break
            except:
                pass
            
        time.sleep(0.5)
        #Book and Page
        if document_type=="Book, Page":
            self.add_input(by=By.ID,value='book',text=book)
            self.add_input(by=By.ID,value='page',text=page)
            self.add_input(by=By.ID,value='page',text=Keys.ENTER)


        #Document Number
        if document_type=="Document Number":
            self.add_input(by=By.ID,value='instrumentNumber',text=DocumentNumber)
            self.add_input(by=By.ID,value='instrumentNumber',text=Keys.ENTER)
            
        a=0
        while(1):
            a=a+1
            if a>1000:
                print("Breaked")
                break
            try:
                self.browser.find_element(by=By.XPATH,value='//*[@id="resultsTable"]/tbody')
                break
            except:
                pass
        try:
            self.click_button(by=By.XPATH,value='/html/body/div[6]/div/div/div/div[2]/div/div[3]/div/div/div[3]/table/tbody/tr/td/div/table/tbody/tr[1]/td[6]')
        except:
            self.click_button(by=By.XPATH,value='/html/body/div[6]/div/div/div/div[2]/div/div[3]/div[1]/div/div[3]/table/tbody/tr/td/div/div[8]/table/tbody/tr[1]/td[7]')

        while(1):
            try:
                page=self.browser.find_element(by=By.XPATH,value='/html/body/div[7]/div/div[2]/div[2]/div/div[1]/div[3]/span[3]').text
                if page!='':
                    break
            except:
                pass
        pages=''
        for i in page:
            if i.isnumeric():
                pages=pages+i

        print("No. of Pages : ",pages)
        
        order=Orders.query.filter_by(o_id=o_id).first() 
        order.no_of_pages=pages
        db.session.commit()
    
        folder_name = 'images'
        if not os.path.isdir(folder_name):
            os.makedirs(folder_name)
        pdf_images=[]
        folderName = datetime.now().strftime("%d%m%Y%H%M%S")
        imageFolderPath = os.path.join(folder_name, folderName)
        os.makedirs(imageFolderPath)

        pdf_path='pdf'
        if not os.path.isdir(pdf_path):
            os.makedirs(pdf_path)
            
        for i in range(int(pages)):
            time.sleep(2)
            image=self.browser.find_element(by=By.XPATH,value='//*[@id="documentImageInner"]')
            image_url=image.get_attribute('src')
            print(image_url)
            # if i!=int(pages)-1:
            #     self.browser.execute_script("document.getElementById('nextDocumentImageButton').style.display='';")
            #     self.click_button(by=By.XPATH,value='//*[@id="nextDocumentImageButton"]')
            # script='window.open("https://www.google.com");'
            script='window.open("'+image_url+'");'
            self.browser.execute_script(script)
            self.browser.switch_to.window(self.browser.window_handles[1])
            print('Loading')
            # Load a page 
            # self.open_page(image_url)
            self.click_button(by=By.TAG_NAME,value='img')
            b64img = self.browser.execute_script(r'''
                            var img = document.getElementsByTagName("img")[0];
                            var canvas = document.createElement("canvas");
                            canvas.width = img.width;
                            canvas.height = img.height;
                            var ctx = canvas.getContext("2d");
                            ctx.drawImage(img, 0, 0);
                            var dataURL = canvas.toDataURL("image/png");
                            return dataURL.replace(/^data:image\/(png|jpg);base64,/, "");
                            ''')
            # close the tab
            self.browser.close()
            self.browser.switch_to.window(self.browser.window_handles[0])
            # Decode from base64, translate to bytes and write to PIL image

            filename=imageFolderPath+'/'+str(i)+".png"
            img_png = Image.open(BytesIO(b64decode(b64img)))
            img_png.save(filename)
            # response = wget.download(image_url, filename)
            if i!=int(pages)-1:
                self.browser.execute_script("document.getElementById('nextDocumentImageButton').style.display='';")
                self.click_button(by=By.XPATH,value='//*[@id="nextDocumentImageButton"]')
        pdf_name=image_Export_to_PDF(folder_name,imageFolderPath,folderName,pdf_path)
        shutil.rmtree(imageFolderPath)
        return pdf_name



        


        

#Record Search Hub
class Record_hub:
    browser, service = None, None

    # Initialise the webdriver with the path to chromedriver.exe
    def __init__(self, driver: str):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('window-size=1920x1080')
        options.add_argument('--disable-dev-shm-usage')
        self.service = Service(driver)
        if browse_params:
            self.browser=webdriver.Chrome()
            # self.browser = webdriver.Chrome(service=self.service)
        else:
            self.browser= webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.browser.maximize_window()
        self.conneticut_counties=['Ansonia, CT', 'Avon, CT', 'Berlin, CT', 'Bethany, CT', 'Bethel, CT', 'Bolton, CT', 'Bozrah, CT', 'Branford, CT', 'Bridgewater, CT', 'Brookfield, CT', 'Burlington, CT', 'Canaan, CT', 'Canton, CT', 'Chaplin, CT', 'Chester, CT', 'Clinton, CT', 'Columbia, CT', 'Danbury, CT', 'Darien, CT', 'East Granby, CT', 'Eastford, CT', 'Ellington, CT', 'Essex, CT', 'Farmington, CT', 'Granby, CT', 'Griswold, CT', 'Groton, CT', 'Guilford, CT', 'Hartland, CT', 'Harwinton, CT', 'Manchester, CT', 'Mansfield, CT', 'Marlborough, CT', 'Montville, CT', 'Morris, CT', 'New Fairfield, CT', 'New Hartford, CT', 'New Milford, CT', 'North Branford, CT', 'North Canaan, CT', 'North Haven, CT', 'Old Lyme, CT', 'Old Saybrook, CT', 'Oxford, CT', 'Plainville, CT', 'Plymouth, CT', 'Pomfret, CT', 'Preston, CT', 'Simsbury, CT', 'Somers, CT', 'Southington, CT', 'Stafford, CT', 'Stonington, CT', 'Suffield, CT', 'Thomaston, CT', 'Trumbull, CT', 'Union, CT', 'Westport, CT', 'Willington, CT', 'Wilton, CT', 'Winchester, CT', 'Windsor Locks, CT', 'Wolcott, CT']
        self.conneticut_counties_urls=['https://recordhub.cottsystems.com/AnsoniaCT/Portal/SearchSites/Plan/?SubscriptionId=1148',
        'https://recordhub.cottsystems.com/AvonCT/Portal/SearchSites/Plan/?SubscriptionId=1182',
        'https://recordhub.cottsystems.com/BerlinCT/Portal/SearchSites/Plan/?SubscriptionId=1209',
        'https://recordhub.cottsystems.com/BethanyCT/Portal/SearchSites/Plan/?SubscriptionId=1158',
        'https://recordhub.cottsystems.com/BethelCT/Portal/SearchSites/Plan/?SubscriptionId=1212',
        'https://recordhub.cottsystems.com/BoltonCT/Portal/SearchSites/Plan/?SubscriptionId=1190',
        'https://recordhub.cottsystems.com/BozrahCT/Portal/SearchSites/Plan/?SubscriptionId=1184',
        'https://recordhub.cottsystems.com/BranfordCT/Portal/SearchSites/Plan/?SubscriptionId=1219',
        'https://recordhub.cottsystems.com/BridgewaterCT/Portal/SearchSites/Plan/?SubscriptionId=1198',
        'https://recordhub.cottsystems.com/BrookfieldCT/Portal/SearchSites/Plan/?SubscriptionId=1236',
        'https://recordhub.cottsystems.com/BurlingtonCT/Portal/SearchSites/Plan/?SubscriptionId=1174',
        'https://recordhub.cottsystems.com/CanaanCT/Portal/SearchSites/Plan/?SubscriptionId=1161',
        'https://recordhub.cottsystems.com/CantonCT/Portal/SearchSites/Plan/?SubscriptionId=1204',
        'https://recordhub.cottsystems.com/ChaplinCT/Portal/SearchSites/Plan/?SubscriptionId=1187',
        'https://recordhub.cottsystems.com/ChesterCT/Portal/SearchSites/Plan/?SubscriptionId=1163',
        'https://recordhub.cottsystems.com/ClintonCT/Portal/SearchSites/Plan/?SubscriptionId=1154',
        'https://recordhub.cottsystems.com/ColumbiaCT/Portal/SearchSites/Plan/?SubscriptionId=1240',
        'https://recordhub.cottsystems.com/DanburyCT/Portal/SearchSites/Plan/?SubscriptionId=1293',
        'https://recordhub.cottsystems.com/DarienCT/Portal/SearchSites/Plan/?SubscriptionId=1637',
        'https://recordhub.cottsystems.com/EastGranbyCT/Portal/SearchSites/Plan/?SubscriptionId=1168',
        'https://recordhub.cottsystems.com/EastfordCT/Portal/SearchSites/Plan/?SubscriptionId=1176',
        'https://recordhub.cottsystems.com/EllingtonCT/Portal/SearchSites/Plan/?SubscriptionId=1159',
        'https://recordhub.cottsystems.com/EssexCT/Portal/SearchSites/Plan/?SubscriptionId=1217',
        'https://recordhub.cottsystems.com/FarmingtonCT/Portal/SearchSites/Plan/?SubscriptionId=1207',
        'https://recordhub.cottsystems.com/GranbyCT/Portal/SearchSites/Plan/?SubscriptionId=1205',
        'https://recordhub.cottsystems.com/GriswoldCT/Portal/SearchSites/Plan/?SubscriptionId=1173',
        'https://recordhub.cottsystems.com/GrotonCT/Portal/SearchSites/Plan/?SubscriptionId=1599',
        'https://recordhub.cottsystems.com/GuilfordCT/Portal/SearchSites/Plan/?SubscriptionId=1155',
        'https://recordhub.cottsystems.com/HartlandCT/Portal/SearchSites/Plan/?SubscriptionId=1169',
        'https://recordhub.cottsystems.com/HarwintonCT/Portal/SearchSites/Plan/?SubscriptionId=1238',
        'https://recordhub.cottsystems.com/ManchesterCT/Portal/SearchSites/Plan/?SubscriptionId=1220',
        'https://recordhub.cottsystems.com/MansfieldCT/Portal/SearchSites/Plan/?SubscriptionId=1194',
        'https://recordhub.cottsystems.com/MarlboroughCT/Portal/SearchSites/Plan/?SubscriptionId=1191',
        'https://recordhub.cottsystems.com/MontvilleCT/Portal/SearchSites/Plan/?SubscriptionId=1208',
        'https://recordhub.cottsystems.com/MorrisCT/Portal/SearchSites/Plan/?SubscriptionId=1188',
        'https://recordhub.cottsystems.com/NewFairfieldCT/Portal/SearchSites/Plan/?SubscriptionId=1866',
        'https://recordhub.cottsystems.com/NewHartfordCT/Portal/SearchSites/Plan/?SubscriptionId=1167',
        'https://recordhub.cottsystems.com/NewMilfordCT/Portal/SearchSites/Plan/?SubscriptionId=1171',
        'https://recordhub.cottsystems.com/NorthBranfordCT/Portal/SearchSites/Plan/?SubscriptionId=1164',
        'https://recordhub.cottsystems.com/NorthCanaanCT/Portal/SearchSites/Plan/?SubscriptionId=1185',
        'https://recordhub.cottsystems.com/NorthHavenCT/Portal/SearchSites/Plan/?SubscriptionId=1193',
        'https://recordhub.cottsystems.com/OldLymeCT/Portal/SearchSites/Plan/?SubscriptionId=1183',
        'https://recordhub.cottsystems.com/OldSaybrookCT/Portal/SearchSites/Plan/?SubscriptionId=1177',
        'https://recordhub.cottsystems.com/OxfordCT/Portal/SearchSites/Plan/?SubscriptionId=1178',
        'https://recordhub.cottsystems.com/PlainvilleCT/Portal/SearchSites/Plan/?SubscriptionId=1157',
        'https://recordhub.cottsystems.com/PlymouthCT/Portal/SearchSites/Plan/?SubscriptionId=1201',
        'https://recordhub.cottsystems.com/PomfretCT/Portal/SearchSites/Plan/?SubscriptionId=1197',
        'https://recordhub.cottsystems.com/PrestonCT/Portal/SearchSites/Plan/?SubscriptionId=1256',
        'https://recordhub.cottsystems.com/SimsburyCT/Portal/SearchSites/Plan/?SubscriptionId=1221',
        'https://recordhub.cottsystems.com/SomersCT/Portal/SearchSites/Plan/?SubscriptionId=1160',
        'https://recordhub.cottsystems.com/SouthingtonCT/Portal/SearchSites/Plan/?SubscriptionId=1222',
        'https://recordhub.cottsystems.com/StaffordCT/Portal/SearchSites/Plan/?SubscriptionId=1166',
        'https://recordhub.cottsystems.com/StoningtonCT/Portal/SearchSites/Plan/?SubscriptionId=1210',
        'https://recordhub.cottsystems.com/SuffieldCT/Portal/SearchSites/Plan/?SubscriptionId=1181',
        'https://recordhub.cottsystems.com/ThomastonCT/Portal/SearchSites/Plan/?SubscriptionId=1180',
        'https://recordhub.cottsystems.com/TrumbullCT/Portal/SearchSites/Plan/?SubscriptionId=1682',
        'https://recordhub.cottsystems.com/UnionCT/Portal/SearchSites/Plan/?SubscriptionId=1153',
        'https://recordhub.cottsystems.com/WestportCT/Portal/SearchSites/Plan/?SubscriptionId=1218',
        'https://recordhub.cottsystems.com/WillingtonCT/Portal/SearchSites/Plan/?SubscriptionId=1165',
        'https://recordhub.cottsystems.com/WiltonCT/Portal/SearchSites/Plan/?SubscriptionId=1589',
        'https://recordhub.cottsystems.com/WinchesterCT/Portal/SearchSites/Plan/?SubscriptionId=1170',
        'https://recordhub.cottsystems.com/WindsorLocksCT/Portal/SearchSites/Plan/?SubscriptionId=1152',
        'https://recordhub.cottsystems.com/WolcottCT/Portal/SearchSites/Plan/?SubscriptionId=1216']
        self.vermont_counties=['Alburgh, VT', 'Bennington, VT', 'Bolton, VT', 'Bradford, VT', 'Brandon, VT', 'Bridport, VT', 'Bristol, VT', 'Cabot, VT', 'Calais, VT', 'Chittenden, VT', 'Concord, VT', 'Cornwall, VT', 'Danville, VT', 'Dover, VT', 'Elmore, VT', 'Fairlee, VT', 'Glover, VT', 'Grafton, VT', 'Groton, VT', 'Hardwick, VT', 'Hartland, VT', 'Huntington, VT', 'Ira, VT', 'Killington, VT', 'Leicester, VT', 'Lunenburg, VT', 'Manchester, VT', 'Marlboro, VT', 'Mendon, VT', 'Mount Holly, VT', 'Newfane, VT', 'Northfield, VT', 'Norwich, VT', 'Orange, VT', 'Panton, VT', 'Poultney, VT', 'Pownal, VT', 'Putney, VT', 'Randolph, VT', 'Salisbury, VT', 'Shaftsbury, VT', 'Sharon, VT', 'South Hero, VT', 'St Albans, VT', 'Stowe, VT', 'Thetford, VT', 'Townshend, VT', 'Troy, VT', 'Vershire, VT', 'Walden, VT', 'Wallingford, VT', 'Weathersfield, VT', 'West Rutland, VT', 'Weybridge, VT', 'Whitingham, VT']
        self.vermont_counties_urls=['https://recordhub.cottsystems.com/AlburghVT/Portal/SearchSites/Plan/?SubscriptionId=1467',
        'https://recordhub.cottsystems.com/BenningtonVT/Portal/SearchSites/Plan/?SubscriptionId=1696',
        'https://recordhub.cottsystems.com/BoltonVT/Portal/SearchSites/Plan/?SubscriptionId=1765',
        'https://recordhub.cottsystems.com/BradfordVT/Portal/SearchSites/Plan/?SubscriptionId=1838',
        'https://recordhub.cottsystems.com/BrandonVT/Portal/SearchSites/Plan/?SubscriptionId=1002',
        'https://recordhub.cottsystems.com/BridportVT/Portal/SearchSites/Plan/?SubscriptionId=1620',
        'https://recordhub.cottsystems.com/BristolVT/Portal/SearchSites/Plan/?SubscriptionId=598',
        'https://recordhub.cottsystems.com/CabotVT/Portal/SearchSites/Plan/?SubscriptionId=1640',
        'https://recordhub.cottsystems.com/CalaisVT/Portal/SearchSites/Plan/?SubscriptionId=1047',
        'https://recordhub.cottsystems.com/ChittendenVT/Portal/SearchSites/Plan/?SubscriptionId=1449',
        'https://recordhub.cottsystems.com/ConcordVT/Portal/SearchSites/Plan/?SubscriptionId=1425',
        'https://recordhub.cottsystems.com/CornwallVT/Portal/SearchSites/Plan/?SubscriptionId=1443',
        'https://recordhub.cottsystems.com/DanvilleVT/Portal/SearchSites/Plan/?SubscriptionId=1300',
        'https://recordhub.cottsystems.com/DoverVT/Portal/SearchSites/Plan/?SubscriptionId=1697',
        'https://recordhub.cottsystems.com/ElmoreVT/Portal/SearchSites/Plan/?SubscriptionId=1354',
        'https://recordhub.cottsystems.com/FairleeVT/Portal/SearchSites/Plan/?SubscriptionId=1056',
        'https://recordhub.cottsystems.com/GloverVT/Portal/SearchSites/Plan/?SubscriptionId=1348',
        'https://recordhub.cottsystems.com/GraftonVT/Portal/SearchSites/Plan/?SubscriptionId=1410',
        'https://recordhub.cottsystems.com/GrotonVT/Portal/SearchSites/Plan/?SubscriptionId=1392',
        'https://recordhub.cottsystems.com/HardwickVT/Portal/SearchSites/Plan/?SubscriptionId=1306',
        'https://recordhub.cottsystems.com/HartlandVT/Portal/SearchSites/Plan/?SubscriptionId=1398',
        'https://recordhub.cottsystems.com/HuntingtonVT/Portal/SearchSites/Plan/?SubscriptionId=1455',
        'https://recordhub.cottsystems.com/IraVT/Portal/SearchSites/Plan/?SubscriptionId=1723',
        'https://recordhub.cottsystems.com/KillngtonVT/Portal/SearchSites/Plan/?SubscriptionId=1141',
        'https://recordhub.cottsystems.com/LeicesterVT/Portal/SearchSites/Plan/?SubscriptionId=1404',
        'https://recordhub.cottsystems.com/LunenburgVT/Portal/SearchSites/Plan/?SubscriptionId=1272',
        'https://recordhub.cottsystems.com/ManchesterVT/Portal/SearchSites/Plan/?SubscriptionId=1020',
        'https://recordhub.cottsystems.com/MarlboroVT/Portal/SearchSites/Plan/?SubscriptionId=1664',
        'https://recordhub.cottsystems.com/MendonVT/Portal/SearchSites/Plan/?SubscriptionId=1362',
        'https://recordhub.cottsystems.com/MountHollyVT/Portal/SearchSites/Plan/?SubscriptionId=1368',
        'https://recordhub.cottsystems.com/NewfaneVT/Portal/SearchSites/Plan/?SubscriptionId=993',
        'https://recordhub.cottsystems.com/NorthfieldVT/Portal/SearchSites/Plan/?SubscriptionId=1431',
        'https://recordhub.cottsystems.com/NorwichVT/Portal/SearchSites/Plan/?SubscriptionId=1068',
        'https://recordhub.cottsystems.com/OrangeVT/Portal/SearchSites/Plan/?SubscriptionId=1705',
        'https://recordhub.cottsystems.com/PantonVT/Portal/SearchSites/Plan/?SubscriptionId=1753',
        'https://recordhub.cottsystems.com/PoultneyVT/Portal/SearchSites/Plan/?SubscriptionId=1086',
        'https://recordhub.cottsystems.com/PownalVT/Portal/SearchSites/Plan/?SubscriptionId=1437',
        'https://recordhub.cottsystems.com/PutneyVT/Portal/SearchSites/Plan/?SubscriptionId=1419',
        'https://recordhub.cottsystems.com/RandolphVT/Portal/SearchSites/Plan/?SubscriptionId=1008',
        'https://recordhub.cottsystems.com/SalisburyVT/Portal/SearchSites/Plan/?SubscriptionId=1652',
        'https://recordhub.cottsystems.com/ShaftsburyVT/Portal/SearchSites/Plan/?SubscriptionId=1658',
        'https://recordhub.cottsystems.com/SharonVT/Portal/SearchSites/Plan/?SubscriptionId=1685',
        'https://recordhub.cottsystems.com/SouthHeroVT/Portal/SearchSites/Plan/?SubscriptionId=1336',
        'https://recordhub.cottsystems.com/StAlbansVT/Portal/SearchSites/Plan/?SubscriptionId=1101',
        'https://recordhub.cottsystems.com/StoweVT/Portal/SearchSites/Plan/?SubscriptionId=973',
        'https://recordhub.cottsystems.com/ThetfordVT/Portal/SearchSites/Plan/?SubscriptionId=1107',
        'https://recordhub.cottsystems.com/TownshendVT/Portal/SearchSites/Plan/?SubscriptionId=1380',
        'https://recordhub.cottsystems.com/TroyVT/Portal/SearchSites/Plan/?SubscriptionId=1759',
        'https://recordhub.cottsystems.com/VershireVT/Portal/SearchSites/Plan/?SubscriptionId=1480',
        'https://recordhub.cottsystems.com/WaldenVT/Portal/SearchSites/Plan/?SubscriptionId=1386',
        'https://recordhub.cottsystems.com/WallingfordVT/Portal/SearchSites/Plan/?SubscriptionId=1374',
        'https://recordhub.cottsystems.com/WeathersfieldVT/Portal/SearchSites/Plan/?SubscriptionId=1113',
        'https://recordhub.cottsystems.com/WestRutlandVT/Portal/SearchSites/Plan/?SubscriptionId=1122',
        'https://recordhub.cottsystems.com/WeybridgeVT/Portal/SearchSites/Plan/?SubscriptionId=1729',
        'https://recordhub.cottsystems.com/WhitinghamVT/Portal/SearchSites/Plan/?SubscriptionId=1473']

    def open_page(self, url: str):
        self.browser.get(url)

    def close_browser(self):
        self.browser.close()
        
    def add_input(self, by: By, value: str, text: str):
        field = self.browser.find_element(by=by, value=value)
        field.send_keys(text)

    def click_button(self, by: By, value: str):
        button = self.browser.find_element(by=by, value=value)
        button.click()
    
    def login(self, username: str, password: str):
        #login
        self.click_button(by=By.XPATH,value='/html/body/div[1]/div[2]/ul/li[4]/a')
        self.add_input(by=By.ID,value='UserName',text=username)
        self.add_input(by=By.ID,value='Password',text=password)
        self.click_button(by=By.ID,value='submit')
        time.sleep(1)
    
    def logout(self):
        self.click_button(by=By.XPATH,value='//*[@id="profileName"]')
        time.sleep(0.5)
        self.click_button(by=By.CSS_SELECTOR,value='#logoutForm > ul > li.dropdown.open > ul > li:nth-child(3) > a')
        
    def county_link(self, county: str):
        county_cleaned=county.replace(" ", "")
        county_cleaned=county_cleaned.replace(",", "")
        search_link='https://recordhub.cottsystems.com/'+str(county_cleaned)+'/Search/Records'
        return search_link
    
    def get_cart_connecticut(self):
        #For Making Connecticut Counties in cart
        for x in self.conneticut_counties_urls:
            self.open_page(x)
            while(1):
                try:
                    self.click_button(by=By.XPATH,value='/html/body/section/section/section/div[2]/div/div[1]/section/div/table/tfoot/tr[1]/td[2]/div[2]/div')
                    break
                except:
                    pass
            while(1):
                    try:
                        self.browser.find_element(by=By.XPATH,value='/html/body/section/section/section/div[2]/div/div[2]/div/div/div/div[2]/div[2]/button[1]')
                        break
                    except:
                        pass
        self.open_page('https://recordhub.cottsystems.com/Portal/Cart')
        while(1):
            try:
                self.click_button(by=By.XPATH,value='//*[@id="Finish"]')
                break
            except:
                pass
    def search_results(self,county: str,book: str,page: str,DocumentNumber: str,document_type: str,o_id):
        self.open_page(self.county_link(county))
        while(1):
            try:
                self.click_button(by=By.XPATH,value='//*[@id="btnSearchType"]')
                if document_type=="Book, Page":
                    self.click_button(by=By.XPATH,value='/html/body/section/section/section/div[2]/div/div[1]/form/div/section/div/div[1]/div[1]/div/div[1]/ul/li[4]/a') # Book and Page
                elif document_type=="Document Number":
                    self.click_button(by=By.XPATH,value='/html/body/section/section/section/div[2]/div/div[1]/form/div/section/div/div[1]/div[1]/div/div[1]/ul/li[5]/a') # Document Number
                break
            except:
                pass
        #Book Page
        if document_type=="Book, Page":
            self.add_input(by=By.ID,value='Book',text=book)
            self.add_input(by=By.ID,value='Page',text=page)
            self.add_input(by=By.ID,value='Page',text=Keys.ENTER)

        #Document Number
        elif document_type=="Document Number":
            self.add_input(by=By.ID,value='SearchTerm',text=DocumentNumber)
            self.add_input(by=By.ID,value='SearchTerm',text=Keys.ENTER)
        iter=0
        while(1):
            iter=iter+1
            if iter>1000:
                print("Document Not Found")
                break
                return "Document Not Found"
            try:
                pages=self.browser.find_element(by=By.XPATH,value='/html/body/section/section/section/div[2]/div/div[1]/div/div/div[5]/div[4]/div[2]/section/div/div/table/tbody/tr/td[4]').text
                break
            except:
                pass
        print("No.of Pages : ",pages)
        
        order=Orders.query.filter_by(o_id=o_id).first() 
        order.no_of_pages=pages
        db.session.commit()
        self.click_button(by=By.XPATH,value='/html/body/section/section/section/div[2]/div/div[1]/div/div/div[5]/div[4]/div[2]/section/div/div/table/tbody/tr/td[3]/a[1]')
        folder_name = 'images'
        if not os.path.isdir(folder_name):
            os.makedirs(folder_name)
        pdf_images=[]
        folderName = datetime.now().strftime("%d%m%Y%H%M%S")
        imageFolderPath = os.path.join(folder_name, folderName)
        os.makedirs(imageFolderPath)

        pdf_path='pdf'
        if not os.path.isdir(pdf_path):
            os.makedirs(pdf_path)
        prev=0
        self.browser.set_window_size(1920, 1080)
        while(1):
            try:
                canvas= self.browser.find_element(by=By.XPATH,value='/html/body/section/section/section/div[2]/div/div[2]/div/div/div[5]/div[4]/div/canvas[1]') 
                break
            except:
                pass
        for i in range(1,int(pages)+1):
            iter=0
            time.sleep(2)
            while(1):
                iter=iter+1
                if iter>5000:
                    break
                try:
                    self.click_button(by=By.XPATH,value='/html/body/section/section/section/div[2]/div/div[1]/div/div[1]/canvas-toolbar/div[4]/a[3]')
                    # if i==1:
                    #     time.sleep(2)
                    canvas= self.browser.find_element(by=By.XPATH,value='/html/body/section/section/section/div[2]/div/div[2]/div/div/div[5]/div[4]/div/canvas[1]')
                    width=canvas.get_attribute('width')
                    # print(width)
                    if int(width)>2000:
                        self.click_button(by=By.XPATH,value='/html/body/section/section/section/div[2]/div/div[1]/div/div[1]/canvas-toolbar/div[4]/a[1]')
                        prev=int(width)
                        break
                except:
                    pass
            print("Downloading Page : ",i)
            # get the canvas as a PNG base64 string
            canvas_base64 = self.browser.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canvas)
            if int(pages)!=i:
                self.click_button(by=By.XPATH,value='//*[@id="NextPage"]') # Next
            # decode
            canvas_png = b64decode(canvas_base64)
            path=imageFolderPath+'/'+str(i)+".png"
            # save to a file
            with open(path, 'wb') as f:
                f.write(canvas_png)
            img=cv2.imread(path)
            img=remove_watermark(img)
            cv2.imwrite(path,img)
            
        pdf_name=image_Export_to_PDF(folder_name,imageFolderPath,folderName,pdf_path)
        shutil.rmtree(imageFolderPath)
        return pdf_name
    
        
    


#GSCCCA
class GSCCCA:
    browser, service = None, None

    # Initialise the webdriver with the path to chromedriver.exe
    def __init__(self, driver: str):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('window-size=1920x1080')
        options.add_argument('--disable-dev-shm-usage')
        self.service = Service(driver)
        if browse_params:
            self.browser=webdriver.Chrome()
            # self.browser = webdriver.Chrome(service=self.service)
        else:
            self.browser= webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.browser.maximize_window()

    def open_page(self, url: str):
        self.browser.get(url)

    def close_browser(self):
        self.browser.close()
        
    def add_input(self, by: By, value: str, text: str):
        field = self.browser.find_element(by=by, value=value)
        field.send_keys(text)

    def click_button(self, by: By, value: str):
        button = self.browser.find_element(by=by, value=value)
        button.click()
    def login(self, username: str, password: str):
        self.click_button(by=By.XPATH,value='/html/body/form/div[3]/div/ul/li[3]/div/a')
        self.add_input(by=By.ID,value='username',text=username)
        self.add_input(by=By.ID,value='password',text=password)
        self.click_button(by=By.ID,value='loginbtn')
        
    
    def search_results(self,county:str,book: str,page_from: str,page_upto: str,type_search: str,o_id):
        # time.sleep(5)
        print(type_search)
        
        if type_search =='Real Estate Records':
            self.open_page('https://search.gsccca.org/RealEstate/bookpagesearch.asp') # Realestate Index
            # selecting dropdown
            # select = Select(self.browser.find_element(By.XPATH, '//*[@id="content"]/div/table/tbody/tr[2]/td/form/p[2]/select'))
        elif type_search=='Lien Documents':
            self.open_page('https://search.gsccca.org/Lien/bookpagesearch.asp') # Lein Book
            # time.sleep(2)
            # select = Select(self.browser.find_element(By.XPATH, '//*[@id="content"]/div/form/table/tbody/tr[2]/td/p[2]/select'))
            
        
        # self.browser.get_screenshot_as_file('s.png')
        select = Select(self.browser.find_element(By.NAME, 'intCountyID'))
        
        # # self.click_button(by=By.XPATH,value='//*[@id="fullpage"]/div[1]/div/div/a[2]')
        # self.click_button(by=By.XPATH,value='//*[@id="aspnetForm"]/div[5]/div/nav/div[2]/a')
        # self.click_button(by=By.XPATH,value='/html/body/form/div[4]/div[1]/div[1]/div/div[2]/h2[1]/span') #Realestate Index
        # self.click_button(by=By.XPATH,value='/html/body/form/div[4]/div[1]/div[1]/div/div[2]/div/div[1]/div[1]/a[2]/h3') # For Realestate Search Book and Page
        # # self.click_button(by=By.XPATH,value='/html/body/form/div[4]/div[1]/div[1]/div/div[3]/h2[1]/span') #Lein Index
        # time.sleep(2)
        
        # self.add_input(by=By.NAME,value='intCountyID',text=county)
        
        
        select.select_by_value(county)
        self.browser.find_element(By.ID,value='txtBook').clear()
        self.add_input(by=By.ID,value='txtBook',text=book)
        self.browser.find_element(By.ID,value='txtPage').clear()
        self.add_input(by=By.ID,value='txtPage',text=page_from)
        if type_search=='Real Estate Records':
            self.click_button(by=By.XPATH,value='/html/body/div[2]/div[2]/div/div/table/tbody/tr[3]/td/div/input[1]')
            try:
                self.click_button(by=By.XPATH,value='//*[@id="content"]/div[1]/table/tbody/tr[2]/td/center/div/form/table/tbody/tr/td/input')
            except:
                return 'No Document Found'
        elif type_search=='Lien Documents':
            self.click_button(by=By.XPATH,value='/html/body/div[2]/div[2]/div/div/form/table/tbody/tr[2]/td/p[6]/input[1]')
            try:
                self.click_button(by=By.XPATH,value='/html/body/div[2]/div[2]/div/div/table/tbody/tr[2]/td/center/form/table/tbody/tr/td/input')
            except:
                return 'No Document Found'
        folder_name = 'images'
        if not os.path.isdir(folder_name):
            os.makedirs(folder_name)
        pdf_images=[]
        folderName = datetime.now().strftime("%d%m%Y%H%M%S")
        imageFolderPath = os.path.join(folder_name, folderName)
        os.makedirs(imageFolderPath)
        
        pdf_path='pdf'
        if not os.path.isdir(pdf_path):
            os.makedirs(pdf_path)
            
        
        main_page = self.browser.current_window_handle
        #get instance of first pop up  window
        whandle = self.browser.window_handles[1]

        #switch to pop up window
        self.browser.switch_to.window(whandle)
        self.browser.maximize_window()
        for i in range(int(page_upto+1)):
            self.add_input(by=By.XPATH,value='/html/body/form/div[6]/div/div[1]/table/tbody/tr/td[6]/select',text='600')
            time.sleep(8)
            canvas= self.browser.find_element(by=By.XPATH,value='/html/body/form/div[6]/div/div[3]/div[2]/div[1]/canvas')
            # get the canvas as a PNG base64 string
            canvas_base64 = self.browser.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canvas)
            self.click_button(by=By.XPATH,value='//*[@id="vtm_main"]/div[1]/table/tbody/tr/td[3]/img')
            # decode
            canvas_png = b64decode(canvas_base64)
            # save to a file
            with open(imageFolderPath+'/'+str(i)+".png", 'wb') as f:
                f.write(canvas_png)
        self.close_browser()   
        self.browser.switch_to.window(main_page)
        pdf_name=image_Export_to_PDF(folder_name,imageFolderPath,folderName,pdf_path)
        shutil.rmtree(imageFolderPath)
        return pdf_name

#SEARCHIQ
class searchiq:
    browser, service = None, None

    # Initialise the webdriver with the path to chromedriver.exe
    def __init__(self, driver: str):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.service = Service(driver)
        if browse_params:
            self.browser=webdriver.Chrome()
            # self.browser = webdriver.Chrome(service=self.service)
        else:
            self.browser= webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.browser.maximize_window()

    def open_page(self, url: str):
        self.browser.get(url)

    def close_browser(self):
        self.browser.close()
        
    def add_input(self, by: By, value: str, text: str):
        field = self.browser.find_element(by=by, value=value)
        field.send_keys(text)

    def click_button(self, by: By, value: str):
        button = self.browser.find_element(by=by, value=value)
        button.click()

    def login(self):
        while(1):
            try:
                self.add_input(by=By.NAME, value='phoneNumber')
                time.sleep(1)
                self.click_button(by=By.XPATH,value='/html/body/div/section/div[2]/delhivery-login-form/div/div[1]/div/div[1]/div/div/div/div/div[2]/form/div[2]/button')
                otp=int(input('Enter OTP'))
                self.add_input(by=By.NAME, value='otpNumber',text=otp)
                time.sleep(1)
                self.click_button(by=By.XPATH,value='/html/body/div/section/div[2]/delhivery-login-form/div/div[1]/div/div[1]/div/div/div/div/div[2]/form/div[2]/button')
                break
            except:
                pass
        while(1):
            try:
                self.add_input(by=By.XPATH,value='/html/body/app-root/layout/div[1]/nav/div/delhivery-services-menu/div/div/div[3]/div/div[2]/center-modal/div/div[2]/div[3]/auto-complete-center/div/input')
                time.sleep(1)
                self.click_button(by=By.XPATH, value='/html/body/app-root/layout/div[1]/nav/div/delhivery-services-menu/div/div/div[3]/div/div[2]/center-modal/div/div[2]/div[3]/auto-complete-center/ul/li')
                break
            except:
                pass
            
    def search_results(self,document_type,book,page,DocumentNumber,o_id,Username=None,Password=None):
        try:
            self.browser.find_element(by=By.ID,value='btnGuestLogin').click()
        except:
            print("No Guest Login")
            self.add_input(by=By.ID,value='username',text=Username)
            self.add_input(by=By.ID,value='password',text=Password)
            self.click_button(by=By.ID,value='cmdLogin')
        try:
            time.sleep(0.5)
            if document_type=='name':
                self.add_input(by=By.ID,value='ContentPlaceHolder1_txtName',text="last_name")
                self.add_input(by=By.ID,value='ContentPlaceHolder1_txtFirstName',text="first_name")
            elif document_type=="Document Number":
                self.add_input(by=By.ID,value='ContentPlaceHolder1_txtUDFNum',text=DocumentNumber)
                print("OK")
            elif document_type=="Book, Page":
                print(book,page)
                self.add_input(by=By.ID,value='ContentPlaceHolder1_txtBook',text=book)
                self.add_input(by=By.ID,value='ContentPlaceHolder1_txtPage',text=page)
                print("HERE")
            self.click_button(by=By.ID,value='ContentPlaceHolder1_cmdSearch')
        except:
            print("No Login Search")
            return 'No Login Search'
        try:
            print("Here")
            self.click_button(by=By.ID,value='ContentPlaceHolder1_grdResults_btnView_0')
            time.sleep(3)
            print("Here")
            self.click_button(by=By.ID,value='divViewer_wdv1_toolbar_Button_FitNone')
        except:
            print('No document Found')
            return 'No document Found'
        no_of_pages=self.browser.find_element(by=By.XPATH,value='/html/body/form/div[6]/table/tbody/tr/td[3]/div[1]/div[2]/span[1]')
        no_of_pages=no_of_pages.text
        no_of_pages=int(no_of_pages[2:])
        # pdf_name=self.browser.find_element(by=By.XPATH,value='/html/body/form/div[6]/table/tbody/tr/td[1]/table/tbody/tr[2]/td/div/span/table/tbody/tr/td/font[1]')
        # pdf_name=pdf_name.text
        # print(no_of_pages,pdf_name)
        #creating a directory to save images
        folder_name = 'images'
        if not os.path.isdir(folder_name):
            os.makedirs(folder_name)
        pdf_images=[]
        folderName = datetime.now().strftime("%d%m%Y%H%M%S")
        imageFolderPath = os.path.join(folder_name, folderName)
        os.makedirs(imageFolderPath)
        
        pdf_path='pdf'
        if not os.path.isdir(pdf_path):
            os.makedirs(pdf_path)
        # imgs=[]
        order=Orders.query.filter_by(o_id=o_id).first() 
        order.no_of_pages=no_of_pages
        db.session.commit()
        img_check='hi'
        for i in range(0,no_of_pages):
            while(1):
                try:
                    # print("Waiting")
                    for _ in range(0,3):
                        self.browser.find_element(by=By.ID,value='txtPageNum').send_keys(Keys.BACK_SPACE)
                    self.add_input(by=By.ID,value='txtPageNum',text=str(i+1))
                    try:
                        self.browser.find_element(by=By.ID,value='txtPageNum').send_keys(Keys.ENTER)
                    except:
                        self.browser.find_element(by=By.ID,value='txtPageNum').send_keys(Keys.RETURN)
                        
                    # print("Image Page Number ",img_page_num)
                    time.sleep(1)
                    img_source=self.browser.find_element(by=By.XPATH, value='//*[@id="divViewer_wdv1_ct"]/div/div/img')
                    # img_source.screenshot(os.path.join(folder_name, str(i)+"12.png"))
                    print('Success')
                    break
                    # if img_source.get_attribute('src') != img_check:
                    #     break
                except:
                    # print('Getting')
                    pass
            imageURL= img_source.get_attribute('src')
            try:
                self.download_image(imageURL, imageFolderPath, i)
                # print(imageURL)
                print("Downloaded element")
                img_check=imageURL
                
                # time.sleep(1)
                # self.click_button(by=By.ID,value='btnToolbarNext')
                # time.sleep(1)
            except:
                try:
                    pass
                    # time.sleep(1)
                    # self.click_button(by=By.ID,value='btnToolbarNext')
                except:
                    print("Couldn't download an image %s, continuing downloading the next one"%(i))
        pdf_name=image_Export_to_PDF(folder_name,imageFolderPath,folderName,pdf_path)
        # os.remove(imageFolderPath)
        shutil.rmtree(imageFolderPath)
        print("Extract Completed")
        return pdf_name
        

        
        


    def download_image(self,url, folder_name, num):
        self.browser.get(url)    
        self.click_button(by=By.XPATH,value='/html/body/img')
        # path=str(num)+".png"
        path=os.path.join(folder_name, str(num)+".png")
        img= self.browser.find_element(by=By.XPATH,value='/html/body/img')
        # img.screenshot(path)
        b64img = self.browser.execute_script(r'''
        var img = document.getElementsByTagName("img")[0];
        var canvas = document.createElement("canvas");
        canvas.width = img.width;
        canvas.height = img.height;
        var ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0);
        var dataURL = canvas.toDataURL("image/png");
        return dataURL.replace(/^data:image\/(png|jpg);base64,/, "");
        ''')

        # Decode from base64, translate to bytes and write to PIL image
        img_png = Image.open(BytesIO(b64decode(b64img)))
        img=remove_watermark(img=img_png,intensity=125)
        # im_pil = Image.fromarray(img)
        # imgs.append(im_pil)
        cv2.imwrite(path,img)
        # img_png.save(path)
        self.browser.back()
        
        

#TAPESTRY

def joiningimages_tap(joinedImagePath,images_path, pageNumber):
        # print("joiningimages")

        list_of_files = filter(lambda x: os.path.isfile(os.path.join(images_path, x)),
                            os.listdir(images_path))
        # Sort list of files based on last modification time in ascending order
        list_of_files = sorted(list_of_files, key=lambda x: os.path.getmtime(os.path.join(images_path, x)))
        
        images = [PIL.Image.open(os.path.join(images_path, x)) for x in list_of_files]
        widths = 0
        size = []
        heights = 0
        for i in images:
            w, h = i.size
            size.append(i.size)
            heights += h
            widths += w

        widths = int(widths / 2)
        heights = int(heights / 2)
        # print("before "+str(heights) + "......." + str(widths))
        output_Image = PIL.Image.new('RGB', (widths, heights))

        # x_offset = 0
        # y_offset = 0

        for num in range(0, 4):
            if num==0:
                output_Image.paste(images[num], (0,0))
            elif num==1:
                output_Image.paste(images[num], (512,0))
            elif num==2:
                output_Image.paste(images[num], (0,512))
            elif num==3:
                output_Image.paste(images[num], (512,512))
        file_name=str(pageNumber) + '.png'
        path=os.path.join(joinedImagePath, file_name)
        output_Image.save(path)
        try:
            os.rmdir(images_path)
        except:
            try:
                shutil.rmtree(images_path)
            except:
                print("Unable to Delete")
        
def image_Export_to_PDF_tap(images_path, pdf_Name,pdf_path,pages):
        print("image_Export_to_PDF")
        imgs=[]
        pdf_name=pdf_Name + '.pdf'
        pdffilename=os.path.join(pdf_path,pdf_name)
        # pdffilename = pdf_path + "/" + pdf_Name + '.pdf'
        count=0
        a=0
        while(count!=int(pages)):
            count=0
            a=a+1
            for path in os.listdir(images_path):
                # check if current path is a file
                if os.path.isfile(os.path.join(images_path, path)):
                    count += 1
            print('File count:', count)
            if count==int(pages):
                break
            if a>1000:
                break
        list_of_files = filter(lambda x: os.path.isfile(os.path.join(images_path, x)),
                                os.listdir(images_path))
        # Sort list of files based on last modification time in ascending order
        list_of_files = sorted(list_of_files, key=lambda x: os.path.getmtime(os.path.join(images_path, x)))
        for filename in list_of_files:
            f = os.path.join(images_path, filename)
            img=Image.open(f,mode="r")
            imgs.append(img)
        im=imgs[0]
        imgs.pop(0)
        im.save(pdffilename, save_all=True, append_images=imgs)
        return pdffilename


class Tapestry:
    browser, service = None, None

    # Initialise the webdriver with the path to chromedriver.exe
    def __init__(self, driver: str):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('window-size=1920x1080')
        options.add_argument('--disable-dev-shm-usage')
        self.service = Service(driver)
        if browse_params:
            self.browser=webdriver.Chrome()
            # self.browser = webdriver.Chrome(service=self.service)
        else:
            self.browser= webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.browser.maximize_window()

    def open_page(self, url: str):
        self.browser.get(url)

    def close_browser(self):
        self.browser.close()
        
    def add_input(self, by: By, value: str, text: str):
        field = self.browser.find_element(by=by, value=value)
        field.send_keys(text)

    def click_button(self, by: By, value: str):
        button = self.browser.find_element(by=by, value=value)
        button.click()
        
    def login(self, username: str, password: str):
        self.open_page("https://tapestry.fidlar.com/Tapestry2/")
        self.click_button(by=By.ID,value='btnLogin')
        time.sleep(1)
        self.add_input(by=By.ID,value='LoginView1_Login1_UserName',text=username)
        self.add_input(by=By.ID,value='LoginView1_Login1_Password',text=password)
        self.click_button(by=By.ID,value='LoginView1_Login1_RememberMe')
        self.click_button(by=By.ID,value='LoginView1_Login1_LoginButton')


    


    def search_results(self):
        self.open_page("https://tapestry.fidlar.com/Tapestry2/Search.aspx")
        try:
            self.add_input(by=By.ID,value='ContentPlaceHolder1_cbxDataSourceState',text="IL")
            time.sleep(2)
            self.browser.find_element(by=By.XPATH, value='/html/body/form/div[3]/div[2]/div/table/tbody/tr[1]/td[1]/div/div/select[2]/option[4]').click()
            time.sleep(2)
        except:
            self.click_button(by=By.ID,value='ContentPlaceHolder1_BtnChooseDatasource')
            time.sleep(2)
            self.add_input(by=By.ID,value='ContentPlaceHolder1_cbxDataSourceState',text="IL")
            time.sleep(2)
            self.browser.find_element(by=By.XPATH, value='/html/body/form/div[3]/div[2]/div/table/tbody/tr[1]/td[1]/div/div/select[2]/option[4]').click()
            time.sleep(2)
        self.add_input(by=By.ID,value='ContentPlaceHolder1_txtFirstName',text="James")
        self.add_input(by=By.ID,value='ContentPlaceHolder1_txtLastName',text="Smith")
        
        self.click_button(by=By.ID,value='ContentPlaceHolder1_btnSearch')
        # pdf_name=self.get_results()
        # return pdf_name
    
    def get_results(self,o_id):
        # self.click_button(by=By.XPATH,value='/html/body/form/div[3]/div[2]/div[2]/div/div[2]/div[1]/div/table/tbody/tr[2]/td[4]')
        self.click_button(by=By.ID,value='ContentPlaceHolder1_btnImage')
        time.sleep(2)
        page_num=self.browser.find_element(by=By.ID, value='ContentPlaceHolder1_ImgViewer_ot')
        page_num=page_num.text
        page_num=page_num.split(' of ')
        pages=page_num[-1]
        print("No.of Pages : ",pages)
        order=Orders.query.filter_by(o_id=o_id).first() 
        order.no_of_pages=pages
        db.session.commit()
        axis=['atala_tx=0&atala_ty=0','atala_tx=0&atala_ty=512','atala_tx=512&atala_ty=0','atala_tx=512&atala_ty=512']
        working_path='Tapestry_downloads'
        if not os.path.isdir(working_path):
                    os.makedirs(working_path)
        out_dir = "output"
        out_dir=os.path.join(working_path,out_dir)
        folderName = datetime.now().strftime("%d%m%Y%H%M%S")
        # folderName=os.path.join(working_path,folderName)
        parent_dir = "images" 
        parent_dir=os.path.join(working_path,parent_dir)
        if not os.path.isdir(parent_dir):
            os.makedirs(parent_dir)
        out_path = os.path.join(out_dir,folderName)
        if not os.path.isdir(out_path):
            os.makedirs(out_path)
        for page in range(int(pages)):
            page_num=page
            imageURL=''
            got=0
            print("Getting Page : ",page)
            status_page="Getting Page : "+str(page+1)
            order=Orders.query.filter_by(o_id=o_id).first() 
            order.status=status_page
            db.session.commit()
            self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='/html/body/form/div[3]/div[2]/div[3]/div/table/tbody/tr[2]/td/table/tbody/tr/td/iframe'))
            x=self.browser.find_elements(by=By.TAG_NAME, value='img')
            ab=0
            while(got==0):
                ab=ab+1
                x=self.browser.find_elements(by=By.XPATH, value='/html/body/div/img')
                # print('No.Of elements',len(x))
                for i in x:
                    # print(i.get_attribute('width'),"Width")
                    # print(i.get_attribute('height'),"Height")
                    imageURL= i.get_attribute('src')
                    # print(imageURL)
                    if i.get_attribute('width')=='512' and i.get_attribute('height')=='512':
                        if 'atala_id=ContentPlaceHolder1_ImgViewer&atala_tx=' in str(imageURL):
                            print(imageURL)
                            got=1
                            break
                if ab>1000:
                    break
            ## Switch back to the "default content" (that is, out of the iframes) ##
            self.browser.switch_to.default_content()
            folderName = datetime.now().strftime("%d%m%Y%H%M%S")+str(page)
            # folderName=os.path.join(working_path,folderName)

            images_path = os.path.join(parent_dir, folderName)
            if not os.path.isdir(images_path):
                os.makedirs(images_path)
            background_download_tap(images_path,imageURL,out_path,page_num)
            # if page==int(pages-1)
            # time.sleep(3.55)
            less=int(pages)-1
            if page!=less:
                self.browser.find_element(by=By.ID,value="ContentPlaceHolder1_ImageButton5").click()
                
        pdf_path='pdf'
        pdf_path=os.path.join(working_path,pdf_path)
        pdf_name=datetime.now().strftime("%d%m%Y%H%M%S")
        if not os.path.isdir(pdf_path):
            os.makedirs(pdf_path)
        pdf_name=image_Export_to_PDF_tap(out_path,pdf_name,pdf_path,pages)
        try:
            os.rmdir(out_path)
        except:
            try:
                shutil.rmtree(out_path)
            except:
                print("Not Worked")
        return pdf_name,pages


def background_download_tap(images_path,imageURL,out_path,page_num):
    axis=['atala_tx=0&atala_ty=0','atala_tx=0&atala_ty=512','atala_tx=512&atala_ty=0','atala_tx=512&atala_ty=512']
    for s in range(0,4):
        # print(s)
        if s==0:
            new='atala_tx=0&atala_ty=0'
        elif s==1:
            new='atala_tx=512&atala_ty=0'
        elif s==2:
            new='atala_tx=0&atala_ty=512'
        elif s==3:
            new='atala_tx=512&atala_ty=512'
        path=images_path+'/'+str(s)+'.png'
        for i in axis:
            if str(i) in str(imageURL):
                src=imageURL.replace(i,new)
                # print(src)
                response = wget.download(src, path)
                break
    joiningimages_tap(joinedImagePath=out_path,images_path=images_path,pageNumber=page_num)
    # os.remove(images_path)



#REMOVE WATERMARK      
def remove_watermark(img,intensity=100):
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    # df=pd.DataFrame(img)
    # df.to_csv('s.csv')
    # cv2.imwrite('s.jpg',img)
    for i in range(len(img)):
        for j in range(len(img[0])):
            if img[i,j] >=intensity:
                # if img[i,(j-1)]>10 and img[(i-1),j]>10 and img[i,(j+1)]>10 and img[(i+1),j]>10:
                img[i,j] =255
    maxIntensity = 255.0 # depends on dtype of image data
    # Parameters for manipulating image data
    phi = 1
    theta = 1

    newImage = (maxIntensity/phi)*(img/(maxIntensity/theta))**2
    newImage = array(newImage,dtype=uint8)
    # cv2.imwrite('newImage123.jpg',newImage)
    return newImage

#REMOVE WATERMARK WestVirginia
def remove_watermark_WS(img):
    try:
        img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    except:
        pass
    ret, thresh = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY)
    #blur the image
    img_rst = cv2.blur(thresh, (2, 2))

    ret,thresh1 = cv2.threshold(img_rst,100,255,cv2.THRESH_BINARY)
    return thresh1



#PDF's
def image_Export_to_PDF(dir_name,images_path, pdf_Name,pdf_path):
    print("image_Export_to_PDF")
    imgs=[]
    pdffilename = pdf_path + "/" + pdf_Name + '.pdf'
    list_of_files = filter(lambda x: os.path.isfile(os.path.join(images_path, x)),
                        os.listdir(images_path))
    # Sort list of files based on last modification time in ascending order
    list_of_files = sorted(list_of_files, key=lambda x: os.path.getmtime(os.path.join(images_path, x)))
    print("List of files: {}".format(list_of_files))
    for filename in list_of_files:
        f = os.path.join(images_path, filename)
        img=Image.open(f,mode="r")
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        imgs.append(img)
    # for filename in os.listdir(images_path):
    #     f = os.path.join(images_path, filename)
    #     img=Image.open(f,mode="r")
    #     imgs.append(img)
    im=imgs[0]
    imgs.pop(0)
    im.save(pdffilename, save_all=True, append_images=imgs)
    return pdffilename

#West_Virginia
class West_Virginia:
    browser, service = None, None

    # Initialise the webdriver with the path to chromedriver.exe
    def __init__(self, driver: str):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('window-size=1920x1080')
        options.add_argument('--disable-dev-shm-usage')
        self.service = Service(driver)
        if browse_params:
            self.browser=webdriver.Chrome()
            # self.browser = webdriver.Chrome(service=self.service)
        else:
            self.browser= webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.browser.maximize_window()

    def open_page(self, url: str):
        self.browser.get(url)

    def close_browser(self):
        self.browser.close()
        
    def add_input(self, by: By, value: str, text: str):
        field = self.browser.find_element(by=by, value=value)
        field.send_keys(text)

    def click_button(self, by: By, value: str):
        button = self.browser.find_element(by=by, value=value)
        button.click()
        
    def search_results(self,county:str,book: str,page: str,o_id):
        # self.open_page(link)
        path='west_virginia_captcha.png'
        b64img = self.browser.execute_script(r'''
                                var img = document.getElementsByTagName("img")[0];
                                var canvas = document.createElement("canvas");
                                canvas.width = img.width;
                                canvas.height = img.height;
                                var ctx = canvas.getContext("2d");
                                ctx.drawImage(img, 0, 0);
                                var dataURL = canvas.toDataURL("image/png");
                                return dataURL.replace(/^data:image\/(png|jpg);base64,/, "");
                                ''')
                                # Decode from base64, translate to bytes and write to PIL image
        img_png = Image.open(BytesIO(b64decode(b64img)))
        img_png.save(path)
        result = solver.normal(path)
        code=str(result['code']).upper()
        print(code)
        _thread.start_new_thread(remove_file_pdf,(path,))
        
        self.click_button(by=By.XPATH,value='/html/body/form/div[3]/table[2]/tbody/tr[1]/td/div/div/div[1]/div[2]/div[1]/div[2]/ul/li[5]/div[1]/div[2]/a[2]/span/span/span')
        main_page = self.browser.current_window_handle
        #get instance of first pop up  window
        whandle = self.browser.window_handles[1]

        #switch to pop up window
        self.browser.switch_to.window(whandle)
        time.sleep(1)

        actions = ActionChains(self.browser) 
        actions.send_keys(Keys.TAB)
        actions.send_keys(Keys.TAB)
        text_verify=''
        a=0
        while(1):
            actions.send_keys(Keys.DOWN)
            actions.perform()
            text=self.browser.find_element(by=By.XPATH, value='/html/body/form/div[3]/table[2]/tbody/tr[2]/td/div/table/tbody/tr[1]/td/div/div[2]/div/div/div/table/tbody/tr/td/div/div/input').get_attribute('value')
            # print(text)
            if text==county:
                actions.send_keys(Keys.ENTER)
                actions.perform()
                print("Done")
                self.add_input(by=By.XPATH,value='/html/body/form/div[3]/table[2]/tbody/tr[2]/td/div/table/tbody/tr[1]/td/div/table[3]/tbody/tr/td[2]/input',text=book)
                self.add_input(by=By.XPATH,value='/html/body/form/div[3]/table[2]/tbody/tr[2]/td/div/table/tbody/tr[1]/td/div/table[5]/tbody/tr/td[2]/input',text=page)
                self.browser.find_element(by=By.XPATH,value='/html/body/form/div[3]/table[2]/tbody/tr[2]/td/div/table/tbody/tr[1]/td/div/table[5]/tbody/tr/td[2]/input').send_keys(Keys.ENTER)
                time.sleep(3)
                break
            elif text==text_verify:
                a=a+1
                if a>3:
                    status='No Type of Search in this County'
                    return status
            text_verify=text
        a=0
        while(1):
            if a>1000:
                print('No Document Found')
                status='No Document Found'
                return status
            a=a+1
            try:
                self.click_button(by=By.XPATH,value='/html/body/form/div[3]/table[2]/tbody/tr[1]/td/div/div/div[1]/div[2]/div/div[2]/ul/li[1]/div[1]/div[1]/a[2]')
                no_of_pages_txt=self.browser.find_element(by=By.XPATH,value='/html/body/form/div[3]/table[2]/tbody/tr[1]/td/div/div/div[1]/div[2]/div/div[2]/ul/li[1]/div[1]/div[2]/div/div/table/tbody/tr[1]/td/table/tbody/tr/td[2]/div/span').get_attribute('innerText')
                no_of_pages=no_of_pages_txt.split(sep=' of ')
                no_of_pages=int(no_of_pages[1])
                if ' of ' in no_of_pages_txt:
                    print("Pages : ",no_of_pages)
                    break
            except:
                pass
            
        folder_name = 'images'
        if not os.path.isdir(folder_name):
            os.makedirs(folder_name)
        pdf_images=[]
        folderName = datetime.now().strftime("%d%m%Y%H%M%S")
        imageFolderPath = os.path.join(folder_name, folderName)
        os.makedirs(imageFolderPath)

        pdf_path='pdf'
        if not os.path.isdir(pdf_path):
            os.makedirs(pdf_path)
        
        order=Orders.query.filter_by(o_id=o_id).first() 
        order.no_of_pages=no_of_pages
        db.session.commit()
            
        for i in range(no_of_pages):
            status_page="Getting Page : "+str(i+1)
            print(status_page)
            order=Orders.query.filter_by(o_id=o_id).first() 
            order.status=status_page
            db.session.commit()
            time.sleep(1)
            for _ in range(100):
                try:
                    img_element=self.browser.find_element(by=By.ID,value='Background')
                    img_src=img_element.get_attribute('src')
                    print(img_src)
                    break
                except:
                    pass
            filename=imageFolderPath+'/'+str(i)+".png"
            self.click_button(by=By.XPATH,value='/html/body/form/div[3]/table[2]/tbody/tr[1]/td/div/div/div[1]/div[2]/div/div[2]/ul/li[1]/div[1]/div[2]/a[1]') #Next Doc
            response = wget.download(img_src, filename)
            img=cv2.imread(filename)
            img_res=remove_watermark_WS(img)
            cv2.imwrite(filename,img_res)
        self.close_browser()   
        self.browser.switch_to.window(main_page)
        pdf_name=image_Export_to_PDF(folder_name,imageFolderPath,folderName,pdf_path)
        shutil.rmtree(imageFolderPath)
        return pdf_name


#Kofiletech
class kofiletech:
    browser, service = None, None

    # Initialise the webdriver with the path to chromedriver.exe
    def __init__(self, driver: str):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('window-size=1920x1080');
        self.service = Service(driver)
        if browse_params:
            self.browser=webdriver.Chrome()
            # self.browser = webdriver.Chrome(service=self.service)
        else:
            self.browser= webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.browser.maximize_window()

    def open_page(self, url: str):
        self.browser.get(url)

    def close_browser(self):
        self.browser.close()
        
    def add_input(self, by: By, value: str, text: str):
        field = self.browser.find_element(by=by, value=value)
        field.send_keys(text)

    def click_button(self, by: By, value: str):
        button = self.browser.find_element(by=by, value=value)
        button.click()
    
    def search_results(self, county: str,document_type,book,page,DocumentNumber,o_id,Username=None,Password=None):
        self.browser.find_element(by=By.LINK_TEXT,value=county).click()
        while(1):
            try:
                self.browser.find_element(by=By.XPATH,value='/html/body/div')
                break
            except:
                pass
                # print('Error')
        #Guest Login
        time.sleep(3)
        for i in range(300):
            if 'Union' in county:
                try:
                    self.click_button(by=By.XPATH,value='/html/body/div[4]/div[2]/table[2]/tbody/tr[1]/td[2]/table/tbody/tr/td/input[2]')
                    break
                except:
                    pass
            elif 'Tarrant' in county:
                try:
                    self.click_button(by=By.XPATH,value='/html/body/div[4]/div[2]/table[2]/tbody/tr[1]/td[2]/table/tbody/tr/td/center/center/center/span/input')
                    break
                except:
                    pass
            elif 'Bell' in county:
                try:
                    self.click_button(by=By.XPATH,value='/html/body/div[4]/div[2]/table[2]/tbody/tr[1]/td[2]/table/tbody/tr/td/center/center/span/input')
                    break
                except:
                    pass
            else:
                try:
                    try:
                        try:
                            self.browser.find_element(by=By.XPATH,value='/html/body/div[4]/div[2]/table[2]/tbody/tr[1]/td[2]/table/tbody/tr/td/input').click()
                            break
                        except:
                            self.browser.find_element(by=By.XPATH,value='/html/body/div[4]/div[2]/table[2]/tbody/tr[1]/td[2]/table/tbody/tr/td/center/span[2]/input').click()
                            break
                    except:
                        self.browser.find_element(by=By.XPATH,value='//*[@id="maindiv"]/table[2]/tbody/tr[1]/td[2]/table/tbody/tr/td/center/span[3]/input').click()
                        break
                except:
                    try:
                        try:
                            self.browser.find_element(by=By.XPATH,value='/html/body/div[4]/div[2]/table[2]/tbody/tr[1]/td[2]/table/tbody/tr/td/center/input[2]').click()
                            break
                        except:
                            self.browser.find_element(by=By.XPATH,value='/html/body/div[4]/div[2]/table[2]/tbody/tr[1]/td[2]/table/tbody/tr/td/center/input[2]').click()
                            break
                    except:
                        try:
                            self.click_button(by=By.XPATH,value='/html/body/div[4]/div[2]/table[2]/tbody/tr[1]/td[2]/table/tbody/tr/td/center/input')
                            break
                        except:
                            pass
                    # print("TRYING")
        if Username:
            self.add_input(by=By.XPATH,value='/html/body/div[4]/div[2]/table[2]/tbody/tr[1]/td[2]/form/table[1]/tbody/tr[2]/td[2]/input',text=Username)
            self.add_input(by=By.XPATH,value='/html/body/div[4]/div[2]/table[2]/tbody/tr[1]/td[2]/form/table[1]/tbody/tr[3]/td[2]/input',text=Password)
            self.click_button(by=By.XPATH,value='/html/body/div[4]/div[2]/table[2]/tbody/tr[1]/td[2]/form/table[1]/tbody/tr[5]/td[2]/input[1]')
        # full_name='Smith James'
        # print(full_name)
        time.sleep(1)
        for i in range(100): # For Notification
            try:
                try:
                    self.click_button(by=By.XPATH,value='/html/body/div[10]/div/table/tbody/tr/td[2]/a/img')
                    break
                except:
                    self.click_button(by=By.XPATH,value='/html/body/div[10]/div/table/tbody/tr/td[2]/a/img')
                    break
            except:
                pass
        time.sleep(1)
        for i in range(300): #Accept Button
            try:
                self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='//*[@id="corediv"]/iframe'))
                self.click_button(by=By.XPATH,value='//*[@id="accept"]')
                self.browser.switch_to.default_content()
                break
            except:
                self.browser.switch_to.default_content()
                pass
        time.sleep(1)
        for i in range(100): # For Notification
            try:
                try:
                    self.click_button(by=By.XPATH,value='/html/body/div[10]/div/table/tbody/tr/td[2]/a/img')
                    break
                except:
                    self.click_button(by=By.XPATH,value='/html/body/div[10]/div/table/tbody/tr/td[2]/a/img')
                    break
            except:
                pass
        time.sleep(1)
        for i in range(300): #For Searching Records Button
            try:
                self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='//*[@id="corediv"]/iframe'))
                self.click_button(by=By.XPATH,value='//*[@id="datagrid-row-r1-2-0"]/td/div')
                self.browser.switch_to.default_content()
                break
            except:
                self.browser.switch_to.default_content()
                pass
        time.sleep(1)
        for i in range(100): # For Notification
            try:
                try:
                    self.click_button(by=By.XPATH,value='/html/body/div[10]/div/table/tbody/tr/td[2]/a/img')
                    break
                except:
                    self.click_button(by=By.XPATH,value='/html/body/div[10]/div/table/tbody/tr/td[2]/a/img')
                    break
            except:
                pass
        for i in range(300):
            try:
                if document_type=='name':
                    print('Here')
                    self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='/html/body/div[3]/iframe'))
                    print('Here1')
                    self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='/html/body/div[3]/iframe'))
                    print('Here2')
                    self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='/html/body/div[1]/div/div[2]/div[2]/div[2]/iframe'))
                    print('Here3')
                    self.add_input(by=By.XPATH,value='//*[@id="elemAllNamesJSP_10"]/table/tbody/tr/td[2]/span/input[1]',text='Smith James')
                    self.browser.find_element(by=By.XPATH,value='/html/body/form[1]/div[1]/div[3]/table/tbody/tr/td[2]/span/input[1]').send_keys(Keys.RETURN)
                    # self.browser.click_button(by=By.XPATH,value='/html/body/div[1]/div/div[1]/div/div/span[2]/a[2]/img')
                    ## Switch back to the "default content" (that is, out of the iframes) ##
                    self.browser.switch_to.default_content()
                    break
                elif document_type=="Book, Page":
                    list=['Book - Page','Book / Page','Volume / Page','Book Page','Liber Page','Volume/Book/Page','Volume - Page','Book (Slide) / Page','Book/ Page']
                    self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='//*[@id="corediv"]/iframe'))
                    self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='//*[@id="dynSearchFrame"]'))
                    # self.click_button(by=By.XPATH,value='//*[@id="datagrid-row-r2-2-3"]/td/div/span')
                    flag_book=0
                    for know in range(10):
                        # print("Trying")
                        if flag_book==1:
                            break
                        try:
                            try:
                                p='//*[@id="datagrid-row-r2-2-'+str(know)+'"]/td/div/span'
                                type=self.browser.find_element(by=By.XPATH,value=p).text
                                # print(type)
                                for check in list:
                                    if type==check:
                                        flag_book=1
                                        self.click_button(by=By.XPATH,value=p)
                                        break
                            except:
                                p='//*[@id="SEARCHTYPE_datagrid-row-r2-2-'+str(know)+'"]/td/div/span'
                                type=self.browser.find_element(by=By.XPATH,value=p).text
                                # print(type)
                                for check in list:
                                    if type==check:
                                        flag_book=1
                                        self.click_button(by=By.XPATH,value=p)
                                        break
                        except:
                            pass
                    self.browser.switch_to.default_content()
                    print('Here')
                    self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='/html/body/div[3]/iframe'))
                    print('Here1')
                    self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='/html/body/div[3]/iframe'))
                    print('Here2')

                    self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='/html/body/div[1]/div/div[2]/div[2]/div[2]/iframe'))
                    print('Here3')
                    if type=='Book - Page'or type=='Volume/Book/Page':
                        try:
                            self.browser.find_element(by=By.XPATH,value='/html/body/form[1]/div[1]/div/table/tbody/tr[2]/td[2]/span/input[1]').clear()
                            self.browser.find_element(by=By.XPATH,value='/html/body/form[1]/div[1]/div/table/tbody/tr[3]/td[2]/span/input[1]').clear()
                            self.add_input(by=By.XPATH,value='/html/body/form[1]/div[1]/div/table/tbody/tr[2]/td[2]/span/input[1]',text=book)
                            self.add_input(by=By.XPATH,value='/html/body/form[1]/div[1]/div/table/tbody/tr[3]/td[2]/span/input[1]',text=page)
                            self.add_input(by=By.XPATH,value='/html/body/form[1]/div[1]/div/table/tbody/tr[2]/td[2]/span/input[1]',text=Keys.ENTER)
                        except:
                            pass
                    elif type=='Volume - Page':
                        try:
                            self.add_input(by=By.XPATH,value='/html/body/form[1]/div[1]/div/table/tbody/tr[1]/td[2]/span/input[1]',text=book)
                            self.add_input(by=By.XPATH,value='/html/body/form[1]/div[1]/div/table/tbody/tr[2]/td[2]/span/input[1]',text=page)
                            self.add_input(by=By.XPATH,value='/html/body/form[1]/div[1]/div/table/tbody/tr[2]/td[2]/span/input[1]',text=Keys.ENTER)
                        except:
                            pass
                    elif 'Milton' in county or 'United States Virgin Islands' in county:
                        try:
                            self.browser.find_element(by=By.XPATH,value='/html/body/form[1]/div[1]/div/table/tbody/tr[2]/td[2]/span/input[1]').clear()
                            self.browser.find_element(by=By.XPATH,value='/html/body/form[1]/div[1]/div/table/tbody/tr[3]/td[2]/table/tbody/tr/td[1]/span/input[1]').clear()
                            self.add_input(by=By.XPATH,value='/html/body/form[1]/div[1]/div/table/tbody/tr[2]/td[2]/span/input[1]',text=book)
                            self.add_input(by=By.XPATH,value='/html/body/form[1]/div[1]/div/table/tbody/tr[3]/td[2]/table/tbody/tr/td[1]/span/input[1]',text=page)
                            self.add_input(by=By.XPATH,value='/html/body/form[1]/div[1]/div/table/tbody/tr[3]/td[2]/table/tbody/tr/td[1]/span/input[1]',text=Keys.ENTER)
                        except:
                            pass
                        
                    elif type=='Volume / Page' or type=='Liber Page' or 'Bell' in county or 'Tarrant' in county or 'Underhill' in county or 'Rockingham' in county or 'Fair Haven' in county:
                        try:
                            self.add_input(by=By.XPATH,value='/html/body/form[1]/div[1]/div/table/tbody/tr[1]/td[2]/span/input[1]',text=book)
                            self.add_input(by=By.XPATH,value='/html/body/form[1]/div[1]/div/table/tbody/tr[2]/td[2]/table/tbody/tr/td[1]/span/input[1]',text=page)
                            self.add_input(by=By.XPATH,value='/html/body/form[1]/div[1]/div/table/tbody/tr[2]/td[2]/table/tbody/tr/td[1]/span/input[1]',text=Keys.ENTER)
                        except:
                            pass
                    else:
                        try: 
                            self.add_input(by=By.XPATH,value='/html/body/form[1]/div[1]/div/table/tbody/tr[3]/td[2]/table/tbody/tr/td[1]/span/input[1]',text=page)
                            self.add_input(by=By.XPATH,value='/html/body/form[1]/div[1]/div/table/tbody/tr[2]/td[2]/span/input[1]',text=book)
                            try:
                                self.browser.find_element(by=By.XPATH,value='//*[@id="elemVBP"]/table/tbody/tr[3]/td[2]/table/tbody/tr/td[1]/span/input[1]').send_keys(Keys.RETURN)
                            except:
                                self.browser.find_element(by=By.XPATH,value='//*[@id="elemVBP"]/table/tbody/tr[3]/td[2]/table/tbody/tr/td[1]/span/input[1]').send_keys(Keys.ENTER)
                        except:
                            self.add_input(by=By.XPATH,value='/html/body/form[1]/div[1]/div/table/tbody/tr[1]/td[2]/span/input[1]',text=book)
                            self.add_input(by=By.XPATH,value='/html/body/form[1]/div[1]/div/table/tbody/tr[2]/td[2]/span/input[1]',text=page)
                            try:
                                self.browser.find_element(by=By.XPATH,value='/html/body/form[1]/div[1]/div/table/tbody/tr[1]/td[2]/span/input[1]').send_keys(Keys.RETURN)
                            except:
                                self.browser.find_element(by=By.XPATH,value='/html/body/form[1]/div[1]/div/table/tbody/tr[1]/td[2]/span/input[1]').send_keys(Keys.ENTER)
                            
                    # self.browser.click_button(by=By.XPATH,value='/html/body/div[1]/div/div[1]/div/div/span[2]/a[2]/img')
                    ## Switch back to the "default content" (that is, out of the iframes) ##
                    self.browser.switch_to.default_content()
                    break
                elif document_type=="Document Number":
                    list=['Document Number','Reception Number','Document / Map Number','Doc Number','Document Number / Instrument Number','Instrument Number']
                    self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='//*[@id="corediv"]/iframe'))
                    self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='//*[@id="dynSearchFrame"]'))
                    for know in range(10):
                        # print("Trying")
                        try:
                            try:
                                p='//*[@id="datagrid-row-r2-2-'+str(know)+'"]/td/div/span'
                                type=self.browser.find_element(by=By.XPATH,value=p).text
                                # print(type)
                                for check in list:
                                    if type==check:
                                        self.click_button(by=By.XPATH,value=p)
                                        break
                            except:
                                p='//*[@id="SEARCHTYPE_datagrid-row-r2-2-'+str(know)+'"]/td/div/span'
                                type=self.browser.find_element(by=By.XPATH,value=p).text
                                # print(type)
                                for check in list:
                                    if type==check:
                                        self.click_button(by=By.XPATH,value=p)
                                        break
                        except:
                            pass
                    self.browser.switch_to.default_content()
                    print('Here')
                    self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='//*[@id="corediv"]/iframe'))
                    print('Here1')
                    self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='//*[@id="dynSearchFrame"]'))
                    print('Here2')

                    self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='//*[@id="criteriaframe"]'))
                    print('Here3')
                    time.sleep(3)
                    if 'Reception' in check:
                        self.add_input(by=By.XPATH,value='/html/body/form[1]/div[1]/div/table/tbody/tr/td[2]/span/input[1]',text=DocumentNumber)
                        try:
                            self.browser.find_element(by=By.XPATH,value='/html/body/form[1]/div[1]/div/table/tbody/tr/td[2]/span/input[1]').send_keys(Keys.RETURN)
                        except:
                            self.browser.find_element(by=By.XPATH,value='/html/body/form[1]/div[1]/div/table/tbody/tr/td[2]/span/input[1]').send_keys(Keys.ENTER)
                    else:
                        try:
                            self.add_input(by=By.XPATH,value='/html/body/form[1]/div[1]/div[1]/table/tbody/tr/td[2]/table/tbody/tr/td[1]/span/input[1]',text=DocumentNumber)
                            try:
                                self.browser.find_element(by=By.XPATH,value='/html/body/form[1]/div[1]/div[1]/table/tbody/tr/td[2]/table/tbody/tr/td[1]/span/input[1]').send_keys(Keys.RETURN)
                            except:
                                self.browser.find_element(by=By.XPATH,value='/html/body/form[1]/div[1]/div[1]/table/tbody/tr/td[2]/table/tbody/tr/td[1]/span/input[1]').send_keys(Keys.ENTER)
                        except:
                            self.add_input(by=By.XPATH,value='/html/body/form[1]/div[1]/div/table/tbody/tr/td[2]/span/input[1]',text=DocumentNumber)
                            try:
                                self.browser.find_element(by=By.XPATH,value='/html/body/form[1]/div[1]/div/table/tbody/tr/td[2]/span/input[1]').send_keys(Keys.RETURN)
                            except:
                                self.browser.find_element(by=By.XPATH,value='/html/body/form[1]/div[1]/div/table/tbody/tr/td[2]/span/input[1]').send_keys(Keys.ENTER)
                            

                    # self.browser.click_button(by=By.XPATH,value='/html/body/div[1]/div/div[1]/div/div/span[2]/a[2]/img')
                    ## Switch back to the "default content" (that is, out of the iframes) ##
                    self.browser.switch_to.default_content()
                    break
            except:
                print("except")
                self.browser.switch_to.default_content()

        path='s.png'
        time.sleep(3)
        for i in range(10):
                try:
                        self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='/html/body/div[3]/iframe'))
                        self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='/html/body/div[4]/iframe'))
                        self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='/html/body/div/div/table/tbody/tr[2]/td/iframe'))
                        # security_code=self.browser.find_element(by=By.XPATH, value='/html/body/img')
                        b64img = self.browser.execute_script(r'''
                                var img = document.getElementsByTagName("img")[0];
                                var canvas = document.createElement("canvas");
                                canvas.width = img.width;
                                canvas.height = img.height;
                                var ctx = canvas.getContext("2d");
                                ctx.drawImage(img, 0, 0);
                                var dataURL = canvas.toDataURL("image/png");
                                return dataURL.replace(/^data:image\/(png|jpg);base64,/, "");
                                ''')
                                # Decode from base64, translate to bytes and write to PIL image
                        img_png = Image.open(BytesIO(b64decode(b64img)))
                        img_png.save(path)
                        result = solver.normal(path)
                        code=str(result['code']).upper()
                        print(code)
                        self.browser.switch_to.default_content()
                        self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='/html/body/div[3]/iframe'))
                        self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='/html/body/div[4]/iframe'))
                        self.add_input(by=By.ID,value='code',text=code)
                        self.click_button(by=By.XPATH,value='/html/body/div/div/form/table/tbody/tr[2]/td/span/input')
                        self.browser.switch_to.default_content()
                        break
                except:
                        self.browser.switch_to.default_content()
                        
        iter_kofile=0
        for i in range(300):
            try:
                self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='/html/body/div[3]/iframe'))
                self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='/html/body/div[4]/iframe'))
                self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='/html/body/form/div[2]/div[2]/iframe'))
                elems = self.browser.find_elements(by=By.XPATH,value="//a[@href]")
                for elem in elems:
                    if document_type=='Book, Page':
                        if book in elem.text:
                            print(elem.text)
                            elem.click()
                            break
                        elif elem.text[0].isnumeric():
                            print(elem.text)
                            elem.click()
                            break
                        for i in range(len(elem.text)):
                            if elem.text[i].isnumeric():
                                print(elem.text)
                                elem.click()
                                iter_kofile=1
                                break
                        if iter_kofile==1:
                            break
                    if document_type=='Document Number':
                        if DocumentNumber in elem.text:
                            print(elem.text)
                            elem.click()
                            break
                        elif elem.text[0].isnumeric():
                            print(elem.text)
                            elem.click()
                            break
                # try:                                    
                #     self.click_button(by=By.XPATH,value='/html/body/form/div/div/div/div/div[2]/div[2]/table/tbody/tr/td/table/tbody/tr/td[2]/div')
                # except:
                #     self.browser.find_element(by=By.XPATH,value='/html/body/form/div/div/div/div/div[2]/div[2]/table/tbody/tr[1]/td[3]/div/span/a').click()
                self.browser.switch_to.default_content()
                break
            except:
                self.browser.switch_to.default_content()
        try:
            self.browser.switch_to.default_content()
        except:
            pass
        # time.sleep(5)
        a=0
        if 'Allendale' in county:
            for i in range(100):
                try:
                    self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='/html/body/div[3]/iframe'))
                    self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='/html/body/div[5]/iframe'))
                    # self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='/html/body/form[1]/div[1]/div[2]/div/div[2]/div/iframe'))
                    self.click_button(by=By.XPATH,value='/html/body/form[1]/div[1]/div[2]/div/div[1]/table/tbody/tr[2]/td[2]/a[2]')
                    self.browser.switch_to.default_content()
                    break
                except:
                    self.browser.switch_to.default_content()
        while(1):
            a=a+1
            if a>600:
                return 'No Images Found'
            try:
                self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='/html/body/div[3]/iframe'))
                self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='/html/body/div[5]/iframe'))
                # self.browser.get_screenshot_as_file("screenshot1.png")
                self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='/html/body/form[1]/div[1]/div[2]/div/div[2]/div/iframe'))
                pages=self.browser.find_element(by=By.XPATH,value='/html/body/div[1]/div[1]/div[1]/div[2]/div/span/span[3]')
                pages=pages.text
                pages=pages.split(' of ')
                pages=pages[-1]
                print('*****',pages,'*****')
                if pages[0].isnumeric():
                    break
            except:
                self.browser.switch_to.default_content()
        order=Orders.query.filter_by(o_id=o_id).first() 
        order.no_of_pages=pages
        db.session.commit()
        
        folder_name = 'images'
        if not os.path.isdir(folder_name):
            os.makedirs(folder_name)
        pdf_images=[]
        folderName = datetime.now().strftime("%d%m%Y%H%M%S")
        imageFolderPath = os.path.join(folder_name, folderName)
        os.makedirs(imageFolderPath)
        
        pdf_path='pdf'
        if not os.path.isdir(pdf_path):
            os.makedirs(pdf_path)

        print("No. of pages found: ",pages)
                    
        for i in range(int(pages)):
            print("Getting page: ",i+1)
            path=imageFolderPath+'/'+str(i+1)+'.png'
            s=0        
            if i!=0:
                self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='/html/body/div[3]/iframe'))
                self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='/html/body/div[5]/iframe'))
                self.browser.switch_to.frame(self.browser.find_element(by=By.XPATH,value='/html/body/form[1]/div[1]/div[2]/div/div[2]/div/iframe'))
                next='/html/body/div[1]/div[1]/div[1]/div[2]/div/span/button[3]'
                self.browser.find_element(by=By.XPATH,value=next).click()
            while(s==0):
                img=self.browser.find_element(by=By.XPATH,value='/html/body/div[1]/div[1]/div[2]/div/div[1]/div/img')
                image_url=img.get_attribute('src')
                if 'jsessionid' in image_url:
                    s=1
            self.browser.switch_to.default_content()
            
            # script='window.open("https://www.google.com");'
            script='window.open("'+image_url+'");'
            self.browser.execute_script(script)
            self.browser.switch_to.window(self.browser.window_handles[1])
            print('Loading')
            # Load a page 
            # self.open_page(image_url)
            self.click_button(by=By.TAG_NAME,value='img')
            b64img = self.browser.execute_script(r'''
                            var img = document.getElementsByTagName("img")[0];
                            var canvas = document.createElement("canvas");
                            canvas.width = img.width;
                            canvas.height = img.height;
                            var ctx = canvas.getContext("2d");
                            ctx.drawImage(img, 0, 0);
                            var dataURL = canvas.toDataURL("image/png");
                            return dataURL.replace(/^data:image\/(png|jpg);base64,/, "");
                            ''')
            # close the tab
            self.browser.close()
            self.browser.switch_to.window(self.browser.window_handles[0])
            # Decode from base64, translate to bytes and write to PIL image
            img_png = Image.open(BytesIO(b64decode(b64img)))
            img=remove_watermark(img=img_png)
            # img_png.save(path)
            cv2.imwrite(path,img)
        pdf_name=image_Export_to_PDF(folder_name,imageFolderPath,folderName,pdf_path)
        shutil.rmtree(imageFolderPath)
        return pdf_name
        
def perform_actions(driver, keys):
    for i in range(0, len(keys)):
        actions = ActionChains(driver)
        actions.send_keys(keys[i])
        time.sleep(.3) #  adjust this if its going to fast\slow
        actions.perform()
    print("Actions performed!")

def delete_cache(driver):
    driver.execute_script("window.open('')")  # Create a separate tab than the main one
    driver.switch_to.window(driver.window_handles[-1])  # Switch window to the second tab
    driver.get('chrome://settings/clearBrowserData')  # Open your chrome settings.
    perform_actions(driver,Keys.TAB * 3 + Keys.LEFT + Keys.TAB * 6 + Keys.ENTER + Keys.TAB + Keys.ENTER + Keys.TAB + Keys.ENTER + Keys.TAB + Keys.ENTER + Keys.TAB * 2 + Keys.ENTER)  # Tab to the time select and key down to say "All Time" then go to the Confirm button and press Enter
    driver.close()  # Close that window
    driver.switch_to.window(driver.window_handles[0])  # Switch Selenium controls to the original tab to continue normal functionality.

#Threading
def remove_file_pdf(path):
    with app.test_request_context():
        time.sleep(15)
        try:
            os.remove(path)
        except:
            pass

def TAP(username,password,type,NET_SessionId,__zlcmid,doc,county,state,o_id):
    with app.test_request_context():
        try:
            if type=='pdf':
                start_time=datetime.now((pytz.timezone('US/Pacific')))
                doc_link='https://tapestry.fidlar.com/Tapestry2/DocDetail.aspx'
                browser = Tapestry('./chromedriver')
                browser.login(username,password)
                browser.browser.add_cookie({"name": "ASP.NET_SessionId", "value": NET_SessionId})
                browser.browser.add_cookie({"name": "__zlcmid", "value": __zlcmid})
                browser.open_page(doc_link)
                pdf_name,pages=browser.get_results(o_id)
                print(pdf_name)
                browser.close_browser()
                end_time=datetime.now((pytz.timezone('US/Pacific')))
                total_sec=end_time-start_time
                order=Orders.query.filter_by(o_id=o_id).first()
                if pdf_name[-4:]=='.pdf':
                    print("Here")
                    order.pdf=convertToBinaryData(pdf_name)
                    order.status='Completed'
                    order.total_sec=total_sec.seconds
                    order.time_completed=datetime.now((pytz.timezone('US/Pacific'))).strftime("%m-%d-%Y, %H:%M:%S")
                    db.session.commit()
                    os.remove(pdf_name)
                else:
                    order.status=pdf_name
                    order.total_sec=total_sec.seconds
                    order.time_completed=datetime.now((pytz.timezone('US/Pacific'))).strftime("%m-%d-%Y, %H:%M:%S")
                    db.session.commit()
        except:
            try:
                browser.close_browser()
            except:
                pass
            try:
                end_time=datetime.now((pytz.timezone('US/Pacific')))
                total_sec=end_time-start_time
                order=Orders.query.filter_by(o_id=o_id).first()
                order.status='Problem has Occurred'
                order.total_sec=total_sec.seconds
                order.time_completed=datetime.now((pytz.timezone('US/Pacific'))).strftime("%m-%d-%Y, %H:%M:%S")
                db.session.commit()
            except:
                print("Order Discarded")
            try:
                os.remove(pdf_name)
            except:
                pass
            

def SQ_WL(link,document_type,book,page,DocumentNumber,o_id,username,password):
    with app.test_request_context():
        try:
            start_time=datetime.now((pytz.timezone('US/Pacific')))
            browser = searchiq('/Applications/Google Chrome')
            browser.open_page(link)
            print(link)
            pdf_name=browser.search_results(document_type,book,page,DocumentNumber,o_id,Username=username,Password=password)
            print(pdf_name)
            browser.close_browser()
            order=Orders.query.filter_by(o_id=o_id).first()
            end_time=datetime.now((pytz.timezone('US/Pacific')))
            total_sec=end_time-start_time
            if pdf_name[-4:]=='.pdf':
                print("Here")
                order.pdf=convertToBinaryData(pdf_name)
                order.status='Completed'
                order.total_sec=total_sec.seconds
                order.time_completed=datetime.now((pytz.timezone('US/Pacific'))).strftime("%m-%d-%Y, %H:%M:%S")
                db.session.commit()
                os.remove(pdf_name)
            else:
                order.status=pdf_name
                order.total_sec=total_sec.seconds
                order.time_completed=datetime.now((pytz.timezone('US/Pacific'))).strftime("%m-%d-%Y, %H:%M:%S")
                db.session.commit()
        except:
            try:
                browser.close_browser()
            except:
                pass
            try:
                end_time=datetime.now((pytz.timezone('US/Pacific')))
                total_sec=end_time-start_time
                order=Orders.query.filter_by(o_id=o_id).first()
                order.status='Problem has Occurred'
                order.total_sec=total_sec.seconds
                order.time_completed=datetime.now((pytz.timezone('US/Pacific'))).strftime("%m-%d-%Y, %H:%M:%S")
                db.session.commit()
            except:
                print("Order Discarded")
            try:
                os.remove(pdf_name)
            except:
                pass
    
def SQ_WOL(link,document_type,book,page,DocumentNumber,o_id):
    with app.test_request_context():
        try:
            start_time=datetime.now((pytz.timezone('US/Pacific')))
            browser = searchiq('/Applications/Google Chrome')
            browser.open_page(link)
            print(link)
            pdf_name=browser.search_results(document_type,book,page,DocumentNumber,o_id)
            print(pdf_name)
            browser.close_browser()
            order=Orders.query.filter_by(o_id=o_id).first()
            end_time=datetime.now((pytz.timezone('US/Pacific')))
            total_sec=end_time-start_time
            if pdf_name[-4:]=='.pdf':
                print("Here")
                order.pdf=convertToBinaryData(pdf_name)
                order.status='Completed'
                order.total_sec=total_sec.seconds
                order.time_completed=datetime.now((pytz.timezone('US/Pacific'))).strftime("%m-%d-%Y, %H:%M:%S")
                db.session.commit()
                os.remove(pdf_name)
            else:
                order.status=pdf_name
                order.total_sec=total_sec.seconds
                order.time_completed=datetime.now((pytz.timezone('US/Pacific'))).strftime("%m-%d-%Y, %H:%M:%S")
                db.session.commit()
        except:
            try:
                browser.close_browser()
            except:
                pass
            try:
                end_time=datetime.now((pytz.timezone('US/Pacific')))
                total_sec=end_time-start_time
                order=Orders.query.filter_by(o_id=o_id).first()
                order.total_sec=total_sec.seconds
                order.status='Problem has Occurred'
                order.time_completed=datetime.now((pytz.timezone('US/Pacific'))).strftime("%m-%d-%Y, %H:%M:%S")
                db.session.commit()
            except:
                print("Order Discarded")
            try:
                os.remove(pdf_name)
            except:
                pass

def DP_WL(username,password,document_type,county,DocumentNumber,book,page,o_id):
    with app.test_request_context():
        start_time=datetime.now((pytz.timezone('US/Pacific')))
        order=Orders.query.filter_by(o_id=o_id).first()
        try:
            pdf_name=doxpopsaveimages(username,password,document_type,county,DocumentNumber,book,page,county,o_id)
            end_time=datetime.now((pytz.timezone('US/Pacific')))
            total_sec=end_time-start_time
            if pdf_name[-4:]=='.pdf':
                print("Here")
                order.pdf=convertToBinaryData(pdf_name)
                order.status='Completed'
                order.total_sec=total_sec.seconds
                order.time_completed=datetime.now((pytz.timezone('US/Pacific'))).strftime("%m-%d-%Y, %H:%M:%S")
                db.session.commit()
                os.remove(pdf_name)
            else:
                order.status=pdf_name
                order.total_sec=total_sec.seconds
                order.time_completed=datetime.now((pytz.timezone('US/Pacific'))).strftime("%m-%d-%Y, %H:%M:%S")
                db.session.commit()
        except:
            try:
                end_time=datetime.now((pytz.timezone('US/Pacific')))
                total_sec=end_time-start_time
                order=Orders.query.filter_by(o_id=o_id).first()
                order.status='Problem has Occurred'
                order.total_sec=total_sec.seconds
                order.time_completed=datetime.now((pytz.timezone('US/Pacific'))).strftime("%m-%d-%Y, %H:%M:%S")
                db.session.commit()
            except:
                print("Order Discarded")
            try:
                os.remove(pdf_name)
            except:
                pass
        

def US_WOL(link,document_type,book,page,DocumentNumber,o_id):
    with app.test_request_context():
        start_time=datetime.now((pytz.timezone('US/Pacific')))
        try:
            browser = Uslandrecord('/Applications/Google Chrome')
            browser.open_page(link)
            pdf_name=browser.search_results(document_type,DocumentNumber,book,page,o_id)
            print(pdf_name)
            browser.close_browser()
            order=Orders.query.filter_by(o_id=o_id).first()
            end_time=datetime.now((pytz.timezone('US/Pacific')))
            total_sec=end_time-start_time
            if pdf_name[-4:]=='.pdf':
                print("Here")
                order.pdf=convertToBinaryData(pdf_name)
                order.status='Completed'
                order.total_sec=total_sec.seconds
                order.time_completed=datetime.now((pytz.timezone('US/Pacific'))).strftime("%m-%d-%Y, %H:%M:%S")
                db.session.commit()
                os.remove(pdf_name)
            else:
                order.status=pdf_name
                order.total_sec=total_sec.seconds
                order.time_completed=datetime.now((pytz.timezone('US/Pacific'))).strftime("%m-%d-%Y, %H:%M:%S")
                db.session.commit()
        except:
            try:
                browser.close_browser()
            except:
                pass
            try:
                end_time=datetime.now((pytz.timezone('US/Pacific')))
                total_sec=end_time-start_time
                order=Orders.query.filter_by(o_id=o_id).first()
                order.status='Problem has Occurred'
                order.total_sec=total_sec.seconds
                order.time_completed=datetime.now((pytz.timezone('US/Pacific'))).strftime("%m-%d-%Y, %H:%M:%S")
                db.session.commit()
            except:
                print("Order Discarded")
            try:
                os.remove(pdf_name)
            except:
                pass

def KF_WOL(link,document_type,book,page,DocumentNumber,o_id):
    with app.test_request_context():
        try:
            start_time=datetime.now((pytz.timezone('US/Pacific')))
            browser = kofiletech('/Applications/Google Chrome')
            links='https://countyfusion1.kofiletech.us/'
            browser.open_page(links)
            print(links)
            pdf_name=browser.search_results(link,document_type,book,page,DocumentNumber,o_id)
            print(pdf_name)
            browser.close_browser()
            end_time=datetime.now((pytz.timezone('US/Pacific')))
            total_sec=end_time-start_time
            order=Orders.query.filter_by(o_id=o_id).first()
            if pdf_name[-4:]=='.pdf':
                print("Here")
                order.pdf=convertToBinaryData(pdf_name)
                order.status='Completed'
                order.total_sec=total_sec.seconds
                order.time_completed=datetime.now((pytz.timezone('US/Pacific'))).strftime("%m-%d-%Y, %H:%M:%S")
                db.session.commit()
                os.remove(pdf_name)
            else:
                order.status=pdf_name
                order.total_sec=total_sec.seconds
                order.time_completed=datetime.now((pytz.timezone('US/Pacific'))).strftime("%m-%d-%Y, %H:%M:%S")
                db.session.commit()
        except:
            try:
                browser.close_browser()
            except:
                pass
            end_time=datetime.now((pytz.timezone('US/Pacific')))
            total_sec=end_time-start_time
            try:
                order=Orders.query.filter_by(o_id=o_id).first()
                order.status='Problem has Occurred'
                order.total_sec=total_sec.seconds
                order.time_completed=datetime.now((pytz.timezone('US/Pacific'))).strftime("%m-%d-%Y, %H:%M:%S")
                db.session.commit()
            except:
                print("Order Discarded")
            try:
                os.remove(pdf_name)
            except:
                pass
            
            
def GS_WL(username,password,document_type,county,DocumentNumber,book,page,o_id,a,type_search,link):
    with app.test_request_context():
        start_time=datetime.now((pytz.timezone('US/Pacific')))
        order=Orders.query.filter_by(o_id=o_id).first()
        order.remark=type_search
        order.no_of_pages=a
        db.session.commit()
        order=Orders.query.filter_by(o_id=o_id).first()
        try:
            print('Here')
            browser = GSCCCA('/Applications/Google Chrome')
            lik='https://www.gsccca.org'
            browser.open_page(lik)
            
            browser.login(username,password)
            time.sleep(0.5)
            # browser.browser.get_screenshot_as_file("screenshot1.png")
            pdf_name=browser.search_results(link,book,page,a,type_search,o_id)
            end_time=datetime.now((pytz.timezone('US/Pacific')))
            total_sec=end_time-start_time
            try:
                browser.close_browser()
            except:
                pass
            if pdf_name[-4:]=='.pdf':
                print("Here")
                order.pdf=convertToBinaryData(pdf_name)
                order.status='Completed'
                order.total_sec=total_sec.seconds
                order.time_completed=datetime.now((pytz.timezone('US/Pacific'))).strftime("%m-%d-%Y, %H:%M:%S")
                db.session.commit()
                os.remove(pdf_name)
            else:
                order.status=pdf_name
                order.total_sec=total_sec.seconds
                order.time_completed=datetime.now((pytz.timezone('US/Pacific'))).strftime("%m-%d-%Y, %H:%M:%S")
                db.session.commit()
        except:
            try:
                browser.close_browser()
            except:
                pass
            try:
                end_time=datetime.now((pytz.timezone('US/Pacific')))
                total_sec=end_time-start_time
                order=Orders.query.filter_by(o_id=o_id).first()
                order.status='Problem has Occurred'
                order.total_sec=total_sec.seconds
                order.time_completed=datetime.now((pytz.timezone('US/Pacific'))).strftime("%m-%d-%Y, %H:%M:%S")
                db.session.commit()
            except:
                print("Order Discarded")
            try:
                os.remove(pdf_name)
            except:
                pass
            

def WV_WOL(link,document_type,book,page,DocumentNumber,o_id,west_virginia_type_search):
    with app.test_request_context():
        try:
            start_time=datetime.now((pytz.timezone('US/Pacific')))
            browser = West_Virginia('/Applications/Google Chrome')
            browser.open_page(link)
            pdf_name=browser.search_results(west_virginia_type_search,book,page,o_id)
            print(pdf_name)
            browser.close_browser()
            end_time=datetime.now((pytz.timezone('US/Pacific')))
            total_sec=end_time-start_time
            order=Orders.query.filter_by(o_id=o_id).first()
            order.remark=west_virginia_type_search
            db.session.commit()
            order=Orders.query.filter_by(o_id=o_id).first()
            if pdf_name[-4:]=='.pdf':
                print("Here")
                order.pdf=convertToBinaryData(pdf_name)
                order.status='Completed'
                order.total_sec=total_sec.seconds
                order.time_completed=datetime.now((pytz.timezone('US/Pacific'))).strftime("%m-%d-%Y, %H:%M:%S")
                db.session.commit()
                os.remove(pdf_name)
            else:
                order.status=pdf_name
                order.total_sec=total_sec.seconds
                order.time_completed=datetime.now((pytz.timezone('US/Pacific'))).strftime("%m-%d-%Y, %H:%M:%S")
                db.session.commit()
        except:
            try:
                browser.close_browser()
            except:
                pass
            try:
                end_time=datetime.now((pytz.timezone('US/Pacific')))
                total_sec=end_time-start_time
                order=Orders.query.filter_by(o_id=o_id).first()
                order.status='Problem has Occurred'
                order.remark=west_virginia_type_search
                order.total_sec=total_sec.seconds
                order.time_completed=datetime.now((pytz.timezone('US/Pacific'))).strftime("%m-%d-%Y, %H:%M:%S")
                db.session.commit()
            except:
                print("Order Discarded")
            try:
                os.remove(pdf_name)
            except:
                pass
            
def RSH_WOL(link,document_type,book,page,DocumentNumber,o_id,county):
    with app.test_request_context():
        try:
            start_time=datetime.now((pytz.timezone('US/Pacific')))
            browser = Record_hub('/Applications/Google Chrome')
            login_portal_link='https://recordhub.cottsystems.com/Portal/Account/Login?returnUrl=/Portal/SearchSites/Selection'
            global record_hub_search_iter
            username=user_list[record_hub_search_iter]
            if record_hub_search_iter==len(user_list)-1:
                record_hub_search_iter=0
            else:
                record_hub_search_iter=record_hub_search_iter+1
            password='Realdoc1234$'
            browser.open_page(login_portal_link)
            browser.login(username,password)
            print("Logged IN")
            pdf_name=browser.search_results(county,book,page,DocumentNumber,document_type,o_id)
            browser.logout()
            print(pdf_name)
            browser.close_browser()
            end_time=datetime.now((pytz.timezone('US/Pacific')))
            total_sec=end_time-start_time
            order=Orders.query.filter_by(o_id=o_id).first()
            if pdf_name[-4:]=='.pdf':
                print("Here")
                order.pdf=convertToBinaryData(pdf_name)
                order.status='Completed'
                order.total_sec=total_sec.seconds
                order.time_completed=datetime.now((pytz.timezone('US/Pacific'))).strftime("%m-%d-%Y, %H:%M:%S")
                db.session.commit()
                os.remove(pdf_name)
            else:
                order.status=pdf_name
                order.total_sec=total_sec.seconds
                order.time_completed=datetime.now((pytz.timezone('US/Pacific'))).strftime("%m-%d-%Y, %H:%M:%S")
                db.session.commit()
        except:
            try:
                browser.logout()
            except:
                pass
            try:
                browser.close_browser()
            except:
                pass
            try:
                end_time=datetime.now((pytz.timezone('US/Pacific')))
                total_sec=end_time-start_time
                order=Orders.query.filter_by(o_id=o_id).first()
                order.status='Problem has Occurred'
                order.total_sec=total_sec.seconds
                order.time_completed=datetime.now((pytz.timezone('US/Pacific'))).strftime("%m-%d-%Y, %H:%M:%S")
                db.session.commit()
            except:
                print("Order Discarded")
            try:
                os.remove(pdf_name)
            except:
                pass
            
def LM_WOL(link,document_type,book,page,DocumentNumber,o_id,county):
    with app.test_request_context():
        try:
            start_time=datetime.now((pytz.timezone('US/Pacific')))
            browser = Land_mark('/Applications/Google Chrome')
            browser.open_page(link)
            pdf_name=browser.search_results(book,page,DocumentNumber,document_type,o_id)
            print(pdf_name)
            browser.close_browser()
            order=Orders.query.filter_by(o_id=o_id).first()
            end_time=datetime.now((pytz.timezone('US/Pacific')))
            total_sec=end_time-start_time
            if pdf_name[-4:]=='.pdf':
                print("Here")
                order.pdf=convertToBinaryData(pdf_name)
                order.status='Completed'
                order.total_sec=total_sec.seconds
                order.time_completed=datetime.now((pytz.timezone('US/Pacific'))).strftime("%m-%d-%Y, %H:%M:%S")
                db.session.commit()
                os.remove(pdf_name)
            else:
                order.status=pdf_name
                order.total_sec=total_sec.seconds
                order.time_completed=datetime.now((pytz.timezone('US/Pacific'))).strftime("%m-%d-%Y, %H:%M:%S")
                db.session.commit()
        except:
            try:
                browser.logout()
            except:
                pass
            try:
                browser.close_browser()
            except:
                pass
            try:
                end_time=datetime.now((pytz.timezone('US/Pacific')))
                total_sec=end_time-start_time
                order=Orders.query.filter_by(o_id=o_id).first()
                order.status='Problem has Occurred'
                order.total_sec=total_sec.seconds
                order.time_completed=datetime.now((pytz.timezone('US/Pacific'))).strftime("%m-%d-%Y, %H:%M:%S")
                db.session.commit()
            except:
                print("Order Discarded")
            try:
                os.remove(pdf_name)
            except:
                pass

if __name__ == '__main__':
    app.run(debug=True) 
