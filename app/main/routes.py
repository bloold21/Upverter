from flask import render_template, flash, redirect, url_for, current_app
from flask import request, g
from werkzeug.urls import url_parse
from app.main import bp
from app import db
from app.main.forms import EditProfileForm, EmptyForm,  PostForm
from app.main.forms import SearchForm
from app.models import User, Post
from flask_login import current_user, login_user, logout_user
from flask_login import login_required
from datetime import datetime
from langdetect import detect, LangDetectException
from flask import jsonify
from app.translate import translate

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        try:
            language = detect(form.post.data)
        except LangDetectException:
            language = ''
        post = Post(body=form.post.data, author=current_user,
                    language=language)
        db.session.add(post)
        db.session.commit()
        flash('The post is submitted')
        return redirect(url_for('main.index'))

    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
                page, current_app.config['POST_PER_PAGE'], False)
    next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None
    
    return render_template('index.html', title='Home Page', posts=posts.items,
                            form=form, next=next_url, prev=prev_url)



@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User %s not found'%username)
            return redirect(url_for('main.index'))
        if user==current_user.username:
            flash('YOu cannot follow yourself')
            return redirect(url_for('main.index'))
        current_user.follow(user)
        db.session.commit()
        flash('Your are follwing %s' %username)
        return redirect(url_for('main.user',username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User %s not found' %username)
            return redirect(url_for('main.index'))
        if user.username == current_user.username:
            flash ('You cannot unfollow yourself')
            return redirect(url_for('main.index'))
        current_user.unfollow(user)
        db.session.commit()
        flash('Your are not following %s' %username)
        return redirect(url_for('main.user', username=current_user.username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = EmptyForm()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page,
                            current_app.config['POST_PER_PAGE'], False)
    next_url = url_for('main.user', username=username, page=posts.next_num) \
            if posts.has_next else None
    prev_url = url_for('main.user', username=username, page=posts.prev_num) \
            if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                            form=form, next_url=next_url, prev_url=prev_url)


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('You change have been saved')
        return redirect(url_for('main.user',username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
                                page, current_app.config['POST_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='Explore', posts=posts.items,
                            next=next_url, prev=prev_url)


@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                        request.form['source_language'],
                                        request.form['dest_language'])})


@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page,
                            current_app.config['POST_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page+1)\
                if total > page*current_app.config['POST_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page-1)\
                if page>1 else None
    return render_template('search.html', title='Search', posts=posts,
                            next_url=next_url, prev_url=prev_url)


@bp.route('/user/<username>/popup')
@login_required
def user_popup(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = EmptyForm()
    return render_template('user_popup.html', user=user, form=form)