# A very simple Flask Hello World app for you to get started with...

from flask import Flask, redirect, render_template, request, url_for, flash
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import mysql.connector
import json

app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'SjdnUends821Jsdlkvxh391ksdODnejdDw'

class PlayerForm(Form):
    player_name = TextField('Player Name:', validators=[validators.required()])
    hand = TextField('Dominant Hand:', validators=[validators.required()])

@app.route('/teams/', methods=["GET", "POST"])
def teams_index():
    cnx = mysql.connector.connect(
      user='jimmyjbling',
      password='cs348project',
      host='jimmyjbling.mysql.pythonanywhere-services.com',
      database='jimmyjbling$baseball'
    )

    cursor = cnx.cursor()

    cursor.execute("SELECT TeamId from team")
    teams = cursor.fetchall()
    teams = [t[0] for t in teams]

    cursor.execute("SELECT PlayerId from player")
    player_ids = cursor.fetchall()
    player_ids = [int(t[0]) for t in player_ids]

    if request.method == "GET":
        return render_template("teams.html", teams=teams)
    if request.method == "POST":
        if "form_add" in request.form:
            team_id=request.form['teamid']
            team_name=request.form['name']
            mascot=request.form['mascot']
            stadium=request.form['stadium']

            # PARSES THE RESULTS TO MAKE SURE THEY ARE VAILD VALUES #

            if team_name != "" and team_id != "":
                if len(team_id) == 3 and not (team_id in teams):
                    # IF ADDING PLAYER TO TEAM RIGHT AWAY, PARSE THE TEAM INPUTS #
                    sql = "insert into team(TeamId, ful_name, mascot, stadium_name, num_players, num_coaches) values ('{a}', '{b}', '{c}', '{d}', 0, 0)".format(
                        a = team_id,
                        b = team_name,
                        c = mascot,
                        d = stadium)
                    try:
                        cursor.execute(sql)
                        cnx.commit()
                        flash("Team added")
                    except Exception as e:
                        cnx.rollback()
                        return(str(e))
                else:
                    flash('Error: Team Id must be unique and only 3 letters (preferablly an abbriviation of the team name)')
            else:
                flash('Error: Team Id and Team Names are Required')

        elif "form_update" in request.form:
            team_id=request.form['teamid']
            team_name=request.form['name']
            mascot=request.form['mascot']
            stadium=request.form['stadium']

            # PARSES THE RESULTS TO MAKE SURE THEY ARE VAILD VALUES #

            if team_id != "":
                sql1 = " update team set"
                update_needed = False
                if team_name != "":
                    sql1 = sql1 + " ful_name = '{a}',".format(a = team_name)
                    update_needed = True
                if mascot != "":
                    sql1 = sql1 + " mascot = '{a}',".format(a = mascot)
                    update_needed = True
                if stadium != "":
                    sql1 = sql1 + " stadium_name = {a},".format(a = stadium)
                    update_needed = True
                sql1 = sql1[:-1] + " WHERE TeamId={a}".format(a = team_id)
                if update_needed:
                    try:
                        cursor.execute(sql1)
                        cnx.commit()
                        flash("Team Updated")
                    except Exception as e:
                        cnx.rollback()
                        return(str(e) + str(sql1))
                else:
                    flash('Team update (but not values changed)')
            else:
                flash('Error: Team Id Required')

        elif "form_remove" in request.form:
            team_id=request.form['teamid']

            # PARSES THE RESULTS TO MAKE SURE THEY ARE VAILD VALUES #

            if team_id != "":
                sql = "delete from coaches_for where TeamId = '{a}'".format(a=team_id)
                try:
                    cursor.execute(sql)
                except Exception as e:
                    cnx.rollback()
                    return(str(e)+ str(sql))

                sql = "delete from manages where TeamId = '{a}'".format(a=team_id)
                try:
                    cursor.execute(sql)
                except Exception as e:
                    cnx.rollback()
                    return(str(e)+ str(sql))

                sql = " update player set current_teamId = NULL where PlayerId in (select PlayerId from plays_for where TeamId = '{a}' and end_date IS NULL)".format(a=team_id)
                try:
                    cursor.execute(sql)
                except Exception as e:
                    cnx.rollback()
                    return(str(e)+ str(sql))

                sql = "delete from plays_for where TeamId='{a}'".format(a=team_id)
                try:
                    cursor.execute(sql)
                except Exception as e:
                    cnx.rollback()
                    return(str(e)+ str(sql))

                sql = "delete from games where team1='{a}' or team2='{a}'".format(a=team_id)
                try:
                    cursor.execute(sql)
                except Exception as e:
                    cnx.rollback()
                    return(str(e)+ str(sql))

                sql = "delete from team where TeamId='{a}'".format(a=team_id)
                try:
                    cursor.execute(sql)
                    cnx.commit()
                    flash("Team Deleted")
                except Exception as e:
                    cnx.rollback()
                    return(str(e) + str(sql))
            else:
                flash('Error: Team Id Required')
        cursor.execute("SELECT TeamId from team")
        teams = cursor.fetchall()
        teams = [t[0] for t in teams]
    return render_template("teams.html", teams=teams)

@app.route('/coaches/', methods=["GET", "POST"])
def coaches_index():
    cnx = mysql.connector.connect(
      user='jimmyjbling',
      password='cs348project',
      host='jimmyjbling.mysql.pythonanywhere-services.com',
      database='jimmyjbling$baseball'
    )

    cursor = cnx.cursor()

    cursor.execute("SELECT TeamId from team")
    teams = cursor.fetchall()
    teams = [t[0] for t in teams]

    cursor.execute("SELECT PlayerId from player")
    player_ids = cursor.fetchall()
    player_ids = [int(t[0]) for t in player_ids]

    if request.method == "GET":
        return render_template("coaches.html", teams=teams)
    if request.method == "POST":
        if "form_add" in request.form:
            coach_name=request.form['name']
            team=request.form['team']
            position=request.form['position']
            salary=request.form['salary']

            # PARSES THE RESULTS TO MAKE SURE THEY ARE VAILD VALUES #

            if coach_name != "":

                # IF ADDING COACH TO TEAM RIGHT AWAY, PARSE THE TEAM INPUTS #

                if team != "" or position != "" or salary != "":
                    if not (team != "" and position != "" and salary != ""):
                        flash("Error: If team, postition or salary entered, all must be filled out")
                        return render_template('coaches.html', teams=teams)
                    try:
                        salary = float(salary)
                        if salary < 0:
                            raise ValueError
                    except:
                        flash("Error: salary must be a number greater than 0")
                        return render_template('coaches.html', teams=teams)

                    # ADD COACH TO COACH, TEAM AND COACHES DATABASES #

                    sql1 = "insert into coach(name) values ('{a}')".format(
                        a = coach_name)
                    try:
                        cursor.execute(sql1)
                    except Exception as e:
                        cnx.rollback()
                        return(str(e))
                    sql2 = "select CoachId FROM coach ORDER BY CoachId DESC LIMIT 1"
                    cursor.execute(sql2)
                    coach_id = cursor.fetchall()
                    coach_id = [t[0] for t in coach_id][0]
                    sql3 = "insert into coaches_for(CoachId, TeamId, salary, start_date, position) values ({a}, '{b}', {c}, NOW(), '{d}')".format(
                        a = coach_id,
                        b = team,
                        c = salary,
                        d = position)
                    try:
                        cursor.execute(sql3)
                    except Exception as e:
                        cnx.rollback()
                        return(str(e))

                    # CHANGE NUM_COACHES IN TEAM BY ADDING ONE TO IT #

                    sql4 = "select num_coaches from team where TeamId='{a}'".format(a=team)
                    cursor.execute(sql4)
                    coach_count = cursor.fetchall()
                    coach_count = int([t[0] for t in coach_count][0])
                    coach_count = coach_count + 1
                    sql5 = "update team set num_coaches = {a} where TeamId='{b}'".format(a=coach_count, b=team)
                    try:
                        cursor.execute(sql5)
                        cnx.commit()
                        flash("Coach added")
                    except Exception as e:
                        cnx.rollback()
                        return(str(e))

                # IF NOT ADDING COACH TO TEAM RIGHT AWAY, JUST ADD COACH TO COACH DATABASE #

                else:
                    sql = "insert into coach(name) values ('{a}')".format(a = coach_name)
                    try:
                        cursor.execute(sql)
                        cnx.commit()
                        flash("Coach added")
                    except Exception as e:
                        cnx.rollback()
                        return(str(e))
            else:
                flash('Error: Coach Name feild is required')
        elif "form_update" in request.form:
            coach_id=request.form['coachid']
            coach_name=request.form['name']
            team=request.form['team']
            position=request.form['position']
            salary=request.form['salary']

            # PARSES THE RESULTS TO MAKE SURE THEY ARE VAILD VALUES #

            if coach_id != "":

                # CHECK THAT THIS COACH ID EXISTS #
                cursor.execute("SELECT CoachId from coach")
                coach_ids = cursor.fetchall()
                coach_ids = [int(t[0]) for t in coach_ids]
                try:
                    if coach_id != "":
                        coach_id = int(coach_id)
                        if coach_id < 0:
                            raise ValueError
                        if coach_id not in coach_ids:
                            raise ValueError
                except:
                    flash("Error: Invalid Coach ID")
                    return render_template('coaches.html', teams=teams)

                # CHECK IF COACH IS ON A TEAM IF TEAM IS UPDATED #

                if team != "" or position != "" or salary != "":
                    # Check if coach is on a team already
                    sql = "select TeamId from coaches_for where CoachId={a} and end_date IS NULL".format(a = coach_id)
                    cursor.execute(sql)
                    curr_team_id = cursor.fetchall()
                    if curr_team_id != []:
                        curr_team_id = [t[0] for t in curr_team_id][0]
                    else:
                        curr_team_id = None

                    # IF COACH NOT ON A TEAM, REQUEST ALL THREE TEAM ELEMENTS BE FILLED

                    if curr_team_id is None:
                        if not (team != "" and position != "" and salary != ""):
                            flash("Error: If team, postition or salary entered, all must be filled out")
                            return render_template('coaches.html', teams=teams)
                    try:
                        if salary != "":
                            salary = float(salary)
                            if salary < 0:
                                raise ValueError
                    except:
                        flash("Error: salary must be a number greater than 0")
                        return render_template('coaches.html', teams=teams)

                # BUILD UPDATE QUERY #
                update_needed = False
                sql1 = " update coach set"
                if coach_name != "":
                    sql1 = sql1 + " name = '{a}',".format(a = coach_name)
                    update_needed = True
                sql1 = sql1[:-1] + " WHERE CoachId={a}".format(a = coach_id)

                if update_needed:
                    try:
                        cursor.execute(sql1)
                    except Exception as e:
                        cnx.rollback()
                        return(str(e) + str(sql1))

                # IF TEAM WAS CHANGED ADD COACH TO COACHES_FOR AND UPDATE NUM_COACHES AND HANDLE TEAM SWAPPING IF NEEDED

                if team != "":

                     # IF HAD EXISITING TEAM UPDATE PLAYS_FOR TO HAVE END TIME AND REDUCE TEAMS PLAYER COUNT BY 1

                    if curr_team_id is not None:
                        sql = "update coaches_for set end_date = NOW() where CoachId={a} and TeamId='{b}' and end_date IS NULL".format(a=coach_id, b=curr_team_id)
                        try:
                            cursor.execute(sql)
                        except Exception as e:
                            cnx.rollback()
                            return(str(e))
                        sql4 = "select num_coaches from team where TeamId='{a}'".format(a=curr_team_id)
                        cursor.execute(sql4)
                        coach_count = cursor.fetchall()
                        coach_count = int([t[0] for t in coach_count][0])
                        coach_count = coach_count - 1
                        sql5 = "update team set num_coaches = {a} where TeamId='{b}'".format(a=coach_count, b=curr_team_id)
                        try:
                            cursor.execute(sql5)
                        except Exception as e:
                            cnx.rollback()
                            return(str(e))

                    sql3 = "insert into coaches_for(CoachId, TeamId, salary, start_date, position) values ({a}, '{b}', {c}, NOW(), '{d}')".format(
                        a = coach_id,
                        b = team,
                        c = salary,
                        d = position)
                    try:
                        cursor.execute(sql3)
                    except Exception as e:
                        cnx.rollback()
                        return(str(e))

                    # CHANGE NUM_PLAYERS IN TEAM BY ADDING ONE TO IT #

                    sql4 = "select num_coaches from team where TeamId='{a}'".format(a=team)
                    cursor.execute(sql4)
                    coach_count = cursor.fetchall()
                    coach_count = int([t[0] for t in coach_count][0])
                    coach_count = coach_count + 1
                    sql5 = "update team set num_coaches = {a} where TeamId='{b}'".format(a=coach_count, b=team)
                    try:
                        cursor.execute(sql5)
                    except Exception as e:
                        cnx.rollback()
                        return(str(e))
                try:
                    cursor.execute(sql5)
                    cnx.commit()
                    flash("Coach updated")
                except Exception as e:
                    cnx.rollback()
                    return(str(e))
            else:
                flash('Error: Coach ID feild is required')
        elif "form_remove" in request.form:
            coach_id=request.form['coachid']

            # VALIDATE INPUT #

            if coach_id != "":

                # CHECK THAT THIS COACH ID EXISTS #
                cursor.execute("SELECT CoachId from coach")
                coach_ids = cursor.fetchall()
                coach_ids = [int(t[0]) for t in coach_ids]
                try:
                    if coach_id != "":
                        coach_id = int(coach_id)
                        if coach_id < 0:
                            raise ValueError
                        if coach_id not in coach_ids:
                            raise ValueError
                except:
                    flash("Error: Invalid Coach ID")
                    return render_template('coaches.html', teams=teams)

                # DELETE COACH FROM COACH, COACHES_FOR AND DOWN COUNT CURRENT TEAM IF IT EXISTS

                # Check if coach is on a team already
                sql = "select TeamId from coaches_for where CoachId={a} and end_date IS NULL".format(a = coach_id)
                cursor.execute(sql)
                curr_team_id = cursor.fetchall()
                curr_team_id = [t[0] for t in curr_team_id][0]

                if curr_team_id is not None:
                    sql4 = "select num_coaches from team where TeamId='{a}'".format(a=curr_team_id)
                    cursor.execute(sql4)
                    coach_count = cursor.fetchall()
                    coach_count = int([t[0] for t in coach_count][0])
                    coach_count = coach_count - 1
                    sql5 = "update team set num_coaches = {a} where TeamId='{b}'".format(a=coach_count, b=curr_team_id)
                    try:
                        cursor.execute(sql5)
                    except Exception as e:
                        cnx.rollback()
                        return(str(e))

                sql = "delete from coaches_for where CoachId={a}".format(a = coach_id)
                try:
                    cursor.execute(sql)
                except Exception as e:
                    cnx.rollback()
                    return(str(e))

                sql = "delete from coach where CoachId={a}".format(a = coach_id)
                try:
                    cursor.execute(sql)
                    cnx.commit()
                    flash("Coach removed")
                except Exception as e:
                    cnx.rollback()
                    return(str(e))
            else:
                flash("Error: Enter Valid Coach id")
    return render_template("coaches.html", teams=teams)

@app.route('/managers/', methods=["GET", "POST"])
def managers_index():
    cnx = mysql.connector.connect(
      user='jimmyjbling',
      password='cs348project',
      host='jimmyjbling.mysql.pythonanywhere-services.com',
      database='jimmyjbling$baseball'
    )

    cursor = cnx.cursor()

    cursor.execute("SELECT TeamId from team")
    teams = cursor.fetchall()
    teams = [t[0] for t in teams]

    cursor.execute("SELECT PlayerId from player")
    player_ids = cursor.fetchall()
    player_ids = [int(t[0]) for t in player_ids]

    if request.method == "GET":
        return render_template("managers.html", teams=teams)
    if request.method == "POST":
        if "form_add" in request.form:
            manager_name=request.form['name']
            team=request.form['team']
            salary=request.form['salary']

            # PARSES THE RESULTS TO MAKE SURE THEY ARE VAILD VALUES #

            if manager_name != "":

                # IF ADDING COACH TO TEAM RIGHT AWAY, PARSE THE TEAM INPUTS #

                if team != "" or salary != "":
                    if not (team != "" and salary != ""):
                        flash("Error: If team or salary entered, both must be filled out")
                        return render_template('manager.html', teams=teams)
                    try:
                        salary = float(salary)
                        if salary < 0:
                            raise ValueError
                    except:
                        flash("Error: salary must be a number greater than 0")
                        return render_template('manager.html', teams=teams)

                    # ADD MANAGER TO Manger, TEAM AND manages DATABASES #

                    sql1 = "insert into manager(name) values ('{a}')".format(
                        a = manager_name)
                    try:
                        cursor.execute(sql1)
                    except Exception as e:
                        cnx.rollback()
                        return(str(e))
                    sql2 = "select ManagerId FROM manager ORDER BY ManagerId DESC LIMIT 1"
                    cursor.execute(sql2)
                    man_id = cursor.fetchall()
                    man_id = [t[0] for t in man_id][0]
                    sql3 = "insert into manages(ManagerId, TeamId, salary, start_date) values ({a}, '{b}', {c}, NOW())".format(
                        a = man_id,
                        b = team,
                        c = salary)
                    try:
                        cursor.execute(sql3)
                        cnx.commit()
                        flash("Manager added")
                    except Exception as e:
                        cnx.rollback()
                        return(str(e))

                # IF NOT ADDING Manager TO TEAM RIGHT AWAY, JUST ADD Manager TO Manager DATABASE #

                else:
                    sql = "insert into manager(name) values ('{a}')".format(a = manager_name)
                    try:
                        cursor.execute(sql)
                        cnx.commit()
                        flash("Manager added")
                    except Exception as e:
                        cnx.rollback()
                        return(str(e))
            else:
                flash('Error: Manager Name feild is required')
        elif "form_update" in request.form:
            man_id=request.form['manid']
            manager_name=request.form['name']
            team=request.form['team']
            salary=request.form['salary']

            # PARSES THE RESULTS TO MAKE SURE THEY ARE VAILD VALUES #

            if man_id != "":

                # CHECK THAT THIS COACH ID EXISTS #
                cursor.execute("SELECT ManagerId from manager")
                man_ids = cursor.fetchall()
                man_ids = [int(t[0]) for t in man_ids]
                try:
                    if man_id != "":
                        man_id = int(man_id)
                        if man_id < 0:
                            raise ValueError
                        if man_id not in man_ids:
                            raise ValueError
                except:
                    flash("Error: Invalid Manager ID")
                    return render_template('manager.html', teams=teams)

                # CHECK IF COACH IS ON A TEAM IF TEAM IS UPDATED #

                if team != "" or salary != "":
                    # Check if coach is on a team already
                    sql = "select TeamId from manages where ManagerId={a} and end_date IS NULL".format(a = man_id)
                    cursor.execute(sql)
                    curr_team_id = cursor.fetchall()
                    if curr_team_id != []:
                        curr_team_id = [t[0] for t in curr_team_id][0]
                    else:
                        curr_team_id = None

                    # IF COACH NOT ON A TEAM, REQUEST ALL THREE TEAM ELEMENTS BE FILLED

                    if curr_team_id is None:
                        if not (team != "" and salary != ""):
                            flash("Error: If team or salary entered, both must be filled out")
                            return render_template('manager.html', teams=teams)
                    try:
                        if salary != "":
                            salary = float(salary)
                            if salary < 0:
                                raise ValueError
                    except:
                        flash("Error: salary must be a number greater than 0")
                        return render_template('manager.html', teams=teams)

                # BUILD UPDATE QUERY #
                update_needed = False
                sql1 = " update manager set"
                if manager_name != "":
                    sql1 = sql1 + " name = '{a}',".format(a = manager_name)
                    update_needed = True
                sql1 = sql1[:-1] + " WHERE ManagerId={a}".format(a = man_id)

                if update_needed:
                    try:
                        cursor.execute(sql1)
                    except Exception as e:
                        cnx.rollback()
                        return(str(e) + str(sql1))

                # IF TEAM WAS CHANGED ADD COACH TO COACHES_FOR AND UPDATE NUM_COACHES AND HANDLE TEAM SWAPPING IF NEEDED

                if team != "":

                     # IF HAD EXISITING TEAM UPDATE PLAYS_FOR TO HAVE END TIME AND REDUCE TEAMS PLAYER COUNT BY 1

                    if curr_team_id is not None:
                        sql = "update manages set end_date = NOW() where ManagerId={a} and TeamId='{b}' and end_date IS NULL".format(a=man_id, b=curr_team_id)
                        try:
                            cursor.execute(sql)
                        except Exception as e:
                            cnx.rollback()
                            return(str(e))

                    sql3 = "insert into manages(ManagerId, TeamId, salary, start_date) values ({a}, '{b}', {c}, NOW())".format(
                        a = man_id,
                        b = team,
                        c = salary)
                    try:
                        cursor.execute(sql3)
                    except Exception as e:
                        cnx.rollback()
                        return(str(e))
                try:
                    cnx.commit()
                    flash("Manager updated")
                except Exception as e:
                    cnx.rollback()
                    return(str(e))
            else:
                flash('Error: Manager ID feild is required')
        elif "form_remove" in request.form:
            man_id=request.form['manid']

            # VALIDATE INPUT #

            if man_id != "":

                # CHECK THAT THIS COACH ID EXISTS #
                cursor.execute("SELECT ManagerId from manager")
                man_ids = cursor.fetchall()
                man_ids = [int(t[0]) for t in man_ids]
                try:
                    if man_id != "":
                        man_id = int(man_id)
                        if man_id < 0:
                            raise ValueError
                        if man_id not in man_ids:
                            raise ValueError
                except:
                    flash("Error: Invalid Manager ID")
                    return render_template('manager.html', teams=teams)

                # DELETE COACH FROM COACH, COACHES_FOR AND DOWN COUNT CURRENT TEAM IF IT EXISTS

                # Check if coach is on a team already
                sql = "select TeamId from manages where ManagerId={a} and end_date IS NULL".format(a = man_id)
                cursor.execute(sql)
                curr_team_id = cursor.fetchall()
                curr_team_id = [t[0] for t in curr_team_id][0]

                if curr_team_id is not None:
                    sql = "delete from manages where ManagerId={a}".format(a = man_id)
                    try:
                        cursor.execute(sql)
                    except Exception as e:
                        cnx.rollback()
                        return(str(e))

                sql = "delete from manager where ManagerId={a}".format(a = man_id)
                try:
                    cursor.execute(sql)
                    cnx.commit()
                    flash("Manager removed")
                except Exception as e:
                    cnx.rollback()
                    return(str(e))
            else:
                flash("Error: Enter Valid Manager id")
    return render_template("managers.html", teams=teams)

@app.route('/games/', methods=["GET", "POST"])
def games_index():
    cnx = mysql.connector.connect(
      user='jimmyjbling',
      password='cs348project',
      host='jimmyjbling.mysql.pythonanywhere-services.com',
      database='jimmyjbling$baseball'
    )

    cursor = cnx.cursor()

    cursor.execute("SELECT TeamId from team")
    teams = cursor.fetchall()
    teams = [t[0] for t in teams]

    cursor.execute("SELECT PlayerId from player")
    player_ids = cursor.fetchall()
    player_ids = [int(t[0]) for t in player_ids]

    if request.method == "GET":
        return render_template("games.html", teams=teams)
    if request.method == "POST":
        if "form_add" in request.form:
            team1_id=request.form['team1id']
            team2_id=request.form['team2id']
            team1_score=request.form['score1']
            team2_score=request.form['score2']
            location=request.form['location']
            date=request.form['date']

            if team1_score != "" and team2_score != "":
                try:
                    team1_score = int(team1_score)
                    if team1_score < 0:
                        raise ValueError
                except:
                    flash("Error: Team 1 Score must be greater than or equal to 0")
                    return render_template('games.html', teams=teams)
                try:
                    team2_score = int(team2_score)
                    if team2_score < 0:
                        raise ValueError
                except:
                    flash("Error: Team 2 Score must be greater than or equal to 0")
                    return render_template('games.html', teams=teams)

                sql = "select team1, team2, DATE_FORMAT(date, '%Y-%m-%d') as d from games"
                cursor.execute(sql)
                pos_ids = cursor.fetchall()
                pos_ids = [t for t in pos_ids]

                if (team1_id, team2_id, date) in pos_ids or (team2_id, team1_id, date) in pos_ids:
                    flash("Error: Game between Team 1 and Team 2 already exisit on this date")
                    return render_template('games.html', teams=teams)

                sql = "insert into games(team1, team2, score1, score2, location, date) values ('{a}', '{b}', {c}, {d}, '{e}', '{f}')".format(
                    a=team1_id,
                    b=team2_id,
                    c=team1_score,
                    d=team2_score,
                    e=location,
                    f=date)

                try:
                    cursor.execute(sql)
                    cnx.commit()
                    flash("Game added")
                except Exception as e:
                    cnx.rollback()
                    return(str(e) + str(sql) + str(request.form) + str(teams))

            else:
                flash("Error: Both team scores are required")

        elif "form_update" in request.form:
            team1_id=request.form['team1id']
            team2_id=request.form['team2id']
            team1_score=request.form['score1']
            team2_score=request.form['score2']
            location=request.form['location']
            date=request.form['date']

            if team1id != "" and team2id != "":
                try:
                    team1_score = int(team1_score)
                    if team1_score < 0:
                        raise ValueError
                except:
                    flash("Error: Team 1 Score must be greater than or equal to 0")
                    return render_template('games.html', teams=teams)
                try:
                    team2_score = int(team2_score)
                    if team2_score < 0:
                        raise ValueError
                except:
                    flash("Error: Team 2 Score must be greater than or equal to 0")
                    return render_template('games.html', teams=teams)

                sql = "select team1, team2, DATE_FORMAT(date, '%Y-%m-%d') as d from games"
                cursor.execute(sql)
                pos_ids = cursor.fetchall()
                pos_ids = [t for t in pos_ids]
                if (team1_id, team2_id, date) not in pos_ids and (team2_id, team1_id, date) not in pos_ids:
                    flash("Error: Game between Team 1 and Team 2 does not exisit on this date")
                    return render_template('games.html', teams=teams)

                if (team2_id, team1_id, date) in pos_ids:
                    team1_score, team2_score = team2_score, team1_score

                # BUILD UPDATE QUERY #
                sql1 = " update games set"
                update_needed = False
                if team1_score != "":
                    sql1 = sql1 + " score1 = '{a}',".format(a = team1_score)
                    update_needed = True
                if team2_score != "":
                    sql1 = sql1 + " score2 = '{a}',".format(a = team2_score)
                    update_needed = True
                if location != "":
                    sql1 = sql1 + " location = {a},".format(a = location)
                    update_needed = True
                sql1 = sql1[:-1] + " WHERE (team1={a} or team1={b}) AND (team2={a} or team2={b}) AND DATE_FORMAT(date, '%Y-%m-%d)={c}".format(a = team1_id, b=team2_id, c=date)
                if update_needed:
                    try:
                        cursor.execute(sql1)
                    except Exception as e:
                        cnx.rollback()
                        return(str(e) + str(sql1) + str(request.form) + str(teams))
                flash("Game updated")
            else:
                flash("Error: Pick both team ids and date of game")

        elif "form_remove" in request.form:
            team1_id=request.form['team1id']
            team2_id=request.form['team2id']
            date=request.form['date']

            if team1_id != ""  and team2_id != "":
                sql = "select team1, team2, DATE_FORMAT(date, '%y-%m-%d') as d from games"
                cursor.execute(sql)
                pos_ids = cursor.fetchall()
                pos_ids = [t for t in pos_ids]
                if (team1_id, team2_id, date) in pos_ids or (team2_id, team1_id, date) in pos_ids:
                    sql = "Delete from games WHERE (team1={a} or team1={b}) AND (team2={a} or team2={b}) AND DATE_FORMAT(date, '%Y-%m-%d)={c}".format(a = team1_id, b=team2_id, c=date)
                    flash("Game deleted")
            else:
                flash("Error: Game between Team 1 and Team 2 does not exisit on this date")
    return render_template("games.html", teams=teams)

@app.route('/players/', methods=["GET", "POST"])
def players_index():

    cnx = mysql.connector.connect(
      user='jimmyjbling',
      password='cs348project',
      host='jimmyjbling.mysql.pythonanywhere-services.com',
      database='jimmyjbling$baseball'
    )

    cursor = cnx.cursor()

    cursor.execute("SELECT TeamId from team")
    teams = cursor.fetchall()
    teams = [t[0] for t in teams]

    cursor.execute("SELECT PlayerId from player")
    player_ids = cursor.fetchall()
    player_ids = [int(t[0]) for t in player_ids]

    if request.method == "GET":
        return render_template("players.html", teams=teams)
    if request.method == "POST":
        ## THIS TAKES CARE OF THE ADDING FORM ##
        if "form_add" in request.form:

            player_name=request.form['name']
            team=request.form['team']
            position=request.form['position']
            hand=request.form['hand']
            bat_avg=request.form['bat_avg']
            obi=request.form['obi']
            slug=request.form['slug']
            strike=request.form['strike']
            salary=request.form['salary']
            date=request.form['date']

            # PARSES THE RESULTS TO MAKE SURE THEY ARE VAILD VALUES #

            if player_name != "" and hand != "":
                try:
                    if bat_avg != "":
                        bat_avg = float(bat_avg)
                        if bat_avg > 1 or bat_avg < 0:
                            raise ValueError
                    else:
                        bat_avg = 0
                except:
                    flash("Error: Batting average must be a number between 0 and 1")
                    return render_template('players.html', teams=teams)
                try:
                    if obi != "":
                        obi = float(obi)
                        if obi > 1 or obi  < 0:
                            raise ValueError
                    else:
                        obi = 0
                except:
                    flash("Error: On Base Percentage must be a number between 0 and 1")
                    return render_template('players.html', teams=teams)
                try:
                    if slug != "":
                        slug = float(slug)
                        if slug > 4 or slug < 0:
                            raise ValueError
                    else:
                        slug = 0
                except:
                    flash("Error: Slugging Percentage must be a number between 0 and 4")
                    return render_template('players.html', teams=teams)
                try:
                    if strike != "":
                        strike = int(strike)
                        if strike < 0:
                            raise ValueError
                    else:
                        strike = 0
                except:
                    flash("Error: Number or Strikeouts must be a whole number greater than 0")
                    return render_template('players.html', teams=teams)

                # IF ADDING PLAYER TO TEAM RIGHT AWAY, PARSE THE TEAM INPUTS #

                if team != "" or position != "" or salary != "":
                    if not (team != "" and position != "" and salary != ""):
                        flash("Error: If team, postition or salary entered, all must be filled out")
                        return render_template('players.html', teams=teams)
                    try:
                        salary = float(salary)
                        if salary < 0:
                            raise ValueError
                    except:
                        flash("Error: salary must be a number greater than 0")
                        return render_template('players.html', teams=teams)

                    # ADD PLAYER TO PLAYER, TEAM AND PLAYS_FOR DATABASES #

                    sql1 = "insert into player(player_name, current_teamId, dominant_hand, batting_average, on_base_per, slug_per, games_played, strikeouts) values ('{a}', '{t}', '{b}', {c}, {d}, {e}, 0, {f})".format(
                        a = player_name,
                        t = team,
                        b = hand,
                        c = bat_avg,
                        d = obi,
                        e = slug,
                        f = strike)
                    try:
                        cursor.execute(sql1)
                    except Exception as e:
                        cnx.rollback()
                        return(str(e))
                    sql2 = "select PlayerId FROM player ORDER BY PlayerId DESC LIMIT 1"
                    cursor.execute(sql2)
                    play_id = cursor.fetchall()
                    play_id = [t[0] for t in play_id][0]
                    if date == "":
                        sql3 = "insert into plays_for(PlayerId, TeamId, salary, start_date, position) values ({a}, '{b}', {c}, NOW(), '{d}')".format(
                            a = play_id,
                            b = team,
                            c = salary,
                            d = position)
                    else:
                        sql3 = "insert into plays_for(PlayerId, TeamId, salary, start_date, position) values ({a}, '{b}', {c}, '{e}', '{d}')".format(
                            a = play_id,
                            b = team,
                            c = salary,
                            d = position,
                            e = date)
                    try:
                        cursor.execute(sql3)
                    except Exception as e:
                        cnx.rollback()
                        return(str(e))

                    # CHANGE NUM_PLAYERS IN TEAM BY ADDING ONE TO IT #

                    sql4 = "select num_players from team where TeamId='{a}'".format(a=team)
                    cursor.execute(sql4)
                    player_count = cursor.fetchall()
                    player_count = int([t[0] for t in player_count][0])
                    player_count = player_count + 1
                    sql5 = "update team set num_players = {a} where TeamId='{b}'".format(a=player_count, b=team)
                    try:
                        cursor.execute(sql5)
                        cnx.commit()
                        flash("Player added")
                    except Exception as e:
                        cnx.rollback()
                        return(str(e))

                # IF NOT ADDING PLAYER TO TEAM RIGHT AWAY, JUST ADD PLAYER TO PLAYER DATABASE #

                else:
                    sql = "insert into player(player_name, dominant_hand, batting_average, on_base_per, slug_per) values ('{a}', '{b}', {c}, {d}, {e})".format(
                        a = player_name,
                        b = hand,
                        c = bat_avg,
                        d = obi,
                        e = slug)
                    try:
                        cursor.execute(sql)
                        cnx.commit()
                        flash("Player added")
                    except Exception as e:
                        cnx.rollback()
                        return(str(e))
            else:
                flash('Error: Player Name and Dominant Hand Fields are Required')

        ##  THIS IS FOR THE UPDATE FORM ##
        elif "form_update" in request.form:
            playerid=request.form['playerid']
            player_name=request.form['name']
            team=request.form['team']
            position=request.form['position']
            hand=request.form['hand']
            bat_avg=request.form['bat_avg']
            obi=request.form['obi']
            slug=request.form['slug']
            strike=request.form['strike']
            salary=request.form['salary']
            date=request.form['date']

            # VALIDATE INPUT #

            if playerid != "":
                try:
                    if playerid != "":
                        playerid = int(playerid)
                        if playerid < 0:
                            raise ValueError
                        if playerid not in player_ids:
                            raise ValueError
                except:
                    flash("Error: Invalid Player ID")
                    return render_template('players.html', teams=teams)
                try:
                    if bat_avg != "":
                        bat_avg = float(bat_avg)
                        if bat_avg > 1 or bat_avg < 0:
                            raise ValueError
                except:
                    flash("Error: Batting average must be a number between 0 and 1")
                    return render_template('players.html', teams=teams)
                try:
                    if obi != "":
                        obi = float(obi)
                        if obi > 1 or obi  < 0:
                            raise ValueError
                except:
                    flash("Error: On Base Percentage must be a number between 0 and 1")
                    return render_template('players.html', teams=teams)
                try:
                    if slug != "":
                        slug = float(slug)
                        if slug > 4 or slug < 0:
                            raise ValueError
                except:
                    flash("Error: Slugging Percentage must be a number between 0 and 4")
                    return render_template('players.html', teams=teams)
                try:
                    if strike != "":
                        strike = int(strike)
                        if strike < 0:
                            raise ValueError
                except:
                    flash("Error: Number or Strikeouts must be a whole number greater than 0")
                    return render_template('players.html', teams=teams)

                # IF TRYING TO UPDATE TEAM OF PLAYER, CHECK IF PLAYER IS ON A TEAM #

                if team != "" or position != "" or salary != "":
                    # Check if player is on a team already
                    sql = "select current_teamId from player where PlayerId={a}".format(a = playerid)
                    cursor.execute(sql)
                    curr_team_id = cursor.fetchall()
                    curr_team_id = [t[0] for t in curr_team_id][0]

                    # IF PLAYER NOT ON A TEAM, REQUEST ALL THREE TEAM ELEMENTS BE FILLED

                    if curr_team_id is None:
                        if not (team != "" and position != "" and salary != ""):
                            flash("Error: If team, postition or salary entered, all must be filled out")
                            return render_template('players.html', teams=teams)
                    try:
                        if salary != "":
                            salary = float(salary)
                            if salary < 0:
                                raise ValueError
                    except:
                        flash("Error: salary must be a number greater than 0")
                        return render_template('players.html', teams=teams)

                # BUILD UPDATE QUERY #
                sql1 = " update player set"
                update_needed = False
                if player_name != "":
                    sql1 = sql1 + " player_name = '{a}',".format(a = player_name)
                    update_needed = True
                if hand != "":
                    sql1 = sql1 + " dominant_hand = '{a}',".format(a = hand)
                    update_needed = True
                if bat_avg != "":
                    sql1 = sql1 + " batting_average = {a},".format(a = bat_avg)
                    update_needed = True
                if obi != "":
                    sql1 = sql1 + " on_base_per = {a},".format(a = obi)
                    update_needed = True
                if slug != "":
                    sql1 = sql1 + " slug_per = {a},".format(a = slug)
                    update_needed = True
                if strike != "":
                    sql1 = sql1 + " strikeouts = {a},".format(a = strike)
                    update_needed = True
                if team != "":
                    sql1 = sql1 + " current_teamId = '{a}',".format(a = team)
                    update_needed = True
                sql1 = sql1[:-1] + " WHERE PlayerId={a}".format(a = playerid)
                if update_needed:
                    try:
                        cursor.execute(sql1)
                    except Exception as e:
                        cnx.rollback()
                        return(str(e) + str(sql1))

                # IF TEAM WAS CHANGED ADD PLAYER TO PLAYS_FOR AND UPDATE NUM_PLAYERS AND HANDLE TEAM SWAPPING IF NEEDED

                if team != "":

                     # IF HAD EXISITING TEAM UPDATE PLAYS_FOR TO HAVE END TIME AND REDUCE TEAMS PLAYER COUNT BY 1
                    if date == "":
                        if curr_team_id is not None:
                            sql = "update plays_for set end_date = NOW() where PlayerId={a} and TeamId='{b}' and end_date IS NULL".format(a=playerid, b=curr_team_id)
                            try:
                                cursor.execute(sql)
                            except Exception as e:
                                cnx.rollback()
                                return(str(e))
                            sql4 = "select num_players from team where TeamId='{a}'".format(a=curr_team_id)
                            cursor.execute(sql4)
                            player_count = cursor.fetchall()
                            player_count = int([t[0] for t in player_count][0])
                            player_count = player_count - 1
                            sql5 = "update team set num_players = {a} where TeamId='{b}'".format(a=player_count, b=curr_team_id)
                            try:
                                cursor.execute(sql5)
                            except Exception as e:
                                cnx.rollback()
                                return(str(e))

                        sql3 = "insert into plays_for(PlayerId, TeamId, salary, start_date, position) values ({a}, '{b}', {c}, NOW(), '{d}')".format(
                            a = playerid,
                            b = team,
                            c = salary,
                            d = position)
                        try:
                            cursor.execute(sql3)
                        except Exception as e:
                            cnx.rollback()
                            return(str(e))

                        # CHANGE NUM_PLAYERS IN TEAM BY ADDING ONE TO IT #

                        sql4 = "select num_players from team where TeamId='{a}'".format(a=team)
                        cursor.execute(sql4)
                        player_count = cursor.fetchall()
                        player_count = int([t[0] for t in player_count][0])
                        player_count = player_count + 1
                        sql5 = "update team set num_players = {a} where TeamId='{b}'".format(a=player_count, b=team)
                        try:
                            cursor.execute(sql5)
                        except Exception as e:
                            cnx.rollback()
                            return(str(e))

                    else:
                         # IF HAD EXISITING TEAM UPDATE PLAYS_FOR TO HAVE END TIME AND REDUCE TEAMS PLAYER COUNT BY 1
                        if curr_team_id is not None:
                            sql = "update plays_for set end_date = '{c}' where PlayerId={a} and TeamId='{b}' and end_date IS NULL".format(a=playerid, b=curr_team_id, c=date)
                            try:
                                cursor.execute(sql)
                            except Exception as e:
                                cnx.rollback()
                                return(str(e))
                            sql4 = "select num_players from team where TeamId='{a}'".format(a=curr_team_id)
                            cursor.execute(sql4)
                            player_count = cursor.fetchall()
                            player_count = int([t[0] for t in player_count][0])
                            player_count = player_count - 1
                            sql5 = "update team set num_players = {a} where TeamId='{b}'".format(a=player_count, b=curr_team_id)
                            try:
                                cursor.execute(sql5)
                            except Exception as e:
                                cnx.rollback()
                                return(str(e))

                        sql3 = "insert into plays_for(PlayerId, TeamId, salary, start_date, position) values ({a}, '{b}', {c}, '{e}', '{d}')".format(
                            a = playerid,
                            b = team,
                            c = salary,
                            d = position,
                            e = date)
                        try:
                            cursor.execute(sql3)
                        except Exception as e:
                            cnx.rollback()
                            return(str(e))

                        # CHANGE NUM_PLAYERS IN TEAM BY ADDING ONE TO IT #

                        sql4 = "select num_players from team where TeamId='{a}'".format(a=team)
                        cursor.execute(sql4)
                        player_count = cursor.fetchall()
                        player_count = int([t[0] for t in player_count][0])
                        player_count = player_count + 1
                        sql5 = "update team set num_players = {a} where TeamId='{b}'".format(a=player_count, b=team)
                        try:
                            cursor.execute(sql5)
                        except Exception as e:
                            cnx.rollback()
                            return(str(e))
                    try:
                        cursor.execute(sql5)
                        cnx.commit()
                        flash("Player updated")
                    except Exception as e:
                        cnx.rollback()
                        return(str(e))

            else:
                flash('Error: Player ID is required to update player')
        elif "form_remove" in request.form:
            playerid=request.form['playerid']

            # VALIDATE INPUT #

            if playerid != "":
                cursor.execute("SELECT PlayerId from player")
                player_ids = cursor.fetchall()
                player_ids = [int(t[0]) for t in player_ids]
                try:
                    if playerid != "":
                        playerid = int(playerid)
                        if playerid < 0:
                            raise ValueError
                        if playerid not in player_ids:
                            raise ValueError
                except:
                    flash("Error: Invalid Player ID")
                    return render_template('players.html', teams=teams)

                # DELETE PLAYER FROM PLAYER, PLAYS_FOR AND DOWN COUNT CURRENT TEAM IF IT EXISTS

                # Check if player is on a team already
                sql = "select current_teamId from player where PlayerId={a}".format(a = playerid)
                cursor.execute(sql)
                curr_team_id = cursor.fetchall()
                curr_team_id = [t[0] for t in curr_team_id][0]

                if curr_team_id is not None:
                    sql4 = "select num_players from team where TeamId='{a}'".format(a=curr_team_id)
                    cursor.execute(sql4)
                    player_count = cursor.fetchall()
                    player_count = int([t[0] for t in player_count][0])
                    player_count = player_count - 1
                    sql5 = "update team set num_players = {a} where TeamId='{b}'".format(a=player_count, b=curr_team_id)
                    try:
                        cursor.execute(sql5)
                    except Exception as e:
                        cnx.rollback()
                        return(str(e))

                sql = "delete from plays_for where PlayerId={a}".format(a = playerid)
                try:
                    cursor.execute(sql)
                except Exception as e:
                    cnx.rollback()
                    return(str(e))

                sql = "delete from player where PlayerId={a}".format(a = playerid)
                try:
                    cursor.execute(sql)
                    cnx.commit()
                    flash("Player removed")
                except Exception as e:
                    cnx.rollback()
                    return(str(e))
            flash("Error: Enter Valid Player id")
    return render_template("players.html", teams=teams)

@app.route('/' , methods=["GET"])
def main_index():
    if request.method == "GET":
        return render_template("main_page.html")

@app.route('/rooster/', methods=["GET", "POST"])
def rooster():
    cnx = mysql.connector.connect(
      user='jimmyjbling',
      password='cs348project',
      host='jimmyjbling.mysql.pythonanywhere-services.com',
      database='jimmyjbling$baseball'
    )

    cursor = cnx.cursor()

    cursor.execute("SELECT TeamId from team")
    teams = cursor.fetchall()
    teams = [t[0] for t in teams]

    cursor.execute("SELECT PlayerId from player")
    player_ids = cursor.fetchall()
    player_ids = [int(t[0]) for t in player_ids]

    if request.method == "GET":
        return render_template("rooster.html", teams = teams)
    if request.method == "POST":
        team = request.form["teamid"]

        sql = "SELECT p.PlayerId as 'Player ID', p.player_name as Player, pl.salary as 'Player Salary', dominant_hand as Hand, batting_average as 'Bat Avg', on_base_per as OBI, slug_per as SLUG, pl.position as Position, DATE_FORMAT(pl.start_date, '%Y-%m-%d') as 'Joined Team on' FROM player p join plays_for pl on p.PlayerId=pl.PlayerId where pl.end_date IS NULL and pl.TeamId='{a}' order by pl.start_date".format(a=team)
        cursor.execute(sql)
        result=cursor.fetchall()
        return "For now it just returns the raw sql dump, but this will be implemented into a table later when stage 3 comes around\n" + str([i[0] for i in cursor.description]) + json.dumps(result)

