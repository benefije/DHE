# -*- coding: utf-8 -*-
"""
@author: quentin
@descript: We meet again, at last.
"""

import meet
import time
import threading as th
import sharedMem as shm

if __name__ == "__main__":
	IPobi = "172.20.11.199"
	PORT = 9559
	meet.main(IPobi,PORT,"obi")

	# status_obi = shm.sharedMem([0,[0.,0.,0.,0.]])
	# mutex_obi = th.Lock()
	# obi = th.Thread(None, meet.main, "Vision", ( IPobi,PORT,"obi"), {})
	# obi.start()
	
	# time.sleep(1)
	
	# IPdark = "172.20.11.131"
	# PORT = 9559

	# status_dark = shm.sharedMem([0,[0.,0.,0.,0.]])
	# mutex_dark = th.Lock()
	# dark = th.Thread(None, meet.main, "Vision", ( IPdark,PORT,"dark"), {})
	# dark.start()