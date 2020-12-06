# A very simple Flask Hello World app for you to get started with...

from flask import Flask, redirect, render_template, request, url_for, flash
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import mysql.connector
import json
import pymysql
import pandas as pd
import numpy as np

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
        elif "rooster" in request.form:
            dbcon = pymysql.connect(
              user='jimmyjbling',
              password='cs348project',
              host='jimmyjbling.mysql.pythonanywhere-services.com',
              db='jimmyjbling$baseball'
            )
            try:
                SQL_Query = pd.read_sql_query("select * from team", dbcon)
            except Exception as e:
                return(str(e))
            df = pd.DataFrame(SQL_Query, columns=['TeamId', 'ful_name', 'stadium_name', 'mascot', 'num_players', 'num_coaches'])
            try:
                SQL_Query = pd.read_sql_query("select p.TeamId, sum(p.salary)+sum(c.salary)+sum(m.salary) as total_salary from plays_for p join coaches_for c on p.TeamId=c.TeamId join manages m on p.TeamId=m.TeamId group by p.TeamId;", dbcon)
            except Exception as e:
                return(str(e))
            costs = pd.DataFrame(SQL_Query, columns=['TeamId', 'total_salary'])
            df = pd.merge(df, costs, how='left', on='TeamId')
            df.rename(columns = {'TeamId':'Team ID', 'ful_name':'Name', 'stadium_name':'Stadium Location', 'num_players':'Number of Players', 'num_coaches':'Number of Coaches', 'start_date':'Date Started'}, inplace = True)
            df.fillna(0, inplace=True)
            return render_template('view.html',tables=[df.to_html()], titles = ['Teams'])
        cursor.execute("SELECT TeamId from team")
        teams = cursor.fetchall()
        teams = [t[0] for t in teams]
        cnx.close()
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
        elif "rooster" in request.form:
            dbcon = pymysql.connect(
              user='jimmyjbling',
              password='cs348project',
              host='jimmyjbling.mysql.pythonanywhere-services.com',
              db='jimmyjbling$baseball'
            )
            try:
                SQL_Query = pd.read_sql_query("select c.CoachId, name, TeamId, salary, position, start_date from coach c join coaches_for cf on c.CoachId=cf.CoachId where end_date is NULL", dbcon)
            except Exception as e:
                return(str(e))
            df = pd.DataFrame(SQL_Query, columns=['CoachId', 'name', 'TeamId', 'salary', 'position', 'start_date'])
            df.rename(columns = {'CoachId':'Coach ID', 'name':'Name', 'TeamId':'Current Team', 'salary':'Salary', 'position':'Position', 'start_date':'Date Started'}, inplace = True)

            return render_template('view.html',tables=[df.to_html()], titles = ['Coaches'])
        cnx.close()
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
        elif "rooster" in request.form:
            dbcon = pymysql.connect(
              user='jimmyjbling',
              password='cs348project',
              host='jimmyjbling.mysql.pythonanywhere-services.com',
              db='jimmyjbling$baseball'
            )
            try:
                SQL_Query = pd.read_sql_query("select m.ManagerId, name, TeamId, salary, start_date from manager m join manages mf on m.ManagerId=mf.ManagerId where end_date is NULL", dbcon)
            except Exception as e:
                return(str(e))
            df = pd.DataFrame(SQL_Query, columns=['ManagerId', 'name', 'TeamId', 'salary', 'start_date'])
            df.rename(columns = {'ManagerId':'Manager ID', 'name':'Name', 'TeamId':'Current Team', 'salary':'Salary', 'start_date':'Date Started'}, inplace = True)
            return render_template('view.html',tables=[df.to_html()], titles = ['Managers'])
        cnx.close()
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

            if team1_id != "" and team2_id != "" and team1_score != "" and team2_score != "":
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

                if team1_score > team2_score:
                    winner = team1_id
                elif team1_score < team2_score:
                    winner = team2_id
                else:
                    winner = "tie"

                sql = "insert into games(team1, team2, score1, score2, winner, location, date) values ('{a}', '{b}', {c}, {d}, '{g}', '{e}', '{f}')".format(
                    a=team1_id,
                    b=team2_id,
                    c=team1_score,
                    d=team2_score,
                    g=winner,
                    e=location,
                    f=date)

                try:
                    cursor.execute(sql)
                except Exception as e:
                    cnx.rollback()
                    return(str(e) + str(sql) + str(request.form) + str(teams))

                sql = "update player set games_played = games_played + 1 where PlayerId in (select pf.PlayerId from plays_for where (TeamId='{a}' or TeamId='{b}') and (('{c}' between start_date and end_date) or ('{c}'>=start_date and end_date is NULL))".format(
                        a=team1_id,
                        b=team2_id,
                        c=date)

                try:
                    cursor.execute(sql)
                    cnx.commit()
                    flash("Game added")
                except Exception as e:
                    cnx.rollback()
                    return(str(e) + str(sql) + str(request.form) + str(teams))

            else:
                flash("Error: Both team ids and scores are required")

        elif "form_update" in request.form:
            team1_id=request.form['team1id']
            team2_id=request.form['team2id']
            team1_score=request.form['score1']
            team2_score=request.form['score2']
            location=request.form['location']
            date=request.form['date']

            if team1_id != "" and team2_id != "":
                try:
                    if team1_score != "":
                        team1_score = int(team1_score)
                        if team1_score < 0:
                            raise ValueError
                except:
                    flash("Error: Team 1 Score must be greater than or equal to 0")
                    return render_template('games.html', teams=teams)
                try:
                    if team2_score != "":
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

                switched = False
                if (team2_id, team1_id, date) in pos_ids:
                    team1_score, team2_score = team2_score, team1_score
                    switched = True

                # BUILD UPDATE QUERY #
                sql1 = " update games set"
                update_needed = False
                update_score = False
                if team1_score != "":
                    sql1 = sql1 + " score1 = {a},".format(a = team1_score)
                    update_needed = True
                    update_score = True
                if team2_score != "":
                    sql1 = sql1 + " score2 = {a},".format(a = team2_score)
                    update_needed = True
                    update_score = True
                if location != "":
                    sql1 = sql1 + " location = '{a}',".format(a = location)
                    update_needed = True
                sql1 = sql1[:-1] + " WHERE ((team1='{a}' AND team2='{b}') OR (team2='{a}' AND team1='{b}')) AND DATE_FORMAT(date, '%Y-%m-%d')=date '{c}'".format(a = team1_id, b=team2_id, c=date)
                if update_needed:
                    try:
                        cursor.execute(sql1)
                        cnx.commit()
                    except Exception as e:
                        cnx.rollback()
                        return(str(e) + str(sql1) + str(request.form) + str(teams))
                    if update_score:
                        if team1_score > team2_score:
                            if switched:
                                winner=team2_id
                            else:
                                winner = team1_id
                        elif team1_score < team2_score:
                            if switched:
                                winner=team1_id
                            else:
                                winner = team2_id
                        else:
                            winner = "tie"
                        sql = "update games set winner='{d}' WHERE ((team1='{a}' AND team2='{b}') OR (team2='{a}' AND team1='{b}')) AND DATE_FORMAT(date, '%Y-%m-%d')=date '{c}'".format(a = team1_id, b=team2_id, c=date, d=winner)
                        try:
                            cursor.execute(sql)
                            cnx.commit()
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
                    sql = "Delete from games WHERE (team1={a} or team1={b}) AND (team2={a} or team2={b}) AND DATE_FORMAT(date, '%Y-%m-%d)='{c}'".format(a = team1_id, b=team2_id, c=date)
                    flash("Game deleted")
            else:
                flash("Error: Game between Team 1 and Team 2 does not exisit on this date")
        elif "rooster" in request.form:
            dbcon = pymysql.connect(
              user='jimmyjbling',
              password='cs348project',
              host='jimmyjbling.mysql.pythonanywhere-services.com',
              db='jimmyjbling$baseball'
            )
            try:
                SQL_Query = pd.read_sql_query("select team1, team2, score1, score2, location, date from games", dbcon)
            except Exception as e:
                return(str(e))
            df = pd.DataFrame(SQL_Query, columns=['team1', 'team2', 'score1', 'score2', 'location', 'date'])
            df.rename(columns = {'team1':'Home Team', 'team2':'Away Team', 'score1':'Home Score', 'score2':'Away Score', 'location':'Game played in', 'date':'Date Played'}, inplace = True)
            return render_template('view.html',tables=[df.to_html()], titles = ['Games'])
        cnx.close()
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

                    sql1 = "insert into player(player_name, current_teamId, dominant_hand, batting_average, on_base_per, slug_per, games_played, strikeouts) values ('{a}', '{t}', '{b}', {c}, {d}, {e}, 1, {f})".format(
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
        elif "rooster" in request.form:
            dbcon = pymysql.connect(
              user='jimmyjbling',
              password='cs348project',
              host='jimmyjbling.mysql.pythonanywhere-services.com',
              db='jimmyjbling$baseball'
            )
            try:
                SQL_Query = pd.read_sql_query("select p.PlayerId, current_teamId, player_name, dominant_hand, batting_average, on_base_per, slug_per, games_played, strikeouts, salary, position, start_date from player p join plays_for pf on p.PlayerId=pf.PlayerId where end_date is NULL", dbcon)
            except Exception as e:
                return(str(e))
            df = pd.DataFrame(SQL_Query, columns=['PlayerId', 'current_teamId', 'player_name', 'dominant_hand', 'batting_average', 'on_base_per', 'slug_per', 'games_played', 'strikeouts', 'salary', 'position', 'start_date'])
            df.rename(columns = {'PlayerId':'Player ID', 'current_teamId':'Current Team', 'player_name':'Player Name', 'dominant_hand':'Dominant Hand', 'batting_average':'Batting Average', 'on_base_per':'On Base Percentage', 'slug_per':'Slugger Percentage', 'games_played':'Games Played', 'strikeouts':'Strikeout (as pitcher)', 'salary':'Salary', 'position':'Position', 'start_date':'Start Date'}, inplace = True)
            return render_template('view.html',tables=[df.to_html()], titles = ['Players'])
        cnx.close()
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
        dbcon = pymysql.connect(
              user='jimmyjbling',
              password='cs348project',
              host='jimmyjbling.mysql.pythonanywhere-services.com',
              db='jimmyjbling$baseball'
            )
        sql = "SELECT p.PlayerId, p.player_name, dominant_hand, batting_average, on_base_per, slug_per, strikeouts, position, DATE_FORMAT(start_date, '%Y-%m-%d') as start_date FROM player p join plays_for pl on p.PlayerId=pl.PlayerId where pl.end_date IS NULL and pl.TeamId='{a}' order by position".format(a=team)
        try:
            SQL_Query = pd.read_sql_query(sql, dbcon)
        except Exception as e:
            return(str(e))
        df_players = pd.DataFrame(SQL_Query, columns=['PlayerId', 'player_name', 'dominant_hand', 'batting_average', 'on_base_per', 'slug_per', 'strikeouts', 'position', 'start_date'])
        df_players.rename(columns = {'PlayerId':'Player ID', 'current_teamId':'Current Team', 'player_name':'Player Name', 'dominant_hand':'Dominant Hand', 'batting_average':'Batting Average', 'on_base_per':'On Base Percentage', 'slug_per':'Slugger Percentage', 'games_played':'Games Played', 'strikeouts':'Strikeout (as pitcher)', 'salary':'Salary', 'position':'Position', 'start_date':'Start Date'}, inplace = True)

        try:
            SQL_Query = pd.read_sql_query("select m.ManagerId, name, TeamId, DATE_FORMAT(start_date, '%Y-%m-%d') as start_date from manager m join manages mf on m.ManagerId=mf.ManagerId where end_date is NULL and mf.TeamId='{a}'".format(a=team), dbcon)
        except Exception as e:
            return(str(e))
        df_man = pd.DataFrame(SQL_Query, columns=['ManagerId', 'name', 'TeamId', 'start_date'])
        df_man.rename(columns = {'ManagerId':'Manager ID', 'name':'Name', 'TeamId':'Current Team', 'start_date':'Date Started'}, inplace = True)

        try:
            SQL_Query = pd.read_sql_query("select c.CoachId, name, TeamId, position, DATE_FORMAT(start_date, '%Y-%m-%d') as start_date from coach c join coaches_for cf on c.CoachId=cf.CoachId where end_date is NULL and cf.TeamId='{a}' order by position".format(a=team), dbcon)
        except Exception as e:
            return(str(e))
        df_co = pd.DataFrame(SQL_Query, columns=['CoachId', 'name', 'TeamId', 'position', 'start_date'])
        df_co.rename(columns = {'CoachId':'Coach ID', 'name':'Name', 'TeamId':'Current Team', 'position':'Position', 'start_date':'Date Started'}, inplace = True)
        return render_template('view.html',tables=[df_players.to_html(), df_co.to_html(), df_man.to_html()], titles = ['na', 'Players', 'Coaches', 'Manager'])

    cnx.close()

@app.route('/gamedata/', methods=["GET", "POST"])
def gamedata():
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
        cnx.close()
        return render_template("gamedata.html", teams = teams)
    if request.method == "POST":
        team1_id=request.form['team1id']
        team2_id=request.form['team2id']
        date=request.form['date']

        if team1_id != "" and team2_id == "":
            dbcon = pymysql.connect(
              user='jimmyjbling',
              password='cs348project',
              host='jimmyjbling.mysql.pythonanywhere-services.com',
              db='jimmyjbling$baseball'
            )
            if date == "":
                try:
                    SQL_Query = pd.read_sql_query("select team1, team2, score1, score2, location, date_format(date, '%Y-%m-%d') as date from games where team1='{a}' or team2='{a}' order by date".format(a=team1_id), dbcon)
                except Exception as e:
                    return(str(e))
                df = pd.DataFrame(SQL_Query, columns=['team1', 'team2', 'score1', 'score2', 'location', 'date'])
                df.rename(columns = {'team1':'Home Team', 'team2':'Away Team', 'score1':'Home Score', 'score2':'Away Score', 'location':'Game played in', 'date':'Date Played'}, inplace = True)
                return render_template('view.html',tables=[df.to_html()], titles = ['Games'])
            else:
                try:
                    SQL_Query = pd.read_sql_query("select team1, team2, score1, score2, location, date_format(date, '%Y-%m-%d') as date from games where (team1='{a}' or team2='{a}') and date=date_format(date('{b}'), '%Y-%m-%d') order by date".format(a=team1_id, b=date), dbcon)
                except Exception as e:
                    return(str(e))
                df = pd.DataFrame(SQL_Query, columns=['team1', 'team2', 'score1', 'score2', 'location', 'date'])
                df.rename(columns = {'team1':'Home Team', 'team2':'Away Team', 'score1':'Home Score', 'score2':'Away Score', 'location':'Game played in', 'date':'Date Played'}, inplace = True)
                return render_template('view.html',tables=[df.to_html()], titles = ['Games'])
        elif team1_id != "" and team2_id != "":
            dbcon = pymysql.connect(
              user='jimmyjbling',
              password='cs348project',
              host='jimmyjbling.mysql.pythonanywhere-services.com',
              db='jimmyjbling$baseball'
            )
            if date == "":
                try:
                    SQL_Query = pd.read_sql_query("select team1, team2, score1, score2, location, date_format(date, '%Y-%m-%d') as date from games where (team1='{a}' and team2='{b}') or (team1='{b}' and team2='{a}') order by date".format(a=team1_id, b=team2_id), dbcon)
                except Exception as e:
                    return(str(e))
                df = pd.DataFrame(SQL_Query, columns=['team1', 'team2', 'score1', 'score2', 'location', 'date'])
                df.rename(columns = {'team1':'Home Team', 'team2':'Away Team', 'score1':'Home Score', 'score2':'Away Score', 'location':'Game played in', 'date':'Date Played'}, inplace = True)
                return render_template('view.html',tables=[df.to_html()], titles = ['Games'])
            else:
                try:
                    SQL_Query = pd.read_sql_query("select team1, team2, score1, score2, location, date_format(date, '%Y-%m-%d') as date from games where ((team1='{a}' and team2='{b}') or (team1='{b}' and team2='{a}')) and date=date_format(date('{c}'), '%Y-%m-%d') order by date".format(a=team1_id, b=team2_id, c=date), dbcon)
                except Exception as e:
                    return(str(e))
                df_game = pd.DataFrame(SQL_Query, columns=['team1', 'team2', 'score1', 'score2', 'location', 'date'])
                df_game.rename(columns = {'team1':'Home Team', 'team2':'Away Team', 'score1':'Home Score', 'score2':'Away Score', 'location':'Game played in', 'date':'Date Played'}, inplace = True)

                if len(df_game)>0:
                    sql = "select p.PlayerId, p.player_name, dominant_hand, batting_average, on_base_per, slug_per, strikeouts, position, DATE_FORMAT(start_date, '%Y-%m-%d') as start_date from plays_for pf join player p on pf.PlayerId=p.PlayerId where ((date '{b}' < end_date) or (end_date is NULL)) and date '{b}' >= start_date and TeamId='{a}' order by position".format(a=team1_id, b=date)
                    try:
                        SQL_Query = pd.read_sql_query(sql, dbcon)
                    except Exception as e:
                        return(str(e))
                    df_players1 = pd.DataFrame(SQL_Query, columns=['PlayerId', 'player_name', 'dominant_hand', 'batting_average', 'on_base_per', 'slug_per', 'strikeouts', 'position', 'start_date'])
                    df_players1.rename(columns = {'PlayerId':'Player ID', 'current_teamId':'Current Team', 'player_name':'Player Name', 'dominant_hand':'Dominant Hand', 'batting_average':'Batting Average', 'on_base_per':'On Base Percentage', 'slug_per':'Slugger Percentage', 'games_played':'Games Played', 'strikeouts':'Strikeout (as pitcher)', 'salary':'Salary', 'position':'Position', 'start_date':'Start Date'}, inplace = True)

                    sql = "select p.PlayerId, p.player_name, dominant_hand, batting_average, on_base_per, slug_per, strikeouts, position, DATE_FORMAT(start_date, '%Y-%m-%d') as start_date from plays_for pf join player p on pf.PlayerId=p.PlayerId where ((date '{b}' < end_date) or (end_date is NULL)) and date '{b}' >= start_date and TeamId='{a}' order by position".format(a=team2_id, b=date)
                    try:
                        SQL_Query = pd.read_sql_query(sql, dbcon)
                    except Exception as e:
                        return(str(e))
                    df_players2 = pd.DataFrame(SQL_Query, columns=['PlayerId', 'player_name', 'dominant_hand', 'batting_average', 'on_base_per', 'slug_per', 'strikeouts', 'position', 'start_date'])
                    df_players2.rename(columns = {'PlayerId':'Player ID', 'current_teamId':'Current Team', 'player_name':'Player Name', 'dominant_hand':'Dominant Hand', 'batting_average':'Batting Average', 'on_base_per':'On Base Percentage', 'slug_per':'Slugger Percentage', 'games_played':'Games Played', 'strikeouts':'Strikeout (as pitcher)', 'salary':'Salary', 'position':'Position', 'start_date':'Start Date'}, inplace = True)

                    return render_template('view.html',tables=[df_game.to_html(), df_players1.to_html(), df_players2.to_html()], titles = ['na', 'Games', team1_id + " Players", team2_id + " Players"])
                else:
                    return render_template('view.html',tables=[df_game.to_html()], titles = ['na', 'Games'])
        else:
            flash('Error: Player ID is required to update player')
            cnx.close()
            return render_template('gamedata.html', teams=teams)

    cnx.close()

@app.route('/playerdata/', methods=["GET", "POST"])
def playerdata():
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
        cnx.close()
        return render_template("playerdata.html", teams = teams)
    if request.method == "POST":
        playerid=request.form['playerid']
        if playerid != "":
            try:
                playerid = int(playerid)
            except Exception as e:
                flash('Error: Player ID is required and must be a number')
            dbcon = pymysql.connect(
                  user='jimmyjbling',
                  password='cs348project',
                  host='jimmyjbling.mysql.pythonanywhere-services.com',
                  db='jimmyjbling$baseball'
                )

            sql = "select p.PlayerId, p.player_name, dominant_hand, batting_average, on_base_per, slug_per, strikeouts, position, games_played from plays_for pf join player p on pf.PlayerId=p.PlayerId where p.PlayerId={a} and end_date is NULL".format(a=playerid)
            try:
                SQL_Query = pd.read_sql_query(sql, dbcon)
            except Exception as e:
                return(str(e))
            df_players1 = pd.DataFrame(SQL_Query, columns=['PlayerId', 'player_name', 'dominant_hand', 'batting_average', 'on_base_per', 'slug_per', 'strikeouts', 'position', 'games_played'])
            df_players1.rename(columns = {'PlayerId':'Player ID', 'current_teamId':'Current Team', 'player_name':'Player Name', 'dominant_hand':'Dominant Hand', 'batting_average':'Batting Average', 'on_base_per':'On Base Percentage', 'slug_per':'Slugger Percentage', 'strikeouts':'Strikeout (as pitcher)', 'salary':'Salary', 'position':'Position', 'games_played':'Number of games played'}, inplace = True)

            try:
                SQL_Query = pd.read_sql_query("select Count(*) as numwins from games g join plays_for pf on g.winner=pf.TeamId where PlayerId={a} and ((date between start_date and end_date) or (date>=start_date and end_date is NULL))".format(a=playerid), dbcon)
            except Exception as e:
                return(str(e))
            df_games = pd.DataFrame(SQL_Query, columns=['numwins'])
            df_games.rename(columns = {'numwins':'Number of Wins'}, inplace = True)

            try:
                SQL_Query = pd.read_sql_query("select count(*) as numpitched from plays_for pf join games g1 on (pf.TeamId=g1.team1 or pf.TeamId=g1.team2) where position='P' and PlayerId={a}".format(a=playerid), dbcon)
            except Exception as e:
                return(str(e))
            df_pitched = pd.DataFrame(SQL_Query, columns=['numwins'])
            df_pitched.fillna(0, inplace=True)
            df_pitched.rename(columns = {'numwins':'Number of Pitched Games'}, inplace = True)
            return render_template('view.html',tables=[df_games.to_html(), df_pitched.to_html(), df_players1.to_html()], titles = ['na', 'Games won', 'Games pitched', 'Player Stats'])

        else:
            flash('Error: Player ID is required and must be a number')

@app.route('/simgame/', methods=["GET", "POST"])
def simegame():
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
        cnx.close()
        return render_template("simgame.html", teams = teams)
    if request.method == "POST":
        team1=request.form['team1id']
        team2=request.form['team2id']
        date=request.form['date']
        addit=request.form['addit']
        if addit == "0":
            addit = False
        else:
            addit = True

        dbcon = pymysql.connect(
                  user='jimmyjbling',
                  password='cs348project',
                  host='jimmyjbling.mysql.pythonanywhere-services.com',
                  db='jimmyjbling$baseball'
                )

        if team1 != "" and team2 != "" and date != "":

            sql = "select team1, team2, DATE_FORMAT(date, '%Y-%m-%d') as d from games"
            cursor.execute(sql)
            pos_ids = cursor.fetchall()
            pos_ids = [t for t in pos_ids]

            if (team1, team2, date) in pos_ids or (team2, team1, date) in pos_ids:
                flash("Error: Game between Team 1 and Team 2 already exisit on this date")
                return render_template('games.html', teams=teams)

            sql = "SELECT p.PlayerId, p.player_name, p.games_played, batting_average, on_base_per, slug_per, strikeouts, pl.position, count(tmp.CoachId) as numCoaches FROM player p join plays_for pl on p.PlayerId=pl.PlayerId left join (select cf.CoachId, TeamId, cf.position from coaches_for cf where (('{b}' between start_date and end_date) or ('{b}'>=start_date and end_date is NULL)) and cf.TeamId='{a}') as tmp on tmp.position=pl.position where (('{b}' between start_date and end_date) or ('{b}'>=start_date and end_date is NULL)) and pl.TeamId='{a}' group by pl.PlayerId".format(a=team1, b=date)
            try:
                SQL_Query = pd.read_sql_query(sql, dbcon)
            except Exception as e:
                return(str(e))
            df_players1 = pd.DataFrame(SQL_Query, columns=['PlayerId', 'player_name', 'games_played', 'batting_average', 'on_base_per', 'slug_per', 'strikeouts', 'position', 'numCoaches'])
            df_players1.fillna(0, inplace=True)

            sql = "SELECT p.PlayerId, p.player_name, p.games_played, batting_average, on_base_per, slug_per, strikeouts, pl.position, count(tmp.CoachId) as numCoaches FROM player p join plays_for pl on p.PlayerId=pl.PlayerId left join (select cf.CoachId, TeamId, cf.position from coaches_for cf where (('{b}' between start_date and end_date) or ('{b}'>=start_date and end_date is NULL)) and cf.TeamId='{a}') as tmp on tmp.position=pl.position where (('{b}' between start_date and end_date) or ('{b}'>=start_date and end_date is NULL)) and pl.TeamId='{a}' group by pl.PlayerId".format(a=team2, b=date)
            try:
                SQL_Query = pd.read_sql_query(sql, dbcon)
            except Exception as e:
                return(str(e))
            df_players2 = pd.DataFrame(SQL_Query, columns=['PlayerId', 'player_name', 'games_played', 'batting_average', 'on_base_per', 'slug_per', 'strikeouts', 'position', 'numCoaches'])
            df_players2.fillna(0, inplace=True)

            ## SIMULATION ALGORITHUM ##
            pitcher1 = df_players1.loc[df_players1['position'] == 'P'].copy()
            pitcher1["Strikeouts Pitched in Game"] = 0
            pitcher2 = df_players2.loc[df_players2['position'] == 'P'].copy()
            pitcher2["Strikeouts Pitched in Game"] = 0

            i = 0
            k1_total = 0
            for index, row in pitcher1.iterrows():
                k1 = np.ceil((int(row['strikeouts']) + 1)/int(row['games_played'])) + np.ceil(min([int(row['games_played'])/10,10])) + np.random.randint(-5, 6)
                k1 = min([np.floor(k1/len(pitcher1)),20])
                pitcher1.at[index, "Strikeouts Pitched in Game"] = k1
                k1_total = k1_total + k1
                i = i + 1
                if addit:
                    sql = "update player set strikeouts=strikeouts+{a} where PlayerId={b}".format(a=k1, b=int(row['PlayerId']))
                    try:
                        cursor.execute(sql)
                        cnx.commit()
                    except Exception as e:
                        cnx.rollback()
                        return(e)
            i = 0
            k2_total = 0
            for index, row in pitcher2.iterrows():
                k2 = np.ceil((int(row['strikeouts']) + 1)/int(row['games_played'])) + np.ceil(min([int(row['games_played'])/10,10])) + np.random.randint(-5, 6)
                k2 = min([np.floor(k2/len(pitcher2)), 20])
                pitcher2.at[index, "Strikeouts Pitched in Game"] = k2
                k2_total = k2_total + k2
                i = i + 1
                if addit:
                    sql = "update player set strikeouts=strikeouts+{a} where PlayerId={b}".format(a=k2, b=int(row['PlayerId']))
                    try:
                        cursor.execute(sql)
                        cnx.commit()
                    except Exception as e:
                        cnx.rollback()
                        return(e)

            hitters1 = df_players1.loc[df_players1['position'] != 'P'].copy()
            hitters1['Runs scored in game'] = 0
            hitters2 = df_players2.loc[df_players2['position'] != 'P'].copy()
            hitters2['Runs scored in game'] = 0


            points1_tot = 0
            for index, row in hitters1.iterrows():
                points = np.floor(((float(row['on_base_per']) * float(row['slug_per'])) + min([int(row['games_played'])/500,0.5]) + min([int(row['numCoaches'])/100,0.5])) * np.random.randint(np.floor(7-min([k2_total/3,2])),np.ceil(12-min([k2_total/3,3]))))
                points = np.floor(points*(9/len(hitters1)))
                if points > 0:
                    points = points + np.random.randint(-points, 3)
                else:
                    points = points + np.random.randint(0, 3)
                hitters1.at[index, 'Runs scored in game'] = points
                points1_tot = points1_tot + points

            points2_tot = 0
            for index, row in hitters2.iterrows():
                points = np.floor(((float(row['on_base_per']) * float(row['slug_per'])) + min([int(row['games_played'])/500,0.5]) + min([int(row['numCoaches'])/100,0.5])) * np.random.randint(np.floor(7-min([k2_total/3,2])),np.ceil(12-min([k2_total/3,3]))))
                points = np.floor(points*(9/len(hitters2)))
                if points > 0:
                    points = points + np.random.randint(-points, 3)
                else:
                    points = points + np.random.randint(0, 3)
                hitters2.at[index, 'Runs scored in game'] = points
                points2_tot = points2_tot + points

            if points1_tot > points2_tot:
                winner = team1
            elif points1_tot < points2_tot:
                winner = team2
            else:
                winner = "tie"

            final_score = pd.DataFrame({team1:[int(points1_tot)], team2:[int(points2_tot)], "Winner":[str(winner)]}, columns=[team1, team2, "Winner"])

            if addit:
                team1_id=team1
                team2_id=team1
                team1_score=points1_tot
                team2_score=points2_tot
                location="Simulation"
                date=date

                if team1_id != "" and team2_id != "" and team1_score != "" and team2_score != "":
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
                        flash("Error: Game between Team 1 and Team 2 already exisit on this date. Set Add to games to No to just run simulation")
                        return render_template('games.html', teams=teams)

                    if team1_score > team2_score:
                        winner = team1_id
                    elif team1_score < team2_score:
                        winner = team2_id
                    else:
                        winner = "tie"

                    sql = "insert into games(team1, team2, score1, score2, winner, location, date) values ('{a}', '{b}', {c}, {d}, '{g}', '{e}', '{f}')".format(
                        a=team1_id,
                        b=team2_id,
                        c=team1_score,
                        d=team2_score,
                        g=winner,
                        e=location,
                        f=date)

                    try:
                        cursor.execute(sql)
                    except Exception as e:
                        cnx.rollback()
                        return(str(e) + str(sql) + str(request.form) + str(teams))

                    sql = "update player set games_played = games_played + 1 where PlayerId in (select pf.PlayerId from plays_for where (TeamId='{a}' or TeamId='{b}') and (('{c}' between start_date and end_date) or ('{c}'>=start_date and end_date is NULL)))".format(
                        a=team1_id,
                        b=team2_id,
                        c=date)

                    try:
                        cursor.execute(sql)
                        cnx.commit()
                        flash("Game added")
                    except Exception as e:
                        cnx.rollback()
                        return(str(e) + str(sql) + str(request.form) + str(teams))

                else:
                    flash("Error: Both team ids and scores are required")

            return render_template('view.html',tables=[final_score.to_html(), pitcher1.to_html(), hitters1.to_html(), pitcher2.to_html(), hitters2.to_html()], titles = ['na', 'Game Outcome', str(team1) +" Pitchers", str(team1) +" Hitters", str(team2) +" Pitchers", str(team2) +" Hitters"])



        else:
            flash("Must pick date and both teams")
            return render_template('games.html', teams=teams)





