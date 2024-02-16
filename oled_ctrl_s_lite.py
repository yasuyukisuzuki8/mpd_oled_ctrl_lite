#!/usr/bin/python
#-*- coding: utf-8 -*-
'''
This is a light version of oled_ctrl_s_20220323.py
https://nw-electric.way-nifty.com/blog/2022/03/post-302231.html
'''

'''
https://akizukidenshi.com/catalog/g/g108276/
'''

''' for Music Player Damon   Pi4   OLED SO1602AW  3.3V I2C 16x2
sudo apt-get update
sudo apt-get install python-smbus
'''
import time
#--> import commands
import subprocess
import smbus
import sys
import re
import socket

host = 'localhost'     # localhost
port = 6600            # mpd port
bufsize = 1024

STOP = 0
PLAY = 1
PAUSE = 2
MSTOP = 1    # Scroll motion stop time 

class i2c(object):
    def __init__(self):
        self.bus = smbus.SMBus(1)
        self.addr = 0x3c          # OLED i2s address
        self.state = STOP         # state
        self.shift = 0            # Scroll shift value
        self.retry = 20           # retry for initialize
        self.old_line1 = " "      # old str 1
        self.old_line2 = " "      # old str 2
        self.old_vol = " "        # old volume
        self.init()

# initialize OLED 
    def init(self):
        while self.retry > 0:
            try:
                self.bus.write_byte_data(self.addr, 0, 0x0c) # Display ON
                self.line1("Music           ")
                self.line2("  Player Daemon ",0)
            except IOError:
                self.retry = self.retry -1
                time.sleep(0.5)
            else:
                return 0
        else:
            sys.exit()

# mpd version 
    def ver_disp(self, ver):
        ver = ver.replace(r"Music Player Daemon ", "")
        self.line1("MPD Version    ")
#-->    self.line2("        "+ver+"  ",0)
        self.line2(ver, 0)
        
# line1 send ascii data 
    def line1(self, str):
        if str != self.old_line1:
            self.old_line1 = str
        else:
            return 0
        try:
            self.bus.write_byte_data(self.addr, 0, 0x80) 
#-->        vv = map(ord, list(str))
            vv = list(map(ord, str))
            self.bus.write_i2c_block_data(self.addr, 0x40, vv)
        except IOError:
            return -1

# line2 send ascii data and Scroll 
    def line2(self, str, sp):
        try:
            self.bus.write_byte_data(self.addr, 0, 0xA0) 
            self.maxlen = len(str) +MSTOP
            if sp < MSTOP:
               sp = 0
            else:
               sp = sp -MSTOP -1
            if self.maxlen > sp + 16:
                self.maxlen = sp + 16
        
            moji = str[sp:self.maxlen]
#-->        moji = map(ord, moji)
            moji = list(map(ord, moji))
            self.bus.write_i2c_block_data(self.addr, 0x40, moji) 
        except IOError:
            return -1

# Display Control 
    def disp(self):
#-->    self.soc.send('status\n')
        self.soc.send(b'status\n')
#-->    st = self.soc.recv(bufsize)
        st = self.soc.recv(bufsize).decode()
        st_list = st.splitlines()

        bitr_val = audio_val = time_val = vol_val = state_val = samp_val = bit_val = ""
        
        for line in range(0,len(st_list)):
            
            # Volume
            if st_list[line].startswith(r"volume: "):
                vol_val = st_list[line]
                vol_val = vol_val.replace("volume: ", "")
                vol_val = "%2d" %int(vol_val)
                vol_val = str(vol_val)+' '
            
            # Play status
            if st_list[line].startswith(r"state: "): # stop play pause
                state_val = st_list[line]
                state_val = state_val.replace("state: ", "")
                
            # Plaing time
            if st_list[line].startswith(r"time: "):
                time_val = st_list[line]
                time_val = time_val.replace("time: ", "")
                time_val = re.split(':',time_val)
                time_val = int(time_val[0])
                time_min = time_val/60
                time_sec = time_val%60
                time_min = "%2d" %time_min
                time_sec = "%02d" %time_sec
                time_val = str(time_min)+":"+str(time_sec)
            
            # Bitrate
            if st_list[line].startswith(r"bitrate: "):
                bitr_val = st_list[line]
                bitr_val = bitr_val.replace("bitrate: ", "")
                bitr_val = bitr_val +'k'
            
            # Sampling rate / bit 
            if st_list[line].startswith(r"audio: "):
                audio_val = st_list[line]
                audio_val = audio_val.replace("audio: ", "")
                audio_val = re.split(':',audio_val)
                
                if audio_val[0] == '44100':
                    samp_val = '44.1k'
                elif audio_val[0] == '48000':
                    samp_val = '48k'
                elif audio_val[0] == '88200':
                    samp_val = '88.2k'
                elif audio_val[0] == '96000':
                    samp_val = '96k'
                elif audio_val[0] == '176400':
                    samp_val = '176.4k'
                elif audio_val[0] == '192000':
                    samp_val = '192k'
                elif audio_val[0] == '352800':
                    samp_val = '352.8k'
                elif audio_val[0] == '384000':
                    samp_val = '384k'
                else:
                    samp_val = ''
                    
                if audio_val[1] == 'dsd':
                    samp_val = bitr_val

                bit_val = audio_val[1]+'bit '
                if audio_val[1] == 'dsd':
                    bit_val = '1 bit '

        # stop
        if state_val == 'stop':
            # get IP address
#-->        ad = commands.getoutput('ip route')
            ad = subprocess.getoutput('ip route')
            ad_list = ad.splitlines()
            #addr_line = re.search('\d+\.\d+\.\d+\.\d+.$', ad_list[1])
            #addr_line = re.search('\d+\.\d+\.\d+\.\d+\s', ad_list[1])
            addr_line = re.search('\d+\.\d+\.\d+\.\d+\s', ad_list[-1])
            addr_str = addr_line.group()

        # Volume string
        if self.old_vol != vol_val:
            self.old_vol = vol_val
            self.vol_disp = 5
        else:
            if self.vol_disp != 0:
                self.vol_disp = self.vol_disp -1

        
        # Volume and status for Line1 
        if state_val == 'stop':
            if self.vol_disp != 0:
                self.line1("STOP     Vol:"+vol_val)
            else:
                self.line1("STOP             ")
            self.line2(addr_str+"        ",0)
            self.old_line2 = " "
        elif state_val == 'play':
#-->        if self.vol_disp != 0:
            self.line1("PLAY     Vol:"+vol_val)
#-->        else:
#-->            self.line1("PLAY      "+time_val+"  ")
        elif state_val == 'pause':
            if self.vol_disp != 0:
                self.line1("PAUSE    Vol:"+vol_val)
            else:
                self.line1("PAUSE     "+time_val+"  ")
        
        # sample rate for Line2 (Light version0) 
        if state_val != 'stop':
#-->        song_txt = self.song()
            sampbit_txt = samp_val+'/'+bit_val+' '
            sampbit_txt = sampbit_txt.rjust(17)
            if sampbit_txt != self.old_line2:
                self.old_line2 = sampbit_txt
                self.shift = 0
            self.line2(self.old_line2, self.shift)

# Soket Communication
    def soket(self):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.connect((host, port))
        aaa = self.soc.recv(bufsize).decode()

def main():
    oled = i2c()
    netlink = False
    time.sleep(1)
#--> ver = commands.getoutput('mpd -V')
    ver = subprocess.getoutput('mpd -V')
    ver_list = ver.splitlines()
    oled.ver_disp(ver_list[0])
    time.sleep(2)
    
    while netlink is False:
#-->    ip = commands.getoutput('ip route')
        ip = subprocess.getoutput('ip route')
        ip_list = ip.splitlines()
        if len(ip_list) >= 1:
            netlink = True
        else:
            time.sleep(1)

    oled.soket()
    
    first = True # First exec of the while loop
    while True:
        if first == True:
            time.sleep(1)
            oled.disp()
            first = False
        else:
            oled.soc.send(b'idle\n')
            ret = oled.soc.recv(bufsize).decode()
        try:
            oled.disp()
        except socket.error:
#-->        print "socket.error"
            print("socket.error")
            oled.soket()
            time.sleep(1)
        pass

if __name__ == '__main__':
        main()
