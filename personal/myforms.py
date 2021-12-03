from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField,TextAreaField
from wtforms import validators
from wtforms.validators import DataRequired, Email, Length
from flask_wtf.file import FileField,FileAllowed


class InvitationForm(FlaskForm):
    ivcard = FileField("Upload I.V: ",validators=[FileAllowed(upload_set=['pdf'],message="Upload a valid IV")])
    msg = StringField("Message ")
    submit= SubmitField("Upload")



class PostForm(FlaskForm):
    title =StringField("Post Title: ",validators=[DataRequired(message='Post title is compulsory')])
    desc =StringField("Description: ",validators=[DataRequired(message='Description is compulsory')])
    mssg =TextAreaField("Content: ",validators=[DataRequired(message='Put a valid content')])
    submit=SubmitField("Submit Post")

    


#d main syntax is variable = FieldType('label',validator=[])    