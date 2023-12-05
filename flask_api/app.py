from flask import Flask, jsonify, request, redirect, render_template, session
import pymysql
import time

app = Flask(__name__)

app.config['SECRET_KEY'] = '123456'
# id=session.get("id")
# 测试
@app.route('/')
def login():
    session['id'] = 2
    return "登陆成功"


# 顾客看公告（已完成）
@app.route('/customer/board', methods=['GET'])
def customer_board():
    conn = pymysql.connect(host="127.0.0.1", port=3306, user='root', passwd='root123', charset='utf8', db='aviation',
                           cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    sql = "SELECT * FROM board"
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    # 转换数据为 JSON 格式并返回
    # return jsonify({"data": data})
    return render_template("customer_board.html", data=data)


# 顾客看航班,顾客选择出发地、目的地、日期查询航班（已完成）
@app.route('/customer/flight', methods=['GET', 'POST'])
def customer_flight():
    conn = pymysql.connect(host="127.0.0.1", port=3306, user='root', passwd='root123', charset='utf8', db='aviation',
                           cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    if request.method == 'GET':
        sql = "SELECT * FROM flight "
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()
        conn.close()

        # 转换数据为 JSON 格式并返回
        # return jsonify({"data": data})
        return render_template("customer_flight.html", data=data)

    departure = request.form.get("departure")
    terminal = request.form.get("terminal")
    leaveDate = request.form.get("leaveDate")

    sql = "SELECT * FROM flight where departure=%s && terminal=%s && date_format(leaveTime,'%%Y-%%m-%%d')=%s"
    cursor.execute(sql, [departure, terminal, leaveDate])
    data = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("customer_flight.html", data=data)


# 顾客买机票（已完成）
@app.route('/customer/flight/buy', methods=['GET', 'POST'])
def customer_buy():
    flight_id = request.args.get('nid')
    flight_id = int(flight_id)

    conn = pymysql.connect(host="127.0.0.1", port=3306, user='root', passwd='root123', charset='utf8', db='aviation',
                           cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    if request.method == 'GET':
        sql = "select leftTicket from flight where id=%s"
        cursor.execute(sql, [flight_id])
        data = cursor.fetchone()
        if data["leftTicket"] == 0:
            return "票卖光了，无法购买！"
        return render_template('buy_ticket.html')  # 购买机票的页面

    # 获取顾客输入的姓名、手机号、座位号
    passengerName = request.form.get("passengerName")
    passengerPhone = request.form.get("passengerPhone")
    seatNumber = request.form.get("seatNumber")
    paidTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    # 获取公司、票价
    sql = "select company,ticketMoney,leftTicket from flight where id=%s"
    cursor.execute(sql, [flight_id])
    data = cursor.fetchone()
    company = data["company"]
    ticketMoney = data["ticketMoney"]
    data["leftTicket"] -= 1
    customer_id = session.get("id")

    sql = "insert into ticket(customeruser,flight,company,seatNumber,passengerName,passengerPhone,paidMoney,paidTime) values(%s,%s,%s,%s,%s,%s,%s,%s)"
    cursor.execute(sql,
                   [customer_id, flight_id, company, seatNumber, passengerName, passengerPhone, ticketMoney, paidTime])
    conn.commit()

    # 航班剩余票数-1
    sql = "update flight set leftTicket=%s where id=%s"
    cursor.execute(sql, [data["leftTicket"], flight_id])
    conn.commit()
    conn.close()
    cursor.close()

    # return jsonify({"msg": "购买成功！"})
    return redirect("/customer/ticket")  # 返回顾客看已购机票的页面


# 顾客看自己买的机票（已完成）
@app.route('/customer/ticket', methods=['GET'])
def customer_ticket():
    # 获取顾客id  id=
    customer_id = session.get("id")

    conn = pymysql.connect(host="127.0.0.1", port=3306, user='root', passwd='root123', charset='utf8', db='aviation',
                           cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    sql = "SELECT * FROM ticket where customeruser=%s"
    cursor.execute(sql, [customer_id])
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    # 转换数据为 JSON 格式并返回
    # return jsonify({"data": data})
    return render_template("self_ticket.html", data=data)


# 顾客退票（已完成）
@app.route('/customer/refund', methods=['GET'])
def customer_refund():
    # 获取机票id ticket_id=
    ticket_id = request.args.get('nid')
    ticket_id = int(ticket_id)

    conn = pymysql.connect(host="127.0.0.1", port=3306, user='root', passwd='root123', charset='utf8', db='aviation',
                           cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    sql = "delete from ticket where id=%s"
    cursor.execute(sql, [ticket_id])
    conn.commit()
    cursor.close()
    conn.close()

    # 转换数据为 JSON 格式并返回
    # return jsonify({"msg": "退票成功！"})
    return redirect("/customer/ticket")


# 显示顾客个人信息（已完成）
@app.route('/customer/show', methods=['GET'])
def customer_show():
    customer_id = session.get("id")

    conn = pymysql.connect(host="127.0.0.1", port=3306, user='root', passwd='root123', charset='utf8', db='aviation',
                           cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    sql = "select * from customeruser where id=%s"
    cursor.execute(sql, [customer_id])
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("customer_show.html", data=data)


# 顾客改自己信息（已完成）
@app.route('/customer/modify', methods=['GET', 'POST'])
def customer_modify():
    if request.method == 'GET':
        return render_template('customer_modify.html')  # 修改信息的页面

    # 获取顾客输入用户名、密码
    userName = request.form.get("userName")
    password = request.form.get("password")
    customer_id = session.get("id")

    conn = pymysql.connect(host="127.0.0.1", port=3306, user='root', passwd='root123', charset='utf8', db='aviation',
                           cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    sql = "update customeruser set userName=%s, password=%s where id=%s"
    cursor.execute(sql, [userName, password, customer_id])
    conn.commit()
    cursor.close()
    conn.close()

    # 转换数据为 JSON 格式并返回
    # return jsonify({"msg": "修改成功！"})
    return redirect("/customer/show")  # 显示顾客个人信息的页面


# 机场管理员看公告（已完成）
@app.route('/airportuser/board', methods=['GET'])
def airportuser_board():
    conn = pymysql.connect(host="127.0.0.1", port=3306, user='root', passwd='root123', charset='utf8', db='aviation',
                           cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    sql = "SELECT * FROM board;"
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    # 转换数据为 JSON 格式并返回
    # return jsonify({"data": data})
    return render_template('airportuser_board.html', data=data)


# 机场管理员加公告（已完成）
@app.route('/airportuser/board/add', methods=['GET', 'POST'])
def board_add():
    if request.method == 'GET':
        return render_template('board_add.html')  # 购买机票的页面

    # 获取机场管理员输入的航班号、截止日期、内容
    flight = request.form.get("flight")
    dueTime = request.form.get("dueTime")
    content = request.form.get("content")

    conn = pymysql.connect(host="127.0.0.1", port=3306, user='root', passwd='root123', charset='utf8', db='aviation',
                           cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    sql = "insert into board(flight, dueTime, content) values(%s,%s,%s);"
    cursor.execute(sql, [flight, dueTime, content])
    conn.commit()
    cursor.close()
    conn.close()

    # 转换数据为 JSON 格式并返回
    # return jsonify({"msg": "添加成功！"})

    return redirect('/airportuser/board')  # 返回机场管理员看公告的页面


# 机场管理员删公告（已完成）
@app.route('/airportuser/board/delete', methods=['GET'])
def board_delete():
    # 获取公告id
    board_id = request.args.get('nid')
    board_id = int(board_id)

    conn = pymysql.connect(host="127.0.0.1", port=3306, user='root', passwd='root123', charset='utf8', db='aviation',
                           cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    sql = "delete from board where id=%s;"
    cursor.execute(sql, [board_id])
    conn.commit()
    cursor.close()
    conn.close()

    # 转换数据为 JSON 格式并返回
    # return jsonify({"msg": "删除成功！"})

    return redirect('/airportuser/board')  # 返回机场管理员看公告的页面


# 机场管理员看航班 //只能看到管理员所在机场的航班
@app.route('/airportuser/flight', methods=['GET'])
def airportuser_flight():
    conn = pymysql.connect(host="127.0.0.1", port=3306, user='root', passwd='root123', charset='utf8', db='aviation',
                           cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    # 根据管理员id查到所属机场id airport_id
    customer_id = session.get("id")
    sql1 = "select airport from airportuser where id=%s"
    cursor.execute(sql1, [customer_id])
    data1 = cursor.fetchone()
    # 根据管理员所属机场id查到机场名airportName
    sql2 = "select airportname from airport where id=%s"
    cursor.execute(sql2, [data1["airport"]])
    data2 = cursor.fetchone()

    sql = "SELECT * FROM flight where departure=%s || terminal=%s"
    cursor.execute(sql, [data2["airportname"], data2["airportname"]])
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    # 转换数据为 JSON 格式并返回
    # return jsonify({"data": data})
    return render_template("airportuser_flight.html", data=data)


# 机场管理员加航班 //只能加与管理员所在机场有关的航班
@app.route('/airportuser/flight/add', methods=['GET', 'POST'])
def flight_add():
    if request.method == 'GET':
        return render_template('flight_add.html')  # 购买机票的页面
    # 获取机场管理员输入的航班信息
    plane = request.form.get("plane")
    departure = request.form.get("departure")
    terminal = request.form.get("terminal")
    leaveTime = request.form.get("leaveTime")
    arriveTime = request.form.get("arriveTime")
    totalTicket = request.form.get("totalTicket")
    ticketMoney = request.form.get("ticketMoney")
    company = request.form.get("company")

    conn = pymysql.connect(host="127.0.0.1", port=3306, user='root', passwd='root123', charset='utf8', db='aviation',
                           cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    # 判断管理员添加的航班是不是与管理员机场有关的航班
    # 根据管理员id查到所属机场id airport_id
    customer_id = session.get("id")
    sql1 = "select airport from airportuser where id=%s"
    cursor.execute(sql1, [customer_id])
    data1 = cursor.fetchone()
    # 根据管理员所属机场id查到机场名airportName
    sql2 = "select airportname from airport where id=%s"
    cursor.execute(sql2, [data1["airport"]])
    data2 = cursor.fetchone()
    if departure!=data2["airportname"] and terminal!=data2["airportname"]:
        return '<script> alert("请添加与本人所属机场有关的航班！");window.open("/url");</script>'


    sql = "insert into flight(plane, departure, terminal,leaveTime,arriveTime,totalTicket,leftTicket,ticketMoney,company) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    cursor.execute(sql,
                   [plane, departure, terminal, leaveTime, arriveTime, totalTicket, totalTicket, ticketMoney, company])
    conn.commit()
    cursor.close()
    conn.close()

    # 转换数据为 JSON 格式并返回
    # return jsonify({"msg": "添加成功！"})
    return redirect('/airportuser/flight')  # 返回机场管理员看航班的页面


# 机场管理员删航班
@app.route('/airportuser/flight/delete', methods=['GET'])
def flight_delete():
    # 获取航班id
    flight_id = request.args.get('nid')
    flight_id = int(flight_id)

    conn = pymysql.connect(host="127.0.0.1", port=3306, user='root', passwd='root123', charset='utf8', db='aviation',
                           cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    sql = "delete from flight where id=%s"
    cursor.execute(sql, [flight_id])
    conn.commit()
    cursor.close()
    conn.close()

    # 转换数据为 JSON 格式并返回
    # return jsonify({"msg": "删除成功！"})
    return redirect('/airportuser/flight')  # 返回机场管理员看航班的页面


if __name__ == '__main__':
    app.run(debug=True)
