# -*- coding: utf-8 -*-
import json

from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)

config_json = None

@app.route("/")
def home():
    return render_template('base.html')


@app.route('/loadconfig', methods=['GET'])
def loadconfig_get():
    """Page de chargement de la config"""
    return render_template('loadconfig.html')


@app.route('/loadconfig', methods=['POST'])
def loadconfig_port():
    text_input = request.form['configuration']
    config = json.loads(text_input)

    # Fuck les espaces dans les noms des participants. Pas le temps de nainser
    for participant in config['participants']:
        participant['name'] = participant['name'].replace(' ', '_')
        participant['index'] = config['participants'].index(participant)

    # Les competitions ont des participants. Pour linstant une liste vide
    for competition in config['competitions']:
        competition['name'] = competition['name'].replace(' ', '_')
        competition['participants'] = []
        competition['index'] = config['competitions'].index(competition)

    global config_json
    config_json = config
    return render_template('base.html', message='Chargement reussi')


@app.route('/participants', methods=['GET'])
def participants_get():
    # Calculer le nombre de participations assigned
    for participant in config_json['participants']:
        nb_competitions = 0
        for competition in config_json['competitions']:
            if participant['name'] in competition['participants']:
                nb_competitions = nb_competitions + 1
        participant['nb_competitions'] = nb_competitions

    return render_template('participants.html', participants=config_json['participants'])


@app.route('/participant/<participant>', methods=['GET'])
def participant_get(participant):
    participant_find = [p for p in config_json['participants'] if p['name'] == participant]
    participant_find = participant_find[0]

    # Calculer le nombre de participations assigned
    nb_competitions = 0
    for competition in config_json['competitions']:
        if participant_find['name'] in competition['participants']:
            nb_competitions = nb_competitions + 1
    participant_find['nb_competitions'] = nb_competitions

    return render_template('participant.html', participant=participant_find)


@app.route('/competitions', methods=['GET'])
def competitions_get():
    return render_template('competitions.html', competitions=config_json['competitions'])


@app.route('/competition/<competition>', methods=['GET'])
def competition_get(competition):
    competition_find = [c for c in config_json['competitions'] if c['name'] == competition]
    competition_find = competition_find[0]

    participants_qui_la_veulent = []
    #Loop en ordre de preference
    for i in range(12):
        # pour chaque participant
        for participant in config_json['participants']:
            if participant['preferences'][i] == competition_find['index']:
                participants_qui_la_veulent.append(participant)

    return render_template('competition.html', competition=competition_find, participants_qui_la_veulent=participants_qui_la_veulent)


@app.route('/assign', methods=['POST'])
def assign_post():
    participant = request.form['participant_name']
    competition_index = int(request.form['competition_index'])
    #ASSIGN THIS BOI
    config_json['competitions'][competition_index]['participants'].append(participant)
    return render_template('base.html', message='Participant %s assigne a la competition %s' % (participant, competition_index))


@app.route('/unassign', methods=['POST'])
def unassign_post():
    participant = request.form['participant_name']
    competition_index = int(request.form['competition_index'])
    #UNASSIGN THIS BOI
    config_json['competitions'][competition_index]['participants'].remove(participant)
    return render_template('base.html', message='Participant %s unassigned a la competition %s' % (participant, competition_index))


@app.route('/horraire', methods=['GET'])
def horraire_get():
    return render_template('horraire.html', competitions=config_json['competitions'])


@app.route('/export', methods=['GET'])
def export_get():
    return json.dumps(config_json)


if __name__ == "__main__":
    app.run(debug=True)
