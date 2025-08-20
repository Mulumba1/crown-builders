import smtplib

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('talk2mulumba@gmail.com', 'pacn fpuf pinl iszm')
print("SMTP connection successful!")
server.quit()