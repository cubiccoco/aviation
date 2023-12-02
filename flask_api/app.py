from flask import Flask, jsonify, request, redirect, render_template
import pymysql
import time

app = Flask(__name__)

USER = {
    "id": "1",
    "name": "",

}


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
    return jsonify({"data": data})


# 顾客看所有航班（已完成）
@app.route('/customer/flight', methods=['GET'])
def customer_flight():
    conn = pymysql.connect(host="127.0.0.1", port=3306, user='root', passwd='root123', charset='utf8', db='aviation',
                           cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    sql = "SELECT * FROM flight;"
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    # 转换数据为 JSON 格式并返回
    return jsonify({"data": data})


# 顾客看自己买的机票（已完成）
@app.route('/customer/ticket', methods=['GET'])
def customer_ticket():
    # 获取顾客id  id=

    conn = pymysql.connect(host="127.0.0.1", port=3306, user='root', passwd='root123', charset='utf8', db='aviation',
                           cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    sql = "SELECT * FROM ticket where customeruser=%s"
    cursor.execute(sql, [USER["id"]])
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
    conn = pymysql.connect(host="127.0.0.1", port=3306, user='root', passwd='root123', charset='utf8', db='aviation',
                           cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    sql = "select * from customeruser where id=%s"
    cursor.execute(sql, [USER["id"]])
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("customer_show.html", data=data)


# 顾客改自己用户名、密码（已完成）
@app.route('/customer/modify', methods=['GET', 'POST'])
def customer_modify():
    if request.method == 'GET':
        return render_template('customer_modify.html')  # 修改信息的页面

    # 获取顾客输入用户名、密码
    userName = request.form.get("userName")
    password = request.form.get("password")

    conn = pymysql.connect(host="127.0.0.1", port=3306, user='root', passwd='root123', charset='utf8', db='aviation',
                           cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    sql = "update customeruser set userName=%s, password=%s where id=%s"
    cursor.execute(sql, [userName, password, USER["id"]])
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


if __name__ == '__main__':
    app.run(debug=True)
