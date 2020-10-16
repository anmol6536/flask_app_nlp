from flask import Flask, jsonify, render_template, Response, url_for,  request, redirect, send_file
import os
import allergan as ag
import mygene
import pandas as pd

static_path = os.path.abspath('./static')
plotting_folder = os.path.abspath('./static/plot/')

mg = mygene.MyGeneInfo()
app = Flask(__name__, static_folder = static_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/search', methods=['GET','POST'])
def search():
    if request.method =='POST':
        gene = request.form['gene']
        try:
            if gene:
                return render_template('result.html', gene=gene, info = information(gene))
        except:
            return ("",404)
    return render_template('search.html')

@app.route('/overview?gene=<gene>', methods=['GET','POST'])
def plot_png(gene):
    try:
        fig = ag.barcode_generator.pl().biogps_plotter(gene)
        return fig
    except:
        return ("", 404)

@app.route('/geo_search', methods=['GET','POST'])
def geo_search():
    if request.method =='POST':
        query = request.form['geo_query']
        if not query:
            return render_template('error.html')
        database = request.form['database']
        df = ag.database_search_run(query)
        if 'error' in df.keys():
            return render_template('geo_search.html', error = 'too many datasets identified try to refine search')
        else:
            df['result'].pop('uids')
            df = pd.DataFrame(df['result'])
        return render_template('geo_search.html', df = df.transpose().to_records(), response = 'result')
    return render_template('geo_search.html')

def information(gene):
    res = mg.querymany([gene], scopes = 'symbol', fields = 'symbol, uniprot, name, summary', as_dataframe=True)
    res = res.dropna()
    try:
        if res[0]['notfound']:
            return ("", 402)
    except:
        return res.to_records()


if __name__ == '__main__':
   app.run(debug = True, use_reloader=True)
