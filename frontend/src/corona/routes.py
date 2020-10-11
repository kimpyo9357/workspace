from flask import render_template, request, redirect, url_for, Response
from flask_sqlalchemy import get_debug_queries

from corona import app, config
from corona.models import db
from corona.models.UploadedFile import UploadedFile
from corona.models.DailyConfirmed import DailyConfirmed

import os
import csv
import codecs
import shutil
from werkzeug.utils import secure_filename
from hashlib import md5


import pyzbar.pyzbar as pyzbar  # pip install pyzbar
import numpy              # pip install numpy
import cv2

import pandas as pd
from io import StringIO

@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('db_read'))
    
@app.route('/self_insert/', methods=['GET', 'POST'])
def db_create():
    if request.method == 'GET':
        return render_template("self_insert.html", msg=request.args.get('msg', ''))
    date = request.form['date'].split()[0]
    today_confirmed = DailyConfirmed(date=request.form['date'], count=request.form['count'])
    db.session.add(today_confirmed)
    db.session.commit()
    return redirect(url_for('db_read'))

@app.route('/QR_insert/', methods=['GET'])
def db_read():
    data_list = DailyConfirmed.query.all()
    if not data_list:
        return redirect(url_for('db_create', msg="데이터가 없습니다. 정보를 입력해주세요"))
    for obj in data_list:
        obj.date = obj.date.strftime("%y년 %-m월 %-d일") 
    return render_template("QR_insert.html", data_list=data_list)

@app.route('/Log/', methods=['GET'])
def db_log():
    data_list = DailyConfirmed.query.all()
    if not data_list:
        return redirect(url_for('db_create', msg="데이터가 없습니다. 정보를 입력해주세요"))
    for obj in data_list:
        obj.date = obj.date.strftime("%y년 %-m월 %-d일 %H:%M") 
    return render_template("Log.html", data_list=data_list)

@app.route('/Headcount/', methods=['GET'])
def db_headcount():
    data_list = DailyConfirmed.query.all()
    if not data_list:
        return redirect(url_for('db_create', msg="데이터가 없습니다. 정보를 입력해주세요"))
    for obj in data_list:
        obj.date = obj.date.strftime("%y년 %-m월 %-d일") 
    return render_template("Headcount.html", data_list=data_list)

@app.route('/edit/<date>', methods=['GET'])
def db_update(date):
    target = DailyConfirmed.query.filter_by(date=date).first()
    if not target:
        return redirect(url_for('db_create', msg="해당 날짜의 데이터가 없어 수정이 불가능합니다."))
    target.count = request.args.get('count', target.count)
    db.session.commit()
    return redirect(url_for('db_read'))

@app.route('/remove_all_data/', methods=['GET'])
def db_delete():
    db.session.query(DailyConfirmed).delete()
    db.session.query(UploadedFile).delete()
    db.session.commit()
    shutil.rmtree(app.config['UPLOAD_FOLDER_LOCATION'])
    return redirect(url_for('db_create', msg="초기화를 완료하였습니다."))

@app.route('/upload/', methods=['POST'])
def upload_file():
    if request.method != 'POST':
        return redirect(url_for('db_create', msg="올바른 방법으로 파일을 업로드하세요"))
    elif 'profile' not in request.files:
        return redirect(url_for('db_create', msg="업로드 할 파일이 없습니다."))
    
    file = request.files['profile']
    if file.filename == '':
        return redirect(url_for('db_create', msg="업로드 할 파일이 없습니다."))

    if file and config.allowed_file(file.filename):
        def decode(img):
            decodedObjects = pyzbar.decode(img)

            for obj in decodedObjects:
                print('Type : ', obj.type)
                print('Data : ', obj.data, '\n')
            return decodedObjects

        npimg = numpy.fromfile(file, numpy.uint8)
         # convert numpy array to image
        img = cv2.imdecode(npimg, cv2.IMREAD_GRAYSCALE)
        pyzbar.decode(img)
        return redirect(url_for('db_read', msg="성공"))
    return redirect(url_for('db_create', msg="파일을 업로드 에러, 다시 시도해주세요."))
    
@app.route('/export/')
def export_csv():
    queryset = DailyConfirmed.query
    # Pandas가 SQL을 읽도록 만들어주기
    df = pd.read_sql(queryset.statement, queryset.session.bind) 
    output = StringIO()
    # 한글 인코딩 위해 UTF-8 with BOM 설정해주기
    output.write(u'\ufeff') 
    df.to_csv(output)
    # CSV 파일 형태로 브라우저가 파일다운로드라고 인식하도록 만들어주기
    response = Response(
        output.getvalue(),
        mimetype="text/csv",
        content_type='application/octet-stream',
    )
    # 다운받았을때의 파일 이름 지정해주기
    response.headers["Content-Disposition"] = "attachment; filename=export.csv" 
    return response