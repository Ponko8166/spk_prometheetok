# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import render_template, redirect, request, url_for
import numpy as np
from flask_paginate import get_page_parameter, Pagination
from flask_login import (
    current_user,
    login_user,
    logout_user
)
from flask_dance.contrib.github import github

from apps import db, login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm, CreateAccountForm
from apps.authentication.models import tabelAlternative, Users, tabelRanking, tabelKriteria

from apps.authentication.util import verify_pass


@blueprint.route('/')
def route_default():
    return redirect(url_for('authentication_blueprint.login'))

# Login & Registration

@blueprint.route("/github")
def login_github():
    """ Github login """
    if not github.authorized:
        return redirect(url_for("github.login"))

    res = github.get("/user")
    return redirect(url_for('home_blueprint.index'))

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:

        # read form data
        user_id  = request.form['username'] # we can have here username OR email
        password = request.form['password']

        # Locate user
        user = Users.find_by_username(user_id)

        # if user not found
        if not user:

            user = Users.find_by_email(user_id)

            if not user:
                return render_template( 'accounts/login.html',
                                        msg='Unknown User or Email',
                                        form=login_form)

        # Check the password
        if verify_pass(password, user.password):

            login_user(user)
            return redirect(url_for('authentication_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template('accounts/login.html',
                               msg='Wrong user or password',
                               form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form)
    return redirect(url_for('home_blueprint.index'))


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username = request.form['username']
        email = request.form['email']

        # Check usename exists
        user = Users.query.filter_by(username=username).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Username already registered',
                                   success=False,
                                   form=create_account_form)

        # Check email exists
        user = Users.query.filter_by(email=email).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Email already registered',
                                   success=False,
                                   form=create_account_form)

        # else we can create the user
        user = Users(**request.form)
        db.session.add(user)
        db.session.commit()

        # Delete user from session
        logout_user()

        return render_template('accounts/register.html',
                               msg='User created successfully.',
                               success=True,
                               form=create_account_form)

    else:
        return render_template('accounts/register.html', form=create_account_form)


@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication_blueprint.login')) 

# Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500


# START Pagination function
def paginate(query, page, per_page):
    offset = (page - 1) * per_page
    return query.offset(offset).limit(per_page).all()
# END Pagination function

# START Retrieve Update Tabel Kriteria
@blueprint.route('/kriteria')
def retrieve_kriteria():
    records = tabelKriteria.query.all()
    return render_template('/home/tabel-kriteria.html', records=records)
# END Retrieve Update Tabel Kriteria


# START CRUD Tabel Alternatif

@blueprint.route('/alternatif/create', methods=['POST', 'GET'])
def create_alternatif():
    # mendapatkan data dari form di HTML
    if request.method == 'POST':
        alternatif_akun = request.form['alternatif_akun']
        total_follower = int(request.form['total_follower'].replace(',', ''))
        total_likes = int(request.form['total_likes'].replace(',', ''))
        overall_engagement = "{:.4f}".format(float(request.form['overall_engagement'].rstrip('%'))/100)
        likes_rate = "{:.4f}".format(float(request.form['likes_rate'].rstrip('%'))/100)
        shares_rate = "{:.4f}".format(float(request.form['shares_rate'].rstrip('%'))/100)
        average_view = int(request.form['average_view'].replace(',', ''))
        average_likes = int(request.form['average_likes'].replace(',', ''))
        average_share = int(request.form['average_share'].replace(',', ''))
        harga = int(request.form['average_share'].replace('%', ''))
        keterangan = request.form['keterangan']

        tabelAlternative_data = tabelAlternative(alternatif_akun=alternatif_akun, 
                              total_follower=total_follower, 
                              total_likes=total_likes, 
                              overall_engagement=overall_engagement, 
                              likes_rate=likes_rate, 
                              shares_rate=shares_rate, 
                              average_view=average_view, 
                              average_likes=average_likes, 
                              average_share=average_share,
                              keterangan=keterangan,
                              harga=harga)
        
        db.session.add(tabelAlternative_data)
        db.session.commit()
        return redirect(url_for('authentication_blueprint.retrieve_alternatif'))
    return redirect(url_for('authentication_blueprint.retrieve_alternatif'))

@blueprint.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    record = tabelAlternative.query.get_or_404(id)
    if request.method == 'POST':
        record.alternatif_akun = request.form['alternatif_akun']
        record.total_follower = request.form['total_follower']
        record.total_likes = request.form['total_likes']
        record.overall_engagement = request.form['overall_engagement']
        record.likes_rate = request.form['likes_rate']
        record.shares_rate = request.form['shares_rate']
        record.average_view = request.form['average_view']
        record.average_likes = request.form['average_likes']
        record.average_share = request.form['average_share']
        record.harga = request.form['harga']
        record.keterangan = request.form['keterangan']
        db.session.commit()
        return redirect(url_for('authentication_blueprint.retrieve_alternatif'))
    return render_template('/home/update_alternatif.html', record=record)

@blueprint.route('/delete/<int:id>')
def delete(id):
    record = tabelAlternative.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for('authentication_blueprint.retrieve_alternatif'))

@blueprint.route('/alternatif')
def retrieve_alternatif():
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Jumlah record per halaman
    records = tabelAlternative.query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template("/home/tabel-alternatif.html", records=records)

# END CRUD Tabel Alternatif


# START Perhitungan metode
@blueprint.route('/perangkingan')
def perhitungan():

    jumlah_records = len(tabelAlternative.query.all()) # Mendapatkan jumlah record pada tabel tabelAlternative
    if jumlah_records < 2: # jika jumlah_records kurang dari 2
        return redirect(url_for('authentication_blueprint.retrieve_alternatif')) # ke retrieve_alternatif()

    try:        
        db.session.query(tabelRanking).delete() # Menghapus seluruh isi tabel_peringkat
        db.session.commit()
    except Exception as e:        
        db.session.rollback() # Notif ika terjadi kesalahan saat menghapus
        return redirect(url_for('authentication_blueprint.internal_error'))

    
    data = tabelAlternative.query.all() # mendapatakan data dari "tabel_alternatif"
    
    # membuat matriks alternatif
    data_matrix = np.array([[row.total_follower, row.total_likes, row.overall_engagement,
                             row.likes_rate, row.shares_rate, row.average_view, row.average_likes,
                             row.average_share, row.harga] for row in data])
    
    jum_criteria = data_matrix.shape[1] 
    jum_alternatives = data_matrix.shape[0]
    cost_benefit = [True, True, True, True, True, True, True, True, False]  # True = benefit/maksimasi | False = cost/minimasi
    nilai_preferensi = np.zeros((jum_alternatives, jum_alternatives, jum_criteria)) # Menyiapkan matriks untuk nilai preferensi (P)

    for k in range(jum_criteria):
        for i in range(jum_alternatives):
            for j in range(jum_alternatives):                
                if cost_benefit[k]: # percabagan apakah tipe kriteria bertipe benefit/cost
                    if (data_matrix[i, k] - data_matrix[j, k])>0: # jika (Aik - Ajk)>0
                        nilai_preferensi[i, j, k] = 1
                    else:
                        nilai_preferensi[i, j, k] = 0                    
                else:
                    if (data_matrix[i, k] - data_matrix[j, k])<=0: # jika (Aik - Ajk)<=0
                        nilai_preferensi[i, j, k] = 1
                    else:
                        nilai_preferensi[i, j, k] = 0
                    

    indeks_preferensi_multikriteria = np.mean(nilai_preferensi, axis=2)
    leaving_flow = np.sum(indeks_preferensi_multikriteria, axis=1)*(1/(jum_criteria-1))
    entering_flow = np.sum(indeks_preferensi_multikriteria, axis=0)*(1/(jum_criteria-1))
    leaving_flow = np.round(leaving_flow, 2)
    entering_flow = np.round(entering_flow, 2)
    net_flow = leaving_flow - entering_flow
    net_flow = np.round(net_flow, 2)

    ranking = np.argsort(-net_flow)

    for i, index in enumerate(ranking):
        # Mendapatkan entri alternatif berdasarkan indeks
        alternatif = data[index]
        # Membuat entri record ke tabel_peringkat
        tabelPerangkingan = tabelRanking(peringkat=i+1, 
                                         alternatif_akun=alternatif.alternatif_akun, 
                                         alternatif_id=alternatif.id,
                                         leaving_flow=leaving_flow[index],
                                         entering_flow=entering_flow[index],
                                         net_flow=net_flow[index]
                                         )
        # Menambahkan ke session dan commit
        db.session.add(tabelPerangkingan)
        db.session.commit()
    
    view_columns = [tabelRanking.peringkat, tabelRanking.alternatif_akun,
                tabelRanking.leaving_flow, tabelRanking.entering_flow,
                tabelRanking.net_flow,
                tabelAlternative.total_follower, tabelAlternative.overall_engagement,
                tabelAlternative.average_view, tabelAlternative.harga,
                tabelAlternative.keterangan, tabelRanking.alternatif_id]
    data_ranking = db.session.query(*view_columns).join(tabelAlternative, tabelRanking.alternatif_id == tabelAlternative.id)
    return render_template("/home/tabel_perangkingan.html", data_ranking=data_ranking)
# END Perhitungan metode

# START Delete tabel peringkat
@blueprint.route('/delete_data_peringkat')
def delete_data_peringkat():
    db.session.query(tabelRanking).delete() # Menghapus seluruh isi tabel_peringkat
    db.session.commit()
    return render_template("/home/tabel_perangkingan.html")
# END Delete tabel peringkat

# START Delete tabel peringkat
@blueprint.route('/delete_data_alternatif')
def delete_data_alternatif():
    db.session.query(tabelAlternative).delete() # Menghapus seluruh isi tabel_peringkat
    db.session.commit()
    return redirect(url_for('authentication_blueprint.retrieve_alternatif'))
# END Delete tabel peringkat