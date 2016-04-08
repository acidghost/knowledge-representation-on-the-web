#!/usr/bin/env python

import json
from flask import Flask, render_template, url_for, request, jsonify, abort
from flask.ext.assets import Environment, Bundle
from services.sparql import SPARQL


# setup app
app = Flask(__name__)
assets = Environment(app)
sparql = SPARQL(app)

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


@app.route('/')
def home():
    app.logger.debug('You arrived at ' + url_for('home'))
    return render_template('index.html')


@app.route('/venues', methods=['GET'])
def venues():
    venues = sparql.venues()
    if venues:
        return jsonify({ 'data': venues})
    else:
        abort(500)


if __name__ == '__main__':
    app.debug = True
    app.run()
