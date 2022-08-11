import openai
import re
from flask import Flask,render_template,redirect,url_for,request,send_from_directory
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, validators,SubmitField
from wtforms.validators import DataRequired, URL
from flask_sqlalchemy import SQLAlchemy
import os

openai.api_key = os.environ.get('MySecret')

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
Bootstrap(app)


class QuestionsForm(FlaskForm):
    q1 = StringField('1.',validators=[DataRequired()] )
    q2 = StringField('2.',validators=[DataRequired()])
    q3 = StringField('3.',validators=[DataRequired()])
    q4 = StringField('4.',validators=[DataRequired()])
    q5 = StringField('5.',validators=[DataRequired()])
    submit = SubmitField('관심도 측정 시작')

Positive_percent=0
Negative_percent=0
result_message = ''


@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])

@app.route('/',methods=["GET", "POST"])
def home():
    global Positive_percent
    global Negative_percent
    global result_message

    form = QuestionsForm()
    istrue=False
    if request.method == 'POST':
        istrue = True
        response = openai.Completion.create(
            model="text-davinci-002",
            prompt=f" \"{request.form.get('q1')}\""
                   f"\n2. \"{request.form.get('q2')}\""
                   f"\n3. \"{request.form.get('q3')}\""
                   f"\n4. \"{request.form.get('q4')}️\""
                   f"\n5. \"{request.form.get('q5')}\""

                   "\n\nTweet sentiment ratings:",
            temperature=0,
            max_tokens=60,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        print(response)
        text = response['choices'][0]['text']
        print(text)
        word_list = re.split('[\n. ]', text)
        print(word_list)
        word = []
        for a in word_list:
            if a == "Positive" or a == "Negative":
                word.append(a)

        print(word)

        Positive_count = 0
        Negative_count = 0
        answer_counter = len(word)

        for division in word:
            if division == "Positive":
                Positive_count += 1
            elif division == "Negative":
                Negative_count += 1
            else:
                pass

        Positive_percent = 100 * Positive_count / answer_counter
        Negative_percent = 100 * Negative_count / answer_counter

        print(Positive_count)
        print(Negative_count)
        print(Positive_percent)
        print(Negative_percent)
        # return redirect(url_for("home"))
        if Positive_percent > 70:
            result_message ='Ai 분석 결과 사람 사이의 관계는 성공할 가능성이 꽤 높은 것으로 보입니다. 그러나 이것이 당신이 열심히 일할 필요가 없다는 것을 의미하지는 않습니다. 초점과 헌신은 사랑만큼 관계에서 필요하다는 것을 기억하십시오.'
        elif Positive_percent > 50:
            result_message ='Ai 분석 결과 잠재적인 관계가 발전할 가능성은 낮지만 가능하다고 생각합니다. 가만히 앉아서 있기보단 상대방을 좀 더 자신을 알리세요!'
        elif Positive_percent > 30:
            result_message = 'Ai 분석 결과 성공적인 관계의 가능성은 그리 높지 않지만 충분한 노력과 시간이 있으면 여전히 가능합니다. 그러나 전혀 효과가 없을 수도 있음 알고 시도해주세요.'
        else:
            result_message = 'Ai 분석 결과 이어질 가능성이 전혀 없다고 하네요.. 빠르게 다른 사람을 찾아보세요. '
    return render_template("index.html",form=form,
                           istrue=istrue,
                           Positive_percent=Positive_percent,
                           Negative_percent=Negative_percent,
                           result_message=result_message)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)