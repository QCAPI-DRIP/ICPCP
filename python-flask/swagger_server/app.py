from flask import Flask, jsonify, request
import requests
#import urllib.request
app = Flask(__name__)

def get_file_from_url(url, file_name):
    # open in binary mode
    with open(file_name, "wb") as out_file:
        response = requests.get(url)
        out_file.write(response.content)


@app.route('/tosca', methods=['GET'])
def tosca():
    git_url = request.args.get('git_url')
    file_name = git_url.split('/')[-1]

    get_file_from_url(git_url, file_name)
    # performance_file_url = request.args.get('performance_file_url')
    # deadline_file_url = request.args.get('deadline_file_url')
    # price_file_url = request.args.get('price_file_url')


if __name__ == '__main__':
    git_url = 'https://raw.githubusercontent.com/common-workflow-library/legacy/master/workflows/make-to-cwl/dna.cwl'
    file_name = git_url.split('/')[-1]
    get_file_from_url(git_url, file_name)
    # download('https://raw.githubusercontent.com/common-workflow-library/legacy/master/workflows/make-to-cwl'
    #                    '/dna.cwl', 'test2')