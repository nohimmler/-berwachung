import poplib
import smtplib
import time
import os
import email
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import email.mime.application
from email.mime.text import MIMEText
from ftplib import FTP
import RPi.GPIO as GPIO
import socket

def ReadConfig():
        global SensorPin
        global username 
        global userpass
        global popserver 
        global smtpserver
        global SenderAddr
        global SubjectPic
        global SubjectVid
        global MailText
        global intervall
        global ftpserver
        global ftpuser
        global ftppwd
        global ftpfile
        global ftpfile
        global picfile
        global vidfile
        global picwidth
        global picheight
        global vidwidth
        global vidheight
        global ftpMode
        global vidtime
        global loctime
        global loctimestring
        global vidmailrec
        global saveon

        loctime = time.localtime()
        loctimestring = time.strftime("%d-%m-%Y-%H-%M", loctime)
        
        configfile = open('config')
        
        for i in configfile:
                if "username" in i:
                        username = str(i[i.find('=')+1:i.find('\n')])
                if "userpass" in i:
                        userpass = str(i[i.find('=')+1:i.find('\n')])
                if "popserver" in i:
                        popserver = str(i[i.find('=')+1:i.find('\n')])
                if "smtpserver" in i:
                        smtpserver = str(i[i.find('=')+1:i.find('\n')])
                if "SenderAddr" in i:
                        SenderAddr = str(i[i.find('=')+1:i.find('\n')])
                if "Subjectvid" in i:
                        SubjectVid = str(i[i.find('=')+1:i.find('\n')])
                if "Subjectpic" in i:
                        SubjectPic = str(i[i.find('=')+1:i.find('\n')])
                if "MailText" in i:
                        MailText = str(i[i.find('=')+1:i.find('\n')])
                if "intervall" in i:
                        intervall = int(i[i.find('=')+1:i.find('\n')])
                if "ftpserver" in i:
                        ftpserver = str(i[i.find('=')+1:i.find('\n')])
                if "ftpuser" in i:
                        ftpuser = str(i[i.find('=')+1:i.find('\n')])
                if "ftppwd" in i:
                        ftppwd = str(i[i.find('=')+1:i.find('\n')])
                if "ftpfile" in i:
                        ftpfile = str(i[i.find('=')+1:i.find('\n')])
                if "picfile" in i:
                        picfile = str(i[i.find('=')+1:i.find('\n')])
                if "picwidth" in i:
                        picwidth = str(i[i.find('=')+1:i.find('\n')])
                if "picheight" in i:
                        picheight = str(i[i.find('=')+1:i.find('\n')])
                if "vidfile" in i:
                        filename = str(i[i.find('=')+1:i.find('\n')])
                if "vidwidth" in i:
                        vidwidth = str(i[i.find('=')+1:i.find('\n')])                      
                if "vidmail" in i:
                        vidmailrec = str(i[i.find('=')+1:i.find('\n')])
                if "vidheight" in i:
                        vidheight = str(i[i.find('=')+1:i.find('\n')])
                if "vidtime" in i:
                        vidtime = int(i[i.find('=')+1:i.find('\n')])
                if "saveon" in i:
                        saveon = str(i[i.find('=')+1:i.find('\n')])
                if "sensorpin" in i:
                        SensorPin = int(i[i.find('=')+1:i.find('\n')])
                if "ftpMode" in i:
                        i = str(i[i.find('=')+1:i.find('\n')])
                        if i.upper() == 'YES':
                                ftpMode = True
                        else:
                                ftpMode = False                 
        configfile.close()
        
        if saveon == 'usb':
                path = '/media/pi/LAUFWERK/'
                vidfile = path + filename
                print(vidfile)
        elif saveon == 'sdcard':
                vidfile = filename
        else:
                pass

def RestartRPI(timer):
        os.system("sudo shutdown -r " + str(timer))

def SetupGpio():
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(SensorPin,GPIO.IN)

def CheckForMove():
        SetupGpio()
        print(GPIO.input(SensorPin))
        if GPIO.input(SensorPin)== 0:
                pass
        else:
                print('Bewegung')
                TakeVid()

def GetAddrFromMail(string):
        intFrom = string.find('<') + 1
        intTo = string.find('>')
        SenderAddr = str(string[intFrom:intTo])
        print("Absender: "+SenderAddr)
        return(SenderAddr)
    
def CheckForNewMail():
        pop = poplib.POP3(popserver)
        time.sleep(0.5)
        print(pop.user(username))
        time.sleep(0.5)
        print(pop.pass_(userpass))
        time.sleep(0.5)
        print(pop.stat())
        mail = str(pop.stat())
        if mail != "(0, 0)":
            print("Mail eingegangen")
            print(pop.list(1))
            ReciverAddr = GetAddrFromMail(str(pop.retr(1)))
            TakePic()
            if SendMailPic(ReciverAddr):
                    print(pop.dele(1))
                    print("Mail geloescht")
            else:
                    print("Mail nicht geloescht")
        else:
            print("keine neue Mail")
        print(pop.quit())

def TakePic():
        global picfileloc
        loctime = time.localtime()
        loctimestring = time.strftime("%d-%m-%Y-%H-%M", loctime)
        picfileloc = picfile + loctimestring + ".jpg"
        
        os.system("raspistill -o " +
                  picfileloc +
                  " -n -t 1 -w " +
                  picwidth + " -h " +
                  picheight)
        print("Bild erstellt!")

def TakeVid():
        loctime = time.localtime()
        loctimestring = time.strftime("%d-%m-%Y-%H-%M", loctime)
        vidfileloc = vidfile + loctimestring + ".h264"
        
        #vidtime in millisekunden konvertien
        if vidtime == 0:
                # wenn keine zeit def. wurde wird 60 sekunden aufgenommen
                vidtimemillisec = 60000
        else:
                vidtimemillisec = vidtime * 1000
        print("Aufnahme gestartet")
        os.system("raspivid -o " +
                  vidfileloc +
                  " -w " +
                  vidwidth + " -h " +
                  vidheight + " -t " +
                  str(vidtimemillisec))
        print("Video erstellt!")
        SendMailVid(vidmailrec)

def SendMailVid(ReciverAddr):
        msg = MIMEMultipart()
        msg['Subject'] = SubjectVid
        msg['From'] = SenderAddr
        msg['To'] = ReciverAddr

        try:
                smtp = smtplib.SMTP(smtpserver, 587)
                smtp.login(username,userpass)
                print("versenden")
                print(smtp.sendmail(SenderAddr,ReciverAddr,msg.as_string()))
                print("Mail gesendet")
                smtp.quit()
                return(True)    
        except:
                print("Mail konnte nicht gesendet werden!")
                return(False)
        
def SendMailPic(ReciverAddr):  
    msg = MIMEMultipart()
    msg['Subject'] = SubjectPic
    msg['From'] = SenderAddr
    msg['To'] = ReciverAddr
    part = MIMEText("Test Anhang")
    msg.attach(part)

    fp = open(picfileloc, 'rb')
    att = email.mime.application.MIMEApplication(fp.read(),_subtype=type)
    att.add_header('Content-Disposition','attachment',filename=picfileloc)
    msg.attach(att)
    fp.close()

    try:
            smtp = smtplib.SMTP(smtpserver, 587)
            smtp.login(username,userpass)
            print("versenden")
            print(smtp.sendmail(SenderAddr,ReciverAddr,msg.as_string()))
            print("Mail gesendet")
            smtp.quit()
            return(True)    
    except:
            print("Mail konnte nicht gesendet werden!")
            return(False)
        
def ftpstore():
        ftp = FTP(ftpserver)
        ftp.login(user=ftpuser,passwd=ftppwd)
        ftp.cwd('Public')
        ftp.storbinary('STOR /Public/'+ftpfile, open(ftpfile))
        ftp.quit()
        
def ftprecive():
        ftp = FTP(ftpserver)
        ftp.login(user=ftpuser,passwd=ftppwd)
        ftp.cwd('Public')
        ftp.retrbinary('RETR /Public/'+ftpfile, open(ftpfile, 'wb').write)
        ftp.dir()
        ftp.quit()

def RunMain():
        RestartRPI(120)
        ReadConfig()
        i = 0
        intervallInt = intervall * 10
        while True:
                #print(str(i))
                if i == intervallInt:
                        i = 0
                        CheckForNewMail()
                else:
                        i += 1
                        time.sleep(0.1)
                        CheckForMove()
                        
if __name__ == '__main__':
        RunMain()
        #ReadConfig()
        #while True:
        #        time.sleep(0.5)
        #        CheckForMove()
