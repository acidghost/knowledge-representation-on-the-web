#!/usr/bin/env python

from flask import Flask, render_template, url_for, request, jsonify
from flask.ext.assets import Environment, Bundle
from SPARQLWrapper import SPARQLWrapper, RDF, JSON
import requests


# setup app
app = Flask(__name__)
assets = Environment(app)

# setup frontend code compilers
coffee = Bundle('coffee/**/*', 'coffee/main.coffee',
            filters='coffeescript')
js = Bundle('components/jquery/dist/jquery.js',
            'components/angular/angular.js',
            'components/angular-bootstrap/ui-bootstrap.js',
            'components/angular-bootstrap/ui-bootstrap-tpls.js',
            'components/angular-ui-router/release/angular-ui-router.js',
            filters='jsmin')
js_all = Bundle(js, coffee,
            filters='jsmin' if app.debug else None,
            output='gen/client.js')
assets.register('js_all', js_all)

less = Bundle('less/style.less',
            filters='less',
            output='gen/style.css')
css_all = Bundle(less, filters='cssmin' if app.debug else None, output='gen/style.css')
assets.register('styles', css_all)


REPOSITORY = 'http://stardog.krw.d2s.labs.vu.nl/group6'


@app.route('/')
def home():
    app.logger.debug('You arrived at ' + url_for('home'))
    return render_template('index.html')


if __name__ == '__main__':
    app.debug = True
    app.run()
