from flask import Flask, request, url_for, render_template, abort, send_from_directory, jsonify, make_response
from blog_insert import BlogInsert
from flask_paginate import Pagination, get_page_parameter
import pymongo
import os
from datetime import datetime
from urllib.parse import urlparse
from dummy_article import TObject

app = Flask(__name__)
app.config.from_object('config.ProductionConfig')
app.config.from_json('config.json')
app.template_folder = app.config.get("TEMPLATE_FOLDER_PATH")
PER_PAGE = 10


def data_collect(table):
    uri = app.config.get("MONGO_URI")
    database = app.config.get("MONGO_DATABASE")
    client = pymongo.MongoClient(uri)
    db = client[database]
    return db[table]


@app.route('/images/<path:filename>')
def custom_images(filename):
    path = app.config['CUSTOM_IMAGES_PATH']
    gallery = app.config.get("MONGO_GALLERY_TABLE")
    gallery_col = data_collect(gallery)
    gallery = gallery_col.find_one({"filename": filename})

    if not gallery:
        abort(404)

    image_path = os.path.join(path, gallery["filepath"])
    return send_from_directory(image_path, filename)


@app.route('/')
def home_page():
    blog = app.config.get("MONGO_BLOG_TABLE")
    blog_col = data_collect(blog)
    page = request.args.get("page", type=int, default=1)

    data_dict = {"blog_code": app.config['BLOG_CODE']}
    total_story = blog_col.find(data_dict).count(True)
    pagination = Pagination(page=page, total=total_story, search=False, record_name='users', css_framework='bootstrap4')

    # No Blog found
    if not (1 <= page <= pagination.total_pages):
        return render_template('public/no_result.html')

    articles = blog_col.find(data_dict) \
        .sort("blog_id", -1) \
        .skip(PER_PAGE * (page - 1)) \
        .limit(PER_PAGE)

    return render_template('home_page.html',
                           articles=articles,
                           pagination=pagination)


@app.route('/category/<category_url>/')
@app.route('/category/<category_url>')
def category_page(category_url):
    blog = app.config.get("MONGO_BLOG_TABLE")
    blog_col = data_collect(blog)
    page = request.args.get("page", type=int, default=1)

    data_dict = {"blog_code": app.config['BLOG_CODE'], "category_url": category_url}
    total_story = blog_col.find(data_dict).count(True)
    pagination = Pagination(page=page, total=total_story, search=False, record_name='users', css_framework='bootstrap4')

    # No Blog found
    if not (1 <= page <= pagination.total_pages):
        return render_template('public/no_result.html')

    articles = blog_col.find(data_dict)\
        .sort("blog_id", -1)\
        .skip(PER_PAGE*(page-1))\
        .limit(PER_PAGE)

    category_table = app.config.get("MONGO_CATEGORY_TABLE")
    category_col = data_collect(category_table)
    category = category_col.find_one({"url": category_url})

    if not category:
        return render_template('public/no_result.html')

    return render_template('category_page.html',
                           articles=articles,
                           category=category,
                           pagination=pagination)


@app.route('/category/<category_url>/<blog_url>/')
@app.route('/category/<category_url>/<blog_url>')
def blog_page(category_url, blog_url):
    blog = app.config.get("MONGO_BLOG_TABLE")
    blog_col = data_collect(blog)
    article = blog_col.find_one({"url": blog_url})

    if not article:
        abort(404)

    return render_template('blog_page.html', article=article)


@app.route("/sitemap.xml")
def sitemap_page():
    host_components = urlparse(request.host_url)
    host_base = host_components.scheme + "://" + host_components.netloc
    dynamic_urls = list()

    home_page = {"loc": host_base,
                 "lastmod": datetime.now().strftime("%Y-%m-%d")}
    dynamic_urls.append(home_page)

    # Dynamic routes - Blog
    blog = app.config.get("MONGO_BLOG_TABLE")
    blog_col = data_collect(blog)
    data_dict = {"blog_code": app.config['BLOG_CODE']}
    articles = blog_col.find(data_dict)

    for article in articles:
        url = {
            "loc": f"{host_base}/category/{article['category_url']}/{article['url']}",
            "lastmod": article['date']
        }
        dynamic_urls.append(url)

    # Dynamic routes - Category
    category = app.config.get("MONGO_CATEGORY_TABLE")
    category_col = data_collect(category)
    categories = category_col.find()

    for rec in categories:
        url = {
            "loc": f"{host_base}/category/{rec['url']}",
            "lastmod": datetime.now().strftime("%Y-%m-%d")
        }
        dynamic_urls.append(url)

    xml_sitemap = render_template("public/sitemap.xml", dynamic_urls=dynamic_urls, host_base=host_base)
    response = make_response(xml_sitemap)
    response.headers["Content-Type"] = "application/xml"

    return response


@app.errorhandler(404)
def page_not_found(error):
    return render_template('public/404.html', title='404'), 404


@app.cli.command('blog_update')
def blog_update():
    path = app.config.get("IMPORT_PATH")
    blog_code = app.config.get("BLOG_CODE")
    blog = app.config.get("MONGO_BLOG_TABLE")
    col = data_collect(blog)
    params = "blog_id"
    file_suffix = "_{0}_blog.json".format(blog_code)

    bi = BlogInsert(path, col, params, file_suffix)
    bi.trigger_import()


@app.cli.command('category_update')
def category_update():
    path = app.config.get("IMPORT_PATH")
    category = app.config.get("MONGO_CATEGORY_TABLE")
    col = data_collect(category)
    params = "category_id"
    file_suffix = "_category.json"

    bi = BlogInsert(path, col, params, file_suffix)
    bi.trigger_import()


@app.cli.command('gallery_update')
def gallery_update():
    path = app.config.get("IMPORT_PATH")
    gallery = app.config.get("MONGO_GALLERY_TABLE")
    col = data_collect(gallery)
    params = "gallery_id"
    file_suffix = "_gallery.json"

    bi = BlogInsert(path, col, params, file_suffix)
    bi.trigger_import()
